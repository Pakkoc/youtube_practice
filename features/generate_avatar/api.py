"""Ditto WSL2 호출 API."""

from __future__ import annotations

import os
import queue
import threading
import time
from pathlib import Path

from shared.lib import subprocess
from shared.lib.logger import get_logger

logger = get_logger()

# If no new output line for this long, consider the process stalled
DEFAULT_STALL_TIMEOUT = 360  # 6 min (slightly above WSL-side 5 min)


def _reader_thread(pipe: object, q: queue.Queue[str | None]) -> None:
    """Read lines from *pipe* in a dedicated thread.

    Pushes each line (str) into *q*, then a ``None`` sentinel when EOF.
    Runs as a daemon thread so it never blocks interpreter shutdown.
    """
    try:
        for raw in iter(pipe.readline, b""):  # type: ignore[arg-type]
            q.put(raw.rstrip())
        q.put(None)  # EOF sentinel
    except Exception:
        q.put(None)


def to_wsl_path(win_path: str | Path) -> str:
    """Windows 경로를 WSL 경로로 변환.

    Args:
        win_path: Windows 스타일 경로 (예: C:\\Users\\...)

    Returns:
        WSL 스타일 경로 (예: /mnt/c/Users/...)
    """
    win_path_str = str(win_path)
    if len(win_path_str) > 1 and win_path_str[1] == ":":
        drive = win_path_str[0].lower()
        return f"/mnt/{drive}{win_path_str[2:].replace(os.sep, '/')}"
    return win_path_str


def run_ditto_inference(
    audio_path: Path,
    image_path: Path,
    output_path: Path,
    *,
    ditto_project_path: str = "C:/Users/hoyoung/Desktop/ditto-talkinghead",
    checkpoint_path: str = "./checkpoints/ditto_pytorch",
    cfg_path: str = "./checkpoints/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl",
) -> Path:
    """WSL2에서 Ditto 모델을 실행하여 립싱크 영상 생성.

    Args:
        audio_path: 입력 오디오 파일 경로 (Windows).
        image_path: 입력 아바타 이미지 경로 (Windows).
        output_path: 출력 영상 경로 (Windows).
        ditto_project_path: Ditto 프로젝트 경로 (Windows).
        checkpoint_path: Ditto 체크포인트 경로 (Ditto 프로젝트 기준 상대 경로).
        cfg_path: Ditto 설정 파일 경로 (Ditto 프로젝트 기준 상대 경로).

    Returns:
        생성된 영상 파일 경로.

    Raises:
        RuntimeError: Ditto 실행 실패 시.
    """
    # 출력 디렉토리 확인
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Windows 경로 → WSL 경로 변환
    wsl_audio = to_wsl_path(audio_path)
    wsl_image = to_wsl_path(image_path)
    wsl_output = to_wsl_path(output_path)
    wsl_ditto = to_wsl_path(ditto_project_path)

    # WSL 명령어 구성
    cmd = f"""
source ~/miniforge3/etc/profile.d/conda.sh && \\
conda activate ditto && \\
cd {wsl_ditto} && \\
python inference.py \\
    --data_root "{checkpoint_path}" \\
    --cfg_pkl "{cfg_path}" \\
    --audio_path "{wsl_audio}" \\
    --source_path "{wsl_image}" \\
    --output_path "{wsl_output}"
"""

    logger.info("Ditto 실행: %s -> %s", audio_path.name, output_path.name)
    logger.debug("WSL 명령어: %s", cmd)

    try:
        result = subprocess.run(
            ["wsl", "-e", "bash", "-c", cmd],
            capture_output=True,
            text=True,
            check=True,
            timeout=1800,  # 30분 타임아웃
        )
        logger.debug("Ditto stdout: %s", result.stdout)

        if not output_path.exists():
            raise RuntimeError(f"Ditto 출력 파일이 생성되지 않음: {output_path}")

        logger.info("Ditto 완료: %s", output_path.name)
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error("Ditto 실행 실패: %s", e.stderr)
        raise RuntimeError(f"Ditto 실행 실패: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Ditto 실행 타임아웃 (30분 초과)") from e


def _cleanup_tmp_files(output_dir: Path) -> int:
    """Remove stale .tmp.mp4 files from output directory."""
    tmp_files = list(output_dir.glob("*.tmp.mp4"))
    for f in tmp_files:
        f.unlink(missing_ok=True)
    if tmp_files:
        logger.info("임시 파일 %d개 정리", len(tmp_files))
    return len(tmp_files)


