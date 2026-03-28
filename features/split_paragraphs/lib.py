"""대본 문단 분리 핵심 로직."""

from __future__ import annotations

import re
from pathlib import Path

from entities.script.model import Paragraph, Script
from shared.lib.file_io import ensure_dir, read_text, write_text
from shared.lib.logger import get_logger

from .model import SplitConfig

logger = get_logger()


def preprocess_script(text: str) -> str:
    """다양한 형식의 대본을 표준 형식(빈 줄 구분)으로 전처리.

    지원 형식:
    - Markdown 헤더 (#, ##, ###)
    - 구분선 (---, ***, ___, ===)
    - 타임스탬프 ([00:00], [00:00:00], 0:00 -, 00:00:00 -)
    - 번호 매기기 (1., 2., 1), 2))
    - Windows/Unix 줄바꿈 혼합

    Args:
        text: 원본 대본 텍스트.

    Returns:
        전처리된 대본 텍스트 (빈 줄로 문단 구분).
    """
    original_length = len(text)

    # 1. 줄바꿈 정규화 (Windows → Unix)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Markdown 헤더 제거 (# 제목 → 제목, 단 줄 시작에서만)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # 3. 구분선을 문단 구분자로 변환
    # ---, ***, ___, === (3개 이상 연속)
    text = re.sub(r"^[-*_=]{3,}\s*$", "\n\n", text, flags=re.MULTILINE)

    # 4. 타임스탬프 제거
    # [00:00], [00:00:00], [0:00], [0:00:00]
    text = re.sub(r"\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*[-–—]?\s*", "", text)

    # 5. 줄 시작 번호 매기기 제거 (선택적)
    # "1. ", "2. ", "1) ", "2) ", "① ", "② "
    text = re.sub(r"^(?:\d+[.)]\s*|[①②③④⑤⑥⑦⑧⑨⑩]\s*)", "", text, flags=re.MULTILINE)

    # 6. 연속된 빈 줄을 2개로 정규화 (문단 구분자)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 7. 각 줄의 앞뒤 공백 제거 (줄 내용은 유지)
    lines = text.split("\n")
    lines = [line.strip() for line in lines]
    text = "\n".join(lines)

    # 8. 시작/끝 공백 제거
    text = text.strip()

    # 9. 최종 정규화: 연속 빈 줄 다시 정리
    text = re.sub(r"\n{3,}", "\n\n", text)

    processed_length = len(text)
    if original_length != processed_length:
        logger.debug(
            "대본 전처리: %d자 → %d자 (%d자 정리)",
            original_length,
            processed_length,
            original_length - processed_length,
        )

    return text


def _auto_detect_line_paragraphs(text: str, line_min_length: int = 40) -> str:
    """단일 줄바꿈으로 구분된 긴 줄들을 문단 구분자(빈 줄)로 변환.

    빈 줄(\\n\\n) 블록과 단일 줄바꿈(\\n) 블록이 혼합된 대본도 처리합니다.
    각 블록별로 독립적으로 80%/line_min_length 휴리스틱을 적용합니다.

    Args:
        text: 전처리된 대본 텍스트.
        line_min_length: 문단으로 인정할 최소 줄 길이 (문자 수).

    Returns:
        문단 구분자가 추가된 텍스트.
    """
    blocks = text.split("\n\n")
    result: list[str] = []

    for block in blocks:
        lines = [line for line in block.split("\n") if line.strip()]

        # 단일 줄 블록은 그대로
        if len(lines) < 2:
            result.append(block)
            continue

        # 긴 줄의 비율 확인 (80% 이상이 line_min_length 초과 시 적용)
        long_lines = [line for line in lines if len(line.strip()) >= line_min_length]
        if len(long_lines) / len(lines) >= 0.8:
            logger.info(
                "자동 문단 감지: %d개 줄을 개별 문단으로 분리",
                len(lines),
            )
            result.extend(line.strip() for line in lines)
        else:
            result.append(block)

    return "\n\n".join(result)


def _merge_splits(splits: list[str], max_length: int) -> list[str]:
    """분할된 조각들을 max_length 이하로 병합."""
    chunks: list[str] = []
    current = ""
    for s in splits:
        s = s.strip()
        if not s:
            continue
        candidate = f"{current} {s}".strip() if current else s
        if len(candidate) <= max_length:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = s
    if current:
        chunks.append(current)
    return chunks


