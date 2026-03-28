"""Whisper STT API 호출."""

from __future__ import annotations

from pathlib import Path

from shared.api.openai_client import transcribe as _whisper_transcribe
from shared.lib.logger import get_logger

logger = get_logger()


def transcribe_audio(audio_path: Path, *, language: str = "ko") -> dict:
    """Whisper API로 오디오를 텍스트로 변환.

    Args:
        audio_path: 오디오 파일 경로.
        language: 언어 코드.

    Returns:
        Whisper 응답 (text, segments, words 등).
    """
    logger.info("Whisper STT 요청: %s (language=%s)", audio_path.name, language)
    result = _whisper_transcribe(audio_path, language=language)
    logger.info("Whisper STT 완료: %d자", len(result.get("text", "")))
    return result
