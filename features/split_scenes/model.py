"""씬 분할 데이터 모델."""

from __future__ import annotations

from pydantic import BaseModel


class SceneSplitConfig(BaseModel):
    """씬 분할 설정."""

    merge_threshold: int = 30  # 이 글자수 미만 문장은 인접 문장과 병합
