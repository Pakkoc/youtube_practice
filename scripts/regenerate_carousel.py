#!/usr/bin/env python3
"""
Carousel PNG renderer — copies each card_NNN.tsx to FreeformCard.tsx,
renders with remotion still, then restores the original FreeformCard.tsx.

Usage:
  python scripts/regenerate_carousel.py <project> [card_nums...] [--force]

Examples:
  python scripts/regenerate_carousel.py test2          # all cards
  python scripts/regenerate_carousel.py test2 1 3 5   # specific cards
  python scripts/regenerate_carousel.py test2 --force  # force re-render
"""

import shutil
import subprocess
import sys
import json
import tempfile
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
REMOTION_DIR = ROOT / "remotion"
FREEFORM_CARD = REMOTION_DIR / "src" / "carousel" / "FreeformCard.tsx"
FREEFORM_CARD_BACKUP = REMOTION_DIR / "src" / "carousel" / "FreeformCard.tsx.bak"

DARK_COLORS = {
    "background": "#0B0C0E",
    "accent": "#7C7FD9",
    "text": "#EDEDEF",
}


def render_card(card_tsx: Path, out_png: Path, card_index: int, total_cards: int) -> bool:
    """Copy card TSX, render, restore."""
    # Backup original if exists
    original_exists = FREEFORM_CARD.exists()
    if original_exists:
        shutil.copy2(FREEFORM_CARD, FREEFORM_CARD_BACKUP)

    try:
        # Overwrite FreeformCard.tsx with this card
        shutil.copy2(card_tsx, FREEFORM_CARD)

        props = {
            "cardIndex": card_index,
            "totalCards": total_cards,
            "colors": DARK_COLORS,
        }
        props_str = json.dumps(props)

        # Write props to a temp JSON file (Windows quote escaping workaround)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir=REMOTION_DIR
        ) as f:
            json.dump(props, f)
            props_file = f.name

        try:
            out_png_str = str(out_png).replace("\\", "/")
            props_file_str = props_file.replace("\\", "/")
            cmd = (
                f'npx remotion still FreeformCard "{out_png_str}"'
                f' --props="{props_file_str}"'
                f" --image-format png"
            )
            result = subprocess.run(
                cmd,
                cwd=REMOTION_DIR,
                shell=True,
                timeout=120,
            )
        finally:
            os.unlink(props_file)
        return result.returncode == 0
    finally:
        # Always restore
        if original_exists and FREEFORM_CARD_BACKUP.exists():
            shutil.copy2(FREEFORM_CARD_BACKUP, FREEFORM_CARD)
            FREEFORM_CARD_BACKUP.unlink(missing_ok=True)


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python scripts/regenerate_carousel.py <project> [card_nums...] [--force]")
        sys.exit(1)

    project = args[0]
    force = "--force" in args
    specific_nums = [int(a) for a in args[1:] if a.isdigit()]

    carousel_dir = ROOT / "projects" / project / "carousel"
    if not carousel_dir.exists():
        print(f"ERROR: {carousel_dir} does not exist")
        sys.exit(1)

    # Collect card TSX files sorted
    tsx_files = sorted(carousel_dir.glob("card_*.tsx"))
    if not tsx_files:
        print("No card_*.tsx files found")
        sys.exit(1)

    total_cards = len(tsx_files)

    if specific_nums:
        tsx_files = [f for f in tsx_files if int(f.stem.split("_")[1]) in specific_nums]

    print(f"Rendering {len(tsx_files)} card(s) for project '{project}' (total={total_cards})")

    success = 0
    for tsx in tsx_files:
        num = int(tsx.stem.split("_")[1])
        out_png = carousel_dir / f"card_{num:03d}.png"

        if out_png.exists() and not force:
            print(f"  [SKIP] card_{num:03d}.png already exists (use --force to re-render)")
            continue

        card_index = num - 1  # 0-indexed
        print(f"  Rendering card_{num:03d} (index={card_index}/{total_cards-1})...", end=" ", flush=True)
        ok = render_card(tsx, out_png, card_index, total_cards)
        if ok:
            print("OK")
            success += 1
        else:
            print("FAILED")

    print(f"\nDone: {success}/{len(tsx_files)} rendered")


if __name__ == "__main__":
    main()
