"""FFmpeg 래퍼 함수들."""

from __future__ import annotations

import functools
import shutil
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess, TimeoutExpired

from shared.lib import subprocess
from shared.lib.logger import get_logger

logger = get_logger()

# 기본 타임아웃 (초)
_TIMEOUT_PROBE = 30  # ffprobe 조회
_TIMEOUT_ENCODE = 600  # 인코딩 작업 (10분)
_TIMEOUT_COPY = 120  # stream copy 작업 (2분)


@functools.lru_cache(maxsize=4)
def _find_binary(name: str) -> str:
    """시스템 PATH에서 바이너리 경로를 찾아 반환. 없으면 이름 그대로 반환."""
    path = shutil.which(name)
    if path:
        return path
    logger.warning("%s를 PATH에서 찾을 수 없습니다. 기본 이름으로 시도합니다.", name)
    return name


def _ffmpeg() -> str:
    """ffmpeg 바이너리 경로."""
    return _find_binary("ffmpeg")


def _ffprobe() -> str:
    """ffprobe 바이너리 경로."""
    return _find_binary("ffprobe")


def _run_ffmpeg(
    cmd: list[str],
    *,
    timeout: int = _TIMEOUT_ENCODE,
    check: bool = True,
    **kwargs: object,
) -> CompletedProcess[str]:
    """FFmpeg 실행 래퍼 — 타임아웃 + 실패 시 stderr 로깅.

    Args:
        cmd: FFmpeg 명령어 리스트.
        timeout: 타임아웃 (초). 기본 600초.
        check: True면 returncode != 0 시 CalledProcessError 발생.
        **kwargs: subprocess.run에 전달할 추가 인자.

    Returns:
        CompletedProcess.
    """
    kwargs.setdefault("capture_output", True)
    try:
        result = subprocess.run(cmd, check=check, timeout=timeout, **kwargs)
        return result
    except CalledProcessError as e:
        stderr_tail = (e.stderr or "")[-800:] if e.stderr else "(no stderr)"
        logger.error(
            "FFmpeg 실패 (returncode=%d): %s\nstderr: %s",
            e.returncode,
            " ".join(cmd[:6]),
            stderr_tail,
        )
        raise
    except TimeoutExpired:
        logger.error(
            "FFmpeg 타임아웃 (%d초 초과): %s", timeout, " ".join(cmd[:6])
        )
        raise


def check_ffmpeg() -> bool:
    """FFmpeg 설치 여부를 확인."""
    ffmpeg_path = _ffmpeg()
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            check=False,
            timeout=_TIMEOUT_PROBE,
        )
        return result.returncode == 0
    except (FileNotFoundError, TimeoutExpired):
        return False


def get_duration(media_path: Path) -> float:
    """미디어 파일의 길이(초)를 반환.

    Args:
        media_path: 미디어 파일 경로.

    Returns:
        재생 시간(초).
    """
    result = _run_ffmpeg(
        [
            _ffprobe(),
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media_path),
        ],
        timeout=_TIMEOUT_PROBE,
    )
    raw = result.stdout.strip()
    try:
        return float(raw)
    except (ValueError, TypeError):
        raise ValueError(
            f"ffprobe returned invalid duration '{raw}' "
            f"for {media_path}"
        )


def _to_concat_entry(file_path: Path, list_dir: Path) -> str:
    """concat 리스트용 경로 문자열 생성 (FFmpeg Windows 호환).

    FFmpeg concat demuxer는 Windows 백슬래시를 파싱하지 못함.
    리스트 파일 기준 상대 경로 + forward slash로 변환.
    """
    try:
        rel = file_path.relative_to(list_dir)
    except ValueError:
        # 다른 드라이브/루트 — 절대 경로 사용
        rel = file_path
    return f"file '{rel.as_posix()}'"


def concat_audio(audio_files: list[Path], output_path: Path) -> Path:
    """여러 오디오 파일을 순서대로 합치기.

    Args:
        audio_files: 합칠 오디오 파일 목록 (순서대로).
        output_path: 출력 파일 경로.

    Returns:
        출력 파일 경로.
    """
    list_file = output_path.parent / "_concat_list.txt"
    list_dir = list_file.parent
    list_content = "\n".join(_to_concat_entry(f, list_dir) for f in audio_files)
    list_file.write_text(list_content, encoding="utf-8")

    try:
        _run_ffmpeg(
            [
                _ffmpeg(),
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c",
                "copy",
                str(output_path),
            ],
            timeout=_TIMEOUT_COPY,
        )
    finally:
        list_file.unlink(missing_ok=True)

    return output_path


def _get_video_resolution(video_path: Path) -> tuple[int, int] | None:
    """비디오 해상도(width, height)를 반환. 실패 시 None."""
    try:
        result = _run_ffmpeg(
            [
                _ffprobe(),
                "-v",
                "quiet",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=p=0",
                str(video_path),
            ],
            timeout=_TIMEOUT_PROBE,
            check=False,
        )
        parts = result.stdout.strip().split(",")
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except (ValueError, CalledProcessError):
        pass
    return None


