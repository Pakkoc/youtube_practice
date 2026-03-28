"""아바타 생성 데이터 모델."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class AvatarClip(BaseModel):
    """아바타 립싱크 영상 클립."""

    video_path: Path
    duration: float
    resolution: tuple[int, int] = (512, 512)  # Ditto 기본 출력 해상도
