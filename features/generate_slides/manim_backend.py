"""Manim CE slide backend -- renders Python scene code to MP4.

2-pass duration control:
  1. Render with `self.wait(0)` placeholder -> measure actual duration
  2. Inject `self.wait(remaining)` -> re-render to match target duration

Also includes Manim code validation utilities (structure checks,
alignment anti-pattern detection, code sanitization).
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

from shared.lib import subprocess
from shared.lib.ffmpeg import get_duration
from shared.lib.logger import get_logger

logger = get_logger()

# ---------------------------------------------------------------------------
# Manim code validation & sanitization
# ---------------------------------------------------------------------------

# Dangerous patterns to block
_BLOCKED_PATTERNS = [
    re.compile(r"\bimport\s+os\b"),
    re.compile(r"\bimport\s+subprocess\b"),
    re.compile(r"\bfrom\s+os\b"),
    re.compile(r"\bfrom\s+subprocess\b"),
    re.compile(r"\bopen\s*\("),
    re.compile(r"\beval\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"\b__import__\s*\("),
    re.compile(r"\bos\.system\s*\("),
    re.compile(r"\bos\.popen\s*\("),
]

# Required structural elements
_REQUIRED_CLASS = re.compile(r"class\s+ManimSlide\s*\(\s*Scene\s*\)")
_REQUIRED_CONSTRUCT = re.compile(r"def\s+construct\s*\(\s*self\s*\)")
_REQUIRED_ACTION = re.compile(r"self\.(play|add|wait)\s*\(")

# Alignment anti-pattern detection
_HAS_LOOP = re.compile(r"\bfor\s+\w+")
_ARRANGE_RIGHT = re.compile(r"\.arrange\(\s*RIGHT")
_FIXED_WIDTH_CONTAINER = re.compile(
    r"(?:RoundedRectangle|Rectangle)\([^)]*width\s*="
)
_CONTENT_CENTER_ON_CARD = re.compile(
    r"\.move_to\(\s*card\.get_center\(\)\s*\)"
)


def check_manim_structure(code: str) -> list[str]:
    """Validate Manim code structure. Returns list of error messages (empty = OK)."""
    errors: list[str] = []

    if not _REQUIRED_CLASS.search(code):
        errors.append("Missing 'class ManimSlide(Scene)'")

    if not _REQUIRED_CONSTRUCT.search(code):
        errors.append("Missing 'def construct(self)'")

    if not _REQUIRED_ACTION.search(code):
        errors.append("Missing self.play(), self.add(), or self.wait() call")

    for pattern in _BLOCKED_PATTERNS:
        match = pattern.search(code)
        if match:
            errors.append(f"Blocked pattern: {match.group()}")

    return errors


def check_manim_alignment(code: str) -> list[str]:
    """Check for alignment anti-patterns that cause visual layout issues.

    Detects patterns known to produce inconsistent row widths, overlapping
    elements, or content drifting to the wrong region of the frame.

    Returns list of warning messages (empty = OK).
    """
    warnings: list[str] = []
    has_loop = bool(_HAS_LOOP.search(code))

    # Pattern 1: SurroundingRectangle inside a loop
    if has_loop and "SurroundingRectangle" in code:
        warnings.append(
            "SurroundingRectangle inside a loop creates varying widths per row. "
            "Use fixed-width RoundedRectangle(width=ROW_WIDTH) as row container."
        )

    # Pattern 2: Multiple arrange(RIGHT) without fixed-width container
    if has_loop:
        arrange_right_count = len(_ARRANGE_RIGHT.findall(code))
        has_fixed_container = bool(_FIXED_WIDTH_CONTAINER.search(code))
        if arrange_right_count >= 2 and not has_fixed_container:
            warnings.append(
                "Multiple arrange(RIGHT) rows without fixed-width container. "
                "Add RoundedRectangle(width=ROW_WIDTH) behind each row "
                "and use move_to() for fixed element positioning."
            )

    # Pattern 3: Content group centered on card.get_center()
    if _CONTENT_CENTER_ON_CARD.search(code):
        has_top_anchor = bool(
            re.search(r"\.to_edge\(\s*UP", code)
            or re.search(r"\.next_to\(\s*underline", code)
        )
        if not has_top_anchor:
            warnings.append(
                "Content positioned at card.get_center() may drift to bottom. "
                "Use .next_to(underline, DOWN, buff=0.55) to anchor below title."
            )

    return warnings


def sanitize_manim_code(response: str) -> str:
    """Strip markdown code fences and fix common API misuse."""
    text = response.strip()

    # Remove ```python ... ``` or ``` ... ```
    if text.startswith("```python"):
        text = text[len("```python") :]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Fix common LLM mistakes
    # arrange(CENTER) is invalid — CENTER is not defined in Manim
    text = re.sub(
        r"\.arrange\(\s*CENTER\s*\)",
        ".arrange(ORIGIN)",
        text,
    )

    return text



_WAIT_PLACEHOLDER = "self.wait(0.01)  # DURATION_PLACEHOLDER"
_WAIT_PATTERN = re.compile(
    r"self\.wait\(0(?:\.0+)?\)\s*#\s*DURATION_PLACEHOLDER"
)

# Remotion design values (from AnimatedBackground.tsx, ProgressBar.tsx)
_GRAD_TOP = "#0A2332"  # rgb(10,35,50)
_GRAD_BOTTOM = "#1E0F3C"  # rgb(30,15,60)
_CARD_COLOR = "#0B0C0E"
_CARD_WIDTH = 13.4  # (1920 - 56*2) / 135 ≈ 13.4 Manim units
_CARD_HEIGHT = 7.28  # (1080 - 48*2) / 135 ≈ 7.28 Manim units
_CARD_RADIUS = 0.15  # 20px / 135
_PROGRESS_HEIGHT = 0.022  # 3px / 135
_PROGRESS_ACCENT = "#7C7FD9"
_PROGRESS_TEAL = "#3CB4B4"


class ManimSlideBackend:
    """Manim CE renderer for individual slides."""

    @staticmethod
    def is_available() -> bool:
        """Check if manim CE is importable in the current environment."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import manim; print(manim.__version__)"],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
            return result.returncode == 0
        except Exception:
            return False

    def render(
        self,
        scene_code: str,
        output_path: Path,
        duration_seconds: float,
        *,
        fps: int = 30,
        width: int = 1920,
        height: int = 1080,
        background_image: Path | None = None,
        slide_index: int | None = None,
        total_slides: int | None = None,
        timeout: int = 120,
    ) -> Path:
        """Render a Manim scene to MP4 with target duration.

        Args:
            scene_code: Python source with class ManimSlide(Scene).
            output_path: Where to write the final MP4.
            duration_seconds: Target duration in seconds.
            fps: Frames per second.
            width: Pixel width.
            height: Pixel height.
            background_image: Optional background image (20% opacity).
            slide_index: 0-based slide index for progress bar.
            total_slides: Total number of slides for progress bar.
            timeout: Max seconds per render pass.

        Returns:
            Path to rendered MP4.

        Raises:
            RuntimeError: If rendering fails.
        """
        # Safety: Manim rejects wait(0), replace with 0.01
        scene_code = re.sub(
            r"self\.wait\(\s*0\s*\)",
            "self.wait(0.01)",
            scene_code,
        )

        # Inject Remotion-style frame (gradient bg + dark card + progress bar)
        scene_code = _inject_frame(scene_code, slide_index, total_slides)

        # Inject background image if provided (inside card area)
        if background_image and background_image.exists():
            scene_code = _inject_background(scene_code, background_image)

        # Pass 1: render with placeholder wait(0)
        pass1_mp4 = self._render_once(scene_code, fps, width, height, timeout)

        try:
            actual_dur = get_duration(pass1_mp4)
        except Exception as e:
            raise RuntimeError(f"Manim pass-1 output unreadable: {e}") from e

        remaining = duration_seconds - actual_dur

        if abs(remaining) <= 0.5:
            # Close enough -- use pass-1 output
            _move_file(pass1_mp4, output_path)
            logger.info(
                "Manim render OK (1-pass): %.1fs (target %.1fs)",
                actual_dur,
                duration_seconds,
            )
            return output_path

        if remaining < 0:
            # Scene is already longer than target -- use as-is
            logger.warning(
                "Manim scene longer than target (%.1fs > %.1fs), using as-is",
                actual_dur,
                duration_seconds,
            )
            _move_file(pass1_mp4, output_path)
            return output_path

        # Pass 2: inject remaining wait and re-render
        wait_sec = max(remaining, 0.01)
        padded_code = _WAIT_PATTERN.sub(
            f"self.wait({wait_sec:.2f})  # DURATION_PLACEHOLDER",
            scene_code,
        )

        if padded_code == scene_code:
            # No placeholder found -- append wait before last line of construct
            padded_code = _append_wait(scene_code, remaining)

        pass2_mp4 = self._render_once(padded_code, fps, width, height, timeout)
        _move_file(pass2_mp4, output_path)

        try:
            final_dur = get_duration(output_path)
        except Exception:
            final_dur = 0.0

        logger.info(
            "Manim render OK (2-pass): %.1fs (target %.1fs, pad %.1fs)",
            final_dur,
            duration_seconds,
            remaining,
        )
        return output_path

    @staticmethod
    def _render_once(
        scene_code: str,
        fps: int,
        width: int,
        height: int,
        timeout: int,
    ) -> Path:
        """Execute manim render and return path to output MP4."""
        with tempfile.TemporaryDirectory(prefix="manim_") as tmpdir:
            tmp = Path(tmpdir)
            scene_file = tmp / "scene.py"
            scene_file.write_text(scene_code, encoding="utf-8")

            media_dir = tmp / "media"

            cmd = [
                sys.executable,
                "-m",
                "manim",
                "render",
                str(scene_file),
                "ManimSlide",
                "--media_dir",
                str(media_dir),
                "--fps",
                str(fps),
                f"--resolution={width},{height}",
                "--format=mp4",
                "--disable_caching",
            ]

            logger.debug("Manim cmd: %s", " ".join(cmd))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )

            if result.returncode != 0:
                stderr_short = (result.stderr or "")[-1000:]
                raise RuntimeError(f"Manim render failed (rc={result.returncode}): {stderr_short}")

            # Find the rendered MP4
            mp4_files = list(media_dir.rglob("*.mp4"))
            if not mp4_files:
                raise RuntimeError("Manim produced no MP4 output")

            # Copy to a persistent temp file (tmpdir will be cleaned up)
            import shutil

            persistent = Path(tempfile.mktemp(suffix=".mp4", prefix="manim_out_"))
            shutil.copy2(mp4_files[0], persistent)
            return persistent


