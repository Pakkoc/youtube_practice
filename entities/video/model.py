"""영상 엔티티 모델."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class Video(BaseModel):
    """영상 파일."""

    file_path: Path
    duration: float = 0.0
    width: int = 1920
    height: int = 1080
    fps: int = 30


class VideoMetadata(BaseModel):
    """유튜브 업로드용 메타데이터."""

    title: str
    description: str = ""
    tags: list[str] = []
    category_id: str = "28"
    thumbnail_path: Path | None = None
