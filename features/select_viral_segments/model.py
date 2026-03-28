"""바이럴 구간 선정 모델."""

from __future__ import annotations

from pydantic import BaseModel


class _LLMViralSegment(BaseModel):
    """LLM 단일 호출 파싱용 (내부 전용)."""

    index: int
    start_time: float
    end_time: float
    hook_title: str
    viral_reason: str
    content_summary: str = ""


class _LLMViralPlan(BaseModel):
    """LLM 단일 호출 파싱용 (내부 전용)."""

    segments: list[_LLMViralSegment]


class ViralSegment(BaseModel):
    """최종 바이럴 구간 (구간 + 후킹 제목)."""

    index: int
    start_time: float  # SRT 기반 (초)
    end_time: float
    hook_title: str  # 1-2줄 훅 문구 (\n 구분)
    viral_reason: str  # 선정 근거 (로깅용)


class ViralSegmentPlan(BaseModel):
    """최종 바이럴 구간 선정 결과."""

    segments: list[ViralSegment]
