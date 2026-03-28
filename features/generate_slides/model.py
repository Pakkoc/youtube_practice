"""슬라이드 생성 데이터 모델."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel


class SlideGenerationResult(BaseModel):
    """슬라이드 생성 결과."""

    index: int
    markdown: str
    md_path: Path | None = None
    png_path: Path | None = None
    video_path: Path | None = None
    paragraph_index: int | None = None  # 씬의 소속 문단 (씬 모드용)
    mode: Literal["freeform", "manim"] = "freeform"
    tsx_code: str | None = None
    manim_code: str | None = None
    plan: dict[str, Any] | None = None
