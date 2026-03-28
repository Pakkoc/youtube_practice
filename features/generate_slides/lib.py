"""슬라이드 생성 핵심 로직 (Remotion 렌더링)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from entities.audio.model import AudioClip
from entities.script.model import Paragraph
from entities.slide.model import Slide
from shared.config.schema import SlidesConfig
from shared.lib.file_io import ensure_dir
from shared.lib.logger import get_logger

from .model import SlideGenerationResult

if TYPE_CHECKING:
    from .remotion_backend import FreeformSlotPool, RemotionSlideBackend

logger = get_logger()


# ===================================================================
# Remotion 백엔드
# ===================================================================


_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def _find_broll_image(broll_dir: Path | None, index: int) -> Path | None:
    """B-roll 이미지 파일을 찾아 반환 (없으면 None)."""
    if broll_dir is None or not broll_dir.exists():
        return None
    for f in broll_dir.glob(f"broll_{index:03d}.*"):
        if f.suffix.lower() in _IMAGE_EXTS:
            return f
    return None


# ===================================================================
# Remotion 백엔드 (2단계 파이프라인: props 생성 -> 렌더링)
# ===================================================================


def generate_remotion_props_for_paragraphs(
    paragraphs: list[Paragraph],
    slides_dir: Path,
    config: SlidesConfig | None = None,
) -> list[SlideGenerationResult]:
    """기존 TSX/PY 파일을 수집하여 SlideGenerationResult 목록으로 반환.

    TSX/PY가 없는 문단은 에러 슬라이드로 처리합니다.
    슬라이드 생성은 /generate-slides 스킬로 사전 실행해야 합니다.

    Args:
        paragraphs: 문단 목록.
        slides_dir: 슬라이드 파일 저장 디렉토리.
        config: 슬라이드 설정.

    Returns:
        SlideGenerationResult 목록.
    """
    if config is None:
        config = SlidesConfig()

    ensure_dir(slides_dir)

    results: list[SlideGenerationResult] = []

    for paragraph in paragraphs:
        tsx_path = slides_dir / f"{paragraph.index:03d}.tsx"
        py_path = slides_dir / f"{paragraph.index:03d}.py"

        # 기존 파일이 있으면 재사용 (TSX 우선, PY 차선)
        if tsx_path.exists():
            logger.info("Freeform TSX 로드: %s", tsx_path.name)
            tsx_code = tsx_path.read_text(encoding="utf-8")
            results.append(
                SlideGenerationResult(
                    index=paragraph.index,
                    markdown=f"[freeform] {tsx_path.name}",
                    mode="freeform",
                    tsx_code=tsx_code,
                )
            )
            continue

        if py_path.exists():
            logger.info("Manim 코드 로드: %s", py_path.name)
            manim_code = py_path.read_text(encoding="utf-8")
            results.append(
                SlideGenerationResult(
                    index=paragraph.index,
                    markdown=f"[manim] {py_path.name}",
                    mode="manim",
                    manim_code=manim_code,
                )
            )
            continue

        logger.warning(
            "슬라이드 파일 없음: 문단 %d/%d",
            paragraph.index,
            len(paragraphs),
        )
        results.append(
            _make_error_slide(paragraph.index, paragraph.text)
        )

    freeform_count = sum(1 for r in results if r.mode == "freeform")
    manim_count = sum(1 for r in results if r.mode == "manim")
    logger.info(
        "전체 %d개 슬라이드 plan 완료 (freeform: %d, manim: %d)",
        len(results),
        freeform_count,
        manim_count,
    )
    return results


def render_remotion_slides(
    props_list: list[SlideGenerationResult],
    audio_clips: list[AudioClip],
    slides_dir: Path,
    config: SlidesConfig | None = None,
    *,
    broll_dir: Path | None = None,
) -> list[Slide]:
    """Remotion TSX + 오디오 duration으로 비디오 슬라이드 렌더링.

    freeform 모드: FreeformSlot{1-4}.tsx 슬롯 풀로 병렬 렌더링.
    manim 모드: ManimSlideBackend로 렌더링.

    Args:
        props_list: generate_remotion_props_for_paragraphs()의 결과.
        audio_clips: TTS 오디오 클립 목록 (duration 추출용).
        slides_dir: 슬라이드 파일 저장 디렉토리.
        config: 슬라이드 설정.
        broll_dir: B-roll 이미지 디렉토리 (있으면 배경에 블러 이미지 적용).

    Returns:
        생성된 Slide 엔티티 목록 (video_path 설정됨).
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from shared.lib.ffmpeg import get_duration

    from .remotion_backend import FreeformSlotPool, RemotionSlideBackend

    if config is None:
        config = SlidesConfig()

    remotion_config = getattr(config, "remotion", None)
    project_path_str = (
        getattr(remotion_config, "remotion_project_path", "remotion")
        if remotion_config
        else "remotion"
    )
    fps = getattr(remotion_config, "fps", 30) if remotion_config else 30
    width = (
        getattr(remotion_config, "width", 1920) if remotion_config else 1920
    )
    height = (
        getattr(remotion_config, "height", 1080) if remotion_config else 1080
    )
    num_slots = (
        getattr(remotion_config, "render_parallel_slots", 4)
        if remotion_config
        else 4
    )

    # 프로젝트 경로 해석
    project_path = Path(project_path_str)
    if not project_path.is_absolute():
        project_path = Path(__file__).parents[2] / project_path

    backend = RemotionSlideBackend(project_path)
    if not backend.is_available():
        raise RuntimeError(
            "Remotion이 사용 불가능합니다. Node.js 설치 및 remotion/ 디렉토리를 확인하세요."
        )

    # Phase 1: 재사용 체크 -> render_tasks 수집
    slides_by_index: dict[int, Slide] = {}
    render_tasks: list[tuple[SlideGenerationResult, float, Path]] = []

    for props_result, audio_clip in zip(props_list, audio_clips):
        mp4_path = slides_dir / f"{props_result.index:03d}.mp4"
        audio_duration = get_duration(audio_clip.file_path)

        # 기존 MP4가 있고 duration이 오디오와 +-0.5초 이내면 재사용
        if mp4_path.exists() and mp4_path.stat().st_size > 0:
            try:
                existing_duration = get_duration(mp4_path)
                if abs(existing_duration - audio_duration) <= 0.5:
                    logger.info(
                        "기존 Remotion 슬라이드 재사용: %s", mp4_path.name
                    )
                    slides_by_index[props_result.index] = Slide(
                        index=props_result.index,
                        markdown=props_result.markdown,
                        video_path=mp4_path,
                    )
                    continue
            except Exception as e:
                logger.warning(
                    "손상된 슬라이드 재생성: %s (%s)",
                    mp4_path.name,
                    e,
                )

        render_tasks.append((props_result, audio_duration, mp4_path))

    if not render_tasks:
        logger.info("모든 슬라이드 재사용됨, 렌더링 불필요")
        return [
            slides_by_index[pr.index]
            for pr in props_list
            if pr.index in slides_by_index
        ]

    # Phase 2: 병렬 렌더링
    has_freeform = any(
        pr.mode == "freeform" and pr.tsx_code for pr, _, _ in render_tasks
    )
    slot_pool = (
        FreeformSlotPool(project_path, num_slots) if has_freeform else None
    )

    logger.info(
        "Remotion 렌더링 시작: %d개 (재사용 %d개, 병렬 슬롯 %d개)",
        len(render_tasks),
        len(slides_by_index),
        num_slots if slot_pool else 0,
    )

    manim_config = getattr(config, "manim", None)
    manim_timeout = (
        getattr(manim_config, "render_timeout", 120) if manim_config else 120
    )

    def _do_render(
        props_result: SlideGenerationResult,
        audio_duration: float,
        mp4_path: Path,
    ) -> Slide:
        """단일 슬라이드 렌더링 (스레드에서 실행)."""
        if props_result.mode == "manim" and props_result.manim_code:
            return _render_manim_slide(
                props_result,
                audio_duration,
                mp4_path,
                fps,
                width,
                height,
                broll_dir,
                props_list,
                backend,
                manim_timeout,
            )
        if props_result.mode == "freeform" and props_result.tsx_code:
            return _render_freeform_slide(
                props_result,
                audio_duration,
                mp4_path,
                project_path,
                backend,
                fps,
                width,
                height,
                broll_dir,
                props_list,
                slot_pool,
            )
        raise ValueError(
            f"슬라이드 {props_result.index}: 렌더링 가능한 코드 없음 "
            f"(mode={props_result.mode})"
        )

    try:
        max_workers = num_slots if num_slots > 1 else 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(_do_render, pr, dur, mp4): pr.index
                for pr, dur, mp4 in render_tasks
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    slide = future.result()
                    slides_by_index[idx] = slide
                except Exception:
                    logger.exception("슬라이드 %d 렌더링 실패", idx)
    finally:
        if slot_pool is not None:
            slot_pool.restore_all()

    # 원래 순서대로 정렬
    slides = [
        slides_by_index[pr.index]
        for pr in props_list
        if pr.index in slides_by_index
    ]

    logger.info("전체 %d개 Remotion 슬라이드 렌더링 완료", len(slides))
    return slides


