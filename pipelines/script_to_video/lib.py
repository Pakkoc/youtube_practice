"""대본 -> 영상 파이프라인 오케스트레이션.

B-roll 이미지를 Remotion 슬라이드 배경으로 통합하는 7단계 파이프라인.
"""

from __future__ import annotations

import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from entities.audio.model import AudioClip
from entities.project.model import Project
from entities.slide.model import Slide
from entities.video.model import Video
from shared.config.schema import AppConfig
from shared.lib.logger import get_logger

logger = get_logger()


def run_script_to_video(
    project: Project,
    config: AppConfig,
    *,
    include_broll: bool = True,
) -> Video:
    """대본에서 영상을 생성하는 전체 파이프라인.

    실행 순서:
    1. 대본 문단 분리
    2. TTS + B-roll 이미지 + Remotion props (3-way 병렬)
    3. Remotion 슬라이드 렌더링 (B-roll 배경 포함)
    4. 영상 합성 (raw)
    5. 자막 생성
    6. 아바타 오버레이 (선택)
    7. 자막 합성 -> final_video.mp4

    Args:
        project: 프로젝트 엔티티.
        config: 전체 설정.
        include_broll: B-roll 생성 여부 (기본: True).

    Returns:
        생성된 Video 엔티티.
    """
    from features.split_paragraphs import load_script_and_split

    project.ensure_dirs()

    # pipeline Control Panel의 broll.enabled와 CLI --no-broll 플래그를 결합
    include_broll = include_broll and config.pipeline.broll.enabled

    # 총 스텝 수 계산
    # Remotion: 문단분리 + 병렬 + 렌더링 + 합성 + 자막생성 + [아바타] + 자막합성
    include_avatar = getattr(config.avatar, "enabled", False)

    # 아웃트로 영상 존재 여부 확인
    outro_video_file = Path(config.outro.video_path)
    if not outro_video_file.is_absolute():
        outro_video_file = Path.cwd() / outro_video_file
    include_outro = config.outro.enabled and outro_video_file.exists()

    total_steps = 7 if include_avatar else 6
    if include_outro:
        total_steps += 1

    logger.info(
        "파이프라인 시작: %s (B-roll: %s, Avatar: %s)",
        project.name,
        include_broll,
        include_avatar,
    )

    # ===================================================================
    # Step 1: 대본 문단 분리
    # ===================================================================
    logger.info("[1/%d] 대본 문단 분리", total_steps)
    script = load_script_and_split(
        script_path=project.script_path,
        output_dir=project.paragraphs_dir,
    )
    logger.info("-> %d개 문단 분리 완료", len(script.paragraphs))

    if not script.paragraphs:
        raise RuntimeError("대본에서 문단을 찾을 수 없습니다.")

    # 씬 분할: 문단을 문장 단위로 재분할하여 paragraphs를 덮어씀
    # 이후 파이프라인은 씬을 문단으로 취급 (TTS도 씬 단위로 직접 생성)
    if config.pipeline.scenes.enabled:
        from features.split_paragraphs.lib import save_paragraphs
        from features.split_scenes import split_paragraphs_into_scenes

        scenes = split_paragraphs_into_scenes(
            script.paragraphs,
            merge_threshold=config.pipeline.scenes.merge_threshold,
        )
        original_count = len(script.paragraphs)

        # 씬을 새로운 Paragraph로 변환
        from entities.script.model import Paragraph, Script

        scene_paragraphs = [Paragraph(index=s.index, text=s.text) for s in scenes]
        script = Script(raw_text=script.raw_text, paragraphs=scene_paragraphs)
        save_paragraphs(script, project.paragraphs_dir)

        logger.info(
            "-> %d개 문단 → %d개 씬으로 재분할 (paragraphs 덮어씀)",
            original_count,
            len(scenes),
        )

    # ===================================================================
    # Step 1.5: TTS 사전 자동 강화 (영어/숫자 발음 보강)
    # ===================================================================
    from features.normalize_text import enhance_tts_dictionary, load_tts_dictionary

    tts_dict = load_tts_dictionary()
    enhance_tts_dictionary(script.paragraphs, tts_dict)

    # ===================================================================
    # Step 2: TTS + B-roll 이미지 + Remotion props (병렬)
    # ===================================================================
    logger.info(
        "[2/%d] TTS + B-roll + 슬라이드 병렬 생성 (backend: remotion)",
        total_steps,
    )

    slides: list[Slide] = []
    audio_clips: list[AudioClip] = []

    slides, audio_clips = _step2_remotion_parallel(
        project=project,
        config=config,
        paragraphs=script.paragraphs,
        include_broll=include_broll,
        total_steps=total_steps,
    )

    # 아바타 클립 생성 시작 (병렬 — Steps 4-5와 동시 진행)
    avatar_future = None
    if include_avatar:
        logger.info("[병렬] 아바타 클립 생성 시작 (Steps 4-5와 동시 진행)")
        _avatar_pool = ThreadPoolExecutor(max_workers=1)
        avatar_future = _avatar_pool.submit(
            _generate_avatar_clips_only, project, config
        )

    # ===================================================================
    # Step 4: 영상 합성
    # ===================================================================
    step_compose = 4
    logger.info("[%d/%d] 영상 합성", step_compose, total_steps)
    from features.compose_video import compose_video

    raw_video_path = project.output_dir / "video_raw.mp4"
    raw_video = compose_video(
        slides=slides,
        audio_clips=audio_clips,
        output_path=raw_video_path,
    )
    logger.info("-> 영상 합성 완료 (%.1f초)", raw_video.duration)

    # ===================================================================
    # 자막 생성
    # ===================================================================
    current_step = step_compose + 1
    logger.info("[%d/%d] 자막 생성", current_step, total_steps)
    from features.generate_subtitles import generate_subtitles
    from features.normalize_text import (
        apply_reverse_dictionary,
        build_reverse_dictionary,
        load_tts_dictionary,
        normalize_for_display,
    )

    # 자막 표시용 텍스트 정규화
    display_texts = normalize_for_display([p.text for p in script.paragraphs])

    # 역 발음 사전 적용: 한글 발음 → 원어 (클로드 → Claude, 엔에이트엔 → n8n)
    tts_dict = load_tts_dictionary()
    reverse_dict = build_reverse_dictionary(tts_dict)
    if reverse_dict:
        display_texts = [apply_reverse_dictionary(t, reverse_dict) for t in display_texts]

    srt_path = project.output_dir / "corrected_subtitles.srt"
    subtitle_result = generate_subtitles(
        paragraphs=script.paragraphs,
        audio_clips=audio_clips,
        output_path=srt_path,
        max_chars_per_line=config.subtitles.max_chars_per_line,
        min_chars_per_line=config.subtitles.min_chars_per_line,
        display_texts=display_texts,
    )
    logger.info("-> 자막 생성: %d개 항목", len(subtitle_result.entries))

    # ===================================================================
    # 아바타 오버레이 (클립은 이미 병렬 생성 중)
    # ===================================================================
    next_input_video = raw_video_path

    if include_avatar and avatar_future is not None:
        current_step += 1
        logger.info("[%d/%d] 아바타 오버레이 (클립 대기 중...)", current_step, total_steps)
        try:
            avatar_clip = avatar_future.result()
            if avatar_clip is not None:
                from features.generate_avatar import overlay_avatar_circular

                video_with_avatar = project.output_dir / "video_with_avatar.mp4"
                overlay_avatar_circular(
                    base_video=next_input_video,
                    avatar_video=avatar_clip.video_path,
                    output_path=video_with_avatar,
                    size=config.avatar.size,
                    margin_x=config.avatar.margin_x,
                    margin_y=config.avatar.margin_y,
                    border_width=config.avatar.border_width,
                    border_color=config.avatar.border_color,
                )
                next_input_video = video_with_avatar
                logger.info("-> 아바타 오버레이 완료")
        except Exception as e:
            logger.error("아바타 생성 실패, 건너뜀: %s", e)

    # ===================================================================
    # 자막 합성 -> final_video.mp4
    # ===================================================================
    current_step += 1
    logger.info("[%d/%d] 자막 합성", current_step, total_steps)
    from features.burn_subtitles import burn_subtitles

    video_with_subtitles = project.output_dir / "video_with_subtitles.mp4"
    burn_subtitles(
        next_input_video,
        srt_path,
        video_with_subtitles,
        config=config.subtitles,
    )

    # 아웃트로 합성
    outro_input = video_with_subtitles

    if include_outro:
        current_step += 1
        logger.info("[%d/%d] 아웃트로 합성", current_step, total_steps)
        from shared.lib.ffmpeg import concat_videos_reencode

        video_with_outro = project.output_dir / "video_with_outro.mp4"
        concat_videos_reencode([outro_input, outro_video_file], video_with_outro)
        outro_input = video_with_outro
        logger.info("-> 아웃트로 합성 완료")

    # 최종 영상 복사
    final_path = project.output_dir / "final_video.mp4"
    shutil.copy2(outro_input, final_path)

    # 리소스 정리
    from features.fetch_broll import cleanup_backends

    cleanup_backends()

    # duration 계산 (아웃트로 포함)
    from shared.lib.ffmpeg import get_duration

    final_duration = get_duration(final_path)

    video = Video(
        file_path=final_path,
        duration=final_duration,
    )

    features_list = []
    if include_broll:
        features_list.append("B-roll")
    if include_avatar:
        features_list.append("아바타")
    features_list.append("자막")

    logger.info(
        "파이프라인 완료: %s (%.1f초, %s)",
        video.file_path,
        video.duration,
        " + ".join(features_list),
    )
    return video


