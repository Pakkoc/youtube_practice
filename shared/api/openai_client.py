"""OpenAI API 클라이언트 래퍼 (Whisper, GPT Image 등)."""

from __future__ import annotations

import os
from pathlib import Path

from openai import APIError, APITimeoutError, OpenAI

from shared.lib.logger import get_logger

logger = get_logger()

_client: OpenAI | None = None

# Whisper API는 긴 오디오 파일 처리 시 느릴 수 있음
_MAX_RETRIES = 3
_TIMEOUT = 300.0  # 5분 (대용량 오디오 대비)


def get_client() -> OpenAI:
    """OpenAI 클라이언트 싱글턴을 반환."""
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        _client = OpenAI(
            api_key=api_key,
            max_retries=_MAX_RETRIES,
            timeout=_TIMEOUT,
        )
    return _client


def transcribe(audio_path: Path, *, language: str = "ko") -> dict:
    """Whisper API로 오디오를 텍스트로 변환.

    Args:
        audio_path: 오디오 파일 경로.
        language: 오디오 언어 코드.

    Returns:
        Whisper API 응답 딕셔너리 (text, segments 등).

    Raises:
        FileNotFoundError: 오디오 파일이 존재하지 않을 때.
        APIError: Whisper API 호출 실패 시.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_path}")

    client = get_client()
    try:
        with open(audio_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],
            )
    except APITimeoutError:
        logger.error("Whisper API 타임아웃 (%.0f초 초과): %s", _TIMEOUT, audio_path.name)
        raise
    except APIError as e:
        logger.error(
            "Whisper API 오류 (status=%s): %s. file=%s",
            getattr(e, "status_code", "?"),
            str(e)[:300],
            audio_path.name,
        )
        raise

    return response.model_dump()