def _render_freeform_slide(
    props_result: SlideGenerationResult,
    audio_duration: float,
    mp4_path: Path,
    project_path: Path,
    backend: RemotionSlideBackend,
    fps: int,
    width: int,
    height: int,
    broll_dir: Path | None,
    props_list: list[SlideGenerationResult],
    slot_pool: FreeformSlotPool | None = None,
) -> Slide:
    """Freeform 모드 슬라이드 렌더링.

    슬롯 풀이 있으면 슬롯을 acquire->write->render->release.
    슬롯 풀이 없으면 기존 방식(Freeform.tsx 덮어쓰기).
    """
    from .remotion_backend import write_freeform_tsx

    assert props_result.tsx_code is not None

    broll_idx = props_result.paragraph_index or props_result.index
    bg_image = _find_broll_image(broll_dir, broll_idx) if broll_dir else None

    # 슬롯 사용 여부 결정
    slot_id: int | None = None
    composition_id = "Freeform"

    if slot_pool is not None:
        slot_id = slot_pool.acquire()
        composition_id = slot_pool.composition_id(slot_id)
        slot_pool.write_slot(slot_id, props_result.tsx_code)
    else:
        write_freeform_tsx(props_result.tsx_code, project_path)

    # 프로그레스 바용 props
    freeform_props = {
        "template": "Freeform",
        "slideIndex": props_result.index,
        "totalSlides": len(props_list),
    }

    logger.info(
        "Freeform 렌더링: 문단 %d/%d (%.1fs, %s%s)",
        props_result.index,
        len(props_list),
        audio_duration,
        composition_id,
        f", bg={bg_image.name}" if bg_image else "",
    )

    try:
        backend.render(
            template_name=composition_id,
            props=freeform_props,
            output_path=mp4_path,
            duration_seconds=audio_duration,
            fps=fps,
            width=width,
            height=height,
            background_image=bg_image,
        )

        return Slide(
            index=props_result.index,
            markdown=props_result.markdown,
            video_path=mp4_path,
        )

    except RuntimeError:
        # Freeform 렌더 실패 -> 실패한 .tsx 삭제 (재사용 방지)
        logger.warning(
            "Freeform 렌더 실패 (문단 %d)",
            props_result.index,
        )
        slides_dir = mp4_path.parent
        failed_tsx = slides_dir / f"{props_result.index:03d}.tsx"
        if failed_tsx.exists():
            failed_tsx.unlink()
            logger.info("실패한 TSX 삭제: %s", failed_tsx.name)
        raise
    finally:
        if slot_pool is not None and slot_id is not None:
            slot_pool.release(slot_id)


