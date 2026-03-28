"""B-roll 분석 모델."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BrollItem(BaseModel):
    """단일 B-roll 삽입 항목."""

    start_time: str  # "HH:MM:SS.mmm" 형식
    duration: int = 3  # 초
    keyword: str  # 영어 검색 키워드
    source: str = "pexels"  # "pexels" 또는 "generate"
    reason: str = ""  # 삽입 이유
    context_chunk: str = ""  # 해당 시점 주변 대본 컨텍스트 (stride 범위)
    video_prompt: str = ""  # Wan2GP용 비디오 프롬프트 (동작/감정 포함)
    paragraph_index: int | None = None  # 소스 문단 인덱스 (1-based)
    scene_group_id: int | None = None  # 씬 그룹 ID (같은 그룹은 동일 이미지 공유)

    @property
    def start_seconds(self) -> float:
        """start_time을 초 단위로 변환."""
        parts = self.start_time.replace(",", ".").split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        if len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        return float(parts[0])


class SceneGroup(BaseModel):
    """연속 문단을 하나의 시각적 장면으로 그룹핑."""

    group_id: int  # 씬 그룹 ID (1-based)
    paragraph_indices: list[int]  # 소속 문단 인덱스 (1-based)
    representative_index: int  # 대표 문단 인덱스 (이미지 생성 대상)
    reason: str = ""  # 그룹핑 이유


class BrollPlan(BaseModel):
    """B-roll 삽입 계획."""

    broll_items: list[BrollItem] = Field(default_factory=list)
