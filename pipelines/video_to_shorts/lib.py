"""영상 -> 쇼츠/릴스 파이프라인 핵심 로직."""

from __future__ import annotations

import json
import re
from pathlib import Path

from entities.project.model import Project
from entities.subtitle.model import WordTimestamp
from entities.video.model import Video
from features.render_shorts import ShortsProps, ShortsWordTimestamp, render_short
from features.select_viral_segments import ViralSegmentPlan, plan_viral_segments
from features.transcribe_audio import transcribe_to_word_timestamps
from shared.config.schema import AppConfig, ShortsConfig
from shared.lib.ffmpeg import _ffmpeg, _run_ffmpeg, get_duration, trim_video
from shared.lib.file_io import read_text
from shared.lib.logger import get_logger

logger = get_logger()

_FPS = 30


def run_video_to_shorts(
    project: Project,
    config: AppConfig,
    *,
    video_path: Path | None = None,
    max_shorts: int | None = None,
) -> list[Video]:
    """기존 영상에서 쇼츠/릴스를 생성하는 파이프라인.

    4단계:
    1. Word timestamps 추출 (Whisper)
    2. 바이럴 구간 선정 (LLM)
    3. 영상 트림
    4. Remotion 렌더링

    Args:
        project: 프로젝트 객체.
        config: 전체 설정.
        video_path: 소스 영상 경로 (미지정 시 자동 탐색).
        max_shorts: 최대 쇼츠 수 오버라이드.

    Returns:
        생성된 Video 리스트.
    """
    shorts_config = config.shorts
    if max_shorts is not None:
        shorts_config = shorts_config.model_copy(update={"max_shorts": max_shorts})

    shorts_dir = project.shorts_dir
    shorts_dir.mkdir(parents=True, exist_ok=True)

    # 소스 영상 결정 (자막 번인 없는 영상 우선)
    source_video = _resolve_source_video(project, video_path)
    logger.info("소스 영상: %s", source_video.name)

    # ── Step 1: Word timestamps 추출 ──
    word_ts_path = shorts_dir / "word_timestamps.json"
    word_timestamps = _step_word_timestamps(source_video, word_ts_path)

    # ── Step 1.5: SRT 기반 텍스트 보정 (기존 SRT 또는 자동 생성) ──
    srt_path = project.output_dir / "corrected_subtitles.srt"
    corrections_path = project.base_dir / "corrections.txt"

    if srt_path.exists():
        # 기존 흐름: script_to_video가 만든 SRT로 word timestamps 텍스트 교정
        word_timestamps = _correct_word_timestamps(word_timestamps, srt_path)
    else:
        # 외부 영상: Whisper word timestamps → SRT 자동 생성
        logger.info("교정된 SRT 없음 → Whisper word timestamps에서 SRT 자동 생성")
        if corrections_path.exists():
            logger.info("corrections.txt 적용: %s", corrections_path)
            word_timestamps = _apply_text_corrections(word_timestamps, corrections_path)
        _generate_srt_from_words(word_timestamps, srt_path)

    # ── Step 2: 바이럴 구간 선정 ──
    viral_plan_path = shorts_dir / "viral_plan.json"
    script_path = project.script_path if project.script_path.exists() else None
    viral_plan = _step_viral_plan(srt_path, script_path, shorts_config, viral_plan_path)

    # ── Step 2.5: 스킬 생성 훅 타이틀 로드 (있으면 오버라이드) ──
    hook_titles_override = _load_hook_titles_override(shorts_dir)
    if hook_titles_override:
        logger.info("스킬 생성 hook_titles.json 로드: %d개", len(hook_titles_override))

    # ── Step 3 & 4: 트림 + 렌더링 ──
    trimmed_dir = shorts_dir / "trimmed"
    trimmed_dir.mkdir(parents=True, exist_ok=True)

    results: list[Video] = []
    for seg in viral_plan.segments:
        idx = seg.index
        trimmed_path = trimmed_dir / f"trim_{idx:03d}.mp4"
        output_path = shorts_dir / f"short_{idx:03d}.mp4"

        # Step 3: 트림
        if not trimmed_path.exists():
            logger.info("트림 %d: %.1f~%.1fs", idx, seg.start_time, seg.end_time)
            trim_video(
                source_video, trimmed_path,
                start=seg.start_time, end=seg.end_time, accurate=True,
            )
        else:
            logger.info("트림 %d: 재사용", idx)

        # Step 4: Remotion 렌더링
        if output_path.exists():
            logger.info("쇼츠 %d: 재사용", idx)
            duration = get_duration(output_path)
            results.append(
                Video(
                    file_path=output_path,
                    duration=duration,
                    width=1080,
                    height=1920,
                    fps=_FPS,
                )
            )
            continue

        # 구간에 해당하는 word timestamps 필터링 + 프레임 변환
        segment_words = _filter_and_convert_words(word_timestamps, seg.start_time, seg.end_time)

        # hook title: 스킬 생성 파일 우선, 없으면 viral plan에서 추출
        hook_line1, hook_line2, sub_detail = _resolve_hook_title(
            seg, idx, hook_titles_override,
        )

        segment_duration = seg.end_time - seg.start_time
        duration_frames = max(1, int(segment_duration * _FPS))

        props = ShortsProps(
            durationInFrames=duration_frames,
            hookTitle=hook_line1,
            hookTitleLine2=hook_line2,
            subDetail=sub_detail,
            videoSrc="",  # render_short에서 업데이트
            words=segment_words,
            accentColor=shorts_config.accent_color,
            backgroundColor=shorts_config.background_color,
            hookFontSize=shorts_config.hook_font_size,
            subtitleFontSize=shorts_config.subtitle_font_size,
        )

        logger.info("쇼츠 %d 렌더링: %s", idx, hook_line1[:20])
        video = render_short(props, trimmed_path, output_path, shorts_config)
        results.append(video)

    logger.info("쇼츠 생성 완료: %d개", len(results))
    return results