# ===================================================================
# 병렬 실행 헬퍼
# ===================================================================


def _step2_remotion_parallel(
    project: Project,
    config: AppConfig,
    paragraphs,
    include_broll: bool,
    total_steps: int,
) -> tuple[list[Slide], list[AudioClip]]:
    """Remotion 경로: TTS + B-roll 이미지 + props 3-way 병렬 -> 렌더링."""
    from features.generate_slides import (
        render_remotion_slides,
    )
    from features.generate_slides.model import SlideGenerationResult

    props_list: list[SlideGenerationResult] = []
    audio_clips: list[AudioClip] = []

    # 병렬 태스크 구성 (TTS + props + B-roll 이미지)
    tasks = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        tasks["props"] = executor.submit(
            _generate_remotion_props_task,
            paragraphs=paragraphs,
            slides_dir=project.slides_dir,
            config=config.slides,
        )
        tasks["tts"] = executor.submit(
            _generate_tts_task,
            paragraphs=paragraphs,
            audio_dir=project.audio_dir,
            config=config.tts,
        )
        if include_broll:
            tasks["broll"] = executor.submit(
                _generate_broll_images_task,
                paragraphs=paragraphs,
                audio_clips_future=tasks["tts"],
                broll_dir=project.broll_dir / "generated",
                config=config,
            )

        # 모든 future 완료 대기 후 에러 확인 (부분 실패 방지)
        errors: list[Exception] = []
        for future in as_completed(tasks.values()):
            try:
                result = future.result()
                if isinstance(result, tuple):
                    if result[0] == "remotion_props":
                        props_list = result[1]
                        logger.info("-> Remotion props 생성 완료: %d개", len(props_list))
                    elif result[0] == "tts":
                        audio_clips = result[1]
                        logger.info("-> TTS 생성 완료: %d개", len(audio_clips))
                    elif result[0] == "broll":
                        logger.info("-> B-roll 이미지 생성 완료: %d개", result[1])
            except Exception as e:
                logger.error("병렬 작업 실패: %s", e)
                errors.append(e)

    if errors:
        raise errors[0]

    # Remotion 렌더링 (오디오 duration + B-roll 배경 필요)
    broll_generated_dir = project.broll_dir / "generated"
    step_render = 3
    logger.info("[%d/%d] Remotion 슬라이드 렌더링", step_render, total_steps)
    slides = render_remotion_slides(
        props_list=props_list,
        audio_clips=audio_clips,
        slides_dir=project.slides_dir,
        config=config.slides,
        broll_dir=broll_generated_dir if include_broll and broll_generated_dir.exists() else None,
    )
    logger.info("-> Remotion 슬라이드 렌더링 완료: %d개", len(slides))

    return slides, audio_clips


