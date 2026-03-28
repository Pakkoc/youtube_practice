# Practical Guide

Hard-won lessons from 3 iterations of project 007 Manim slides.

## Duration-Aware Design

The 2-pass renderer (`manim_backend.py`) adjusts `self.wait()` at the end to match TTS audio duration. Your animations consume time from the total budget.

**Rule**: Short paragraphs (<6 seconds) = max 3 combined animation groups.

| Duration | Max play() calls | Strategy |
|----------|-------------------|----------|
| <6s | 3–4 | Merge related animations with `AnimationGroup` |
| 6–10s | 5–7 | Standard pacing, `run_time=0.5–0.8` each |
| 10–15s | 7–10 | Can afford sequential reveals |
| >15s | 10+ | Rare; add detail or slow `run_time` |

**Combining animations** to save time:

```python
# BAD: 3 separate play() calls = 3 * 0.5s = 1.5s consumed
self.play(FadeIn(card), run_time=0.5)
self.play(FadeIn(label), run_time=0.5)
self.play(FadeIn(icon), run_time=0.5)

# GOOD: 1 play() call = 0.5s consumed
self.play(FadeIn(card), FadeIn(label), FadeIn(icon), run_time=0.5)
```

## Animation Combining Techniques

### AnimationGroup for staggered entrance

```python
self.play(
    AnimationGroup(
        *[FadeIn(item, shift=DOWN * 0.15) for item in items],
        lag_ratio=0.12,
    ),
    run_time=0.6,
)
```

### Spreading list comprehensions in play()

```python
# Multiple related animations in one call
self.play(
    *[GrowArrow(g[1]) for g in group],
    *[FadeIn(g[0], scale=0.5) for g in group],
    run_time=1.0,
)
```

### MoveToTarget for bulk property changes

When you need to change colors/opacity/size of many existing objects at once:

```python
# Set up targets
for token in tokens:
    token.generate_target()
    token.target.set_stroke(color=NEW_COLOR, width=2)
    token.target.set_fill(opacity=0.3)

# Apply all at once
self.play(*[MoveToTarget(t) for t in tokens], run_time=0.8)
```

### ReplacementTransform for data flow

```python
# Show data transforming from one form to another
self.play(
    *[ReplacementTransform(source[i], dest[i]) for i in range(n)],
    run_time=0.7,
)
```

## Label Placement Rules

### Labels INSIDE boxes

```python
# GOOD: label inside the box
lbl = Text("Label", font="Pretendard", font_size=20, color=TEXT)
lbl.move_to(box)

# BAD: label outside with tiny buff (overlaps on dense layouts)
lbl.next_to(box, DOWN, buff=0.05)
```

### Combined step labels next to arrows

```python
# GOOD: step number + description as one text, next to arrow
lbl = Text("1  Step Name", font="Pretendard", font_size=22, color=ACCENT)
lbl.next_to(arrow, RIGHT, buff=0.2)

# BAD: separate step number and description
num = Text("1", font="Pretendard", font_size=22)
desc = Text("Step Name", font="Pretendard", font_size=22)
num.next_to(arrow, LEFT)  # clutters layout
```

### Cluster/category labels at semantic positions

```python
# GOOD: label near the cluster it describes
tag = Text("Category", font="Pretendard", font_size=26, color=ACCENT_B)
tag.move_to(axes.c2p(2.5, 2.2))  # near the cluster

# BAD: label centered or at edge
tag.to_edge(RIGHT)  # disconnected from data
```

## Anti-Patterns (NEVER Do These)

### 1. SurroundingRectangle in loop

```python
# BAD: each rectangle adapts to text width → inconsistent widths
for item in items:
    rect = SurroundingRectangle(item)  # different width each time

# GOOD: fixed-width RoundedRectangle
ROW_W = 11.0
for item in items:
    bg = RoundedRectangle(width=ROW_W, height=1.3, corner_radius=0.15)
    item.move_to(bg)
```

### 2. arrange(RIGHT) without fixed-width container

```python
# BAD: row width depends on text length
row = VGroup(number, text).arrange(RIGHT, buff=0.3)

# GOOD: fixed-width background, position elements explicitly
bg = RoundedRectangle(width=ROW_W, height=1.3, corner_radius=0.15)
number.move_to(bg.get_left() + RIGHT * 1.0)
text.move_to(bg.get_center() + RIGHT * 0.8)
```

### 3. move_to(card.get_center()) without top anchor

```python
# BAD: content floats to vertical center of card
content.move_to(card.get_center())

# GOOD: anchor to top, flow downward
content.next_to(underline, DOWN, buff=0.55)
card.move_to(content)  # card wraps content, not the other way
```

### 4. arrange(CENTER)

```python
# BAD: CENTER is NOT a valid direction for arrange()
group.arrange(CENTER)

# GOOD: use ORIGIN or move_to()
group.arrange(ORIGIN)
# or
group.move_to(target_position)
```

### 5. next_to(off_center_label, DOWN) for wide rows

```python
# BAD: rows inherit x=-3.5 from label → left side clips off screen
label.set_x(-3.5)
rows.next_to(label, DOWN, buff=0.2)  # rows centered at x=-3.5!

# GOOD: position rows below label, then force center
rows.next_to(label, DOWN, buff=0.2)
rows.set_x(0)  # reset to horizontal center

# ALSO GOOD: position label and rows independently
label.next_to(underline, DOWN, buff=0.35)
rows.next_to(label, DOWN, buff=0.2)
rows.set_x(0)
```

**Rule**: After `next_to()`, always verify the group's x-center is near 0. Wide groups (ROW_W > 6) must be explicitly centered with `.set_x(0)`.

## Security Rules

Only allowed imports:

```python
from manim import *       # always required
import numpy as np         # only when needed for math
```

**NEVER** import: `os`, `subprocess`, `pathlib`, `shutil`, `sys`
**NEVER** use: `open()`, `eval()`, `exec()`, `__import__()`

## Ruff / Lint Exclusions

`projects/*/slides/*.py` files are exempt from these ruff rules (configured in `pyproject.toml`):
- `F403` / `F405`: wildcard imports (`from manim import *`)
- `N806`: uppercase variable names (`TEXT`, `ACCENT`, etc.)
- `E741`: ambiguous variable names

No need to add `# noqa` comments to slide files.

## Checklist Before Submitting a Manim Slide

1. Class name is `ManimSlide(Scene)`
2. Background is `#0B0C0E`
3. All 5 base colors defined at top
4. All `Text()` uses `font="Pretendard"`
5. Title at `to_edge(UP, buff=0.55)` with gradient underline
6. Ends with `self.wait(0.01)  # DURATION_PLACEHOLDER`
7. Content in upper 2/3 (bottom 1/3 = subtitle zone)
8. No forbidden imports
9. Animation count fits duration budget
10. No anti-patterns (SurroundingRectangle in loop, arrange(CENTER), etc.)
11. Wide groups (ROW_W > 6) centered with `.set_x(0)` after positioning