def _resolve_source_video(project: Project, video_path: Path | None) -> Path:
    """소스 영상을 결정 (자막 번인 없는 영상 우선)."""
    if video_path is not None:
        if not video_path.exists():
            raise FileNotFoundError(f"소스 영상을 찾을 수 없습니다: {video_path}")
        return video_path

    candidates = [
        project.output_dir / "video_with_avatar.mp4",
        project.output_dir / "video_raw.mp4",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"소스 영상을 찾을 수 없습니다. 먼저 script-to-video 파이프라인을 실행하세요.\n"
        f"탐색 경로: {[str(c) for c in candidates]}"
    )


def _step_word_timestamps(
    source_video: Path,
    cache_path: Path,
) -> list[WordTimestamp]:
    """Step 1: Word timestamps 추출 (캐싱)."""
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            logger.info("Word timestamps 재사용: %s", cache_path.name)
            return [WordTimestamp.model_validate(w) for w in data]
        except Exception as e:
            logger.warning("캐시 파일 손상, 재생성: %s (%s)", cache_path.name, e)
            cache_path.unlink(missing_ok=True)

    # 오디오 추출 (MP3: Whisper API 25MB 제한 대응, WAV는 장영상에서 초과)
    audio_path = cache_path.parent / "_temp_audio.mp3"
    _extract_audio_mp3(source_video, audio_path)

    try:
        words = transcribe_to_word_timestamps(audio_path)
    finally:
        audio_path.unlink(missing_ok=True)

    # 캐싱
    data = [w.model_dump() for w in words]
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Word timestamps 저장: %d개 -> %s", len(words), cache_path.name)
    return words