def _step2_remotion_scenes(
    project: Project,
    config: AppConfig,
    paragraphs,
    scenes,
    include_broll: bool,
    total_steps: int,
) -> tuple[list[Slide], list[AudioClip], list[AudioClip]]:
    """씬 모드: TTS(문단) || props(씬) || B-roll(문단) 병렬 -> 오디오 분할 -> 렌더링.

    Returns:
        (slides, scene_audio_clips, paragraph_audio_clips) 튜플.
        scene_audio_clips: 씬 단위 오디오 (영상 합성용).
        paragraph_audio_clips: 문단 단위 오디오 (자막 생성용).
    """
    from features.generate_slides import render_remotion_slides
    from features.generate_slides.model import SlideGenerationResult
    from shared.lib.ffmpeg import split_audio_by_ratio

    props_list: list[SlideGenerationResult] = []
    paragraph_audio_clips: list[AudioClip] = []

    # 병렬: TTS(문단) + props(씬) + B-roll(문단)
    tasks = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        tasks["props"] = executor.submit(
            _generate_remotion_props_scenes_task,
            scenes=scenes,
            slides_dir=project.slides_dir,
            config=config.slides,
        )
        tasks["tts"] = executor.submit(
            _generate_tts_task,
            paragraphs=paragraphs,
            audio_dir=project.audio_dir,
            config=config.tts,
        )
        if include_broll:
            tasks["broll"] = executor.submit(
                _generate_broll_images_task,
                paragraphs=paragraphs,
                audio_clips_future=tasks["tts"],
                broll_dir=project.broll_dir / "generated",
                config=config,
            )

        errors: list[Exception] = []
        for future in as_completed(tasks.values()):
            try:
                result = future.result()
                if isinstance(result, tuple):
                    if result[0] == "remotion_props":
                        props_list = result[1]
                        logger.info(
                            "-> Remotion props 생성 완료: %d개 (씬)",
                            len(props_list),
                        )
                    elif result[0] == "tts":
                        paragraph_audio_clips = result[1]
                        logger.info(
                            "-> TTS 생성 완료: %d개 (문단)",
                            len(paragraph_audio_clips),
                        )
                    elif result[0] == "broll":
                        logger.info(
                            "-> B-roll 이미지 생성 완료: %d개",
                            result[1],
                        )
            except Exception as e:
                logger.error("병렬 작업 실패: %s", e)
                errors.append(e)

    if errors:
        raise errors[0]

    # 오디오 분할: 문단 오디오 -> 씬별 오디오 (글자 수 비례)
    logger.info("씬별 오디오 분할 시작")
    scenes_audio_dir = project.root / "scenes_audio"
    scenes_audio_dir.mkdir(parents=True, exist_ok=True)

    scene_audio_clips: list[AudioClip] = []

    # 문단별로 소속 씬을 그룹화
    from collections import defaultdict

    para_scenes: dict[int, list] = defaultdict(list)
    for scene in scenes:
        para_scenes[scene.paragraph_index].append(scene)

    for para_clip in paragraph_audio_clips:
        para_idx = para_clip.index
        scene_group = para_scenes.get(para_idx, [])

        if len(scene_group) <= 1:
            # 씬이 1개면 분할 불필요 — 원본 오디오 그대로 사용
            for s in scene_group:
                scene_audio_clips.append(
                    AudioClip(
                        index=s.index,
                        file_path=para_clip.file_path,
                        duration=para_clip.duration,
                        sample_rate=para_clip.sample_rate,
                    )
                )
            continue

        # 글자 수 비율 계산
        char_counts = [len(s.text) for s in scene_group]
        total_chars = sum(char_counts)
        ratios = [c / total_chars for c in char_counts]

        # 오디오 분할
        start_idx = scene_group[0].index
        split_paths = split_audio_by_ratio(
            audio_path=para_clip.file_path,
            ratios=ratios,
            output_dir=scenes_audio_dir,
            start_index=start_idx,
        )

        from shared.lib.ffmpeg import get_duration

        for path, scene in zip(split_paths, scene_group):
            dur = get_duration(path)
            scene_audio_clips.append(
                AudioClip(
                    index=scene.index,
                    file_path=path,
                    duration=dur,
                    sample_rate=para_clip.sample_rate,
                )
            )

    logger.info(
        "-> 씬별 오디오 분할 완료: %d개",
        len(scene_audio_clips),
    )

    # Remotion 렌더링 (씬 단위)
    broll_generated_dir = project.broll_dir / "generated"
    step_render = 3
    logger.info(
        "[%d/%d] Remotion 슬라이드 렌더링 (씬 모드)",
        step_render,
        total_steps,
    )
    slides = render_remotion_slides(
        props_list=props_list,
        audio_clips=scene_audio_clips,
        slides_dir=project.slides_dir,
        config=config.slides,
        broll_dir=(broll_generated_dir if include_broll and broll_generated_dir.exists() else None),
    )

    # B-roll 매칭: slide.paragraph_index로 문단 B-roll 공유
    for slide, props_result in zip(slides, props_list):
        slide.paragraph_index = props_result.paragraph_index

    logger.info(
        "-> Remotion 슬라이드 렌더링 완료: %d개 (씬)",
        len(slides),
    )

    return slides, scene_audio_clips, paragraph_audio_clips


