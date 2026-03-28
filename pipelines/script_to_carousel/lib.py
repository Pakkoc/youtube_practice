"""대본 -> 카루셀(카드뉴스) 파이프라인 핵심 로직 (Freeform TSX 전용)."""

from __future__ import annotations

from pathlib import Path

from entities.project.model import Project
from features.generate_carousel import render_freeform_cards
from shared.config.schema import AppConfig
from shared.lib.logger import get_logger

logger = get_logger()


def run_script_to_carousel(
    project: Project,
    config: AppConfig,
) -> list[Path]:
    """카드뉴스 이미지를 생성하는 파이프라인 (Freeform TSX 전용).

    사전 조건: /generate-carousel 스킬로 card_*.tsx 파일이 생성되어 있어야 함.

    Args:
        project: 프로젝트 객체.
        config: 전체 설정.

    Returns:
        생성된 PNG 파일 경로 리스트.

    Raises:
        FileNotFoundError: card_*.tsx 파일이 없을 때.
    """
    carousel_config = config.carousel
    carousel_dir = project.carousel_dir
    carousel_dir.mkdir(parents=True, exist_ok=True)

    tsx_files = sorted(carousel_dir.glob("card_*.tsx"))
    if not tsx_files:
        raise FileNotFoundError(
            f"Freeform TSX 파일이 없습니다: {carousel_dir}\n"
            f"/generate-carousel 스킬로 먼저 TSX 파일을 생성하세요."
        )

    logger.info("Freeform TSX 감지: %d cards", len(tsx_files))
    cards = render_freeform_cards(tsx_files, carousel_dir, carousel_config)
    logger.info("카루셀 파이프라인 완료: %d cards -> %s", len(cards), carousel_dir)
    return cards
