"""자막 합성 (영상에 자막 굽기)."""

from __future__ import annotations

from pathlib import Path

from shared.config.schema import SubtitlesConfig
from shared.lib.ffmpeg import _ffmpeg, _run_ffmpeg
from shared.lib.logger import get_logger

logger = get_logger()


def burn_subtitles(
    video_path: Path,
    srt_path: Path,
    output_path: Path,
    *,
    config: SubtitlesConfig | None = None,
) -> Path:
    """영상에 SRT 자막을 합성(하드코딩).

    ASS 스타일 템플릿이 있으면 사용하고, 없으면 subtitles 필터 사용.

    Args:
        video_path: 입력 영상 경로.
        srt_path: SRT 자막 파일 경로.
        output_path: 출력 영상 경로.
        config: 자막 설정 (없으면 기본값 사용).

    Returns:
        출력 영상 경로.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if config is None:
        config = SubtitlesConfig()

    # SRT 파일 경로에 특수문자가 있을 수 있으므로 이스케이프 처리
    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")

    # subtitles 필터 (폰트, 크기, 색상 설정)
    style = _build_subtitle_style(config)
    vf = f"subtitles='{srt_escaped}':force_style='{style}'"

    cmd = [
        _ffmpeg(), "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    logger.info("자막 합성: %s + %s → %s", video_path.name, srt_path.name, output_path.name)

    _run_ffmpeg(cmd, timeout=600)

    return output_path


def burn_subtitles_with_ass(
    video_path: Path,
    ass_path: Path,
    output_path: Path,
) -> Path:
    """ASS 스타일 파일을 사용하여 자막을 합성.

    Args:
        video_path: 입력 영상 경로.
        ass_path: ASS 자막/스타일 파일 경로.
        output_path: 출력 영상 경로.

    Returns:
        출력 영상 경로.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
    vf = f"ass='{ass_escaped}'"

    cmd = [
        _ffmpeg(), "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    logger.info("ASS 자막 합성: %s → %s", video_path.name, output_path.name)

    _run_ffmpeg(cmd, timeout=600)

    return output_path


def _build_subtitle_style(config: SubtitlesConfig) -> str:
    """SubtitlesConfig에서 ASS 스타일 문자열을 생성."""
    color_hex = _color_to_ass(config.color)
    bg_hex = _parse_background_color(config.background)

    margin_v = getattr(config, "margin_v", 50)
    parts = [
        f"FontName={config.font}",
        f"FontSize={config.font_size}",
        f"PrimaryColour={color_hex}",
        f"BackColour={bg_hex}",
        "BorderStyle=4",  # 박스 스타일
        "Outline=0",
        "Shadow=0",
        f"Alignment={'2' if config.position == 'bottom' else '8'}",
        f"MarginV={margin_v}",
    ]
    return ",".join(parts)


def _color_to_ass(color: str) -> str:
    """CSS 색상을 ASS 색상 코드로 변환 (&HAABBGGRR)."""
    color_map = {
        "white": "&H00FFFFFF",
        "black": "&H00000000",
        "yellow": "&H0000FFFF",
        "red": "&H000000FF",
    }
    return color_map.get(color.lower(), "&H00FFFFFF")


def _parse_background_color(bg: str) -> str:
    """배경색 문자열을 ASS 색상 코드로 변환."""
    if "rgba" in bg:
        # rgba(0,0,0,0.7) → &H00000000 + alpha
        return "&H80000000"
    return "&H80000000"