def _render_manim_slide(
    props_result: SlideGenerationResult,
    audio_duration: float,
    mp4_path: Path,
    fps: int,
    width: int,
    height: int,
    broll_dir: Path | None,
    props_list: list[SlideGenerationResult],
    remotion_backend: RemotionSlideBackend,
    timeout: int = 120,
) -> Slide:
    """Manim 모드 슬라이드 렌더링."""
    from .manim_backend import ManimSlideBackend

    assert props_result.manim_code is not None

    broll_idx = props_result.paragraph_index or props_result.index
    bg_image = _find_broll_image(broll_dir, broll_idx) if broll_dir else None

    logger.info(
        "Manim 렌더링: 문단 %d/%d (%.1fs%s)",
        props_result.index,
        len(props_list),
        audio_duration,
        f", bg={bg_image.name}" if bg_image else "",
    )

    try:
        manim_be = ManimSlideBackend()
        manim_be.render(
            scene_code=props_result.manim_code,
            output_path=mp4_path,
            duration_seconds=audio_duration,
            fps=fps,
            width=width,
            height=height,
            background_image=bg_image,
            slide_index=props_result.index,
            total_slides=len(props_list),
            timeout=timeout,
        )

        return Slide(
            index=props_result.index,
            markdown=props_result.markdown,
            video_path=mp4_path,
        )

    except (RuntimeError, OSError):
        # Manim 렌더 실패 -> .py 삭제 (재사용 방지)
        logger.warning(
            "Manim 렌더 실패 (문단 %d)",
            props_result.index,
        )
        slides_dir = mp4_path.parent
        failed_py = slides_dir / f"{props_result.index:03d}.py"
        if failed_py.exists():
            failed_py.unlink()
            logger.info("실패한 Manim 코드 삭제: %s", failed_py.name)
        raise


