"""자막 교정 핵심 로직."""

from __future__ import annotations

from pathlib import Path

from entities.subtitle.model import SubtitleSegment, SubtitleTrack
from shared.lib.file_io import write_text
from shared.lib.logger import get_logger

from .api import correct_subtitles_via_llm
from .model import CorrectionResult

logger = get_logger()


def correct_subtitle_track(
    track: SubtitleTrack,
    original_script: str,
) -> tuple[SubtitleTrack, CorrectionResult]:
    """자막 트랙을 원본 대본과 비교하여 교정.

    타임스탬프는 그대로 유지하고 텍스트만 교정합니다.

    Args:
        track: 원본 SubtitleTrack (Whisper STT 결과).
        original_script: 원본 대본 텍스트.

    Returns:
        (교정된 SubtitleTrack, CorrectionResult) 튜플.
    """
    # 텍스트만 추출하여 전달 (타임스탬프 제외)
    subtitle_lines = [seg.text for seg in track.segments]

    # LLM에게 교정 요청 (변경된 줄만 반환)
    corrections = correct_subtitles_via_llm(original_script, subtitle_lines)

    # 기존 세그먼트에 교정 텍스트 적용 (타임스탬프 유지)
    corrected_segments: list[SubtitleSegment] = []
    for seg in track.segments:
        corrected_text = corrections.get(seg.index, seg.text)
        corrected_segments.append(
            SubtitleSegment(
                index=seg.index,
                start=seg.start,
                end=seg.end,
                text=corrected_text,
            )
        )

    result = CorrectionResult(
        original_count=len(track.segments),
        corrected_count=len(corrected_segments),
        changes_made=len(corrections),
    )

    corrected_track = SubtitleTrack(segments=corrected_segments)
    logger.info(
        "자막 교정: %d개 중 %d개 수정",
        result.original_count,
        result.changes_made,
    )
    return corrected_track, result


def correct_and_save_srt(
    track: SubtitleTrack,
    original_script: str,
    output_path: Path,
) -> tuple[SubtitleTrack, CorrectionResult]:
    """자막을 교정하고 SRT 파일로 저장.

    Args:
        track: 원본 SubtitleTrack.
        original_script: 원본 대본 텍스트.
        output_path: 교정된 SRT 파일 저장 경로.

    Returns:
        (교정된 SubtitleTrack, CorrectionResult) 튜플.
    """
    corrected_track, result = correct_subtitle_track(track, original_script)
    srt_content = corrected_track.to_srt()
    write_text(output_path, srt_content)
    logger.info("교정된 SRT 저장: %s", output_path.name)
    return corrected_track, result