def _generate_avatar_clips_only(
    project: Project,
    config: AppConfig,
):
    """아바타 클립만 생성 (오버레이 제외, 병렬 실행용).

    Steps 4-5와 동시에 실행되어 파이프라인 소요 시간을 단축합니다.
    """
    from features.generate_avatar import generate_avatar_clips

    avatar_dir = project.root / "avatar"
    avatar_dir.mkdir(parents=True, exist_ok=True)

    avatar_image = Path(config.avatar.image_path)
    if not avatar_image.is_absolute():
        avatar_image = Path.cwd() / avatar_image

    if not avatar_image.exists():
        logger.warning("아바타 이미지 없음: %s, 건너뜀", avatar_image)
        return None

    clip = generate_avatar_clips(
        audio_dir=project.audio_dir,
        avatar_image=avatar_image,
        output_dir=avatar_dir,
        ditto_project_path=config.avatar.ditto_project_path,
    )
    logger.info(
        "-> 아바타 클립 생성 완료: %s (%.1f초)",
        clip.video_path.name,
        clip.duration,
    )
    return clip


# ===================================================================
# 개별 태스크 함수
# ===================================================================


def _generate_remotion_props_task(paragraphs, slides_dir, config):
    """Remotion props 생성 병렬 태스크 (기존 TSX/PY 수집)."""
    from features.generate_slides import generate_remotion_props_for_paragraphs

    logger.info(
        "  [Remotion] props 수집 시작 (%d개)",
        len(paragraphs),
    )
    props_list = generate_remotion_props_for_paragraphs(
        paragraphs=paragraphs,
        slides_dir=slides_dir,
        config=config,
    )
    return ("remotion_props", props_list)


