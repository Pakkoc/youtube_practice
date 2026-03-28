"""캐러셀 배경 이미지 생성 도메인 모델."""

from __future__ import annotations

from pydantic import BaseModel


class CarouselBackgroundItem(BaseModel):
    """개별 카드 배경 이미지 생성 항목."""

    card_number: int  # 1-indexed
    image_prompt: str  # 시네마틱 프롬프트
    card_role: str = "body"  # cover | cta | quote | body


class CarouselBackgroundPlan(BaseModel):
    """캐러셀 배경 이미지 생성 계획."""

    items: list[CarouselBackgroundItem]