def _inject_frame(
    scene_code: str,
    slide_index: int | None,
    total_slides: int | None,
) -> str:
    """Inject Remotion-style gradient frame + dark card + progress bar.

    Inserts Manim objects right after ``def construct(self):`` so they
    render beneath all user content (added later via self.play/self.add).

    Elements:
        1. Full-frame gradient rectangle (covers camera background)
        2. Dark content card with margins and subtle border
        3. Progress bar at card bottom (if slide_index provided)
    """
    # Build the code snippet to inject
    grad_top = _GRAD_TOP
    grad_bot = _GRAD_BOTTOM
    card_color = _CARD_COLOR
    cw = _CARD_WIDTH
    ch = _CARD_HEIGHT
    cr = _CARD_RADIUS
    ph = _PROGRESS_HEIGHT

    # Use 2-level indent (class > method) for injected code
    i = "        "  # 8-space indent

    lines = [
        "",
        f"{i}# --- AUTO-INJECTED FRAME (Remotion visual match) ---",
        f"{i}_grad_bg = Rectangle(",
        f"{i}    width=config.frame_width + 0.5,",
        f"{i}    height=config.frame_height + 0.5,",
        f"{i})",
        f'{i}_grad_bg.set_color('
        f'[ManimColor("{grad_top}"), ManimColor("{grad_bot}")])',
        f"{i}_grad_bg.set_sheen_direction(DOWN)",
        f"{i}_grad_bg.set_fill(opacity=1)",
        f"{i}_grad_bg.set_stroke(width=0)",
        f"{i}self.add(_grad_bg)",
        "",
        f"{i}_dark_card = RoundedRectangle(",
        f"{i}    width={cw}, height={ch},",
        f"{i}    corner_radius={cr},",
        f'{i}    fill_color=ManimColor("{card_color}"),',
        f"{i}    fill_opacity=1,",
        f"{i}    stroke_color=WHITE,",
        f"{i}    stroke_opacity=0.04, stroke_width=1,",
        f"{i})",
        f"{i}self.add(_dark_card)",
    ]

    # Progress bar at screen bottom (matches Remotion: bottom:0, full width)
    if (
        slide_index is not None
        and total_slides is not None
        and total_slides > 0
    ):
        progress_frac = slide_index / total_slides
        # Full frame width for track, proportional for fill
        fw_str = "config.frame_width"
        fill_width_expr = f"{fw_str} * {progress_frac:.4f}"
        accent = _PROGRESS_ACCENT
        teal = _PROGRESS_TEAL
        lines += [
            "",
            f"{i}_prog_track = Rectangle(",
            f"{i}    width=config.frame_width,",
            f"{i}    height={ph},",
            f"{i}    fill_color=WHITE, fill_opacity=0.06,",
            f"{i}    stroke_width=0,",
            f"{i})",
            f"{i}_prog_track.to_edge(DOWN, buff=0)",
            f"{i}self.add(_prog_track)",
            f"{i}_prog_fill = Rectangle(",
            f"{i}    width={fill_width_expr},",
            f"{i}    height={ph},",
            f'{i}    fill_color=ManimColor("{accent}"),',
            f"{i}    fill_opacity=1, stroke_width=0,",
            f"{i})",
            f"{i}_prog_fill.set_color(",
            f'{i}    [ManimColor("{accent}"),'
            f' ManimColor("{teal}")]',
            f"{i})",
            f"{i}_prog_fill.set_sheen_direction(RIGHT)",
            f"{i}_prog_fill.move_to(_prog_track)",
            f"{i}_prog_fill.align_to(_prog_track, LEFT)",
            f"{i}self.add(_prog_fill)",
        ]

    lines += [
        "        # --- END AUTO-INJECTED FRAME ---",
        "",
    ]

    snippet = "\n".join(lines)

    # Insert after `def construct(self):` line
    pattern = re.compile(r"(def construct\(self\):.*\n)")
    match = pattern.search(scene_code)
    if match:
        insert_pos = match.end()
        return scene_code[:insert_pos] + snippet + scene_code[insert_pos:]
    return scene_code


