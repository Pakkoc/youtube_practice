"""TTS JSON sidecar 동기화."""

from __future__ import annotations

import json
from pathlib import Path

from shared.lib.logger import get_logger

logger = get_logger()


def read_tts_sidecar(wav_path: Path) -> dict | None:
    """WAV와 쌍을 이루는 JSON sidecar를 읽어 반환. 없거나 손상 시 None."""
    meta_path = wav_path.with_suffix(".json")
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def sync_tts_sidecar(
    wav_path: Path,
    text: str,
    tts_text: str,
    duration: float,
    language_code: str = "ko",
) -> None:
    """WAV와 쌍을 이루는 JSON sidecar를 현재 문단 기준으로 동기화.

    기존 JSON이 없거나 text가 다르면 갱신한다.
    """
    meta_path = wav_path.with_suffix(".json")
    meta = {
        "audio": str(wav_path.resolve()),
        "text": text,
        "tts_text": tts_text,
        "language_code": language_code,
        "duration": round(duration, 2),
    }

    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
            if existing.get("text") == text and abs(existing.get("duration", 0) - duration) < 0.1:
                return
        except (json.JSONDecodeError, KeyError):
            pass
        logger.info("TTS sidecar 갱신: %s", meta_path.name)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
