"""오디오 전사(Transcription) 핵심 로직."""

from __future__ import annotations

from pathlib import Path

from entities.subtitle.model import SubtitleSegment, SubtitleTrack, WordTimestamp
from shared.lib.file_io import write_text
from shared.lib.logger import get_logger

from .api import transcribe_audio

logger = get_logger()


def transcribe_to_subtitle_track(
    audio_path: Path,
    *,
    language: str = "ko",
) -> SubtitleTrack:
    """오디오 파일을 전사하여 SubtitleTrack을 반환.

    Args:
        audio_path: 오디오 파일 경로.
        language: 언어 코드.

    Returns:
        SubtitleTrack (타임스탬프 포함).
    """
    result = transcribe_audio(audio_path, language=language)

    segments: list[SubtitleSegment] = []
    for i, seg in enumerate(result.get("segments", []), start=1):
        segments.append(
            SubtitleSegment(
                index=i,
                start=seg.get("start", 0.0),
                end=seg.get("end", 0.0),
                text=seg.get("text", "").strip(),
            )
        )

    track = SubtitleTrack(segments=segments)
    logger.info("전사 완료: %d개 세그먼트", len(segments))
    return track


def transcribe_to_word_timestamps(
    audio_path: Path,
    *,
    language: str = "ko",
) -> list[WordTimestamp]:
    """오디오 파일을 전사하여 단어별 타임스탬프 리스트를 반환.

    Args:
        audio_path: 오디오 파일 경로.
        language: 언어 코드.

    Returns:
        WordTimestamp 리스트 (word-level timestamps).
    """
    result = transcribe_audio(audio_path, language=language)

    words: list[WordTimestamp] = []
    for w in result.get("words", []):
        words.append(
            WordTimestamp(
                word=w.get("word", "").strip(),
                start=w.get("start", 0.0),
                end=w.get("end", 0.0),
            )
        )

    logger.info("단어 타임스탬프 추출 완료: %d개 단어", len(words))
    return words


def transcribe_and_save_srt(
    audio_path: Path,
    output_path: Path,
    *,
    language: str = "ko",
) -> SubtitleTrack:
    """오디오를 전사하고 SRT 파일로 저장.

    Args:
        audio_path: 오디오 파일 경로.
        output_path: SRT 파일 저장 경로.
        language: 언어 코드.

    Returns:
        SubtitleTrack.
    """
    track = transcribe_to_subtitle_track(audio_path, language=language)
    srt_content = track.to_srt()
    write_text(output_path, srt_content)
    logger.info("SRT 저장: %s (%d개 세그먼트)", output_path.name, len(track.segments))
    return track