def _split_long_paragraphs(text: str, max_length: int = 150) -> str:
    """과도하게 긴 문단을 한국어 문장 경계에서 분할.

    슬라이드에 담기 적합한 크기로 문단을 나눕니다.
    한국어 문장 종결 패턴(다., 요., 죠., 니다. 등)을 기준으로 분할합니다.

    Args:
        text: 대본 텍스트.
        max_length: 문단 최대 글자수.

    Returns:
        긴 문단이 분할된 텍스트.
    """
    paragraphs = text.split("\n\n")
    result = []

    for para in paragraphs:
        para = para.strip()
        if not para or len(para) <= max_length:
            result.append(para)
            continue

        # 한국어 문장 종결 패턴에서 분할
        # "다.", "요.", "죠." 등 + 물음표/느낌표 + 닫는 인용부호
        # ?!" ?" 등 인용부호 안 물음표는 인용부호까지 포함해서 분할
        # 단, ?"라고 / ?"하고 등 인용 종결 후 이어지는 문장은 분할하지 않음
        splits = re.split(
            r"(?<=[다요죠]\.)\s*"
            r'|(?<=[?!]["\u201D\u2019])(?!\s*(?:라고|라며|하고|하며|이라고))\s*'
            r'|(?<=[?!])(?!["\u201D\u2019])\s*',
            para,
        )

        chunks = _merge_splits(splits, max_length)

        # 문장 경계로 분할 실패한 청크 → 쉼표/마침표+공백 폴백
        final: list[str] = []
        for chunk in chunks:
            if len(chunk) > max_length:
                sub = re.split(r"(?<=[,.])\s+", chunk)
                final.extend(_merge_splits(sub, max_length))
            else:
                final.append(chunk)

        if len(final) > 1:
            logger.info(
                "긴 문단 분할: %d자 → %d개 문단 (%s)",
                len(para),
                len(final),
                ", ".join(f"{len(c)}자" for c in final),
            )

        result.extend(final)

    return "\n\n".join(result)


def split_script(
    script_text: str,
    config: SplitConfig | None = None,
    *,
    preprocess: bool = True,
) -> Script:
    """대본 텍스트를 문단으로 분리하여 Script 객체를 반환.

    Args:
        script_text: 전체 대본 텍스트.
        config: 분리 설정. None이면 기본값 사용.
        preprocess: 전처리 수행 여부 (기본: True).

    Returns:
        분리된 문단이 포함된 Script 객체.
    """
    if config is None:
        config = SplitConfig()

    # 전처리 (다양한 형식 → 표준 형식)
    if preprocess:
        script_text = preprocess_script(script_text)

    # 단일 줄바꿈으로 구분된 긴 줄 자동 감지
    if config.auto_detect_lines:
        script_text = _auto_detect_line_paragraphs(
            script_text, line_min_length=config.line_min_length
        )

    # 과도하게 긴 문단 자동 분할
    if config.max_paragraph_length > 0:
        script_text = _split_long_paragraphs(
            script_text, max_length=config.max_paragraph_length
        )

    raw_paragraphs = script_text.split(config.separator)

    paragraphs: list[Paragraph] = []
    idx = 1
    for raw in raw_paragraphs:
        text = raw.strip()
        if len(text) < config.min_length:
            continue
        paragraphs.append(Paragraph(index=idx, text=text))
        idx += 1

    logger.info("대본을 %d개 문단으로 분리 완료", len(paragraphs))
    return Script(raw_text=script_text, paragraphs=paragraphs)


def save_paragraphs(script: Script, output_dir: Path) -> list[Path]:
    """분리된 문단을 개별 파일로 저장.

    Args:
        script: 분리된 Script 객체.
        output_dir: 문단 파일 저장 디렉토리.

    Returns:
        저장된 파일 경로 목록.
    """
    ensure_dir(output_dir)
    saved: list[Path] = []

    for paragraph in script.paragraphs:
        file_path = output_dir / paragraph.filename
        write_text(file_path, paragraph.text)
        logger.debug("문단 저장: %s", file_path)
        saved.append(file_path)

    logger.info("%d개 문단 파일 저장: %s", len(saved), output_dir)
    return saved


def load_script_and_split(
    script_path: Path,
    output_dir: Path,
    config: SplitConfig | None = None,
) -> Script:
    """스크립트 파일을 읽어 문단 분리 후 파일로 저장.

    Args:
        script_path: 대본 파일 경로.
        output_dir: 문단 파일 저장 디렉토리.
        config: 분리 설정.

    Returns:
        분리된 Script 객체.
    """
    text = read_text(script_path)
    script = split_script(text, config)
    save_paragraphs(script, output_dir)
    return script
