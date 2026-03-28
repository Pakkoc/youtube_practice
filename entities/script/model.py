"""대본 엔티티 모델."""

from __future__ import annotations

from pydantic import BaseModel


class Paragraph(BaseModel):
    """대본의 단일 문단."""

    index: int
    text: str

    @property
    def filename(self) -> str:
        return f"{self.index:03d}.txt"


class Script(BaseModel):
    """대본 전체."""

    title: str = ""
    raw_text: str
    paragraphs: list[Paragraph] = []
