"""자막 교정 모델."""

from __future__ import annotations

from pydantic import BaseModel


class CorrectionResult(BaseModel):
    """자막 교정 결과."""

    original_count: int
    corrected_count: int
    changes_made: int = 0
