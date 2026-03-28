"""B-roll 이미지 수집 API (Pexels + OpenAI Image Generation)."""

from __future__ import annotations

import os
from pathlib import Path

import requests

from shared.api.http import download_file
from shared.lib.logger import get_logger

logger = get_logger()

_PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"


def search_pexels(keyword: str, *, per_page: int = 1) -> list[dict]:
    """Pexels API로 이미지를 검색.

    Args:
        keyword: 검색 키워드 (영어).
        per_page: 검색 결과 수.

    Returns:
        Pexels 사진 정보 딕셔너리 리스트.
    """
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY 환경 변수가 설정되지 않았습니다.")

    headers = {"Authorization": api_key}
    params = {
        "query": keyword,
        "per_page": per_page,
        "orientation": "landscape",
    }

    response = requests.get(
        _PEXELS_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    photos = data.get("photos", [])
    logger.debug("Pexels 검색 '%s': %d개 결과", keyword, len(photos))
    return photos


def download_pexels_image(
    keyword: str,
    dest: Path,
    *,
    size: str = "large",
) -> Path | None:
    """Pexels에서 이미지를 검색하고 다운로드.

    Args:
        keyword: 검색 키워드.
        dest: 저장할 파일 경로.
        size: 이미지 크기 ("original", "large", "medium", "small").

    Returns:
        다운로드된 파일 경로, 실패 시 None.
    """
    photos = search_pexels(keyword, per_page=1)
    if not photos:
        logger.warning("Pexels 검색 결과 없음: '%s'", keyword)
        return None

    photo = photos[0]
    url = photo.get("src", {}).get(size) or photo.get("src", {}).get("large")
    if not url:
        logger.warning("Pexels 이미지 URL 없음: '%s'", keyword)
        return None

    logger.info("Pexels 이미지 다운로드: '%s' → %s", keyword, dest.name)
    return download_file(url, dest)


def generate_image_via_openai(
    prompt: str,
    dest: Path,
    *,
    size: str = "1792x1024",
    model: str = "gpt-image-1",
) -> Path | None:
    """OpenAI Image Generation API로 이미지를 생성.

    Args:
        prompt: 이미지 생성 프롬프트 (영어).
        dest: 저장할 파일 경로.
        size: 이미지 크기.
        model: 사용할 모델.

    Returns:
        생성된 이미지 파일 경로, 실패 시 None.
    """
    try:
        import base64

        from openai import OpenAI

        client = OpenAI()

        logger.info("OpenAI 이미지 생성: '%s'", prompt[:80])
        result = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size=size,
        )

        # base64 응답 처리
        image_data = result.data[0]
        if hasattr(image_data, "b64_json") and image_data.b64_json:
            img_bytes = base64.b64decode(image_data.b64_json)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(img_bytes)
            return dest

        # URL 응답 처리
        if hasattr(image_data, "url") and image_data.url:
            return download_file(image_data.url, dest)

        logger.warning("OpenAI 이미지 응답에 데이터 없음")
        return None
    except Exception as e:
        logger.error("OpenAI 이미지 생성 실패: %s", e)
        return None
