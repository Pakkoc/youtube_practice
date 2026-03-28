"""대본 -> 쇼츠 파이프라인 오케스트레이션.

TSX 슬라이드 + 훅 타이틀 + 워드 자막을 1080x1920으로 렌더링하는 6단계 파이프라인.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from entities.audio.model import AudioClip
from entities.project.model import Project
from entities.video.model import Video
from shared.config.schema import AppConfig
from shared.lib.logger import get_logger

logger = get_logger()


def run_script_to_shorts(
    project: Project,
    config: AppConfig,
    *,
    include_broll: bool = False,
) -> Video:
    """대본에서 9:16 쇼츠를 생성하는 전체 파이프라인.

    실행 순서:
    1. 대본 문단 분리 + 씬 분할
    2. TTS 생성 (ElevenLabs)
    3. Whisper 워드 타임스탬프
    4. 훅 타이틀 생성 (GPT-5-mini)
    5. Remotion 렌더링 (ShortsSlotPool 병렬)
    6. FFmpeg 합성 → final_shorts.mp4

    Args:
        project: 프로젝트 엔티티.
        config: 전체 설정.
        include_broll: B-roll 배경 사용 여부.

    Returns:
        생성된 Video 엔티티.
    """
    from features.split_paragraphs import load_script_and_split

    project.ensure_dirs()

    shorts_config = config.shorts_slide
    slides_dir = project.shorts_slides_dir / "slides"
    output_dir = project.shorts_slides_dir / "output"
    slides_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    total_steps = 6

    logger.info("Script-to-Shorts 파이프라인 시작: %s", project.name)

    # ===================================================================
    # Step 1: 대본 문단 분리 + 씬 분할
    # ===================================================================
    logger.info("[1/%d] 대본 문단 분리", total_steps)
    script = load_script_and_split(
        script_path=project.script_path,
        output_dir=project.paragraphs_dir,
    )
    logger.info("-> %d개 문단 분리 완료", len(script.paragraphs))

    if not script.paragraphs:
        raise RuntimeError("대본에서 문단을 찾을 수 없습니다.")

    if config.pipeline.scenes.enabled:
        from features.split_paragraphs.lib import save_paragraphs
        from features.split_scenes import split_paragraphs_into_scenes

        scenes = split_paragraphs_into_scenes(
            script.paragraphs,
            merge_threshold=config.pipeline.scenes.merge_threshold,
        )
        original_count = len(script.paragraphs)

        from entities.script.model import Paragraph, Script

        scene_paragraphs = [
            Paragraph(index=s.index, text=s.text)
            for s in scenes
        ]
        script = Script(raw_text=script.raw_text, paragraphs=scene_paragraphs)
        save_paragraphs(script, project.paragraphs_dir)

        logger.info(
            "-> %d개 문단 → %d개 씬으로 재분할",
            original_count, len(scenes),
        )

    paragraphs = script.paragraphs

    # ===================================================================
    # Step 1.5: TTS 사전 자동 강화 (영어/숫자 발음 보강)
    # ===================================================================
    from features.normalize_text import enhance_tts_dictionary, load_tts_dictionary

    tts_dict = load_tts_dictionary()
    enhance_tts_dictionary(paragraphs, tts_dict)

    # ===================================================================
    # Step 2: TTS 생성
    # ===================================================================
    logger.info("[2/%d] TTS 생성", total_steps)
    audio_clips = _generate_tts(paragraphs, project.audio_dir, config.tts)
    logger.info("-> TTS 생성 완료: %d개", len(audio_clips))

    # ===================================================================
    # Step 3: Whisper 워드 타임스탬프
    # ===================================================================
    logger.info("[3/%d] Whisper 워드 타임스탬프 추출", total_steps)
    word_data = _extract_word_timestamps(
        audio_clips=audio_clips,
        slides_dir=slides_dir,
        language=shorts_config.whisper_language,
        fps=shorts_config.fps,
    )
    logger.info("-> 워드 타임스탬프 완료: %d개 씬", len(word_data))

    # 원본 스크립트 텍스트로 자막 정렬 (Whisper 전사 → 원본 대본)
    word_data = _align_words_to_script(word_data, paragraphs)

    # 워드 자막 표시 정규화 (한글 숫자 → 아라비아 숫자)
    word_data = _normalize_word_display(word_data)

    # ===================================================================
    # Step 4: 훅 타이틀 생성
    # ===================================================================
    logger.info("[4/%d] 훅 타이틀 생성", total_steps)
    hook_titles = _generate_hook_titles(
        slides_dir=slides_dir,
        paragraph_count=len(paragraphs),
    )
    logger.info("-> 훅 타이틀 완료: %d개", len(hook_titles))

    # ===================================================================
    # Step 5: Remotion 렌더링 (ShortsSlotPool 병렬)
    # ===================================================================
    logger.info("[5/%d] Remotion 쇼츠 슬라이드 렌더링", total_steps)
    slide_videos = _render_shorts_slides(
        paragraphs=paragraphs,
        audio_clips=audio_clips,
        word_data=word_data,
        hook_titles=hook_titles,
        slides_dir=slides_dir,
        config=shorts_config,
    )
    logger.info("-> 렌더링 완료: %d개 슬라이드", len(slide_videos))

    # ===================================================================
    # Step 6: FFmpeg 합성 → final_shorts.mp4
    # ===================================================================
    logger.info("[6/%d] FFmpeg 합성 (video + audio)", total_steps)
    from shared.lib.ffmpeg import compose_video_slideshow

    video_audio_pairs = [
        (v.file_path, clip.file_path)
        for v, clip in zip(slide_videos, audio_clips)
    ]
    final_path = output_dir / "final_shorts.mp4"
    compose_video_slideshow(
        video_audio_pairs,
        final_path,
        fps=shorts_config.fps,
        width=shorts_config.width,
        height=shorts_config.height,
    )

    from shared.lib.ffmpeg import get_duration

    duration = get_duration(final_path)

    video = Video(
        file_path=final_path,
        duration=duration,
        width=shorts_config.width,
        height=shorts_config.height,
        fps=shorts_config.fps,
    )

    logger.info(
        "Script-to-Shorts 완료: %s (%.1f초, %dx%d)",
        video.file_path,
        video.duration,
        video.width,
        video.height,
    )
    return video


# ===================================================================
# 개별 스텝 함수
# ===================================================================


def _normalize_word_display(word_data: list[list[dict]]) -> list[list[dict]]:
    """워드 타임스탬프의 표시 텍스트를 정규화.

    2단계 처리:
    1. 역 발음 사전: Whisper 전사의 한글 발음 → 원어 (클로드 → Claude)
    2. normalize_for_display: 한글 숫자 → 아라비아 숫자 (삼십퍼센트 → 30%)

    씬별로 단어를 조합 → 정규화 → 재분리. 단어 수가 달라지면 원본 유지.
    """
    from features.normalize_text import (
        apply_reverse_dictionary,
        build_reverse_dictionary,
        load_tts_dictionary,
        normalize_for_display,
    )

    # Step 1: 역 발음 사전 적용 (단어 단위)
    tts_dict = load_tts_dictionary()
    reverse_dict = build_reverse_dictionary(tts_dict)
    if reverse_dict:
        for words in word_data:
            for w in words:
                w["word"] = apply_reverse_dictionary(w["word"], reverse_dict)

    # Step 2: 한글 숫자 → 아라비아 숫자 (씬 단위)
    scene_texts = [" ".join(w["word"] for w in words) for words in word_data]
    normalized_texts = normalize_for_display(scene_texts)

    for i, (words, normalized) in enumerate(zip(word_data, normalized_texts)):
        normalized_words = normalized.split()
        if len(normalized_words) == len(words):
            for w, nw in zip(words, normalized_words):
                w["word"] = nw
        else:
            logger.debug(
                "씬 %d: 정규화 후 단어 수 불일치 (%d → %d), 원본 유지",
                i + 1,
                len(words),
                len(normalized_words),
            )

    return word_data


def _align_words_to_script(
    word_data: list[list[dict]],
    paragraphs,
) -> list[list[dict]]:
    """Whisper 워드 타임스탬프의 표시 텍스트를 원본 스크립트로 교체.

    Whisper 전사는 발음 기반이므로 원본과 다를 수 있다.
    (예: '/init' -> '이닛', 'CLAUDE.md' -> 'cloud samd')
    타이밍은 Whisper 기준을 유지하고 표시 텍스트만 원본으로 교체.

    워드 수 일치: 1:1 텍스트 교체 (타이밍 유지).
    워드 수 불일치: 문자 수 비례로 시간 재분배.
    """
    for words, para in zip(word_data, paragraphs):
        original_words = para.text.split()

        if not words or not original_words:
            continue

        if len(original_words) == len(words):
            for ow, ww in zip(original_words, words):
                ww["word"] = ow
        else:
            whisper_count = len(words)
            total_start = words[0]["startFrame"]
            total_end = words[-1]["endFrame"]
            total_duration = max(1, total_end - total_start)

            char_counts = [max(1, len(w)) for w in original_words]
            total_chars = sum(char_counts)

            new_words = []
            current_frame = total_start
            for i, word in enumerate(original_words):
                weight = char_counts[i] / total_chars
                duration = int(total_duration * weight)
                start_frame = current_frame
                end_frame = start_frame + duration

                if i == len(original_words) - 1:
                    end_frame = total_end

                new_words.append({
                    "word": word,
                    "startFrame": start_frame,
                    "endFrame": end_frame,
                })
                current_frame = end_frame

            words.clear()
            words.extend(new_words)

            logger.debug(
                "워드 수 불일치 (Whisper %d -> 원본 %d), 시간 비례 재분배",
                whisper_count,
                len(original_words),
            )

    return word_data


def _generate_tts(paragraphs, audio_dir: Path, tts_config) -> list[AudioClip]:
    """TTS 생성 (기존 파일 재사용)."""
    from features.generate_tts import create_tts_backend, generate_tts_for_paragraphs

    tts_backend = create_tts_backend(tts_config)
    logger.info("  [TTS] 백엔드: %s", tts_backend.name)

    audio_clips = generate_tts_for_paragraphs(
        paragraphs=paragraphs,
        audio_dir=audio_dir,
        config=tts_config,
        backend=tts_backend,
    )
    return audio_clips


def _extract_word_timestamps(
    audio_clips: list[AudioClip],
    slides_dir: Path,
    language: str,
    fps: int,
) -> list[list[dict]]:
    """각 오디오 클립에서 Whisper 워드 타임스탬프 추출.

    캐시: slides_dir/words_{idx}.json

    Returns:
        씬별 워드 타임스탬프 리스트 (각 엔트리: [{"word", "startFrame", "endFrame"}, ...])
    """
    from features.transcribe_audio import transcribe_to_word_timestamps

    all_words: list[list[dict]] = []

    for clip in audio_clips:
        idx = clip.index
        cache_path = slides_dir / f"words_{idx:03d}.json"

        if cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            all_words.append(cached)
            logger.debug("워드 타임스탬프 캐시 사용: %s", cache_path.name)
            continue

        word_timestamps = transcribe_to_word_timestamps(
            clip.file_path, language=language,
        )

        frame_words = [
            {
                "word": w.word,
                "startFrame": int(w.start * fps),
                "endFrame": int(w.end * fps),
            }
            for w in word_timestamps
        ]

        cache_path.write_text(
            json.dumps(frame_words, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        all_words.append(frame_words)
        logger.info("워드 타임스탬프 추출: %s (%d 단어)", clip.file_path.name, len(frame_words))

    return all_words


def _generate_hook_titles(
    slides_dir: Path,
    paragraph_count: int,
) -> list[dict]:
    """훅 타이틀 로드 (스킬 사전 생성 필수, API 미사용).

    /generate-shorts-title 스킬로 미리 생성된 hook_titles.json을 로드한다.
    파일이 없으면 에러를 발생시킨다.

    캐시: slides_dir/hook_titles.json

    Returns:
        [{"index": 1, "line1": "...", "line2": "...", "subDetail": "..."}, ...]
    """
    cache_path = slides_dir / "hook_titles.json"

    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if len(cached) >= paragraph_count:
            logger.info("훅 타이틀 로드: %d개", len(cached))
            return cached
        logger.warning(
            "훅 타이틀 수 부족 (%d < %d), 기존 항목으로 패딩",
            len(cached), paragraph_count,
        )
        # 마지막 항목의 제목으로 부족분 패딩
        last = cached[-1]
        while len(cached) < paragraph_count:
            cached.append({
                "index": len(cached) + 1,
                "line1": last["line1"],
                "line2": last.get("line2", ""),
            })
        cache_path.write_text(
            json.dumps(cached, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return cached

    raise FileNotFoundError(
        f"훅 타이틀 파일이 없습니다: {cache_path}\n"
        f"/generate-shorts-title 스킬로 먼저 hook_titles.json을 생성하세요."
    )


def _render_shorts_slides(
    paragraphs,
    audio_clips: list[AudioClip],
    word_data: list[list[dict]],
    hook_titles: list[dict],
    slides_dir: Path,
    config,
) -> list[Video]:
    """ShortsSlotPool을 사용하여 쇼츠 슬라이드 병렬 렌더링.

    TSX 파일이 slides_dir/{idx:03d}.tsx에 존재해야 함.
    """
    from features.render_shorts_slides import (
        ShortsSlideProps,
        ShortsSlideWordTimestamp,
        ShortsSlotPool,
        render_shorts_slide,
    )

    remotion_project_path = Path(__file__).parents[2] / "remotion"
    slot_pool = ShortsSlotPool(
        remotion_project_path,
        num_slots=config.render_parallel_slots,
    )

    total_slides = len(paragraphs)
    tasks: list[tuple[int, AudioClip, list[dict], dict]] = []

    for i, (clip, words, hook) in enumerate(
        zip(audio_clips, word_data, hook_titles)
    ):
        tasks.append((i, clip, words, hook))

    results: list[tuple[int, Video]] = []
    errors: list[Exception] = []

    def _render_one(
        idx: int,
        clip: AudioClip,
        words: list[dict],
        hook: dict,
    ) -> tuple[int, Video]:
        tsx_path = slides_dir / f"{clip.index:03d}.tsx"
        output_mp4 = slides_dir / f"{clip.index:03d}.mp4"

        # 캐시 체크: mp4 존재 + duration 일치
        if output_mp4.exists():
            from shared.lib.ffmpeg import get_duration

            existing_dur = get_duration(output_mp4)
            expected_dur = clip.duration
            if abs(existing_dur - expected_dur) < 0.5:
                logger.info("쇼츠 렌더 캐시: %s", output_mp4.name)
                return idx, Video(
                    file_path=output_mp4,
                    duration=existing_dur,
                    width=config.width,
                    height=config.height,
                    fps=config.fps,
                )

        if not tsx_path.exists():
            raise FileNotFoundError(
                f"TSX 파일이 없습니다: {tsx_path}. "
                f"/generate-shorts-slides 스킬로 먼저 TSX를 생성하세요."
            )

        tsx_code = tsx_path.read_text(encoding="utf-8")
        duration_frames = max(1, int(clip.duration * config.fps))

        word_timestamps = [
            ShortsSlideWordTimestamp(
                word=w["word"],
                startFrame=w["startFrame"],
                endFrame=w["endFrame"],
            )
            for w in words
        ]

        props = ShortsSlideProps(
            durationInFrames=duration_frames,
            hookTitle=hook.get("line1", ""),
            hookTitleLine2=hook.get("line2", ""),
            subDetail=hook.get("subDetail", ""),
            words=word_timestamps,
            accentColor=config.accent_color,
            backgroundColor=config.background_color,
            hookFontSize=config.hook_font_size,
            subtitleFontSize=config.subtitle_font_size,
            slideIndex=idx + 1,
            totalSlides=total_slides,
        )

        video = render_shorts_slide(
            props=props,
            tsx_code=tsx_code,
            output_path=output_mp4,
            config=config,
            slot_pool=slot_pool,
        )
        return idx, video

    with ThreadPoolExecutor(max_workers=slot_pool.num_slots) as executor:
        futures = {
            executor.submit(_render_one, idx, clip, words, hook): idx
            for idx, clip, words, hook in tasks
        }

        for future in as_completed(futures):
            try:
                idx, video = future.result()
                results.append((idx, video))
            except Exception as e:
                logger.error("쇼츠 슬라이드 렌더 실패: %s", e)
                errors.append(e)

    # 슬롯 원본 복원
    slot_pool.restore_all()

    if errors:
        raise errors[0]

    # 인덱스 순서로 정렬
    results.sort(key=lambda x: x[0])
    return [v for _, v in results]
