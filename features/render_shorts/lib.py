"""쇼츠 Remotion 렌더링 핵심 로직."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from entities.video.model import Video
from shared.config.schema import ShortsConfig
from shared.lib import subprocess
from shared.lib.ffmpeg import get_duration
from shared.lib.logger import get_logger

from .model import ShortsProps

logger = get_logger()

_IS_WINDOWS = sys.platform == "win32"


def render_short(
    props: ShortsProps,
    trimmed_video: Path,
    output_path: Path,
    config: ShortsConfig,
    remotion_project_path: Path | None = None,
) -> Video:
    """Remotion으로 쇼츠 영상을 렌더링.

    Args:
        props: ShortsComposition에 전달할 props.
        trimmed_video: 트림된 소스 영상 경로.
        output_path: 출력 MP4 경로.
        config: 쇼츠 설정.
        remotion_project_path: Remotion 프로젝트 경로.

    Returns:
        렌더링된 Video 객체.
    """
    if remotion_project_path is None:
        remotion_project_path = Path(__file__).parents[2] / "remotion"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # trimmed video를 remotion/public/에 임시 복사
    video_name = f"_shorts_{output_path.stem}.mp4"
    video_temp_path = remotion_project_path / "public" / video_name
    shutil.copy2(trimmed_video, video_temp_path)

    # videoSrc를 파일명으로 업데이트
    render_props = props.model_dump()
    render_props["videoSrc"] = video_name

    # props를 임시 JSON 파일로 전달
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(render_props, f, ensure_ascii=False)
        props_path = Path(f.name)

    try:
        cmd = [
            "npx",
            "remotion",
            "render",
            "ShortsComposition",
            str(output_path.absolute()),
            f"--props={props_path}",
            "--width=1080",
            "--height=1920",
            "--fps=30",
            f"--frames=0-{props.durationInFrames - 1}",
            "--codec=h264",
        ]

        logger.info(
            "Shorts render: %s (%d frames, hook=%s)",
            output_path.name,
            props.durationInFrames,
            props.hookTitle[:20],
        )

        result = subprocess.run(
            cmd if not _IS_WINDOWS else " ".join(cmd),
            cwd=str(remotion_project_path),
            capture_output=True,
            text=True,
            check=False,
            shell=_IS_WINDOWS,
            timeout=600,
        )

        if result.returncode != 0:
            stderr_tail = result.stderr[-500:] if result.stderr else ""
            logger.error("Shorts render error: %s", stderr_tail)
            raise RuntimeError(f"Shorts rendering failed: {output_path.name}\n{stderr_tail}")

        duration = get_duration(output_path)
        return Video(
            file_path=output_path,
            duration=duration,
            width=1080,
            height=1920,
            fps=30,
        )
    finally:
        props_path.unlink(missing_ok=True)
        if video_temp_path.exists():
            video_temp_path.unlink(missing_ok=True)
