"""TTS 생성 데이터 모델."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


class TTSRequest(BaseModel):
    """TTS 생성 요청."""

    text: str
    tts_text: str = ""  # 전처리된 TTS용 텍스트 (비어있으면 text 사용)
    speaker: str = "Sohee"
    language: str = "Korean"
    output_path: Path
    instruct: str = ""


class TTSResult(BaseModel):
    """TTS 생성 결과."""

    output_path: Path
    duration: float = 0.0
    sample_rate: int = 24000
    success: bool = True
    error: str = ""


class TTSBackend(ABC):
    """TTS 백엔드 추상 클래스."""

    @abstractmethod
    def generate(self, request: TTSRequest) -> TTSResult:
        """텍스트에서 음성을 생성.

        Args:
            request: TTS 생성 요청.

        Returns:
            TTS 생성 결과.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """백엔드 사용 가능 여부를 반환."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """백엔드 이름을 반환."""
        ...
