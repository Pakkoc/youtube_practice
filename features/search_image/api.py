"""이미지 검색 API (SerperDev + OpenAI Vision 검증)."""

from __future__ import annotations

import os
from pathlib import Path

import requests

from shared.api.http import download_file
from shared.lib.logger import get_logger

from .model import ImageSearchResult, ImageValidationResult

logger = get_logger()

_SERPER_IMAGES_URL = "https://google.serper.dev/images"


def search_images_serperdev(
    query: str,
    *,
    num_results: int = 5,
) -> list[ImageSearchResult]:
    """SerperDev API로 Google 이미지 검색.

    Args:
        query: 검색 쿼리 (영어 권장).
        num_results: 검색 결과 수.

    Returns:
        ImageSearchResult 리스트.
    """
    api_key = os.environ.get("SERPER_API_KEY") or os.environ.get("SERPERDEV_API_KEY")
    if not api_key:
        raise RuntimeError("SERPER_API_KEY 또는 SERPERDEV_API_KEY 환경 변수가 설정되지 않았습니다.")

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "q": query,
        "num": num_results,
    }

    try:
        response = requests.post(
            _SERPER_IMAGES_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        images = data.get("images", [])

        results = []
        for img in images:
            results.append(
                ImageSearchResult(
                    url=img.get("imageUrl", ""),
                    title=img.get("title", ""),
                    source=img.get("source", ""),
                    width=img.get("imageWidth", 0),
                    height=img.get("imageHeight", 0),
                )
            )

        logger.debug("SerperDev 이미지 검색 '%s': %d개 결과", query, len(results))
        return results

    except requests.RequestException as e:
        logger.error("SerperDev 검색 실패: %s", e)
        return []


def validate_image_relevance(
    image_url: str,
    context: str,
    *,
    model: str = "gpt-5.4-mini",
) -> ImageValidationResult:
    """OpenAI Vision으로 이미지가 컨텍스트에 적합한지 검증.

    Args:
        image_url: 검증할 이미지 URL.
        context: B-roll 삽입 시점의 대본 컨텍스트.
        model: 사용할 모델 (기본: gpt-5.4-mini).

    Returns:
        ImageValidationResult.
    """
    from shared.api.claude import get_client

    client = get_client()

    prompt = f"""Evaluate if this image is appropriate for use as B-roll footage in a video.

## Context
The video is discussing the following content
(text in 【brackets】 is the exact moment where this B-roll will appear):

{context}

## Task
Determine if this image visually relates to and supports the content being discussed.

## Criteria for "relevant":
1. The image visually represents concepts, objects, or themes mentioned in the context
2. The image is appropriate for educational/informational content
3. The image has good visual quality (not blurry, not too small)
4. The image does not contain inappropriate content
5. The image does NOT have visible watermarks, stock photo logos, or overlay text
6. The image is a clean photograph or illustration without distracting UI elements or website chrome

## Response Format
Respond with JSON only:
```json
{{
  "is_relevant": true/false,
  "confidence": 0.0-1.0,
  "reason": "brief explanation"
}}
```"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_completion_tokens=2048,
        )

        # JSON 파싱
        text = response.choices[0].message.content or ""
        import json

        # JSON 추출
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            text = text[start:end].strip()

        data = json.loads(text)

        return ImageValidationResult(
            is_relevant=data.get("is_relevant", False),
            confidence=float(data.get("confidence", 0.0)),
            reason=data.get("reason", ""),
        )

    except Exception as e:
        logger.error("이미지 검증 실패: %s", e)
        return ImageValidationResult(
            is_relevant=False,
            confidence=0.0,
            reason=f"Validation error: {e}",
        )


def download_image(url: str, dest: Path) -> Path | None:
    """이미지를 다운로드.

    Args:
        url: 이미지 URL.
        dest: 저장할 파일 경로.

    Returns:
        다운로드된 파일 경로, 실패 시 None.
    """
    try:
        return download_file(url, dest)
    except Exception as e:
        logger.error("이미지 다운로드 실패 '%s': %s", url, e)
        return None