def _extract_audio_mp3(video_path: Path, output_path: Path) -> Path:
    """영상에서 오디오를 MP3로 추출 (Whisper API 크기 제한 대응).

    WAV(PCM)는 장영상에서 25MB를 초과할 수 있음.
    MP3 64kbps 16kHz 모노 → 10분 영상 ~4.8MB.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(
        [
            _ffmpeg(), "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "libmp3lame",
            "-ar", "16000",
            "-ac", "1",
            "-b:a", "64k",
            str(output_path),
        ],
        timeout=300,
    )
    return output_path


def _step_viral_plan(
    srt_path: Path,
    script_path: Path | None,
    config: ShortsConfig,
    cache_path: Path,
) -> ViralSegmentPlan:
    """Step 2: 바이럴 구간 선정 (캐싱)."""
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            logger.info("바이럴 계획 재사용: %s", cache_path.name)
            return ViralSegmentPlan.model_validate(data)
        except Exception as e:
            logger.warning("캐시 파일 손상, 재생성: %s (%s)", cache_path.name, e)
            cache_path.unlink(missing_ok=True)

    if not srt_path.exists():
        raise FileNotFoundError(
            f"자막 SRT를 찾을 수 없습니다: {srt_path}\n"
            "Step 1.5에서 SRT가 생성되었어야 합니다."
        )

    plan = plan_viral_segments(srt_path, script_path, config)

    # 캐싱
    cache_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    logger.info("바이럴 계획 저장: %d개 구간 -> %s", len(plan.segments), cache_path.name)
    return plan


def _filter_and_convert_words(
    all_words: list[WordTimestamp],
    start_time: float,
    end_time: float,
) -> list[ShortsWordTimestamp]:
    """구간에 해당하는 단어만 필터링하고 프레임 단위로 변환.

    타임스탬프를 구간 시작 기준 상대 시간으로 변환합니다.
    """
    result: list[ShortsWordTimestamp] = []
    for w in all_words:
        if w.end < start_time or w.start > end_time:
            continue
        # 구간 시작 기준 상대 시간 -> 프레임
        relative_start = max(0.0, w.start - start_time)
        relative_end = max(0.0, w.end - start_time)
        result.append(
            ShortsWordTimestamp(
                word=w.word,
                startFrame=int(relative_start * _FPS),
                endFrame=int(relative_end * _FPS),
            )
        )
    return result


# ── corrections.txt 기반 텍스트 교정 + SRT 자동 생성 ──


def _apply_text_corrections(
    words: list[WordTimestamp],
    corrections_path: Path,
) -> list[WordTimestamp]:
    """corrections.txt 매핑으로 word timestamps 텍스트를 일괄 교정.

    파일 형식:
        틀린단어 → 올바른단어  (또는 ->)
        # 주석, 빈 줄은 무시
    """
    mappings = _parse_corrections(corrections_path)
    if not mappings:
        return words

    corrected: list[WordTimestamp] = []
    total_fixes = 0
    for w in words:
        new_word = w.word
        for wrong, right in mappings:
            if wrong in new_word:
                new_word = new_word.replace(wrong, right)
        if new_word != w.word:
            total_fixes += 1
        corrected.append(WordTimestamp(word=new_word, start=w.start, end=w.end))

    logger.info("corrections.txt 적용: %d개 단어 교정 (%d개 매핑)", total_fixes, len(mappings))
    return corrected


def _parse_corrections(corrections_path: Path) -> list[tuple[str, str]]:
    """corrections.txt를 파싱하여 (틀린단어, 올바른단어) 리스트 반환."""
    content = corrections_path.read_text(encoding="utf-8")
    mappings: list[tuple[str, str]] = []

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # → 또는 -> 구분자
        if "→" in line:
            parts = line.split("→", 1)
        elif "->" in line:
            parts = line.split("->", 1)
        else:
            continue

        wrong = parts[0].strip()
        right = parts[1].strip()
        if wrong and right:
            mappings.append((wrong, right))

    return mappings


def _generate_srt_from_words(
    words: list[WordTimestamp],
    srt_path: Path,
) -> None:
    """Word timestamps를 SRT 자막 파일로 변환.

    세그먼트 분리 기준:
    - 단어 간 gap > 0.7초
    - 세그먼트 길이 > 40자
    - 세그먼트 duration > 4초
    """
    if not words:
        logger.warning("word timestamps가 비어있어 SRT 생성 건너뜀")
        return

    segments: list[tuple[float, float, str]] = []
    seg_words: list[str] = []
    seg_start = words[0].start
    seg_text_len = 0
    prev_end = words[0].start

    for w in words:
        gap = w.start - prev_end
        seg_duration = w.end - seg_start

        # 새 세그먼트 시작 조건
        if seg_words and (gap > 0.7 or seg_text_len > 40 or seg_duration > 4.0):
            segments.append((seg_start, prev_end, " ".join(seg_words)))
            seg_words = []
            seg_start = w.start
            seg_text_len = 0

        seg_words.append(w.word)
        seg_text_len += len(w.word) + 1  # +1 for space
        prev_end = w.end

    # 마지막 세그먼트
    if seg_words:
        segments.append((seg_start, prev_end, " ".join(seg_words)))

    # SRT 포맷 출력
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, (start, end, text) in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
        lines.append(text)
        lines.append("")

    srt_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("SRT 자동 생성: %d개 세그먼트 → %s", len(segments), srt_path.name)


def _format_srt_time(seconds: float) -> str:
    """초를 SRT 타임스탬프 형식(HH:MM:SS,mmm)으로 변환."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ── SRT 파싱 + Word Timestamp 텍스트 보정 ──


