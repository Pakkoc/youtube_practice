"""텍스트 정규화 모델."""

from __future__ import annotations

from pydantic import BaseModel


class TextPair(BaseModel):
    """TTS용 텍스트와 자막 표시용 텍스트 쌍."""

    original: str
    tts_text: str
    display_text: str
