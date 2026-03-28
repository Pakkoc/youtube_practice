"""바이럴 구간 선정 핵심 로직."""

from __future__ import annotations

from pathlib import Path

from shared.config.schema import ShortsConfig
from shared.lib.file_io import read_text
from shared.lib.logger import get_logger

from .api import select_viral_segments
from .model import ViralSegmentPlan

logger = get_logger()


def plan_viral_segments(
    srt_path: Path,
    script_path: Path | None,
    config: ShortsConfig,
) -> ViralSegmentPlan:
    """SRT와 대본에서 바이럴 구간을 선정.

    Args:
        srt_path: 교정된 자막 SRT 파일 경로.
        script_path: 원본 대본 경로 (외부 영상이면 None).
        config: 쇼츠 설정.

    Returns:
        ViralSegmentPlan (선정된 구간 리스트).
    """
    srt_text = read_text(srt_path)
    script_text = read_text(script_path) if script_path and script_path.exists() else "(대본 없음)"

    return select_viral_segments(
        srt_text=srt_text,
        script_text=script_text,
        max_shorts=config.max_shorts,
        min_duration=config.min_duration,
        max_duration=config.max_duration,
        model=config.model,
    )
