"""씬 엔티티 모델."""

from __future__ import annotations

from pydantic import BaseModel


class Scene(BaseModel):
    """문단 내 개별 씬 (문장 단위).

    문단을 문장 단위로 분할한 결과. TTS/B-roll은 문단 단위로 유지하되,
    슬라이드는 씬 단위로 생성하여 더 빠른 전환 효과를 구현.
    """

    index: int  # 전체 씬 인덱스 (1-based, 연속)
    paragraph_index: int  # 소속 문단 인덱스 (1-based)
    text: str

    @property
    def filename(self) -> str:
        return f"{self.index:03d}.txt"
