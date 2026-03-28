"""오디오 엔티티 모델."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class AudioClip(BaseModel):
    """단일 오디오 클립."""

    index: int
    file_path: Path
    duration: float = 0.0
    sample_rate: int = 24000

    @property
    def filename(self) -> str:
        return f"{self.index:03d}.wav"
