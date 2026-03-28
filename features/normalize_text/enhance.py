"""TTS 발음 사전 자동 강화 — 대본에서 영어/숫자를 스캔하여 한글 발음 자동 생성."""

from __future__ import annotations

import json
import re
from pathlib import Path

from entities.script.model import Paragraph
from shared.lib.logger import get_logger

logger = get_logger()

_DEFAULT_DICT_PATH = Path(__file__).resolve().parents[2] / "config" / "tts_dictionary.yaml"

# TTS가 잘 처리하는 짧은 영어 단어 (사전 등록 불필요)
_COMMON_WORDS = {
    "is", "the", "of", "and", "or", "in", "to", "for", "by", "at", "on",
    "it", "as", "an", "be", "do", "if", "so", "no", "up", "my", "we",
    "he", "me", "us", "am", "not", "but", "all", "can", "had", "has",
    "was", "are", "you", "his", "her", "its", "our", "who", "how",
    "new", "now", "may", "one", "two", "get", "got", "let", "say",
    "see", "use", "way", "day", "too", "any", "few", "old", "own",
    "set", "run", "try", "ask", "put", "end", "why", "big", "top",
    "also", "just", "than", "then", "them", "they", "this", "that",
    "with", "from", "been", "have", "will", "what", "when", "your",
    "more", "make", "like", "over", "such", "take", "each", "only",
    "very", "into", "some", "well", "back", "much", "good",
}


def enhance_tts_dictionary(
    paragraphs: list[Paragraph],
    dictionary: dict[str, str],
    *,
    model: str = "gpt-5.1",
) -> dict[str, str]:
    """대본 스캔 후 미등록 영어/숫자 발음을 LLM으로 생성하여 사전에 추가.

    Args:
        paragraphs: 분리된 문단 목록.
        dictionary: 기존 TTS 발음 사전 (in-place 수정됨).
        model: 발음 생성에 사용할 LLM 모델.

    Returns:
        업데이트된 발음 사전.
    """
    full_text = "\n\n".join(p.text for p in paragraphs)

    # 영어 단어 추출 (2글자 이상)
    english_words = set(re.findall(r"[A-Za-z]{2,}", full_text))
    english_words -= _COMMON_WORDS

    # 기존 사전에 없는 단어만 필터링
    dict_keys_lower = {k.lower() for k in dictionary}
    new_words = {w for w in english_words if w.lower() not in dict_keys_lower}

    if not new_words:
        logger.info("사전 강화: 미등록 영어 토큰 없음")
        return dictionary

    logger.info("사전 강화: %d개 미등록 영어 토큰 발견, LLM 분석 시작", len(new_words))

    try:
        from shared.api.claude import ask

        existing_sample = ", ".join(
            f"{k}={v}" for k, v in list(dictionary.items())[:30]
        )

        system = (
            "You are a Korean TTS pronunciation dictionary generator.\n"
            "Given a Korean script, find English words/phrases and number expressions "
            "that ElevenLabs TTS might mispronounce, and provide natural Korean pronunciations.\n\n"
            "Rules:\n"
            "- Brand names: commonly accepted Korean (OpenAI = 오픈에이아이)\n"
            "- Abbreviations: spell out each letter (API = 에이피아이, GPU = 지피유)\n"
            "- Technical terms: natural transliteration (Embedding = 임베딩)\n"
            "- Mixed alphanumeric: read naturally (H100 = 에이치백, RTX 5090 = 알티엑스 오천구십)\n"
            "- Version numbers: Korean reading (v2.1 = 버전 이쩜일, 3.0 = 삼쩜영)\n"
            "- Multi-word terms: transliterate as unit (Machine Learning = 머신러닝)\n"
            "- Skip terms already in the existing dictionary\n"
            "- Skip common English words TTS handles correctly (is, the, of, etc.)\n"
            "- Only include terms that appear in the script\n\n"
            "Output: JSON object only. {\"term\": \"korean_pronunciation\", ...}\n"
            "If no new terms needed, output: {}"
        )

        prompt = (
            f"## 기존 사전 (제외 대상):\n{existing_sample}\n\n"
            f"## 미등록 토큰 (참고):\n{', '.join(sorted(new_words)[:60])}\n\n"
            f"## 대본:\n{full_text[:6000]}\n\n"
            "TTS가 잘못 읽을 수 있는 영어/숫자 표현의 한글 발음을 JSON으로 반환하세요."
        )

        result = ask(prompt=prompt, system=system, model=model, max_tokens=2048)

        # JSON 파싱 (코드블록 또는 raw JSON)
        json_str = result.strip()
        if "```" in json_str:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", json_str, re.DOTALL)
            if match:
                json_str = match.group(1)
        else:
            match = re.search(r"\{[^{}]*\}", json_str, re.DOTALL)
            if match:
                json_str = match.group()

        new_entries: dict[str, str] = json.loads(json_str)

        if not new_entries:
            logger.info("사전 강화: LLM이 신규 항목 없음 판단")
            return dictionary

        # 중복 제거 후 병합
        added: dict[str, str] = {}
        for term, pronunciation in new_entries.items():
            if (
                term not in dictionary
                and isinstance(pronunciation, str)
                and pronunciation.strip()
            ):
                dictionary[term] = pronunciation.strip()
                added[term] = pronunciation.strip()

        if added:
            _append_to_dictionary(added)
            sample = ", ".join(f"{k}={v}" for k, v in list(added.items())[:5])
            logger.info("사전 강화 완료: %d개 추가 (%s)", len(added), sample)

        return dictionary

    except Exception as e:
        logger.warning("사전 강화 실패 (기존 사전 유지): %s", e)
        return dictionary


def _needs_quoting(key: str) -> bool:
    """YAML 키에 따옴표가 필요한지 확인."""
    if not key:
        return True
    try:
        float(key)
        return True
    except ValueError:
        pass
    if key.lower() in ("true", "false", "null", "yes", "no", "on", "off"):
        return True
    if key[0] in "#-[{&*!|>'\"%@`?":
        return True
    if ": " in key or key.endswith(":"):
        return True
    return False


def _append_to_dictionary(
    entries: dict[str, str], path: Path | None = None
) -> None:
    """사전 파일 끝에 새 항목 추가 (기존 파일 구조 보존)."""
    dict_path = path or _DEFAULT_DICT_PATH
    if not entries:
        return

    with open(dict_path, "a", encoding="utf-8") as f:
        f.write("\n")
        for key, value in entries.items():
            key_str = f'"{key}"' if _needs_quoting(key) else key
            f.write(f"  {key_str}: {value}\n")

    logger.info("TTS 사전 파일 업데이트: +%d개", len(entries))
