"""텍스트 정규화 — 발음 사전 치환 + 자막 표시 정규화."""

from __future__ import annotations

import re
from pathlib import Path

from shared.lib.logger import get_logger

from .model import TextPair

logger = get_logger()

# 한글 음절 블록 범위 (가-힣)
_HANGUL_SYLLABLE_RE = re.compile(r"[\uAC00-\uD7A3]")

# 프로젝트 루트의 config/tts_dictionary.yaml
_DEFAULT_DICTIONARY_PATH = Path(__file__).resolve().parents[2] / "config" / "tts_dictionary.yaml"


def load_tts_dictionary(path: Path | None = None) -> dict[str, str]:
    """YAML 발음 사전을 로드.

    Args:
        path: 사전 파일 경로. None이면 기본 경로 사용.

    Returns:
        {원문: 한글 발음} 딕셔너리.
    """
    dict_path = path or _DEFAULT_DICTIONARY_PATH
    if not dict_path.exists():
        logger.warning("TTS 발음 사전 없음: %s", dict_path)
        return {}

    try:
        import yaml

        with open(dict_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        pronunciation = data.get("tts_pronunciation", {})
        if pronunciation:
            logger.info("TTS 발음 사전 로드: %d개 항목", len(pronunciation))
        return pronunciation or {}

    except Exception as e:
        logger.warning("TTS 발음 사전 로드 실패: %s", e)
        return {}


def apply_tts_dictionary(text: str, dictionary: dict[str, str]) -> str:
    """발음 사전 기반으로 텍스트 내 단어를 치환.

    단어 경계 매칭으로 부분 일치를 방지합니다.
    대소문자를 구분하며, 긴 키부터 매칭합니다.

    Args:
        text: 원본 텍스트.
        dictionary: {원문: 한글 발음} 딕셔너리.

    Returns:
        치환된 텍스트.
    """
    if not dictionary or not text:
        return text

    result = text
    # 긴 키부터 매칭 (LangChain이 Lang보다 먼저 매칭되도록)
    for key in sorted(dictionary.keys(), key=len, reverse=True):
        replacement = dictionary[key]
        # 단어 경계 매칭: 영어 키는 \b, 한글 키는 한글 음절 경계 사용
        if key and key[0].isascii() and key[0].isalnum():
            pattern = re.compile(r"\b" + re.escape(key) + r"\b")
        elif _HANGUL_SYLLABLE_RE.match(key):
            pattern = re.compile(
                r"(?<![\uAC00-\uD7A3])" + re.escape(key) + r"(?![\uAC00-\uD7A3])"
            )
        else:
            pattern = re.compile(re.escape(key))
        new_result = pattern.sub(replacement, result)
        if new_result != result:
            logger.debug("TTS 사전 치환: '%s' -> '%s'", key, replacement)
            result = new_result

    return result


def normalize_for_display(texts: list[str]) -> list[str]:
    """자막 표시용 텍스트 정규화 (LLM 기반 일괄 처리).

    한글 숫자 → 아라비아 숫자, 영어 용어 원형 유지.
    모든 텍스트를 하나의 LLM 호출로 일괄 처리하여 비용 최소화.

    Args:
        texts: 원본 텍스트 목록.

    Returns:
        정규화된 텍스트 목록 (입력과 동일한 길이).
    """
    if not texts:
        return []

    # 한글 숫자가 포함된 텍스트가 있는지 확인
    korean_number_pattern = re.compile(r"[일이삼사오육칠팔구십백천만억조]+")
    has_korean_numbers = any(korean_number_pattern.search(t) for t in texts)

    if not has_korean_numbers:
        # 한글 숫자가 없으면 원본 그대로 반환
        logger.debug("한글 숫자 없음 — 자막 표시 정규화 건너뜀")
        return list(texts)

    try:
        from shared.api.claude import ask

        # 문단 번호로 구분하여 일괄 처리
        numbered_lines = []
        for i, text in enumerate(texts, 1):
            numbered_lines.append(f"[{i}] {text}")
        input_block = "\n".join(numbered_lines)

        system_prompt = (
            "You are a Korean subtitle text normalizer. "
            "Convert Korean number words to Arabic numerals for better readability.\n\n"
            "Rules:\n"
            "1. 한글 숫자 → 아라비아 숫자: 백만 → 100만, 삼십 → 30, 오천 → 5000, "
            "이십오 → 25, 삼백 → 300\n"
            "2. 숫자+단위 표기 통일: 삼십퍼센트 → 30%, 백만원 → 100만원, "
            "오십달러 → 50달러\n"
            "3. Keep English terms/abbreviations as-is (AI, API, Claude, etc.)\n"
            "4. Do NOT change anything else — preserve all non-number text exactly\n"
            "5. Output format: one line per input, with [N] prefix preserved\n"
            "6. Return ONLY the converted lines, nothing else."
        )

        result = ask(
            prompt=input_block,
            system=system_prompt,
            model="gpt-5.4-mini",
        )

        if not result or not result.strip():
            logger.warning("자막 표시 정규화 빈 응답 — 원본 사용")
            return list(texts)

        # 결과 파싱: [N] 접두사로 매칭
        normalized = list(texts)  # 기본값은 원본
        for line in result.strip().split("\n"):
            line = line.strip()
            match = re.match(r"\[(\d+)\]\s*(.*)", line)
            if match:
                idx = int(match.group(1)) - 1
                if 0 <= idx < len(texts):
                    normalized[idx] = match.group(2).strip()

        changed = sum(1 for o, n in zip(texts, normalized) if o != n)
        if changed:
            logger.info("자막 표시 정규화: %d/%d개 변경", changed, len(texts))

        return normalized

    except Exception as e:
        logger.warning("자막 표시 정규화 실패 (원본 사용): %s", e)
        return list(texts)


def build_reverse_dictionary(dictionary: dict[str, str]) -> dict[str, str]:
    """TTS 발음 사전의 역변환 맵 생성 (한글 발음 → 원문).

    자막 표시 시 한글 발음을 원어로 복원하는 데 사용.
    예: 클로드 → Claude, 엔에이트엔 → n8n

    Args:
        dictionary: {원문: 한글 발음} TTS 사전.

    Returns:
        {한글 발음: 원문} 역변환 사전.
    """
    if not dictionary:
        return {}
    return {v: k for k, v in dictionary.items()}


def apply_reverse_dictionary(text: str, reverse_dict: dict[str, str]) -> str:
    """역 발음 사전으로 한글 발음을 원어로 복원.

    Args:
        text: Whisper 전사 등 한글 발음이 포함된 텍스트.
        reverse_dict: build_reverse_dictionary()로 생성한 역변환 사전.

    Returns:
        원어가 복원된 텍스트.
    """
    if not reverse_dict or not text:
        return text

    result = text
    for key in sorted(reverse_dict.keys(), key=len, reverse=True):
        replacement = reverse_dict[key]
        # 한글 키: 어절 시작 위치에서만 매칭 (부분 일치 방지)
        # 예: "머지"가 "나머지" 내부에서 매칭되는 것을 방지
        if _HANGUL_SYLLABLE_RE.match(key):
            pattern = re.compile(r"(?<![\uAC00-\uD7A3])" + re.escape(key))
        else:
            pattern = re.compile(r"\b" + re.escape(key) + r"\b")
        new_result = pattern.sub(replacement, result)
        if new_result != result:
            logger.debug("역사전 복원: '%s' -> '%s'", key, replacement)
            result = new_result

    return result


def normalize_text(text: str, dictionary: dict[str, str]) -> TextPair:
    """TTS용 + 자막 표시용 텍스트를 모두 생성.

    Args:
        text: 원본 텍스트.
        dictionary: TTS 발음 사전.

    Returns:
        TextPair (original, tts_text, display_text).
    """
    tts_text = apply_tts_dictionary(text, dictionary)
    display_texts = normalize_for_display([text])
    return TextPair(
        original=text,
        tts_text=tts_text,
        display_text=display_texts[0],
    )