def _make_error_slide(index: int, text: str) -> SlideGenerationResult:
    """모든 생성 시도 실패 시 에러 결과 반환."""
    logger.warning("슬라이드 %d: TSX/PY 파일 없음 — /generate-slides 실행 필요", index)
    return SlideGenerationResult(
        index=index,
        markdown=f"[error] 슬라이드 생성 실패: {text[:50]}",
        mode="freeform",
        tsx_code=None,
    )


# ===================================================================
# 씬 모드 (문장 단위 슬라이드)
# ===================================================================


def generate_remotion_props_for_scenes(
    scenes: list,
    slides_dir: Path,
    config: SlidesConfig | None = None,
) -> list[SlideGenerationResult]:
    """여러 씬에 대한 Remotion TSX를 수집 (씬 모드).

    generate_remotion_props_for_paragraphs()와 동일한 구조이되:
    - 입력: scenes (Scene 목록, 문장 단위)
    - 결과에 paragraph_index 포함

    Args:
        scenes: 씬 목록 (Scene 객체).
        slides_dir: 슬라이드 파일 저장 디렉토리.
        config: 슬라이드 설정.

    Returns:
        SlideGenerationResult 목록 (paragraph_index 포함).
    """
    if config is None:
        config = SlidesConfig()

    ensure_dir(slides_dir)

    results: list[SlideGenerationResult] = []

    for scene in scenes:
        tsx_path = slides_dir / f"{scene.index:03d}.tsx"
        py_path = slides_dir / f"{scene.index:03d}.py"

        # 기존 파일이 있으면 재사용 (TSX 우선, PY 차선)
        if tsx_path.exists():
            logger.info("기존 Freeform TSX 재사용: %s", tsx_path.name)
            tsx_code = tsx_path.read_text(encoding="utf-8")
            results.append(
                SlideGenerationResult(
                    index=scene.index,
                    paragraph_index=scene.paragraph_index,
                    markdown=f"[freeform] {tsx_path.name}",
                    mode="freeform",
                    tsx_code=tsx_code,
                )
            )
            continue

        if py_path.exists():
            logger.info("기존 Manim 코드 재사용: %s", py_path.name)
            manim_code = py_path.read_text(encoding="utf-8")
            results.append(
                SlideGenerationResult(
                    index=scene.index,
                    paragraph_index=scene.paragraph_index,
                    markdown=f"[manim] {py_path.name}",
                    mode="manim",
                    manim_code=manim_code,
                )
            )
            continue

        # TSX/PY가 없으면 /generate-slides로 먼저 생성해야 함
        logger.warning(
            "슬라이드 파일 없음: 씬 %d/%d — "
            "/generate-slides 스킬로 먼저 TSX를 생성하세요",
            scene.index,
            len(scenes),
        )
        results.append(
            SlideGenerationResult(
                index=scene.index,
                paragraph_index=scene.paragraph_index,
                markdown=f"[error] TSX 없음: {scene.text[:50]}",
                mode="freeform",
            )
        )

    freeform_count = sum(1 for r in results if r.mode == "freeform")
    manim_count = sum(1 for r in results if r.mode == "manim")
    logger.info(
        "전체 %d개 씬 슬라이드 plan 완료 (freeform: %d, manim: %d)",
        len(results),
        freeform_count,
        manim_count,
    )
    return results
