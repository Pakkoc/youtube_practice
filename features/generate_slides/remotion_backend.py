"""Remotion CLI 렌더링 백엔드 (슬라이드 비디오 생성)."""

from __future__ import annotations

import json
import os
import queue
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

from shared.lib import subprocess
from shared.lib.logger import get_logger

logger = get_logger()

_IS_WINDOWS = sys.platform == "win32"

# Freeform 슬롯 파일명 (1-indexed)
_SLOT_FILENAMES = [
    "FreeformSlot1.tsx",
    "FreeformSlot2.tsx",
    "FreeformSlot3.tsx",
    "FreeformSlot4.tsx",
]


def validate_tsx(tsx_code: str, project_path: Path, timeout: int = 30) -> str | None:
    """Freeform TSX 코드를 tsc --noEmit 으로 검증.

    Freeform.tsx 를 임시로 덮어쓰고 타입 체크 후 원본 복원.

    Args:
        tsx_code: 검증할 TSX 코드.
        project_path: Remotion 프로젝트 경로.
        timeout: tsc 타임아웃(초).

    Returns:
        에러 메시지 문자열, 또는 None (통과).
    """
    freeform_path = project_path / "src" / "slides" / "Freeform.tsx"

    # 원본 백업
    original_code: str | None = None
    if freeform_path.exists():
        original_code = freeform_path.read_text(encoding="utf-8")

    try:
        # 임시로 TSX 덮어쓰기
        freeform_path.write_text(tsx_code, encoding="utf-8")

        cmd = "npx tsc --noEmit" if _IS_WINDOWS else ["npx", "tsc", "--noEmit"]
        result = subprocess.run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            check=False,
            shell=_IS_WINDOWS,
            timeout=timeout,
        )

        if result.returncode == 0:
            return None

        # Freeform.tsx 관련 에러만 추출
        lines = (result.stdout or "").split("\n") + (result.stderr or "").split("\n")
        freeform_errors = [line for line in lines if "Freeform.tsx" in line or "error TS" in line][
            :10
        ]  # 최대 10줄
        return "\n".join(freeform_errors) if freeform_errors else "tsc failed (unknown error)"

    except subprocess.TimeoutExpired:
        return "tsc timeout (>30s)"
    except Exception as e:
        return f"tsc execution error: {e}"
    finally:
        # 원본 복원
        if original_code is not None:
            freeform_path.write_text(original_code, encoding="utf-8")


_freeform_lock = threading.Lock()


def write_freeform_tsx(tsx_code: str, project_path: Path) -> None:
    """Freeform.tsx 파일을 덮어쓰기 (thread-safe).

    Args:
        tsx_code: LLM이 생성한 TSX 코드.
        project_path: Remotion 프로젝트 경로.
    """
    freeform_path = project_path / "src" / "slides" / "Freeform.tsx"
    with _freeform_lock:
        freeform_path.write_text(tsx_code, encoding="utf-8")
    logger.info("Freeform.tsx 덮어쓰기: %d chars", len(tsx_code))


class FreeformSlotPool:
    """Thread-safe Freeform 렌더링 슬롯 풀.

    4개의 FreeformSlot{1-4}.tsx 파일을 독립 렌더링 슬롯으로 관리.
    각 슬롯은 독립 Composition ID를 가지므로 동시 렌더링이 가능.
    """

    def __init__(self, project_path: Path, num_slots: int = 4) -> None:
        self._project_path = project_path
        self._num_slots = min(num_slots, len(_SLOT_FILENAMES))
        self._queue: queue.Queue[int] = queue.Queue()
        self._originals: dict[int, str] = {}

        # 슬롯 번호를 큐에 넣고 원본 백업
        slides_dir = project_path / "src" / "slides"
        for i in range(self._num_slots):
            slot_id = i + 1  # 1-indexed
            self._queue.put(slot_id)
            slot_path = slides_dir / _SLOT_FILENAMES[i]
            if slot_path.exists():
                self._originals[slot_id] = slot_path.read_text(encoding="utf-8")

    @property
    def num_slots(self) -> int:
        """사용 가능한 슬롯 수."""
        return self._num_slots

    def acquire(self) -> int:
        """큐에서 슬롯 번호 획득 (사용 가능한 슬롯이 없으면 대기)."""
        return self._queue.get()

    def release(self, slot_id: int) -> None:
        """슬롯을 큐에 반환."""
        self._queue.put(slot_id)

    def write_slot(self, slot_id: int, tsx_code: str) -> None:
        """슬롯 파일에 원자적 쓰기 (temp → rename).

        다른 슬롯의 번들러가 쓰기 도중의 불완전한 파일을 읽는 것을 방지.
        """
        slot_path = self._project_path / "src" / "slides" / _SLOT_FILENAMES[slot_id - 1]
        tmp_path = slot_path.with_suffix(".tsx.tmp")
        tmp_path.write_text(tsx_code, encoding="utf-8")
        os.replace(str(tmp_path), str(slot_path))
        logger.debug("Slot %d 원자적 쓰기: %d chars", slot_id, len(tsx_code))

    def composition_id(self, slot_id: int) -> str:
        """슬롯 번호에 해당하는 Remotion Composition ID."""
        return f"FreeformSlot{slot_id}"

    def restore_all(self) -> None:
        """모든 슬롯 파일을 원본 placeholder로 복원."""
        slides_dir = self._project_path / "src" / "slides"
        for slot_id, original_code in self._originals.items():
            slot_path = slides_dir / _SLOT_FILENAMES[slot_id - 1]
            slot_path.write_text(original_code, encoding="utf-8")
        logger.info("Freeform 슬롯 %d개 원본 복원 완료", len(self._originals))


