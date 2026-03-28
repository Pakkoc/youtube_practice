"""이미지 검색 핵심 로직."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from shared.lib.logger import get_logger

from .api import download_image, search_images_serperdev, validate_image_relevance
from .model import SearchImageRequest, SearchImageResponse

if TYPE_CHECKING:
    from shared.config.schema import ImageSearchConfig

logger = get_logger()

# 이미 사용한 이미지 URL 추적 (중복 방지)
_used_image_urls: set[str] = set()


def _resize_image_to_16_9(
    image_path: Path,
    target_width: int = 1280,
    target_height: int = 720,
) -> None:
    """이미지를 16:9 비율로 리사이즈/패딩 처리.

    원본 이미지를 16:9 비율에 맞게 리사이즈하거나 패딩을 추가합니다.
    가로세로 비율을 유지하면서 여백은 검은색으로 채웁니다.

    Args:
        image_path: 이미지 파일 경로 (인플레이스 수정).
        target_width: 목표 너비 (기본: 1280).
        target_height: 목표 높이 (기본: 720).
    """
    try:
        from PIL import Image

        img = Image.open(str(image_path))
        orig_w, orig_h = img.size

        # 원본 이미지 비율
        orig_ratio = orig_w / orig_h
        target_ratio = target_width / target_height  # 1.777 (16:9)

        if orig_ratio > target_ratio:
            # 원본이 더 넓음 (예: 2.0)
            # 높이를 target_height에 맞추고 양옆에 패딩
            new_h = target_height
            new_w = int(target_height * orig_ratio)
        else:
            # 원본이 더 좁음 (예: 1.5)
            # 너비를 target_width에 맞추고 위아래에 패딩
            new_w = target_width
            new_h = int(target_width / orig_ratio)

        # 리사이즈
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 최종 이미지 생성 (검은색 배경)
        final_img = Image.new("RGB", (target_width, target_height), (0, 0, 0))

        # 중앙에 리사이즈된 이미지 붙이기
        x = (target_width - new_w) // 2
        y = (target_height - new_h) // 2
        final_img.paste(img_resized, (x, y))

        # 원본 파일 덮어쓰기
        final_img.save(str(image_path), "JPEG", quality=95)
        logger.debug(
            "이미지 리사이즈: %dx%d → %dx%d (16:9)",
            orig_w,
            orig_h,
            target_width,
            target_height,
        )

    except Exception as e:
        logger.warning("이미지 리사이즈 실패 '%s': %s", image_path.name, e)


def search_and_validate_image(
    request: SearchImageRequest,
    output_path: Path,
    *,
    config: ImageSearchConfig | None = None,
    validation_threshold: float = 0.6,
) -> SearchImageResponse:
    """이미지를 검색하고 컨텍스트 적합성을 검증.

    Args:
        request: 검색 요청.
        output_path: 이미지 저장 경로.
        config: 이미지 검색 설정.
        validation_threshold: 검증 통과 신뢰도 임계값.

    Returns:
        SearchImageResponse (선택된 이미지 또는 fallback 플래그).
    """
    # 설정에서 값 가져오기
    validation_model = "gpt-5.4-mini"
    validation_enabled = True

    if config is not None:
        validation_model = config.validation_model
        validation_enabled = config.validation_enabled

    # 1. SerperDev로 이미지 검색
    logger.info("이미지 검색: '%s'", request.query)
    candidates = search_images_serperdev(
        request.query,
        num_results=request.num_results,
    )

    if not candidates:
        logger.warning("검색 결과 없음, 생성으로 전환: '%s'", request.query)
        return SearchImageResponse(
            query=request.query,
            fallback_to_generate=True,
        )

    # 2. 이미 사용한 URL 필터링
    available_candidates = [c for c in candidates if c.url not in _used_image_urls]
    if not available_candidates:
        logger.warning("모든 검색 결과가 이미 사용됨, 생성으로 전환: '%s'", request.query)
        return SearchImageResponse(
            query=request.query,
            all_candidates=candidates,
            fallback_to_generate=True,
        )

    # 3. 검증 비활성화 시 첫 번째 미사용 이미지 사용
    if not validation_enabled:
        selected = available_candidates[0]
        downloaded = download_image(selected.url, output_path)
        if downloaded:
            _resize_image_to_16_9(output_path)
            _used_image_urls.add(selected.url)
            return SearchImageResponse(
                query=request.query,
                selected_image=selected,
                all_candidates=candidates,
            )
        return SearchImageResponse(
            query=request.query,
            all_candidates=candidates,
            fallback_to_generate=True,
        )

    # 4. 각 후보를 검증하여 적합한 이미지 찾기 (미사용 URL만)
    for i, candidate in enumerate(available_candidates):
        logger.debug(
            "이미지 검증 중 [%d/%d]: %s", i + 1, len(available_candidates), candidate.title[:50]
        )

        validation = validate_image_relevance(
            candidate.url,
            request.context,
            model=validation_model,
        )

        # 임계값 이상이면 선택
        if validation.is_relevant and validation.confidence >= validation_threshold:
            logger.info(
                "적합한 이미지 발견: '%s' (신뢰도: %.2f)",
                candidate.title[:50],
                validation.confidence,
            )

            # 이미지 다운로드
            downloaded = download_image(candidate.url, output_path)
            if downloaded:
                _resize_image_to_16_9(output_path)
                _used_image_urls.add(candidate.url)
                return SearchImageResponse(
                    query=request.query,
                    selected_image=candidate,
                    validation=validation,
                    all_candidates=candidates,
                )

    # 5. 모든 후보 검증 실패 → 생성으로 전환
    logger.warning("적합한 검색 이미지 없음, 생성으로 전환: '%s'", request.query)
    return SearchImageResponse(
        query=request.query,
        all_candidates=candidates,
        fallback_to_generate=True,
    )


def reset_used_images() -> None:
    """사용한 이미지 URL 목록 초기화.

    새 프로젝트 시작 시 호출하여 중복 방지 목록을 리셋합니다.
    """
    global _used_image_urls
    _used_image_urls = set()
    logger.debug("이미지 URL 사용 목록 초기화")


def search_image_for_broll(
    query: str,
    context: str,
    output_path: Path,
    *,
    config: ImageSearchConfig | None = None,
) -> Path | None:
    """B-roll용 이미지를 검색하고 다운로드.

    간편한 인터페이스로, 내부적으로 search_and_validate_image를 호출합니다.

    Args:
        query: 검색 쿼리.
        context: B-roll 컨텍스트 (검증용).
        output_path: 이미지 저장 경로.
        config: 이미지 검색 설정.

    Returns:
        다운로드된 이미지 경로, 실패/fallback 시 None.
    """
    request = SearchImageRequest(
        query=query,
        context=context,
        num_results=config.max_candidates if config else 5,
    )

    response = search_and_validate_image(
        request,
        output_path,
        config=config,
    )

    if response.fallback_to_generate:
        return None

    return output_path if output_path.exists() else None
