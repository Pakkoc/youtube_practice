"""영상 합성 핵심 로직 (슬라이드 + 오디오 -> 영상)."""

from __future__ import annotations

from pathlib import Path

from entities.audio.model import AudioClip
from entities.slide.model import Slide
from entities.video.model import Video
from shared.lib.ffmpeg import (
    check_ffmpeg,
    compose_slideshow,
    compose_video_slideshow,
    get_duration,
)
from shared.lib.file_io import ensure_dir
from shared.lib.logger import get_logger

logger = get_logger()


def compose_video(
    slides: list[Slide],
    audio_clips: list[AudioClip],
    output_path: Path,
    fps: int = 30,
) -> Video:
    """슬라이드와 오디오 클립을 결합하여 영상을 생성.

    슬라이드가 비디오(Remotion)인 경우 video slideshow,
    이미지인 경우 기존 image slideshow를 사용합니다.

    Args:
        slides: 슬라이드 목록 (이미지 또는 비디오 경로 포함).
        audio_clips: 오디오 클립 목록.
        output_path: 출력 영상 파일 경로.
        fps: 프레임레이트.

    Returns:
        생성된 Video 엔티티.
    """
    if not check_ffmpeg():
        raise RuntimeError("FFmpeg가 설치되지 않았습니다.")

    if len(slides) != len(audio_clips):
        raise ValueError(
            f"슬라이드({len(slides)}개)와 오디오({len(audio_clips)}개) 개수가 일치하지 않습니다."
        )

    ensure_dir(output_path.parent)

    # 비디오 슬라이드 여부 판단 (첫 번째 슬라이드 기준)
    use_video = any(slide.is_video for slide in slides)

    if use_video:
        # Remotion 비디오 슬라이드 경로
        video_audio_pairs: list[tuple[Path, Path]] = []
        for slide, clip in zip(slides, audio_clips):
            media = slide.media_path
            if media is None:
                raise ValueError(f"슬라이드 {slide.index}에 미디어 경로가 없습니다.")
            video_audio_pairs.append((media, clip.file_path))

        logger.info(
            "영상 합성 시작 (video slides): %d개 세그먼트 -> %s",
            len(video_audio_pairs),
            output_path.name,
        )
        compose_video_slideshow(
            video_audio_pairs,
            output_path,
            fps=fps,
        )
    else:
        # 이미지 슬라이드 경로 (fallback)
        image_audio_pairs: list[tuple[Path, Path]] = []
        for slide, clip in zip(slides, audio_clips):
            if slide.image_path is None:
                raise ValueError(f"슬라이드 {slide.index}에 이미지 경로가 없습니다.")
            image_audio_pairs.append((slide.image_path, clip.file_path))

        logger.info(
            "영상 합성 시작: %d개 세그먼트 -> %s",
            len(image_audio_pairs),
            output_path.name,
        )
        compose_slideshow(image_audio_pairs, output_path, fps=fps)

    duration = get_duration(output_path)

    logger.info("영상 합성 완료: %s (%.1f초)", output_path.name, duration)

    return Video(
        file_path=output_path,
        duration=duration,
        fps=fps,
    )