def _correct_word_timestamps(
    words: list[WordTimestamp],
    srt_path: Path,
) -> list[WordTimestamp]:
    """교정된 SRT 텍스트로 Whisper word timestamps를 보정.

    Whisper raw word timestamps는 오타가 많음 (예: 숏츠→쇼츠).
    corrected_subtitles.srt의 정확한 텍스트를 word-level 타이밍에 매핑합니다.
    """
    if not srt_path.exists():
        logger.warning("교정된 SRT 없음, word timestamps 보정 건너뜀: %s", srt_path)
        return words

    srt_segments = _parse_srt_segments(srt_path)
    if not srt_segments:
        return words

    corrected: list[WordTimestamp] = []
    word_idx = 0

    for seg_start, seg_end, seg_text in srt_segments:
        # 이 SRT 세그먼트 시간 범위에 속하는 Whisper 단어 수집
        segment_words: list[WordTimestamp] = []
        scan_idx = word_idx
        while scan_idx < len(words):
            w = words[scan_idx]
            # 단어의 중간점이 세그먼트 범위에 들어가는지 판단
            mid = (w.start + w.end) / 2
            if mid > seg_end + 0.15:
                break
            if mid >= seg_start - 0.15:
                segment_words.append(w)
            scan_idx += 1

        if not segment_words:
            continue

        # 다음 세그먼트 시작점 업데이트
        word_idx = scan_idx

        # SRT 텍스트를 단어로 분리 (구두점 제거하여 토큰화)
        corrected_tokens = seg_text.split()
        if not corrected_tokens:
            corrected.extend(segment_words)
            continue

        if len(corrected_tokens) == len(segment_words):
            # 단어 수 일치: 1:1 텍스트 교체, 타이밍 유지
            for w, ct in zip(segment_words, corrected_tokens):
                corrected.append(WordTimestamp(word=ct, start=w.start, end=w.end))
        else:
            # 단어 수 불일치: 글자 수 비례로 타이밍 재분배
            total_start = segment_words[0].start
            total_end = segment_words[-1].end
            total_duration = total_end - total_start

            if total_duration <= 0:
                corrected.extend(segment_words)
                continue

            total_chars = sum(len(t) for t in corrected_tokens)
            if total_chars == 0:
                corrected.extend(segment_words)
                continue

            current_time = total_start
            for ct in corrected_tokens:
                char_ratio = len(ct) / total_chars
                word_duration = total_duration * char_ratio
                corrected.append(
                    WordTimestamp(
                        word=ct,
                        start=round(current_time, 3),
                        end=round(current_time + word_duration, 3),
                    )
                )
                current_time += word_duration

    # SRT 범위 밖의 남은 단어 처리
    while word_idx < len(words):
        corrected.append(words[word_idx])
        word_idx += 1

    logger.info(
        "Word timestamps 텍스트 보정 완료: %d -> %d words (%d SRT segments)",
        len(words), len(corrected), len(srt_segments),
    )
    return corrected


def _parse_srt_segments(srt_path: Path) -> list[tuple[float, float, str]]:
    """SRT 파일을 파싱하여 (start, end, text) 리스트를 반환."""
    content = read_text(srt_path)
    segments: list[tuple[float, float, str]] = []

    # SRT 블록 분리 (빈 줄 기준)
    blocks = re.split(r"\n\s*\n", content.strip())
    timestamp_re = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})"
    )

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue

        # 타임스탬프 라인 찾기
        ts_match = None
        text_start_idx = 0
        for i, line in enumerate(lines):
            ts_match = timestamp_re.search(line)
            if ts_match:
                text_start_idx = i + 1
                break

        if not ts_match or text_start_idx >= len(lines):
            continue

        h1, m1, s1, ms1, h2, m2, s2, ms2 = ts_match.groups()
        start = int(h1) * 3600 + int(m1) * 60 + int(s1) + int(ms1) / 1000
        end = int(h2) * 3600 + int(m2) * 60 + int(s2) + int(ms2) / 1000
        text = " ".join(lines[text_start_idx:]).strip()

        if text:
            segments.append((start, end, text))

    return segments


# ── 스킬 생성 훅 타이틀 오버라이드 ──


def _load_hook_titles_override(shorts_dir: Path) -> list[dict] | None:
    """스킬(/generate-shorts-title)로 사전 생성된 hook_titles.json 로드.

    파일이 있으면 리스트 반환, 없으면 None (viral plan fallback).
    """
    path = shorts_dir / "hook_titles.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list) and data:
            return data
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.warning("hook_titles.json 파싱 실패: %s", e)
    return None


def _resolve_hook_title(
    seg,
    idx: int,
    hook_titles_override: list[dict] | None,
) -> tuple[str, str, str]:
    """훅 타이틀 결정: 스킬 파일 우선, 없으면 viral plan fallback.

    Returns:
        (line1, line2, subDetail)
    """
    if hook_titles_override:
        for entry in hook_titles_override:
            if entry.get("index") == idx:
                return (
                    entry.get("line1", ""),
                    entry.get("line2", ""),
                    entry.get("subDetail", ""),
                )
        # 매칭 실패 시 첫 번째 항목 사용 (전체 동일 제목)
        first = hook_titles_override[0]
        return (
            first.get("line1", ""),
            first.get("line2", ""),
            first.get("subDetail", ""),
        )

    # Fallback: viral plan의 hook_title (\n으로 2줄 분리)
    hook_lines = seg.hook_title.split("\n", 1)
    hook_line1 = hook_lines[0].strip()
    hook_line2 = hook_lines[1].strip() if len(hook_lines) > 1 else ""
    return hook_line1, hook_line2, ""