def _check_concat_compatibility(video_files: list[Path]) -> bool:
    """모든 비디오 파일의 해상도가 동일한지 확인."""
    if len(video_files) <= 1:
        return True
    first_res = _get_video_resolution(video_files[0])
    if first_res is None:
        return False
    for f in video_files[1:]:
        res = _get_video_resolution(f)
        if res != first_res:
            logger.warning(
                "해상도 불일치: %s=%s vs %s=%s -> 재인코딩으로 전환",
                video_files[0].name, first_res, f.name, res,
            )
            return False
    return True


def concat_videos(video_files: list[Path], output_path: Path) -> Path:
    """여러 비디오 파일을 순서대로 합치기.

    해상도가 동일하면 stream copy (빠름), 불일치 시 자동으로 재인코딩.

    Args:
        video_files: 합칠 비디오 파일 목록 (순서대로).
        output_path: 출력 파일 경로.

    Returns:
        출력 파일 경로.
    """
    if not _check_concat_compatibility(video_files):
        logger.info("concat_videos: 해상도 불일치 감지, 재인코딩으로 전환")
        return concat_videos_reencode(video_files, output_path)

    list_file = output_path.parent / "_concat_video_list.txt"
    list_dir = list_file.parent
    list_content = "\n".join(_to_concat_entry(f, list_dir) for f in video_files)
    list_file.write_text(list_content, encoding="utf-8")

    try:
        _run_ffmpeg(
            [
                _ffmpeg(),
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c",
                "copy",
                str(output_path),
            ],
            timeout=_TIMEOUT_COPY,
        )
    finally:
        list_file.unlink(missing_ok=True)

    return output_path


def concat_videos_reencode(video_files: list[Path], output_path: Path) -> Path:
    """여러 비디오 파일을 filter_complex concat으로 합치기 (재인코딩).

    코덱 파라미터가 다른 영상도 안전하게 합칩니다.
    concat demuxer(stream copy)에서 타임스탬프 오류가 발생하는 경우 사용.

    Args:
        video_files: 합칠 비디오 파일 목록 (순서대로).
        output_path: 출력 파일 경로.

    Returns:
        출력 파일 경로.
    """
    inputs: list[str] = []
    for f in video_files:
        inputs.extend(["-i", str(f)])

    n = len(video_files)
    filter_parts = "".join(f"[{i}:v:0][{i}:a:0]" for i in range(n))
    filter_complex = f"{filter_parts}concat=n={n}:v=1:a=1[outv][outa]"

    _run_ffmpeg(
        [
            _ffmpeg(),
            "-y",
            *inputs,
            "-filter_complex",
            filter_complex,
            "-map",
            "[outv]",
            "-map",
            "[outa]",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ],
        timeout=_TIMEOUT_ENCODE,
    )
    return output_path


def trim_video(
    input_path: Path,
    output_path: Path,
    *,
    start: float,
    end: float,
    accurate: bool = False,
) -> Path:
    """비디오를 지정 구간으로 트림.

    Args:
        input_path: 입력 비디오 경로.
        output_path: 출력 비디오 경로.
        start: 시작 시간(초).
        end: 종료 시간(초).
        accurate: True면 재인코딩으로 프레임 정확도 보장 (쇼츠 등).
            False면 stream copy (빠르지만 keyframe 단위).

    Returns:
        출력 비디오 경로.
    """
    mode = "재인코딩" if accurate else "stream copy"
    logger.debug("비디오 트림 (%s): %s (%.1f~%.1f초)", mode, input_path.name, start, end)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    duration = end - start

    if accurate:
        # 재인코딩: -ss before -i (빠른 seek) + 재인코딩 (프레임 정확)
        _run_ffmpeg(
            [
                _ffmpeg(),
                "-y",
                "-ss",
                str(start),
                "-i",
                str(input_path),
                "-t",
                str(duration),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-avoid_negative_ts",
                "make_zero",
                str(output_path),
            ],
            timeout=_TIMEOUT_ENCODE,
        )
    else:
        # Stream copy: 빠르지만 keyframe 단위로만 정확
        _run_ffmpeg(
            [
                _ffmpeg(),
                "-y",
                "-ss",
                str(start),
                "-i",
                str(input_path),
                "-t",
                str(duration),
                "-c",
                "copy",
                "-avoid_negative_ts",
                "make_zero",
                str(output_path),
            ],
            timeout=_TIMEOUT_COPY,
        )

    return output_path


