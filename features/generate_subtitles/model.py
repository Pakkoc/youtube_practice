"""자막 생성 모델."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class SubtitleEntry(BaseModel):
    """단일 자막 항목."""

    index: int
    start_time: float  # 초 단위
    end_time: float  # 초 단위
    text: str


class SubtitleResult(BaseModel):
    """자막 생성 결과."""

    entries: list[SubtitleEntry]
    srt_path: Path
    total_duration: float
