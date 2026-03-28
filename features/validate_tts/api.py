"""TTS 검증 API (Whisper STT)."""

from __future__ import annotations

from pathlib import Path

from shared.api.openai_client import transcribe
from shared.lib.logger import get_logger

logger = get_logger()


def transcribe_audio(audio_path: Path, language: str = "ko") -> str:
    """Whisper API로 오디오를 텍스트로 변환.

    Args:
        audio_path: 오디오 파일 경로.
        language: 오디오 언어 코드.

    Returns:
        변환된 텍스트.
    """
    logger.debug("Whisper STT 요청: %s", audio_path.name)
    result = transcribe(audio_path, language=language)
    text = result.get("text", "")
    logger.debug("Whisper STT 결과: %s", text[:100])
    return text
