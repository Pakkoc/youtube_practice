"""바이럴 구간 선정 + 후킹 제목 생성 LLM API 호출."""

from __future__ import annotations

import json

from pydantic import ValidationError

from shared.api.claude import ask
from shared.constants import PROMPTS_DIR
from shared.lib.file_io import read_text
from shared.lib.logger import get_logger

from .model import (
    ViralSegment,
    ViralSegmentPlan,
    _LLMViralPlan,
)

logger = get_logger()

_PROMPT_PATH = PROMPTS_DIR / "viral_segment_selection.txt"

_SYSTEM = """당신은 유튜브 쇼츠/릴스 바이럴 전문가입니다.
조회수 100만 회 이상 쇼츠를 기획해 온 편집자로서,
긴 영상에서 바이럴 가능성이 높은 구간을 선별하고 후킹 제목까지 작성합니다.

핵심 원칙:
- 3초 훅 규칙: 첫 3초에 스크롤을 멈추게 하는 강력한 문장이 있어야 한다
- 자기완결성: 해당 구간만으로 맥락이 완전히 이해되어야 한다
- 감정 트리거: 호기심, 공감, 불안, 놀라움 중 하나 이상 자극해야 한다

반드시 JSON 형식으로만 출력하세요. 부가 설명 없이 JSON만 작성합니다."""


def select_viral_segments(
    srt_text: str,
    script_text: str,
    *,
    max_shorts: int,
    min_duration: int,
    max_duration: int,
    model: str = "gpt-5.4-mini",
) -> ViralSegmentPlan:
    """단일 LLM 호출로 바이럴 구간 선정 + 후킹 제목 생성.

    Args:
        srt_text: SRT 자막 전문.
        script_text: 대본 전문.
        max_shorts: 최대 쇼츠 수.
        min_duration: 최소 길이 (초).
        max_duration: 최대 길이 (초).
        model: 사용할 모델 ID.

    Returns:
        ViralSegmentPlan (구간 + 후킹 제목).
    """
    prompt_template = read_text(_PROMPT_PATH)

    prompt = prompt_template.replace("{srt_text}", srt_text)
    prompt = prompt.replace("{script_text}", script_text)
    prompt = prompt.replace("{max_shorts}", str(max_shorts))
    prompt = prompt.replace("{min_duration}", str(min_duration))
    prompt = prompt.replace("{max_duration}", str(max_duration))

    logger.info("바이럴 구간 선정 (max=%d, %d~%ds)", max_shorts, min_duration, max_duration)

    try:
        response = ask(
            prompt,
            system=_SYSTEM,
            model=model,
            max_tokens=8192,
        )
    except Exception as e:
        logger.error("바이럴 구간 선정 API 호출 실패: %s", str(e)[:300])
        raise

    try:
        parsed = _parse_json_response(response)
        llm_plan = _LLMViralPlan.model_validate(parsed)
        logger.info("바이럴 구간 선정 완료: %d개 구간", len(llm_plan.segments))
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error("바이럴 구간 파싱 실패: %s", str(e)[:200])
        raise

    # _LLMViralPlan → ViralSegmentPlan 변환
    segments = [
        ViralSegment(
            index=seg.index,
            start_time=seg.start_time,
            end_time=seg.end_time,
            hook_title=seg.hook_title,
            viral_reason=seg.viral_reason,
        )
        for seg in llm_plan.segments
    ]

    return ViralSegmentPlan(segments=segments)


def _parse_json_response(response: str) -> dict:
    """API 응답에서 JSON을 추출."""
    text = response.strip()

    if text.startswith("```json"):
        text = text[len("```json") :]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())