def _inject_background(scene_code: str, image_path: Path) -> str:
    """Insert ImageMobject background constrained to card area (not full frame)."""
    bg_snippet = f'''
        _bg = ImageMobject(r"{image_path}")
        _bg.height = {_CARD_HEIGHT}
        _bg.width = {_CARD_WIDTH}
        _bg.set_opacity(0.1)
        self.add(_bg)
'''
    # Insert after the auto-injected frame block, or after construct() line
    end_marker = "# --- END AUTO-INJECTED FRAME ---"
    marker_pos = scene_code.find(end_marker)
    if marker_pos != -1:
        insert_pos = scene_code.index("\n", marker_pos) + 1
        return scene_code[:insert_pos] + bg_snippet + scene_code[insert_pos:]

    # Fallback: insert after `def construct(self):` line
    pattern = re.compile(r"(def construct\(self\):.*\n)")
    match = pattern.search(scene_code)
    if match:
        insert_pos = match.end()
        return scene_code[:insert_pos] + bg_snippet + scene_code[insert_pos:]
    return scene_code


def _append_wait(scene_code: str, seconds: float) -> str:
    """Append self.wait() before the last line of construct() method."""
    lines = scene_code.split("\n")
    # Find the last non-empty line inside construct
    insert_idx = len(lines) - 1
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith("#"):
            insert_idx = i + 1
            break

    indent = "        "  # 2-level indent (class > method)
    wait_line = f"{indent}self.wait({seconds:.2f})"
    lines.insert(insert_idx, wait_line)
    return "\n".join(lines)


def _move_file(src: Path, dst: Path) -> None:
    """Move file from src to dst, creating parent dirs."""
    import shutil

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
