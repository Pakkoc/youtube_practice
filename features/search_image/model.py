"""이미지 검색 모델."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ImageSearchResult(BaseModel):
    """단일 이미지 검색 결과."""

    url: str  # 이미지 URL
    title: str = ""  # 이미지 제목
    source: str = ""  # 출처 (예: Wikipedia, news site)
    width: int = 0
    height: int = 0


class ImageValidationResult(BaseModel):
    """이미지 검증 결과."""

    is_relevant: bool  # 컨텍스트에 적합한지
    confidence: float = 0.0  # 신뢰도 (0-1)
    reason: str = ""  # 판단 이유


class SearchImageRequest(BaseModel):
    """이미지 검색 요청."""

    query: str  # 검색 쿼리
    context: str = ""  # B-roll 컨텍스트 (검증용)
    num_results: int = 5  # 검색 결과 수


class SearchImageResponse(BaseModel):
    """이미지 검색 + 검증 응답."""

    query: str
    selected_image: ImageSearchResult | None = None
    validation: ImageValidationResult | None = None
    all_candidates: list[ImageSearchResult] = Field(default_factory=list)
    fallback_to_generate: bool = False  # 검증 실패로 생성으로 전환