def compose_slideshow(
    image_audio_pairs: list[tuple[Path, Path]],
    output_path: Path,
    fps: int = 30,
) -> Path:
    """이미지+오디오 쌍으로 슬라이드쇼 영상을 합성.

    각 이미지는 대응하는 오디오 길이만큼 표시된다.

    Args:
        image_audio_pairs: (이미지, 오디오) 경로 쌍 목록.
        output_path: 출력 영상 경로.
        fps: 프레임레이트.

    Returns:
        출력 영상 경로.
    """
    segments: list[Path] = []
    temp_dir = output_path.parent / "_temp_segments"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        for i, (img, audio) in enumerate(image_audio_pairs):
            segment_path = temp_dir / f"segment_{i:03d}.mp4"

            # 오디오 길이를 먼저 구해서 -t 옵션으로 명시적 지정
            # (-shortest가 -loop 1과 함께 사용 시 정확하지 않은 문제 해결)
            audio_duration = get_duration(audio)

            _run_ffmpeg(
                [
                    _ffmpeg(),
                    "-y",
                    "-loop",
                    "1",
                    "-i",
                    str(img),
                    "-i",
                    str(audio),
                    "-c:v",
                    "libx264",
                    "-tune",
                    "stillimage",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-pix_fmt",
                    "yuv420p",
                    "-vf",
                    f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black,fps={fps}",
                    "-t",
                    str(audio_duration),
                    str(segment_path),
                ],
                timeout=_TIMEOUT_ENCODE,
            )
            segments.append(segment_path)

        # 세그먼트 합치기
        list_content = "\n".join(
            _to_concat_entry(s, temp_dir) for s in segments
        )
        list_file = temp_dir / "_segments_list.txt"
        list_file.write_text(list_content, encoding="utf-8")

        _run_ffmpeg(
            [
                _ffmpeg(),
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c",
                "copy",
                str(output_path),
            ],
            timeout=_TIMEOUT_COPY,
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return output_path



def compose_video_slideshow(
    video_audio_pairs: list[tuple[Path, Path]],
    output_path: Path,
    fps: int = 30,
    width: int = 1920,
    height: int = 1080,
) -> Path:
    """비디오 슬라이드 + 오디오 쌍으로 슬라이드쇼 영상을 합성.

    Remotion 슬라이드(MP4)와 오디오를 결합합니다.
    각 비디오 슬라이드는 오디오 duration에 맞춰 잘립니다.

    Args:
        video_audio_pairs: (비디오, 오디오) 경로 쌍 목록.
        output_path: 출력 영상 경로.
        fps: 프레임레이트.
        width: 출력 영상 가로 해상도.
        height: 출력 영상 세로 해상도.

    Returns:
        출력 영상 경로.
    """
    segments: list[Path] = []
    temp_dir = output_path.parent / "_temp_segments"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        for i, (video, audio) in enumerate(video_audio_pairs):
            segment_path = temp_dir / f"segment_{i:03d}.mp4"
            audio_duration = get_duration(audio)

            vf = (
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:-1:-1:color=black,fps={fps}"
            )

            _run_ffmpeg(
                [
                    _ffmpeg(),
                    "-y",
                    "-i",
                    str(video),
                    "-i",
                    str(audio),
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-pix_fmt",
                    "yuv420p",
                    "-vf",
                    vf,
                    "-t",
                    str(audio_duration),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    str(segment_path),
                ],
                timeout=_TIMEOUT_ENCODE,
            )
            segments.append(segment_path)

        # 세그먼트 합치기
        list_content = "\n".join(
            _to_concat_entry(s, temp_dir) for s in segments
        )
        list_file = temp_dir / "_segments_list.txt"
        list_file.write_text(list_content, encoding="utf-8")

        _run_ffmpeg(
            [
                _ffmpeg(),
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c",
                "copy",
                str(output_path),
            ],
            timeout=_TIMEOUT_COPY,
        )
    finally:
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    return output_path


def split_audio_by_ratio(
    audio_path: Path,
    ratios: list[float],
    output_dir: Path,
    start_index: int = 1,
) -> list[Path]:
    """오디오를 비율 목록에 따라 분할.

    Args:
        audio_path: 입력 오디오 파일 경로.
        ratios: 각 씬의 글자 수 비율 (합계 = 1.0).
        output_dir: 출력 디렉토리.
        start_index: 출력 파일 시작 인덱스 (1-based).

    Returns:
        분할된 오디오 파일 경로 목록.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    total_duration = get_duration(audio_path)

    # 비율을 시각(초)으로 변환
    cumulative = 0.0
    segments: list[tuple[float, float]] = []
    for i, ratio in enumerate(ratios):
        start = cumulative * total_duration
        if i == len(ratios) - 1:
            # 마지막 세그먼트는 끝까지 (부동소수점 오차 방지)
            end = total_duration
        else:
            end = (cumulative + ratio) * total_duration
        segments.append((start, end))
        cumulative += ratio

    output_paths: list[Path] = []
    for i, (start, end) in enumerate(segments):
        idx = start_index + i
        output_path = output_dir / f"{idx:03d}.wav"
        duration = end - start

        if duration <= 0:
            logger.warning("씬 %d 오디오 duration이 0 이하 (%.3f초), 건너뜀", idx, duration)
            continue

        _run_ffmpeg(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(audio_path),
                "-ss",
                str(start),
                "-t",
                str(duration),
                "-c",
                "copy",
                str(output_path),
            ],
            timeout=_TIMEOUT_COPY,
        )
        output_paths.append(output_path)

    return output_paths


