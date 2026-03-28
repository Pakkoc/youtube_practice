"""프로젝트 엔티티 모델."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, computed_field

from shared.constants import PROJECTS_DIR


class Project(BaseModel):
    """영상 프로젝트."""

    name: str
    base_dir: Path = Field(default=PROJECTS_DIR)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def project_type(self) -> Literal["standard", "cc"]:
        """프로젝트 이름 패턴으로 타입 분류."""
        return "cc" if re.match(r"cc-\d+", self.name) else "standard"

    @property
    def root(self) -> Path:
        return self.base_dir / self.name

    @property
    def script_path(self) -> Path:
        return self.root / "script.txt"

    @property
    def paragraphs_dir(self) -> Path:
        return self.root / "paragraphs"

    @property
    def slides_dir(self) -> Path:
        return self.root / "slides"

    @property
    def audio_dir(self) -> Path:
        return self.root / "audio"

    @property
    def broll_dir(self) -> Path:
        return self.root / "broll"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def shorts_dir(self) -> Path:
        return self.root / "shorts"

    @property
    def carousel_dir(self) -> Path:
        return self.root / "carousel"

    @property
    def shorts_slides_dir(self) -> Path:
        return self.root / "shorts_slides"

    def ensure_dirs(self) -> None:
        """모든 프로젝트 서브 디렉토리를 생성."""
        for d in [
            self.paragraphs_dir,
            self.slides_dir,
            self.audio_dir,
            self.broll_dir,
            self.output_dir,
            self.shorts_dir,
            self.carousel_dir,
            self.shorts_slides_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)
