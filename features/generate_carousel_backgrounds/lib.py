"""캐러셀 AI 배경 이미지 생성 핵심 로직.

NanoBanana (Gemini) 백엔드를 활용하여 선택적 캐러셀 카드에
시네마틱 배경 이미지를 생성합니다.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from features.generate_carousel_backgrounds.model import (
    CarouselBackgroundItem,
    CarouselBackgroundPlan,
)
from shared.config.schema import CarouselBackgroundConfig
from shared.lib.logger import get_logger

logger = get_logger()

_DEFAULT_PROMPT_SUFFIX = (
    "cinematic lighting, dark moody atmosphere, professional quality, high detail, "
    "subject positioned in upper half of frame, "
    "leaving bottom 40% relatively clear for text overlay"
)


def generate_carousel_backgrounds(
    plan: CarouselBackgroundPlan,
    output_dir: Path,
    config: CarouselBackgroundConfig | None = None,
    *,
    force: bool = False,
) -> dict[int, Path]:
    """배경 이미지를 NanoBanana (Gemini)로 생성.

    Args:
        plan: 카드별 이미지 프롬프트 계획.
        output_dir: 배경 이미지 저장 디렉토리 (backgrounds/).
        config: 캐러셀 배경 설정. None이면 기본값 사용.
        force: True이면 기존 이미지 덮어쓰기.

    Returns:
        card_number → 생성된 이미지 Path 매핑.
    """
    from features.fetch_broll.backends.nanobanana import NanoBananaBackend

    if config is None:
        config = CarouselBackgroundConfig()

    prompt_suffix = config.prompt_suffix or _DEFAULT_PROMPT_SUFFIX

    backend = NanoBananaBackend(
        aspect_ratio="3:4",  # 4:5에 가장 가까운 Gemini 지원 비율
        height=1350,
        width=1080,
        use_reference=False,
        save_captions=True,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[int, Path] = {}

    for i, item in enumerate(plan.items):
        card_num = item.card_number
        output_path = output_dir / f"bg_{card_num:03d}.png"

        # 기존 이미지 재사용
        if output_path.exists() and not force:
            logger.info(
                "배경 %d/%d: 재사용 %s",
                i + 1,
                len(plan.items),
                output_path.name,
            )
            results[card_num] = output_path
            continue

        # 프롬프트 조합
        enhanced_prompt = f"{item.image_prompt}. {prompt_suffix}"

        logger.info(
            "배경 %d/%d 생성 (card %d, %s): %s",
            i + 1,
            len(plan.items),
            card_num,
            item.card_role,
            item.image_prompt[:80],
        )

        # 생성 시도 (1회 재시도)
        result_path = _generate_with_retry(backend, enhanced_prompt, output_path)

        if result_path is not None:
            results[card_num] = result_path
            logger.info("배경 저장: %s", result_path.name)
        else:
            logger.warning("배경 생성 실패 (card %d), 건너뜀", card_num)

        # Rate limit 방지: 카드간 2초 대기
        if i < len(plan.items) - 1:
            time.sleep(2)

    backend.cleanup()

    logger.info(
        "캐러셀 배경 생성 완료: %d/%d 성공 → %s",
        len(results),
        len(plan.items),
        output_dir,
    )
    return results


def _generate_with_retry(
    backend,
    prompt: str,
    output_path: Path,
    max_retries: int = 1,
) -> Path | None:
    """NanoBanana 이미지 생성 (재시도 포함).

    Args:
        backend: NanoBananaBackend 인스턴스.
        prompt: 강화된 프롬프트.
        output_path: 출력 경로.
        max_retries: 최대 재시도 횟수.

    Returns:
        생성된 이미지 경로, 실패 시 None.
    """
    for attempt in range(1 + max_retries):
        result = backend.generate(prompt, output_path)
        if result is not None:
            return result
        if attempt < max_retries:
            logger.warning("재시도 %d/%d...", attempt + 1, max_retries)
            time.sleep(3)
    return None


def parse_copy_deck_image_prompts(copy_deck_path: Path) -> CarouselBackgroundPlan:
    """copy_deck.md에서 image_prompt 필드를 파싱.

    카드 섹션 (### Card N — Role) 내의 `- image_prompt: "..."` 라인을 추출합니다.

    Args:
        copy_deck_path: copy_deck.md 파일 경로.

    Returns:
        파싱된 CarouselBackgroundPlan.
    """
    text = copy_deck_path.read_text(encoding="utf-8")
    items: list[CarouselBackgroundItem] = []

    # 카드 섹션 패턴: ### Card N — Role
    card_pattern = re.compile(
        r"###\s+Card\s+(\d+)\s*[—–-]\s*(.+?)(?:\n|$)",
        re.IGNORECASE,
    )
    # image_prompt 패턴: - image_prompt: "..." 또는 - image_prompt: ...
    prompt_pattern = re.compile(
        r"-\s*image_prompt\s*:\s*[\"']?(.+?)[\"']?\s*$",
        re.MULTILINE,
    )

    # 각 카드 섹션을 찾아서 image_prompt 추출
    card_matches = list(card_pattern.finditer(text))
    for idx, match in enumerate(card_matches):
        card_num = int(match.group(1))
        card_role_raw = match.group(2).strip().lower()

        # 카드 역할 정규화
        card_role = "body"
        if "cover" in card_role_raw:
            card_role = "cover"
        elif "cta" in card_role_raw:
            card_role = "cta"
        elif "quote" in card_role_raw:
            card_role = "quote"

        # 이 카드 섹션의 텍스트 범위
        start = match.end()
        end = card_matches[idx + 1].start() if idx + 1 < len(card_matches) else len(text)
        section_text = text[start:end]

        prompt_match = prompt_pattern.search(section_text)
        if prompt_match:
            image_prompt = prompt_match.group(1).strip()
            if image_prompt:
                items.append(
                    CarouselBackgroundItem(
                        card_number=card_num,
                        image_prompt=image_prompt,
                        card_role=card_role,
                    )
                )

    logger.info("copy_deck 파싱: %d개 카드에서 image_prompt 발견", len(items))
    return CarouselBackgroundPlan(items=items)


def parse_bg_prompts_json(json_path: Path) -> CarouselBackgroundPlan:
    """bg_prompts.json에서 배경 이미지 프롬프트를 파싱.

    JSON 형식:
    [
        {"card_number": 1, "image_prompt": "...", "card_role": "cover"},
        {"card_number": 3, "image_prompt": "...", "card_role": "quote"}
    ]

    Args:
        json_path: bg_prompts.json 파일 경로.

    Returns:
        파싱된 CarouselBackgroundPlan.
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))
    items = [CarouselBackgroundItem(**item) for item in data]
    logger.info("bg_prompts.json 파싱: %d개 항목", len(items))
    return CarouselBackgroundPlan(items=items)
