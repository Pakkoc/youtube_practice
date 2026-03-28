"""자막 추가 파이프라인 (Whisper STT -> 교정 -> 합성)."""

from __future__ import annotations

from pathlib import Path

from entities.project.model import Project
from shared.config.schema import AppConfig
from shared.lib.file_io import read_text
from shared.lib.logger import get_logger

logger = get_logger()


def run_add_subtitles(
    project: Project,
    config: AppConfig,
    *,
    video_path: Path | None = None,
) -> Path:
    """자막 추가 파이프라인을 실행.

    단계:
        1. Whisper STT로 오디오 전사
        2. Claude로 자막 교정
        3. 자막 합성

    Args:
        project: 프로젝트 정보.
        config: 애플리케이션 설정.
        video_path: 입력 영상 경로 (없으면 output/final_video.mp4).

    Returns:
        최종 영상 경로.
    """
    from features.burn_subtitles import burn_subtitles
    from features.correct_subtitles import correct_subtitle_track
    from features.transcribe_audio import transcribe_to_subtitle_track

    # 입력 영상 결정
    if video_path is None:
        video_path = project.output_dir / "final_video.mp4"

    if not video_path.exists():
        raise FileNotFoundError(f"입력 영상을 찾을 수 없습니다: {video_path}")

    # 1. Whisper STT
    logger.info("=== [1/3] Whisper STT 전사 ===")
    raw_track = transcribe_to_subtitle_track(video_path, language="ko")

    # 2. 자막 교정
    logger.info("=== [2/3] 자막 교정 ===")
    original_script = ""
    if project.script_path.exists():
        original_script = read_text(project.script_path)

    corrected_track, correction_result = correct_subtitle_track(
        raw_track, original_script,
    )
    logger.info("자막 교정: %d개 수정", correction_result.changes_made)

    # SRT 저장
    srt_path = project.output_dir / "corrected_subtitles.srt"
    from shared.lib.file_io import write_text
    write_text(srt_path, corrected_track.to_srt())

    # 3. 자막 합성
    logger.info("=== [3/3] 자막 합성 ===")
    final_output = project.output_dir / "final_video_subtitled.mp4"
    burn_subtitles(
        video_path,
        srt_path,
        final_output,
        config=config.subtitles,
    )

    logger.info("파이프라인 완료: %s", final_output)
    return final_output
