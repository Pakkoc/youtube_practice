"""아바타 생성 및 오버레이 로직."""

from __future__ import annotations

from pathlib import Path

from shared.lib.ffmpeg import (
    _TIMEOUT_ENCODE,
    _ffmpeg,
    _run_ffmpeg,
    concat_videos,
    get_duration,
)
from shared.lib.logger import get_logger

from .api import run_ditto_batch_inference, run_ditto_inference
from .model import AvatarClip

logger = get_logger()

MAX_RETRIES = 2


def generate_avatar_video(
    audio_path: Path,
    avatar_image: Path,
    output_path: Path,
    *,
    ditto_project_path: str = "C:/Users/hoyoung/Desktop/ditto-talkinghead",
) -> AvatarClip:
    """아바타 이미지 + 오디오로 립싱크 영상을 생성.

    Args:
        audio_path: 입력 오디오 파일 경로.
        avatar_image: 아바타 이미지 경로.
        output_path: 출력 영상 경로.
        ditto_project_path: Ditto 프로젝트 경로.

    Returns:
        생성된 AvatarClip.
    """
    logger.info("아바타 영상 생성 시작: %s", audio_path.name)

    # Ditto 실행
    run_ditto_inference(
        audio_path=audio_path,
        image_path=avatar_image,
        output_path=output_path,
        ditto_project_path=ditto_project_path,
    )

    # 영상 길이 확인
    duration = get_duration(output_path)

    return AvatarClip(
        video_path=output_path,
        duration=duration,
        resolution=(512, 512),
    )


def generate_avatar_clips(
    audio_dir: Path,
    avatar_image: Path,
    output_dir: Path,
    *,
    ditto_project_path: str = "C:/Users/hoyoung/Desktop/ditto-talkinghead",
    num_workers: int = 4,
) -> AvatarClip:
    """문단별 오디오로 개별 아바타 클립 생성 후 연결.

    SDK를 1회만 로드하고 N개 클립을 순차 처리하여 효율적.
    개별 클립은 avatar/clips/avatar_001.mp4 형태로 저장되며,
    기존 클립이 있으면 자동으로 건너뜀 (재사용).
    실패 시 워커 수를 줄여 최대 2회 재시도.

    Args:
        audio_dir: 문단별 오디오 디렉토리 (001.wav, 002.wav, ...).
        avatar_image: 아바타 이미지 경로.
        output_dir: 아바타 출력 디렉토리 (clips/ 하위에 개별 클립 저장).
        ditto_project_path: Ditto 프로젝트 경로.
        num_workers: 병렬 워커 수.

    Returns:
        연결된 최종 AvatarClip.
    """
    logger.info("아바타 배치 생성 시작: %s", audio_dir)

    clips_dir = output_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    n_audio = len(list(audio_dir.glob("*.wav")))

    for attempt in range(MAX_RETRIES + 1):
        # Retry 시 워커 수 축소 (CUDA 경합 완화)
        workers = num_workers if attempt == 0 else max(1, num_workers // 2)

        if attempt > 0:
            # Clean up tmp files before retry
            for tmp in clips_dir.glob("*.tmp.mp4"):
                tmp.unlink(missing_ok=True)
            logger.info(
                "재시도 %d/%d (워커 %d개로 축소)",
                attempt,
                MAX_RETRIES,
                workers,
            )

        clip_paths = run_ditto_batch_inference(
            audio_dir=audio_dir,
            image_path=avatar_image,
            output_dir=clips_dir,
            ditto_project_path=ditto_project_path,
            num_workers=workers,
        )

        if len(clip_paths) >= n_audio:
            break

        missing = n_audio - len(clip_paths)
        logger.warning(
            "시도 %d: %d/%d 클립 완료, %d개 누락",
            attempt + 1,
            len(clip_paths),
            n_audio,
            missing,
        )

    if not clip_paths:
        raise RuntimeError(f"아바타 클립이 생성되지 않음: {clips_dir}")

    if len(clip_paths) < n_audio:
        logger.warning(
            "아바타 배치 부분 완료: %d/%d 클립 (%d회 시도 후)",
            len(clip_paths),
            n_audio,
            MAX_RETRIES + 1,
        )

    # 클립 연결
    avatar_video = output_dir / "avatar.mp4"
    logger.info("아바타 클립 연결: %d개 -> %s", len(clip_paths), avatar_video.name)
    concat_videos(clip_paths, avatar_video)

    duration = get_duration(avatar_video)

    return AvatarClip(
        video_path=avatar_video,
        duration=duration,
        resolution=(512, 512),
    )


def overlay_avatar_circular(
    base_video: Path,
    avatar_video: Path,
    output_path: Path,
    *,
    size: int = 180,
    margin_x: int = 30,
    margin_y: int = 120,
    border_width: int = 3,
    border_color: str = "white",
) -> Path:
    """원형 아바타를 메인 영상 우측 하단에 오버레이.

    Args:
        base_video: 베이스 영상 경로.
        avatar_video: 아바타 영상 경로.
        output_path: 출력 영상 경로.
        size: 원형 아바타 지름 (픽셀).
        margin_x: 우측 여백 (픽셀).
        margin_y: 하단 여백 (픽셀, 자막 피하기 위해).
        border_width: 테두리 두께 (픽셀).
        border_color: 테두리 색상.

    Returns:
        출력 영상 경로.
    """
    logger.info("아바타 오버레이: %s + %s", base_video.name, avatar_video.name)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 반지름 계산
    radius = size // 2
    inner_radius = radius - border_width

    # FFmpeg 필터:
    # 1. 아바타 영상을 원하는 크기로 스케일
    # 2. 원형 마스크 적용 (geq 필터로 원 외부 투명화)
    # 3. 테두리 추가 (drawcircle)
    # 4. 베이스 영상에 오버레이

    # 아바타 영상 길이에 맞춰 반복 재생 (loop)
    filter_complex = (
        # 아바타 스케일 + 포맷 변환 (알파 채널 지원)
        f"[1:v]scale={size}:{size},format=yuva420p,"
        # 원형 마스크 (원 외부는 알파=0)
        f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':"
        f"a='if(gt(pow(X-{radius},2)+pow(Y-{radius},2),{inner_radius}*{inner_radius}),0,255)',"
        # 원형 테두리 추가
        f"drawbox=x=0:y=0:w={size}:h={size}:color={border_color}@0:t=fill,"
        f"drawbox=x={border_width}:y={border_width}:"
        f"w={size - 2 * border_width}:h={size - 2 * border_width}:color=black@0:t=fill"
        f"[avatar];"
        # 베이스 영상에 오버레이 (우측 하단)
        f"[0:v][avatar]overlay=W-w-{margin_x}:H-h-{margin_y}:format=auto:shortest=1"
    )

    # 아바타 영상이 베이스보다 짧을 수 있으므로 반복 재생 설정
    cmd = [
        _ffmpeg(),
        "-y",
        "-i",
        str(base_video),
        "-stream_loop",
        "-1",  # 무한 반복
        "-i",
        str(avatar_video),
        "-filter_complex",
        filter_complex,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "copy",
        "-shortest",  # 베이스 영상 길이에 맞춤
        str(output_path),
    ]

    logger.debug("FFmpeg 명령어: %s", " ".join(cmd))

    _run_ffmpeg(cmd, timeout=_TIMEOUT_ENCODE)
    logger.info("아바타 오버레이 완료: %s", output_path.name)
    return output_path