def _generate_remotion_props_scenes_task(
    scenes,
    slides_dir,
    config,
):
    """Remotion props 생성 병렬 태스크 (씬 모드, 기존 TSX/PY 수집)."""
    from features.generate_slides import generate_remotion_props_for_scenes

    logger.info(
        "  [Remotion] props 수집 시작 (%d개 씬)",
        len(scenes),
    )
    props_list = generate_remotion_props_for_scenes(
        scenes=scenes,
        slides_dir=slides_dir,
        config=config,
    )
    return ("remotion_props", props_list)


def _generate_tts_task(paragraphs, audio_dir, config):
    """TTS 생성 병렬 태스크."""
    from features.generate_tts import create_tts_backend, generate_tts_for_paragraphs

    logger.info("  [TTS] 생성 시작 (%d개)", len(paragraphs))
    tts_backend = create_tts_backend(config)
    logger.info("  [TTS] 백엔드: %s", tts_backend.name)

    audio_clips = generate_tts_for_paragraphs(
        paragraphs=paragraphs,
        audio_dir=audio_dir,
        config=config,
        backend=tts_backend,
    )
    return ("tts", audio_clips)


def _generate_broll_images_task(paragraphs, audio_clips_future, broll_dir, config):
    """B-roll 이미지 생성 병렬 태스크.

    TTS future에서 audio_clips를 가져와서 B-roll 시간 계산에 사용.
    """
    # TTS 완료를 기다림 (B-roll 타이밍 계산에 duration 필요)
    tts_result = audio_clips_future.result()
    audio_clips = tts_result[1] if isinstance(tts_result, tuple) else tts_result

    count = _generate_broll_images_sync(
        paragraphs=paragraphs,
        audio_clips=audio_clips,
        broll_dir=broll_dir,
        config=config,
    )
    return ("broll", count)


