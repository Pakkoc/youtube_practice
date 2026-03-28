"""TTS 품질 검증 핵심 로직."""

from __future__ import annotations

import difflib
from pathlib import Path

from shared.config.schema import ValidationConfig
from shared.lib.logger import get_logger

from .api import transcribe_audio

logger = get_logger()


class ValidationResult:
    """TTS 검증 결과."""

    def __init__(self, original: str, transcribed: str, match_rate: float, passed: bool):
        self.original = original
        self.transcribed = transcribed
        self.match_rate = match_rate
        self.passed = passed

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"ValidationResult({status}, match={self.match_rate:.1%})"


def calculate_match_rate(original: str, transcribed: str) -> float:
    """원본 텍스트와 STT 결과의 일치율을 계산.

    Args:
        original: 원본 텍스트.
        transcribed: Whisper STT 결과 텍스트.

    Returns:
        0.0 ~ 1.0 사이의 일치율.
    """
    # 공백/특수문자 정규화
    orig_normalized = _normalize(original)
    trans_normalized = _normalize(transcribed)

    if not orig_normalized:
        return 1.0 if not trans_normalized else 0.0

    matcher = difflib.SequenceMatcher(None, orig_normalized, trans_normalized)
    return matcher.ratio()


def _normalize(text: str) -> str:
    """텍스트를 비교용으로 정규화."""
    import re

    text = text.strip()
    # 구두점, 특수문자 제거
    text = re.sub(r"[^\w\s]", "", text)
    # 연속 공백 제거
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def validate_tts(
    audio_path: Path,
    original_text: str,
    config: ValidationConfig | None = None,
    language: str = "ko",
) -> ValidationResult:
    """TTS 출력 음성의 품질을 검증.

    Whisper STT로 역변환하여 원본 텍스트와 비교한다.

    Args:
        audio_path: TTS 출력 오디오 파일 경로.
        original_text: 원본 텍스트.
        config: 검증 설정.
        language: 언어 코드.

    Returns:
        검증 결과.
    """
    if config is None:
        config = ValidationConfig()

    logger.info("TTS 검증 중: %s", audio_path.name)

    transcribed = transcribe_audio(audio_path, language=language)
    match_rate = calculate_match_rate(original_text, transcribed)
    passed = match_rate >= config.min_match_rate

    result = ValidationResult(
        original=original_text,
        transcribed=transcribed,
        match_rate=match_rate,
        passed=passed,
    )

    if passed:
        logger.info("TTS 검증 통과: %s (%.1f%%)", audio_path.name, match_rate * 100)
    else:
        logger.warning(
            "TTS 검증 실패: %s (%.1f%% < %.1f%%)",
            audio_path.name,
            match_rate * 100,
            config.min_match_rate * 100,
        )

    return result


def validate_and_retry(
    audio_path: Path,
    original_text: str,
    regenerate_fn,
    config: ValidationConfig | None = None,
    language: str = "ko",
) -> ValidationResult:
    """TTS 검증 실패 시 재생성을 시도.

    Args:
        audio_path: TTS 출력 오디오 파일 경로.
        original_text: 원본 텍스트.
        regenerate_fn: 재생성 함수 (호출 시 새 오디오 생성).
        config: 검증 설정.
        language: 언어 코드.

    Returns:
        최종 검증 결과.
    """
    if config is None:
        config = ValidationConfig()

    if not config.enabled:
        logger.info("TTS 검증 비활성화됨, 검증 건너뜀")
        return ValidationResult(
            original=original_text,
            transcribed="",
            match_rate=1.0,
            passed=True,
        )

    for attempt in range(1, config.max_retries + 1):
        result = validate_tts(audio_path, original_text, config, language)

        if result.passed:
            return result

        if attempt < config.max_retries:
            logger.info(
                "TTS 재생성 시도 %d/%d (일치율: %.1f%%)",
                attempt,
                config.max_retries,
                result.match_rate * 100,
            )
            regenerate_fn()

    return result
