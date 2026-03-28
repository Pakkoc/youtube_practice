"""B-roll 이미지 수집 핵심 로직."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from features.analyze_broll.model import BrollItem, BrollPlan
from shared.lib.logger import get_logger

from .api import download_pexels_image, generate_image_via_openai

if TYPE_CHECKING:
    from shared.config.schema import BrollConfig

    from .backends.flux2_klein import Flux2KleinBackend
    from .backends.flux_kontext import FluxKontextBackend
    from .backends.nanobanana import NanoBananaBackend

logger = get_logger()

# 전역 백엔드 인스턴스 (재사용을 위해)
_flux2_backend: Flux2KleinBackend | None = None
_flux_kontext_backend: FluxKontextBackend | None = None
_nanobanana_backend: NanoBananaBackend | None = None


def _get_flux2_backend(config: BrollConfig) -> Flux2KleinBackend:
    """FLUX.2 Klein 백엔드 싱글톤 반환."""
    global _flux2_backend

    if _flux2_backend is None:
        from .backends.flux2_klein import Flux2KleinBackend

        flux_config = config.flux2_klein
        _flux2_backend = Flux2KleinBackend(
            model_id=flux_config.model_id,
            num_inference_steps=flux_config.num_inference_steps,
            height=flux_config.height,
            width=flux_config.width,
            guidance_scale=flux_config.guidance_scale,
            device=flux_config.device,
        )

    return _flux2_backend


def _get_flux_kontext_backend(config: BrollConfig) -> FluxKontextBackend:
    """Flux Kontext 백엔드 싱글톤 반환."""
    global _flux_kontext_backend

    if _flux_kontext_backend is None:
        from .backends.flux_kontext import FluxKontextBackend

        kontext_config = config.flux_kontext
        _flux_kontext_backend = FluxKontextBackend(
            base_model_path=kontext_config.base_model_path,
            lora_path=kontext_config.lora_path,
            num_inference_steps=kontext_config.num_inference_steps,
            height=kontext_config.height,
            width=kontext_config.width,
            guidance_scale=kontext_config.guidance_scale,
            lora_scale=kontext_config.lora_scale,
            device=kontext_config.device,
        )

    return _flux_kontext_backend


def _get_nanobanana_backend(config: BrollConfig) -> NanoBananaBackend:
    """NanoBanana 백엔드 싱글톤 반환."""
    global _nanobanana_backend

    if _nanobanana_backend is None:
        from .backends.nanobanana import NanoBananaBackend

        nb_config = config.nanobanana
        _nanobanana_backend = NanoBananaBackend(
            model=nb_config.model,
            height=nb_config.height,
            width=nb_config.width,
            use_reference=nb_config.use_reference,
            save_captions=nb_config.save_captions,
        )

    return _nanobanana_backend


def fetch_broll_image(
    item: BrollItem,
    output_path: Path,
    *,
    backend: str | None = None,
    config: BrollConfig | None = None,
    reference_dir: Path | None = None,
) -> Path | None:
    """단일 B-roll 항목의 이미지를 수집.

    Args:
        item: B-roll 항목.
        output_path: 이미지 저장 경로.
        backend: 사용할 백엔드 ("flux2_klein", "flux_kontext", "nanobanana" 또는 None=기존 방식).
        config: B-roll 설정 (로컬 백엔드 사용 시 필요).
        reference_dir: 레퍼런스 이미지 디렉토리 (선택).

    Returns:
        이미지 파일 경로, 실패 시 None.
    """
    # 이미지 검색 source 처리
    if item.source == "search":
        result = _fetch_via_search(item, output_path, config)
        if result:
            return result
        # 검색 실패 시 생성으로 fallback
        logger.info("이미지 검색 실패, 생성으로 전환: '%s'", item.keyword)
        # source를 generate로 변경하고 계속 진행
        item = BrollItem(
            start_time=item.start_time,
            duration=item.duration,
            keyword=item.keyword,
            source="generate",
            reason=item.reason,
            context_chunk=item.context_chunk,
        )

    # FLUX.2 Klein 백엔드 사용
    if backend == "flux2_klein" and config is not None:
        return _fetch_via_flux2(item, output_path, config, reference_dir)

    # Flux Kontext + LoRA 백엔드 사용
    if backend == "flux_kontext" and config is not None:
        return _fetch_via_flux_kontext(item, output_path, config, reference_dir)

    # NanoBanana (Gemini) 백엔드 사용
    if backend == "nanobanana" and config is not None:
        return _fetch_via_nanobanana(item, output_path, config, reference_dir)

    # 기존 방식: OpenAI 또는 Pexels
    if item.source == "generate":
        result = generate_image_via_openai(item.keyword, output_path)
        if result:
            return result
        # 생성 실패 시 Pexels 폴백
        logger.info("AI 생성 실패, Pexels 폴백: '%s'", item.keyword)

    return download_pexels_image(item.keyword, output_path)


def _fetch_via_search(
    item: BrollItem,
    output_path: Path,
    config: BrollConfig | None = None,
) -> Path | None:
    """이미지 검색으로 B-roll 이미지 수집.

    SerperDev로 검색하고 OpenAI Vision으로 검증합니다.

    Args:
        item: B-roll 항목 (keyword에 search_query가 저장됨).
        output_path: 이미지 저장 경로.
        config: B-roll 설정.

    Returns:
        다운로드된 이미지 경로, 실패 시 None.
    """
    from features.search_image import search_image_for_broll

    # 이미지 검색 설정
    image_search_config = None
    if config is not None:
        image_search_config = config.image_search

    return search_image_for_broll(
        query=item.keyword,  # search_query가 keyword에 저장됨
        context=item.context_chunk,
        output_path=output_path,
        config=image_search_config,
    )


def _fetch_via_flux2(
    item: BrollItem,
    output_path: Path,
    config: BrollConfig,
    reference_dir: Path | None = None,
) -> Path | None:
    """FLUX.2 Klein 백엔드로 이미지 생성.

    Args:
        item: B-roll 항목.
        output_path: 이미지 저장 경로.
        config: B-roll 설정.
        reference_dir: 레퍼런스 이미지 디렉토리.

    Returns:
        생성된 이미지 경로, 실패 시 None.
    """
    backend = _get_flux2_backend(config)

    # 레퍼런스 이미지 찾기 (있으면 스타일 참조)
    reference_image = None
    if config.flux2_klein.use_reference and reference_dir is not None:
        reference_image = _find_reference_image(reference_dir, item.keyword)

    return backend.generate(
        prompt=item.keyword,
        output_path=output_path,
        reference_image=reference_image,
    )



def _fetch_via_flux_kontext(
    item: BrollItem,
    output_path: Path,
    config: BrollConfig,
    reference_dir: Path | None = None,
) -> Path | None:
    """Flux Kontext + LoRA 백엔드로 이미지 생성 (img2img).

    Args:
        item: B-roll 항목.
        output_path: 이미지 저장 경로.
        config: B-roll 설정.
        reference_dir: 레퍼런스 이미지 디렉토리 (필수).

    Returns:
        생성된 이미지 경로, 실패 시 None.
    """
    backend = _get_flux_kontext_backend(config)

    # 참조 이미지 찾기 (Kontext는 img2img 전용이라 필수)
    reference_image = None
    if reference_dir is not None:
        reference_image = _find_reference_image(reference_dir, item.keyword)

    return backend.generate(
        prompt=item.keyword,
        output_path=output_path,
        reference_image=reference_image,
    )


def _fetch_via_nanobanana(
    item: BrollItem,
    output_path: Path,
    config: BrollConfig,
    reference_dir: Path | None = None,
) -> Path | None:
    """NanoBanana (Gemini) 백엔드로 이미지 생성/편집.

    Args:
        item: B-roll 항목.
        output_path: 이미지 저장 경로.
        config: B-roll 설정.
        reference_dir: 레퍼런스 이미지 디렉토리.

    Returns:
        생성된 이미지 경로, 실패 시 None.
    """
    backend = _get_nanobanana_backend(config)

    # 레퍼런스 이미지 찾기 (있으면 편집 모드)
    reference_image = None
    if config.nanobanana.use_reference and reference_dir is not None:
        reference_image = _find_reference_image(reference_dir, item.keyword)

    return backend.generate(
        prompt=item.keyword,
        output_path=output_path,
        reference_image=reference_image,
    )


def _find_reference_image(
    reference_dir: Path,
    keyword: str,
) -> Path | None:
    """레퍼런스 이미지 디렉토리에서 적절한 이미지를 찾음.

    키워드와 매칭되는 파일이 있으면 해당 파일을, 없으면 랜덤 이미지를 반환.

    Args:
        reference_dir: 레퍼런스 이미지 디렉토리.
        keyword: 검색 키워드.

    Returns:
        레퍼런스 이미지 경로, 없으면 None.
    """
    if not reference_dir.exists():
        return None

    image_exts = {".jpg", ".jpeg", ".png", ".webp"}
    images = [f for f in reference_dir.iterdir() if f.suffix.lower() in image_exts]

    if not images:
        return None

    # 키워드와 매칭되는 파일 찾기
    keyword_lower = keyword.lower()
    for img in images:
        if keyword_lower in img.stem.lower():
            logger.debug("레퍼런스 이미지 매칭: '%s' → %s", keyword, img.name)
            return img

    # 매칭 없으면 키워드 기반 결정론적 선택 (재현성 보장)
    images.sort(key=lambda p: p.name)
    idx = hash(keyword) % len(images)
    selected = images[idx]
    logger.debug("레퍼런스 이미지 결정론적 선택: '%s' → %s", keyword, selected.name)
    return selected


def fetch_all_broll(
    plan: BrollPlan,
    broll_dir: Path,
    *,
    config: BrollConfig | None = None,
    reference_dir: Path | None = None,
    scene_groups: list[dict] | None = None,
) -> list[tuple[BrollItem, Path | None]]:
    """B-roll 계획의 모든 이미지를 수집.

    Args:
        plan: B-roll 삽입 계획.
        broll_dir: B-roll 이미지 저장 디렉토리.
        config: B-roll 설정 (선택).
        reference_dir: 레퍼런스 이미지 디렉토리 (선택).
        scene_groups: 씬 그룹 리스트 (있으면 대표 문단만 생성, 나머지 복사).

    Returns:
        (BrollItem, 이미지 경로 또는 None) 튜플 리스트.
    """
    broll_dir.mkdir(parents=True, exist_ok=True)
    results: list[tuple[BrollItem, Path | None]] = []

    # 씬 그룹이 있으면 대표 인덱스 집합과 매핑 구성
    representative_indices: set[int] | None = None
    para_to_representative: dict[int, int] = {}
    if scene_groups:
        representative_indices = set()
        for sg in scene_groups:
            rep = sg["representative_index"]
            representative_indices.add(rep)
            for pi in sg["paragraph_indices"]:
                para_to_representative[pi] = rep

    # 백엔드 결정
    backend = None
    if config is not None and config.force_backend:
        backend = config.force_backend
        logger.info("B-roll 백엔드: %s", backend)

    # Phase 1: 대표 문단만 이미지 생성 (또는 scene_groups 없으면 전체 생성)
    for i, item in enumerate(plan.broll_items):
        para_idx = item.paragraph_index

        # 씬 그룹 모드에서 비대표 문단은 skip (Phase 2에서 복사)
        if representative_indices is not None and para_idx not in representative_indices:
            results.append((item, None))  # placeholder
            continue

        # 기존 파일 확인 (확장자 무관하게 검색)
        existing_files = list(broll_dir.glob(f"broll_{i + 1:03d}.*"))
        image_exts = {".png", ".jpg", ".jpeg", ".webp"}
        existing_image = next(
            (f for f in existing_files if f.suffix.lower() in image_exts and f.stat().st_size > 0),
            None,
        )

        if existing_image is not None:
            logger.info(
                "[%d/%d] 기존 B-roll 재사용: %s",
                i + 1,
                len(plan.broll_items),
                existing_image.name,
            )
            results.append((item, existing_image))
            continue

        # 확장자 결정: 로컬 생성은 PNG, 검색/Pexels는 JPG
        if backend in ("flux2_klein", "flux_kontext", "nanobanana"):
            ext = ".png"
        elif item.source == "search":
            ext = ".jpg"  # 검색 이미지는 보통 JPG
        elif item.source == "generate":
            ext = ".png"
        else:
            ext = ".jpg"
        output_path = broll_dir / f"broll_{i + 1:03d}{ext}"

        logger.info(
            "[%d/%d] B-roll 수집: '%s' (%s)",
            i + 1,
            len(plan.broll_items),
            item.keyword[:60] + "..." if len(item.keyword) > 60 else item.keyword,
            item.source if item.source == "search" else (backend or item.source),
        )

        image_path = fetch_broll_image(
            item,
            output_path,
            backend=backend,
            config=config,
            reference_dir=reference_dir,
        )
        results.append((item, image_path))

        if image_path:
            logger.info("  -> 저장: %s", image_path.name)
        else:
            logger.warning("  -> 실패: '%s'", item.keyword)

    # Phase 2: 씬 그룹 모드일 때 대표 이미지를 비대표 인덱스에 복사
    if representative_indices is not None:
        # paragraph_index -> (list index, image path) 매핑
        para_to_result: dict[int, tuple[int, Path | None]] = {}
        for idx, (item, path) in enumerate(results):
            if item.paragraph_index is not None:
                para_to_result[item.paragraph_index] = (idx, path)

        copied = 0
        for i, (item, path) in enumerate(results):
            if path is not None:
                continue  # 이미 생성됨 또는 재사용
            if item.paragraph_index is None:
                continue

            rep_idx = para_to_representative.get(item.paragraph_index)
            if rep_idx is None:
                continue

            rep_result = para_to_result.get(rep_idx)
            if rep_result is None or rep_result[1] is None:
                continue

            src_path = rep_result[1]
            dst_path = broll_dir / f"broll_{i + 1:03d}{src_path.suffix}"
            shutil.copy2(src_path, dst_path)
            results[i] = (item, dst_path)
            copied += 1
            logger.debug(
                "씬 복사: broll_%03d <- %s (그룹 대표)",
                i + 1,
                src_path.name,
            )

        if copied > 0:
            logger.info("씬 그룹 이미지 복사: %d개 (생성 절감)", copied)

    success = sum(1 for _, p in results if p is not None)
    logger.info("B-roll 수집 완료: %d/%d 성공", success, len(results))
    return results


def cleanup_backends() -> None:
    """모든 백엔드 리소스 정리."""
    global _flux2_backend, _flux_kontext_backend, _nanobanana_backend

    if _flux2_backend is not None:
        _flux2_backend.cleanup()
        _flux2_backend = None

    if _flux_kontext_backend is not None:
        _flux_kontext_backend.cleanup()
        _flux_kontext_backend = None

    if _nanobanana_backend is not None:
        _nanobanana_backend.cleanup()
        _nanobanana_backend = None