def _generate_broll_images_sync(paragraphs, audio_clips, broll_dir, config) -> int:
    """B-roll 이미지를 동기적으로 생성. 생성된 이미지 수를 반환."""
    from features.analyze_broll import generate_paragraph_broll_plan
    from features.analyze_broll.lib import apply_scene_grouping, load_broll_prompts
    from features.fetch_broll import fetch_all_broll
    from features.search_image import reset_used_images

    reset_used_images()

    # prompts.json 감지: 스킬이 사전 생성한 프롬프트가 있으면 API 호출 skip
    prompts_path = broll_dir.parent / "prompts.json"
    if prompts_path.exists():
        logger.info("B-roll prompts.json 감지 -> 사전 생성된 프롬프트 사용")
        broll_plan, scene_group_models = load_broll_prompts(prompts_path, audio_clips)
        scene_groups = (
            [sg.model_dump() for sg in scene_group_models]
            if scene_group_models
            else None
        )
        logger.info(
            "-> B-roll 계획: %d개 (prompts.json)", len(broll_plan.broll_items)
        )
    else:
        # Fallback: API 경로 (headless 실행용)
        logger.info("prompts.json 없음 -> API로 B-roll 프롬프트 생성")
        character_description = getattr(config.broll, "character_description", "")
        image_search_config = getattr(config.broll, "image_search", None)
        enable_image_search = (
            image_search_config.enabled if image_search_config else False
        )
        source_decision_model = (
            image_search_config.source_decision_model
            if image_search_config
            else "gpt-5-nano"
        )

        force_backend = config.broll.force_backend

        broll_plan = generate_paragraph_broll_plan(
            paragraphs=paragraphs,
            audio_clips=audio_clips,
            character_description=character_description,
            enable_image_search=enable_image_search,
            source_decision_model=source_decision_model,
            image_gen_backend=force_backend,
        )
        logger.info(
            "-> B-roll 계획: %d개 (문단 기반 1:1:1)", len(broll_plan.broll_items)
        )

        # 씬 그룹핑: 연속 문단을 장면으로 묶어 이미지 생성 수 절감
        scene_groups = None
        if config.pipeline.broll.scene_grouping and len(paragraphs) >= 3:
            broll_plan, scene_group_models = apply_scene_grouping(
                broll_plan, paragraphs
            )
            scene_groups = [sg.model_dump() for sg in scene_group_models]

    reference_base = config.broll.reference_base_dir
    reference_style = config.broll.reference_style
    reference_dir = Path(reference_base) / reference_style

    if not reference_dir.exists():
        logger.warning("레퍼런스 폴더가 없습니다: %s", reference_dir)
        reference_dir.mkdir(parents=True, exist_ok=True)

    broll_results = fetch_all_broll(
        broll_plan,
        broll_dir,
        config=config.broll,
        reference_dir=reference_dir,
        scene_groups=scene_groups,
    )

    generated_count = sum(1 for _, path in broll_results if path is not None)
    return generated_count
