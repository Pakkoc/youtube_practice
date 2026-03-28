"""슬라이드 엔티티 모델."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class Slide(BaseModel):
    """단일 슬라이드."""

    index: int
    markdown: str
    image_path: Path | None = None
    video_path: Path | None = None
    paragraph_index: int | None = None  # 씬 모드에서 B-roll 매칭용

    @property
    def is_video(self) -> bool:
        """슬라이드가 비디오(Remotion)인지 여부."""
        return self.video_path is not None

    @property
    def media_path(self) -> Path | None:
        """비디오 우선, 없으면 이미지 경로 반환."""
        return self.video_path or self.image_path

    @property
    def md_filename(self) -> str:
        return f"{self.index:03d}.md"

    @property
    def png_filename(self) -> str:
        return f"{self.index:03d}.png"
