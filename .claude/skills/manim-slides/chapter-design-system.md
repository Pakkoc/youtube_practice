# Design System

Visual tokens that must match the Remotion design system. All values are extracted from production slides (project 007: 030, 050, 051, 095, 096).

## Color Palette

```python
# Required — every slide uses these 5
TEXT    = ManimColor("#EDEDEF")   # primary text, titles
ACCENT  = ManimColor("#7C7FD9")  # primary accent (purple)
ACCENT_B = ManimColor("#9B9EFF") # bright accent (light purple)
TEAL    = ManimColor("#3CB4B4")  # secondary accent (teal)
MUTED   = ManimColor("#9394A1")  # labels, axes, de-emphasized

# Optional — use sparingly for specific semantics
DIM     = ManimColor("#444455")  # grayed-out / disabled elements
RED     = ManimColor("#FF6B6B")  # negative / warning / "bad" side
```

Always define colors at the top of `construct()`. Never use raw hex strings inline.

## Typography Scale

| Role | font_size | weight | Usage |
|------|-----------|--------|-------|
| Title | 44–50 | `ULTRABOLD` (800) | Main slide title (`to_edge(UP, buff=0.55)`) |
| Section label | 24–26 | `BOLD` (700) | Panel headings, cluster labels, panel titles |
| Body / label | 20–22 | `MEDIUM` (500) | Descriptions, angle labels, context labels |
| Detail | 15–18 | `MEDIUM` (500) | Step labels, chunk labels, small annotations |
| Number emphasis | 64–88 | `ULTRABOLD` (800) | BigNumber equivalent |

Always: `font="Pretendard"`, always specify `weight`. Math only: `MathTex`.

**Pango weight constants** (all exported from `from manim import *`):
- `NORMAL` = 400, `MEDIUM` = 500, `SEMIBOLD` = 600
- `BOLD` = 700, `ULTRABOLD` = 800, `HEAVY` = 900

## Glass Card Recipe

Background container for main content area:

```python
card = RoundedRectangle(
    width=11.5, height=4.5,     # adjust to content (fits inside auto-injected card 13.4x7.28)
    corner_radius=0.25,
    fill_color=WHITE, fill_opacity=0.03,
    stroke_color=WHITE, stroke_opacity=0.06,
)
card.next_to(underline, DOWN, buff=0.3)
```

For smaller panels (dual panel layout):
```python
panel = RoundedRectangle(
    width=6.0, height=4.5, corner_radius=0.2,
    fill_color=WHITE, fill_opacity=0.025,
    stroke_color=WHITE, stroke_opacity=0.05,
)
```

## Glow Effect Recipe

Soft circle behind important elements (dots, boxes, cards):

```python
# Behind a dot/point (small glow)
glow = Circle(
    radius=0.15–0.35,
    fill_color=ACCENT_B,     # match element color
    fill_opacity=0.15–0.25,  # MINIMUM 0.15 for visibility
    stroke_width=0,
)
glow.move_to(element)
```

**Key rule**: `fill_opacity >= 0.15` for visible fills. Values like 0.08 are invisible on dark backgrounds.

## Gradient Underline Recipe

Signature element below every title:

```python
underline = Line(LEFT * 3.5, RIGHT * 3.5, stroke_width=3)
underline.set_color_by_gradient(ACCENT, TEAL)
underline.next_to(title, DOWN, buff=0.15)
```

## Fill Opacity Guidelines

| Element | fill_opacity | Notes |
|---------|-------------|-------|
| Glass card background | 0.03 | Nearly invisible, just structure |
| Glass card stroke | 0.06 (stroke_opacity) | Subtle border |
| Glow circle | 0.15–0.25 | Must be visible |
| Token/chunk box fill | 0.12–0.25 | Colored but not solid |
| Highlighted state | 0.3–0.65 | After animation emphasis |
| DB/result box | 0.08–0.12 | Subtle colored container |

## Spacing Constants

| Spacing | Value | Usage |
|---------|-------|-------|
| Title to top edge | `buff=0.5–0.55` | `title.to_edge(UP, buff=0.55)` |
| Title to underline | `buff=0.15` | `underline.next_to(title, DOWN, buff=0.15)` |
| Underline to content | `buff=0.3–0.35` | `card.next_to(underline, DOWN, buff=0.35)` |
| Between card sections | `buff=0.25–0.35` | Vertical spacing inside cards |
| Arrow to next element | `buff=0.15` | `next_element.next_to(arrow, DOWN, buff=0.15)` |
| Label to element | `buff=0.08–0.12` | `label.next_to(element, DOWN, buff=0.12)` |

## Font Weight Mapping (Manim ↔ Remotion)

| Remotion (CSS) | weight value | Manim constant | Pretendard file |
|----------------|-------------|----------------|-----------------|
| ExtraBold (title) | 800 | `ULTRABOLD` | Pretendard-ExtraBold |
| Bold | 700 | `BOLD` | Pretendard-Bold |
| SemiBold | 600 | `SEMIBOLD` | Pretendard-SemiBold |
| Medium (body) | 500 | `"MEDIUM"` | Pretendard-Medium |
| Regular | 400 | `NORMAL` | Pretendard-Regular |

## Auto-Injected Frame (manim_backend.py)

`manim_backend.py` automatically injects Remotion-style frame elements at render time. **Slide code should NOT create its own outer frame or background rectangle.**

Injected layers (in order):
1. **Gradient background**: full-frame rectangle, `#0A2332` (top) → `#1E0F3C` (bottom)
2. **Dark content card**: `13.4 × 7.28` Manim units, `#0B0C0E`, corner_radius `0.15`, subtle white border
3. **B-roll image** (if available): constrained to card dimensions, **10% opacity** (matches Remotion `0.1`)
4. **Progress bar** (if slide_index provided): 3px track at **screen bottom** (full frame width), `#7C7FD9→#3CB4B4` gradient fill

Content zone is the card interior: **13.4 wide × 7.28 tall**. All user content renders ON TOP of these frame elements via DOM/add order.

## Remotion ↔ Manim Mapping

Remotion `theme.ts` values and their Manim equivalents:

| Remotion (CSS px @ 1920x1080) | Manim equivalent | Notes |
|-------------------------------|------------------|-------|
| FONT.title.size = 76px, weight 800 | font_size=48, ULTRABOLD | 1 Manim unit ≈ 135px |
| FONT.bullet.size = 36px, weight 500 | font_size=28-30, MEDIUM | |
| FONT.subtitle.size = 28px, weight 500 | font_size=22, MEDIUM | |
| FONT.bigNumber.size = 120px, weight 800 | font_size=80, ULTRABOLD | |
| FONT.context.size = 32px, weight 500 | font_size=24-26, MEDIUM | |
| LAYOUT.padding.top = 100px | `buff=1.10` from card top | `to_edge(UP, buff=0.55)` = 74px from frame top |
| LAYOUT.padding.left/right = 120px | ~0.89 units → content max width ≈ 11.5 | |
| CARD_MARGIN = {48, 56, 48, 56} | Auto-injected card (13.4 × 7.28) | |
| B-roll opacity = 0.1 | `_bg.set_opacity(0.1)` | |
| ProgressBar bottom: 0 (full width) | `to_edge(DOWN, buff=0)` | Screen bottom, not card bottom |

## Content Zone

Upper 2/3 of frame for content. Bottom 1/3 reserved for subtitles. In practice:
- Title at `buff=0.55` from top
- Content card height: 4.5–5.2
- Nothing below `card.get_bottom()` except key messages near bottom edge
