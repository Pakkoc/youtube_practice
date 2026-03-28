"""이미지 검색 feature 모듈.

Google 이미지 검색 (SerperDev API)과 OpenAI Vision을 사용한
컨텍스트 기반 이미지 검증을 제공합니다.
"""

from .api import (
    download_image,
    search_images_serperdev,
    validate_image_relevance,
)
from .lib import reset_used_images, search_and_validate_image, search_image_for_broll
from .model import (
    ImageSearchResult,
    ImageValidationResult,
    SearchImageRequest,
    SearchImageResponse,
)

__all__ = [
    # Models
    "ImageSearchResult",
    "ImageValidationResult",
    "SearchImageRequest",
    "SearchImageResponse",
    # API functions
    "search_images_serperdev",
    "validate_image_relevance",
    "download_image",
    # High-level functions
    "search_and_validate_image",
    "search_image_for_broll",
    "reset_used_images",
]
