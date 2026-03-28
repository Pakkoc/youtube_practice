"""쇼츠 슬라이드 렌더링 핵심 로직.

ShortsSlotPool을 사용하여 TSX 콘텐츠를 1080x1920 쇼츠로 병렬 렌더링.

Race condition 방지:
- write_slot()은 원자적 쓰기 (temp file → rename)
- 렌더 실패 시 최대 2회 재시도 (번들러 경쟁 조건 대응)
"""

from __future__ import annotations

import json
import os
import queue
import sys
import tempfile
import time
from pathlib import Path

from entities.video.model import Video
from shared.config.schema import ShortsSlideConfig
from shared.lib import subprocess
from shared.lib.ffmpeg import get_duration
from shared.lib.logger import get_logger

from .model import ShortsSlideProps

logger = get_logger()

_IS_WINDOWS = sys.platform == "win32"

_SHORTS_SLOT_FILENAMES = [
    "ShortsContentSlot1.tsx",
    "ShortsContentSlot2.tsx",
    "ShortsContentSlot3.tsx",
    "ShortsContentSlot4.tsx",
]

_MAX_RENDER_RETRIES = 2
_RETRY_DELAY_SECONDS = 2


class ShortsSlotPool:
    """Thread-safe 쇼츠 슬라이드 렌더링 슬롯 풀.

    4개의 ShortsContentSlot{1-4}.tsx 파일을 독립 렌더링 슬롯으로 관리.
    """

    def __init__(self, project_path: Path, num_slots: int = 4) -> None:
        self._project_path = project_path
        self._num_slots = min(num_slots, len(_SHORTS_SLOT_FILENAMES))
        self._queue: queue.Queue[int] = queue.Queue()
        self._originals: dict[int, str] = {}

        slides_dir = project_path / "src" / "slides"
        for i in range(self._num_slots):
            slot_id = i + 1
            self._queue.put(slot_id)
            slot_path = slides_dir / _SHORTS_SLOT_FILENAMES[i]
            if slot_path.exists():
                self._originals[slot_id] = slot_path.read_text(encoding="utf-8")

    @property
    def num_slots(self) -> int:
        return self._num_slots

    def acquire(self) -> int:
        return self._queue.get()

    def release(self, slot_id: int) -> None:
        self._queue.put(slot_id)

    def write_slot(self, slot_id: int, tsx_code: str) -> None:
        """슬롯 TSX 파일에 원자적 쓰기 (temp → rename).

        다른 슬롯의 번들러가 쓰기 도중의 불완전한 파일을 읽는 것을 방지.
        Windows에서 번들러가 파일 핸들을 잡고 있을 수 있어 재시도 로직 포함.
        """
        slot_path = self._project_path / "src" / "slides" / _SHORTS_SLOT_FILENAMES[slot_id - 1]
        tmp_path = slot_path.with_suffix(".tsx.tmp")
        tmp_path.write_text(tsx_code, encoding="utf-8")
        # 원자적 교체: Windows 파일 잠금 대비 최대 5회 재시도
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                os.replace(str(tmp_path), str(slot_path))
                break
            except OSError as e:
                if attempt < max_attempts - 1:
                    logger.warning(
                        "슬롯 파일 교체 재시도 %d/%d (slot=%d): %s",
                        attempt + 1, max_attempts, slot_id, e,
                    )
                    time.sleep(0.5)
                else:
                    # 최종 실패 시 직접 쓰기로 폴백
                    logger.warning("원자적 교체 실패, 직접 쓰기 폴백 (slot=%d)", slot_id)
                    slot_path.write_text(tsx_code, encoding="utf-8")
                    if tmp_path.exists():
                        tmp_path.unlink(missing_ok=True)
        logger.debug("Shorts Slot %d 원자적 쓰기: %d chars", slot_id, len(tsx_code))

    def composition_id(self, slot_id: int) -> str:
        return f"ShortsSlideSlot{slot_id}"

    def restore_all(self) -> None:
        slides_dir = self._project_path / "src" / "slides"
        for slot_id, original_code in self._originals.items():
            slot_path = slides_dir / _SHORTS_SLOT_FILENAMES[slot_id - 1]
            slot_path.write_text(original_code, encoding="utf-8")
        logger.info("Shorts 슬롯 %d개 원본 복원 완료", len(self._originals))


def render_shorts_slide(
    props: ShortsSlideProps,
    tsx_code: str,
    output_path: Path,
    config: ShortsSlideConfig,
    slot_pool: ShortsSlotPool,
) -> Video:
    """단일 쇼츠 슬라이드를 렌더링.

    번들러 경쟁 조건 대비 최대 2회 재시도.

    Args:
        props: ShortsSlideWrapper에 전달할 props.
        tsx_code: TSX 콘텐츠 코드.
        output_path: 출력 MP4 경로.
        config: 쇼츠 슬라이드 설정.
        slot_pool: 슬롯 풀.

    Returns:
        렌더링된 Video 객체.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    slot_id = slot_pool.acquire()
    try:
        slot_pool.write_slot(slot_id, tsx_code)
        composition = slot_pool.composition_id(slot_id)

        render_props = props.model_dump()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(render_props, f, ensure_ascii=False)
            props_path = Path(f.name)

        try:
            cmd = [
                "npx",
                "remotion",
                "render",
                composition,
                str(output_path.absolute()),
                f"--props={props_path}",
                f"--width={config.width}",
                f"--height={config.height}",
                f"--fps={config.fps}",
                f"--frames=0-{props.durationInFrames - 1}",
                "--codec=h264",
            ]

            logger.info(
                "Shorts slide render: %s (slot=%d, %d frames, hook=%s)",
                output_path.name,
                slot_id,
                props.durationInFrames,
                props.hookTitle[:20],
            )

            last_error = ""
            for attempt in range(_MAX_RENDER_RETRIES + 1):
                if attempt > 0:
                    # 재시도 전 슬롯 TSX 재작성 (번들 캐시 무효화)
                    slot_pool.write_slot(slot_id, tsx_code)
                    time.sleep(_RETRY_DELAY_SECONDS)
                    logger.warning(
                        "Shorts slide render 재시도 %d/%d: %s (slot=%d)",
                        attempt,
                        _MAX_RENDER_RETRIES,
                        output_path.name,
                        slot_id,
                    )

                result = subprocess.run(
                    cmd if not _IS_WINDOWS else " ".join(cmd),
                    cwd=str(slot_pool._project_path),
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=_IS_WINDOWS,
                    timeout=600,
                )

                if result.returncode == 0 and output_path.exists():
                    duration = get_duration(output_path)
                    return Video(
                        file_path=output_path,
                        duration=duration,
                        width=config.width,
                        height=config.height,
                        fps=config.fps,
                    )

                last_error = result.stderr[-500:] if result.stderr else "(no stderr)"
                logger.error(
                    "Shorts slide render 실패 (attempt=%d, slot=%d): %s\n%s",
                    attempt,
                    slot_id,
                    output_path.name,
                    last_error,
                )

            raise RuntimeError(
                f"Shorts slide rendering failed after {_MAX_RENDER_RETRIES + 1} attempts: "
                f"{output_path.name}\n{last_error}"
            )
        finally:
            props_path.unlink(missing_ok=True)
    finally:
        slot_pool.release(slot_id)
