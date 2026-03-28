"""LLM API를 이용한 자막 교정."""

from __future__ import annotations

from shared.api.claude import ask
from shared.constants import PROMPTS_DIR
from shared.lib.file_io import read_text
from shared.lib.logger import get_logger

logger = get_logger()

_PROMPT_PATH = PROMPTS_DIR / "subtitle_correction.txt"


def correct_subtitles_via_llm(
    original_script: str,
    subtitle_lines: list[str],
) -> dict[int, str]:
    """LLM에게 자막 교정을 요청.

    변경된 줄만 반환하여 토큰 사용량 절감.

    Args:
        original_script: 원본 대본 텍스트.
        subtitle_lines: 자막 텍스트 리스트 (index 순서).

    Returns:
        교정된 {index: text} 딕셔너리 (변경된 줄만 포함).
    """
    # 줄 번호 + 텍스트 형식으로 변환
    numbered_lines = "\n".join(
        f"{i + 1}|{text}" for i, text in enumerate(subtitle_lines)
    )

    prompt_template = read_text(_PROMPT_PATH)
    prompt = prompt_template.format(
        original_script=original_script,
        subtitle_lines=numbered_lines,
    )

    logger.info("자막 교정 요청 중...")
    response = ask(prompt)

    corrections = _parse_corrections(response)
    logger.info("자막 교정 완료: %d개 수정", len(corrections))
    return corrections


def _parse_corrections(text: str) -> dict[int, str]:
    """LLM 응답에서 교정 결과를 파싱.

    형식: "번호|교정된 텍스트" (줄 단위)

    Returns:
        {index: corrected_text} 딕셔너리.
    """
    corrections: dict[int, str] = {}

    # 코드 블록 제거
    content = text
    if "```" in content:
        parts = content.split("```")
        # 코드 블록 내부 추출
        for part in parts[1::2]:
            # 첫 줄이 언어 태그면 제거
            lines = part.strip().split("\n")
            if lines and "|" not in lines[0]:
                lines = lines[1:]
            content = "\n".join(lines)
            break

    for line in content.strip().split("\n"):
        line = line.strip()
        if not line or "|" not in line:
            continue

        parts = line.split("|", 1)
        if len(parts) != 2:
            continue

        try:
            index = int(parts[0].strip())
            corrected_text = parts[1].strip()
            if corrected_text:
                corrections[index] = corrected_text
        except ValueError:
            continue

    return corrections