def run_ditto_batch_inference(
    audio_dir: Path,
    image_path: Path,
    output_dir: Path,
    *,
    ditto_project_path: str = "C:/Users/hoyoung/Desktop/ditto-talkinghead",
    checkpoint_path: str = "./checkpoints/ditto_pytorch",
    cfg_path: str = "./checkpoints/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl",
    timeout: int = 7200,
    num_workers: int = 4,
    stall_timeout: int = DEFAULT_STALL_TIMEOUT,
) -> list[Path]:
    """WSL2에서 Ditto 병렬 배치 추론 실행.

    N개 워커가 각각 SDK를 로드하여 병렬 처리.
    Popen으로 실시간 출력 스트리밍 + stall 감지.

    Args:
        audio_dir: 입력 오디오 디렉토리 (001.wav, 002.wav, ...).
        image_path: 입력 아바타 이미지 경로 (Windows).
        output_dir: 출력 클립 디렉토리 (avatar_001.mp4, ...).
        ditto_project_path: Ditto 프로젝트 경로 (Windows).
        checkpoint_path: 체크포인트 경로 (상대 경로).
        cfg_path: 설정 파일 경로 (상대 경로).
        timeout: 전체 타임아웃 (초, 기본 2시간).
        num_workers: 병렬 워커 수 (기본 4).
        stall_timeout: 워커 stall 타임아웃 (초, 기본 360).

    Returns:
        생성된 아바타 클립 경로 리스트 (정렬됨).

    Raises:
        RuntimeError: Ditto 배치 실행 실패 시.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean up temp files from previous failed runs
    _cleanup_tmp_files(output_dir)

    wsl_audio_dir = to_wsl_path(audio_dir.resolve())
    wsl_image = to_wsl_path(image_path.resolve())
    wsl_output_dir = to_wsl_path(output_dir.resolve())
    wsl_ditto = to_wsl_path(ditto_project_path)

    cmd = f"""
source ~/miniforge3/etc/profile.d/conda.sh && \\
conda activate ditto && \\
cd {wsl_ditto} && \\
python inference_batch_parallel.py \\
    --data_root "{checkpoint_path}" \\
    --cfg_pkl "{cfg_path}" \\
    --audio_dir "{wsl_audio_dir}" \\
    --source_path "{wsl_image}" \\
    --output_dir "{wsl_output_dir}" \\
    --num_workers {num_workers} \\
    --stall_timeout {stall_timeout}
"""

    n_audio = len(list(audio_dir.glob("*.wav")))
    logger.info(
        "Ditto 병렬 배치: %s -> %s (%d개, %d워커)",
        audio_dir,
        output_dir,
        n_audio,
        num_workers,
    )
    logger.debug("WSL 명령어: %s", cmd)

    process = subprocess.Popen(
        ["wsl", "-e", "bash", "-c", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    t_start = time.time()
    last_activity = time.time()
    stdout_lines: list[str] = []

    # Read stdout in a daemon thread so readline() never blocks the main loop.
    # The thread pushes lines into a queue; main loop polls with short timeout.
    line_q: queue.Queue[str | None] = queue.Queue()
    reader = threading.Thread(
        target=_reader_thread, args=(process.stdout, line_q), daemon=True
    )
    reader.start()

    try:
        while True:
            # Drain all available lines (non-blocking)
            try:
                line = line_q.get(timeout=2)
            except queue.Empty:
                line = ...  # sentinel: no data this tick

            if line is None:
                # EOF — process closed stdout
                break

            if line is not ...:
                stdout_lines.append(line)
                last_activity = time.time()

                # Log progress lines
                if "Done" in line or "SKIP" in line or "Finished" in line:
                    logger.info("[Ditto] %s", line)
                elif "DIED" in line or "STALLED" in line or "FAILED" in line:
                    logger.warning("[Ditto] %s", line)
                elif "Worker" in line or "Total" in line or "Launching" in line:
                    logger.info("[Ditto] %s", line)

            # Check if process ended
            retcode = process.poll()
            if retcode is not None:
                # Drain remaining lines
                while not line_q.empty():
                    rem = line_q.get_nowait()
                    if rem is None or rem is ...:
                        break
                    stdout_lines.append(rem)
                    if rem.strip():
                        logger.info("[Ditto] %s", rem)
                break

            # Check total timeout
            elapsed = time.time() - t_start
            if elapsed > timeout:
                logger.error(
                    "Ditto 배치 전체 타임아웃 (%ds 초과). 프로세스 종료.",
                    timeout,
                )
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                break

            # Check stall (no output for stall_timeout)
            stall_elapsed = time.time() - last_activity
            if stall_elapsed > stall_timeout:
                logger.error(
                    "Ditto 배치 출력 없음 (%ds). 프로세스 종료.",
                    int(stall_elapsed),
                )
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                break

    except Exception as e:
        process.kill()
        process.wait()
        raise RuntimeError(f"Ditto 배치 모니터링 실패: {e}") from e

    # Clean up temp files after completion
    _cleanup_tmp_files(output_dir)

    # Collect completed clips
    clips = sorted(output_dir.glob("avatar_*.mp4"))
    retcode = process.returncode

    # exit code 2 = dead workers detected (partial success)
    if retcode == 2:
        logger.warning(
            "Ditto 배치 부분 완료: %d/%d 클립 (일부 워커 크래시)",
            len(clips),
            n_audio,
        )
    elif retcode != 0:
        stderr_text = ""
        if process.stderr:
            stderr_text = process.stderr.read()
        logger.error("Ditto 배치 실패 (exit %d): %s", retcode, stderr_text)
        if not clips:
            raise RuntimeError(
                f"Ditto 배치 실행 실패 (exit {retcode}): {stderr_text}"
            )
        logger.warning("부분 결과 %d개 클립 사용", len(clips))
    else:
        logger.info("Ditto 배치 완료: %d개 클립 생성", len(clips))

    return clips
