"""카루셀 카드 Remotion PNG 렌더링 (Freeform TSX 전용)."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from shared.config.schema import CarouselConfig
from shared.lib import subprocess
from shared.lib.logger import get_logger

logger = get_logger()

_IS_WINDOWS = sys.platform == "win32"


def render_freeform_cards(
    tsx_files: list[Path],
    output_dir: Path,
    config: CarouselConfig,
    remotion_project_path: Path | None = None,
    total_cards_override: int | None = None,
    background_images: dict[int, Path] | None = None,
) -> list[Path]:
    """Freeform TSX 카드들을 Remotion still로 PNG 렌더링.

    FreeformCard.tsx를 각 카드의 TSX 코드로 덮어쓰고 렌더링 후 복원.

    Args:
        tsx_files: TSX 파일 경로 리스트 (card_001.tsx, ...).
        output_dir: 출력 디렉토리 (card_001.png, ...).
        config: 카루셀 설정.
        remotion_project_path: Remotion 프로젝트 경로.
        total_cards_override: 전체 카드 수 (특정 카드만 렌더링할 때 사용).
        background_images: 카드 번호 → 배경 이미지 경로 매핑 (선택).

    Returns:
        생성된 PNG 파일 경로 리스트.
    """
    if remotion_project_path is None:
        remotion_project_path = Path(__file__).parents[2] / "remotion"

    output_dir.mkdir(parents=True, exist_ok=True)
    total_cards = total_cards_override if total_cards_override is not None else len(tsx_files)

    freeform_path = remotion_project_path / "src" / "carousel" / "FreeformCard.tsx"
    original_code = freeform_path.read_text(encoding="utf-8") if freeform_path.exists() else None

    colors = {
        "background": config.background_color,
        "accent": config.accent_color,
        "text": config.text_color,
    }

    results: list[Path] = []

    try:
        for i, tsx_path in enumerate(tsx_files):
            card_num = int(tsx_path.stem.split("_")[-1]) if "_" in tsx_path.stem else i + 1
            output_path = output_dir / f"card_{card_num:03d}.png"

            # 기존 PNG 재사용
            if output_path.exists():
                logger.info(
                    "Freeform 카드 %d/%d: 재사용 %s",
                    i + 1,
                    total_cards,
                    output_path.name,
                )
                results.append(output_path)
                continue

            # TSX 코드로 FreeformCard.tsx 덮어쓰기
            tsx_code = tsx_path.read_text(encoding="utf-8")
            freeform_path.write_text(tsx_code, encoding="utf-8")

            # 배경 이미지 → remotion/public/ 임시 복사
            bg_temp_path: Path | None = None
            bg_static_name: str | None = None
            if background_images and card_num in background_images:
                bg_src = background_images[card_num]
                bg_static_name = f"_carousel_bg_{card_num:03d}{bg_src.suffix}"
                bg_temp_path = remotion_project_path / "public" / bg_static_name
                shutil.copy2(bg_src, bg_temp_path)
                logger.info("배경 이미지 복사: %s → %s", bg_src.name, bg_static_name)

            # props 생성 (cardIndex는 파일명 기반 0-indexed)
            render_props: dict = {
                "cardIndex": card_num - 1,
                "totalCards": total_cards,
                "colors": colors,
                "themeName": config.theme,
            }
            if bg_static_name:
                render_props["backgroundImage"] = bg_static_name

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False,
                encoding="utf-8",
            ) as f:
                json.dump(render_props, f, ensure_ascii=False)
                props_path = Path(f.name)

            try:
                output_abs = str(output_path.absolute())
                props_abs = str(props_path)

                logger.info(
                    "Freeform 카드 %d/%d 렌더링: %s -> %s",
                    i + 1,
                    total_cards,
                    tsx_path.name,
                    output_path.name,
                )

                if _IS_WINDOWS:
                    cmd: str | list[str] = (
                        f'npx remotion still FreeformCard "{output_abs}"'
                        f' "--props={props_abs}"'
                        f" --width={config.width}"
                        f" --height={config.height}"
                        f" --image-format=png"
                    )
                else:
                    cmd = [
                        "npx",
                        "remotion",
                        "still",
                        "FreeformCard",
                        output_abs,
                        f"--props={props_abs}",
                        f"--width={config.width}",
                        f"--height={config.height}",
                        "--image-format=png",
                    ]

                result = subprocess.run(
                    cmd,
                    cwd=str(remotion_project_path),
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=_IS_WINDOWS,
                    timeout=120,
                )

                if result.returncode != 0:
                    stderr_tail = result.stderr[-500:] if result.stderr else ""
                    logger.error(
                        "Freeform 카드 렌더링 오류 (%s): %s",
                        output_path.name,
                        stderr_tail,
                    )
                    raise RuntimeError(
                        f"Freeform card rendering failed: {output_path.name}\n{stderr_tail}"
                    )

                results.append(output_path)
            finally:
                props_path.unlink(missing_ok=True)
                if bg_temp_path is not None:
                    bg_temp_path.unlink(missing_ok=True)

    finally:
        # 원본 FreeformCard.tsx 복원
        if original_code is not None:
            freeform_path.write_text(original_code, encoding="utf-8")
            logger.info("FreeformCard.tsx 원본 복원 완료")

    logger.info(
        "Freeform 카루셀 렌더링 완료: %d cards -> %s",
        len(results),
        output_dir,
    )
    return results
