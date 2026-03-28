"""대본 문단 분리 데이터 모델."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SplitConfig(BaseModel):
    """문단 분리 설정."""

    min_length: int = Field(default=10, description="최소 문단 길이 (문자 수)")
    separator: str = Field(default="\n\n", description="문단 구분자")
    auto_detect_lines: bool = Field(
        default=True,
        description="단일 줄바꿈으로 구분된 긴 줄을 자동으로 문단 분리",
    )
    line_min_length: int = Field(
        default=40,
        description="자동 감지 시 문단으로 인정하는 최소 줄 길이",
    )
    max_paragraph_length: int = Field(
        default=150,
        description="이 글자수를 초과하는 문단은 문장 경계에서 자동 분할",
    )