class RemotionSlideBackend:
    """Remotion을 사용한 동적 슬라이드 비디오 렌더링."""

    def __init__(self, project_path: Path | None = None) -> None:
        if project_path is None:
            project_path = Path(__file__).parents[2] / "remotion"
        self._project_path = project_path

    def is_available(self) -> bool:
        """Node.js와 Remotion 프로젝트 존재 여부 확인."""
        try:
            if shutil.which("node") is None:
                return False
            return (self._project_path / "package.json").exists()
        except Exception:
            return False

    def render(
        self,
        template_name: str,
        props: dict,
        output_path: Path,
        duration_seconds: float,
        *,
        fps: int = 30,
        width: int = 1920,
        height: int = 1080,
        background_image: Path | None = None,
    ) -> Path:
        """Remotion 템플릿을 비디오 클립으로 렌더링.

        Args:
            template_name: Remotion Composition ID (Freeform, FreeformSlot1-4 등).
            props: 템플릿 props (JSON 직렬화 가능).
            output_path: 출력 MP4 경로.
            duration_seconds: 클립 길이(초).
            fps: 프레임레이트.
            width: 출력 너비.
            height: 출력 높이.
            background_image: B-roll 이미지 경로 (있으면 배경에 블러 처리).

        Returns:
            출력 비디오 경로.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        duration_frames = max(1, int(duration_seconds * fps))

        # durationInFrames를 props에 주입 → calculateMetadata가 읽어서 동적 설정
        # slideIndex/totalSlides는 호출측에서 props에 미리 주입
        render_props = {**props, "durationInFrames": duration_frames}

        # B-roll 배경 이미지를 remotion/public/ 에 임시 복사
        bg_temp_path: Path | None = None
        if background_image and background_image.exists():
            bg_name = f"_bg_{output_path.stem}{background_image.suffix}"
            bg_temp_path = self._project_path / "public" / bg_name
            shutil.copy2(background_image, bg_temp_path)
            render_props["backgroundImage"] = bg_name
            logger.info("배경 이미지 주입: %s", background_image.name)

        # props를 임시 JSON 파일로 전달
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
                template_name,
                str(output_path.absolute()),
                f"--props={props_path}",
                f"--fps={fps}",
                f"--width={width}",
                f"--height={height}",
                f"--frames=0-{duration_frames - 1}",
                "--codec=h264",
            ]

            logger.info(
                "Remotion slide: %s -> %s (%.1fs, %d frames%s)",
                template_name,
                output_path.name,
                duration_seconds,
                duration_frames,
                ", +bg" if bg_temp_path else "",
            )

            max_retries = 2
            last_error = ""
            for attempt in range(max_retries + 1):
                if attempt > 0:
                    time.sleep(2)
                    logger.warning(
                        "Remotion slide 재시도 %d/%d: %s -> %s",
                        attempt, max_retries, template_name, output_path.name,
                    )

                try:
                    result = subprocess.run(
                        cmd if not _IS_WINDOWS else " ".join(cmd),
                        cwd=str(self._project_path),
                        capture_output=True,
                        text=True,
                        check=False,
                        shell=_IS_WINDOWS,
                        timeout=600,
                    )
                except subprocess.TimeoutExpired:
                    last_error = "timed out (600s)"
                    logger.error("Remotion slide timeout: %s", template_name)
                    continue

                if result.returncode == 0 and output_path.exists():
                    return output_path

                last_error = result.stderr[-500:] if result.stderr else "(no stderr)"
                logger.error(
                    "Remotion slide 실패 (attempt=%d): %s -> %s\n%s",
                    attempt, template_name, output_path.name, last_error,
                )

            raise RuntimeError(
                f"Remotion slide rendering failed after {max_retries + 1} attempts: "
                f"{template_name} -> {output_path.name}\n{last_error}"
            )
        finally:
            props_path.unlink(missing_ok=True)
            if bg_temp_path and bg_temp_path.exists():
                bg_temp_path.unlink(missing_ok=True)
