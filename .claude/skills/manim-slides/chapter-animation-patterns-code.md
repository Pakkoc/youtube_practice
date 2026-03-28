# Animation Patterns — Full Code Reference

Pattern summaries and decision flowchart → `chapter-animation-patterns.md`

---

## Pattern 1: Vector Space

```python
from manim import *

class ManimSlide(Scene):
    def construct(self):
        self.camera.background_color = "#0B0C0E"
        TEXT = ManimColor("#EDEDEF")
        ACCENT = ManimColor("#7C7FD9")
        ACCENT_B = ManimColor("#9B9EFF")
        TEAL = ManimColor("#3CB4B4")
        MUTED = ManimColor("#9394A1")

        # Title + underline (standard)
        title = Text("TITLE", font="Pretendard", font_size=46, color=TEXT, weight=ULTRABOLD)
        title.to_edge(UP, buff=0.55)
        underline = Line(LEFT * 3, RIGHT * 3, stroke_width=3)
        underline.set_color_by_gradient(ACCENT, TEAL)
        underline.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), run_time=0.7)
        self.play(Create(underline), run_time=0.5)

        # Glass card + axes (fits inside auto-injected 13.4x7.28 card)
        card = RoundedRectangle(
            width=11.5, height=4.8, corner_radius=0.25,
            fill_color=WHITE, fill_opacity=0.03,
            stroke_color=WHITE, stroke_opacity=0.06,
        )
        card.next_to(underline, DOWN, buff=0.35)
        self.play(FadeIn(card), run_time=0.3)

        axes = Axes(
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],
            x_length=11.5, y_length=4.5,
            axis_config={"color": MUTED, "stroke_width": 1,
                         "include_ticks": False, "stroke_opacity": 0.5},
        )
        axes.move_to(card).shift(DOWN * 0.1)
        self.play(FadeIn(axes), run_time=0.4)

        # Cluster: glow + arrow + dot + label per point
        points = [(1.8, 1.4, "Label A"), (2.5, 0.7, "Label B")]
        grp, lbls = VGroup(), VGroup()
        for px, py, name in points:
            glow = Circle(radius=0.18, fill_color=ACCENT_B,
                          fill_opacity=0.2, stroke_width=0)
            glow.move_to(axes.c2p(px, py))
            arr = Arrow(axes.c2p(0, 0), axes.c2p(px, py),
                        buff=0, color=ACCENT_B, stroke_width=3,
                        max_tip_length_to_length_ratio=0.1)
            dot = Dot(axes.c2p(px, py), radius=0.1, color=ACCENT_B)
            lbl = Text(name, font="Pretendard", font_size=22, color=ACCENT_B, weight=MEDIUM)
            lbl.next_to(dot, DOWN, buff=0.12)
            grp.add(VGroup(glow, arr, dot))
            lbls.add(lbl)

        # Staggered entrance: arrows + glows + dots together
        self.play(
            AnimationGroup(*[GrowArrow(g[1]) for g in grp], lag_ratio=0.15),
            AnimationGroup(*[FadeIn(g[0], scale=0.5) for g in grp], lag_ratio=0.15),
            AnimationGroup(*[FadeIn(g[2], scale=0.3) for g in grp], lag_ratio=0.15),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(*[FadeIn(lb, shift=DOWN * 0.1) for lb in lbls], lag_ratio=0.08),
            run_time=0.5,
        )

        # Angle arc between vectors (optional)
        angle = Angle(
            Line(axes.c2p(0, 0), axes.c2p(1.8, 1.4)),
            Line(axes.c2p(0, 0), axes.c2p(2.5, 0.7)),
            radius=1.4, color=ACCENT_B, stroke_width=2.5,
        )
        self.play(Create(angle), run_time=0.6)

        self.wait(0.01)  # DURATION_PLACEHOLDER
```

---

## Pattern 2: Vertical Step Flow

```python
from manim import *

class ManimSlide(Scene):
    def construct(self):
        self.camera.background_color = "#0B0C0E"
        TEXT = ManimColor("#EDEDEF")
        ACCENT = ManimColor("#7C7FD9")
        ACCENT_B = ManimColor("#9B9EFF")
        TEAL = ManimColor("#3CB4B4")
        MUTED = ManimColor("#9394A1")

        # Title + underline (standard)
        title = Text("TITLE", font="Pretendard", font_size=46, color=TEXT, weight=ULTRABOLD)
        title.to_edge(UP, buff=0.55)
        underline = Line(LEFT * 3, RIGHT * 3, stroke_width=3)
        underline.set_color_by_gradient(ACCENT, TEAL)
        underline.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), run_time=0.7)
        self.play(Create(underline), run_time=0.5)

        # Phase 1: Source element
        source = RoundedRectangle(
            width=10, height=1.2, corner_radius=0.18,
            fill_color=WHITE, fill_opacity=0.04,
            stroke_color=MUTED, stroke_width=1.5,
        )
        source.next_to(underline, DOWN, buff=0.35)
        self.play(FadeIn(source, shift=UP * 0.15), run_time=0.4)

        # Arrow + combined step label
        arr1 = Arrow(
            source.get_bottom(), source.get_bottom() + DOWN * 0.6,
            buff=0.05, color=ACCENT, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.15,
        )
        lbl1 = Text("1  Step Name", font="Pretendard",
                     font_size=22, color=ACCENT, weight=MEDIUM)
        lbl1.next_to(arr1, RIGHT, buff=0.2)
        self.play(GrowArrow(arr1), FadeIn(lbl1), run_time=0.4)

        # Phase 2: Result boxes
        boxes = VGroup()
        for color in [ACCENT, ACCENT_B, TEAL]:
            box = RoundedRectangle(
                width=3.0, height=0.8, corner_radius=0.12,
                fill_color=color, fill_opacity=0.12,
                stroke_color=color, stroke_width=1.5,
            )
            boxes.add(box)
        boxes.arrange(RIGHT, buff=0.25)
        boxes.next_to(arr1, DOWN, buff=0.15)

        self.play(
            AnimationGroup(
                *[FadeIn(b, shift=DOWN * 0.15) for b in boxes],
                lag_ratio=0.12,
            ),
            run_time=0.6,
        )

        # ReplacementTransform for pipeline progression
        # (transform source items into result items)

        # Phase 3: Final destination with glow
        arr2 = Arrow(
            boxes.get_bottom(), boxes.get_bottom() + DOWN * 0.6,
            buff=0.05, color=TEAL, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.15,
        )
        dest_card = RoundedRectangle(
            width=5, height=0.9, corner_radius=0.15,
            fill_color=TEAL, fill_opacity=0.1,
            stroke_color=TEAL, stroke_width=2,
        )
        dest_card.next_to(arr2, DOWN, buff=0.15)

        db_glow = Circle(radius=0.4, fill_color=TEAL,
                         fill_opacity=0.1, stroke_width=0)
        db_glow.move_to(dest_card)

        self.play(GrowArrow(arr2), run_time=0.4)
        self.play(FadeIn(db_glow), FadeIn(dest_card, shift=DOWN * 0.1),
                  run_time=0.5)

        self.wait(0.01)  # DURATION_PLACEHOLDER
```

---

## Pattern 3: Query Search

```python
from manim import *
import numpy as np

class ManimSlide(Scene):
    def construct(self):
        self.camera.background_color = "#0B0C0E"
        TEXT = ManimColor("#EDEDEF")
        ACCENT = ManimColor("#7C7FD9")
        ACCENT_B = ManimColor("#9B9EFF")
        TEAL = ManimColor("#3CB4B4")
        MUTED = ManimColor("#9394A1")

        # Title + underline + glass card + axes (standard setup)
        # ... (same as Vector Space pattern)

        # Stored vectors as dots with subtle glow
        stored = [(-2.5, 1.2), (-1.8, 0.6), (1.5, 1.0), (2.0, -0.3)]
        dots = VGroup()
        for sx, sy in stored:
            glow = Circle(radius=0.15, fill_color=ACCENT,
                          fill_opacity=0.1, stroke_width=0)
            glow.move_to(axes.c2p(sx, sy))
            dot = Dot(axes.c2p(sx, sy), radius=0.09,
                      color=ACCENT, fill_opacity=0.6)
            dots.add(VGroup(glow, dot))

        self.play(
            AnimationGroup(*[FadeIn(d, scale=0.5) for d in dots],
                           lag_ratio=0.04),
            run_time=0.6,
        )

        # Query vector with prominent glow
        qx, qy = 1.2, 0.7
        q_glow = Circle(radius=0.35, fill_color=TEAL,
                        fill_opacity=0.25, stroke_width=0)
        q_glow.move_to(axes.c2p(qx, qy))
        q_dot = Dot(axes.c2p(qx, qy), radius=0.14, color=TEAL)
        q_lbl = Text("Query", font="Pretendard", font_size=24, color=TEAL, weight=MEDIUM)
        q_lbl.next_to(q_dot, UP + LEFT, buff=0.12)

        self.play(
            GrowFromCenter(q_glow),
            FadeIn(q_dot, scale=0.3),
            FadeIn(q_lbl, shift=UP * 0.1),
            run_time=0.6,
        )

        # Distance lines (dashed, subtle)
        dist_lines = VGroup()
        for sx, sy in stored:
            dl = DashedLine(
                axes.c2p(qx, qy), axes.c2p(sx, sy),
                color=MUTED, stroke_width=0.8,
                stroke_opacity=0.25, dash_length=0.08,
            )
            dist_lines.add(dl)

        self.play(
            AnimationGroup(*[Create(dl) for dl in dist_lines],
                           lag_ratio=0.03),
            run_time=0.5,
        )

        # Highlight nearest (compute distances, pick top-k)
        dists = sorted(
            [(np.sqrt((sx - qx)**2 + (sy - qy)**2), i)
             for i, (sx, sy) in enumerate(stored)]
        )
        nearest = [dists[j][1] for j in range(2)]

        for idx in nearest:
            sx, sy = stored[idx]
            bl = Line(axes.c2p(qx, qy), axes.c2p(sx, sy),
                      color=ACCENT_B, stroke_width=3)
            self.play(
                dots[idx][1].animate.set_color(ACCENT_B).scale(2.0),
                dots[idx][0].animate.set_fill(color=ACCENT_B, opacity=0.3),
                Create(bl), run_time=0.35,
            )

        self.play(FadeOut(dist_lines), run_time=0.3)

        self.wait(0.01)  # DURATION_PLACEHOLDER
```

---

## Pattern 4: Dual Panel Comparison

```python
from manim import *

class ManimSlide(Scene):
    def construct(self):
        self.camera.background_color = "#0B0C0E"
        TEXT = ManimColor("#EDEDEF")
        ACCENT = ManimColor("#7C7FD9")
        ACCENT_B = ManimColor("#9B9EFF")
        TEAL = ManimColor("#3CB4B4")
        MUTED = ManimColor("#9394A1")
        DIM = ManimColor("#444455")
        RED = ManimColor("#FF6B6B")

        # Title (slightly smaller for long titles)
        title = Text("A vs B", font="Pretendard", font_size=48, color=TEXT, weight=ULTRABOLD)
        title.to_edge(UP, buff=0.65)
        underline = Line(LEFT * 3.5, RIGHT * 3.5, stroke_width=3)
        underline.set_color_by_gradient(ACCENT, TEAL)
        underline.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), run_time=0.7)
        self.play(Create(underline), run_time=0.5)

        # Center divider
        div = DashedLine(
            underline.get_center() + DOWN * 0.3,
            underline.get_center() + DOWN * 4.8,
            color=MUTED, stroke_width=1, dash_length=0.1,
            stroke_opacity=0.3,
        )
        self.play(Create(div), run_time=0.3)

        # LEFT panel (negative side)
        left_card = RoundedRectangle(
            width=6.0, height=4.5, corner_radius=0.2,
            fill_color=WHITE, fill_opacity=0.025,
            stroke_color=WHITE, stroke_opacity=0.05,
        )
        left_card.next_to(underline, DOWN, buff=0.35)
        left_card.set_x(-3.3)

        left_title = Text("Side A", font="Pretendard",
                          font_size=28, color=ACCENT_B, weight=BOLD)
        left_title.move_to(left_card.get_top() + DOWN * 0.35)
        self.play(FadeIn(left_card), FadeIn(left_title), run_time=0.3)

        # ... left panel content ...
        # Gray out / DIM color for negative outcome
        result_l = Text("Negative result", font="Pretendard",
                        font_size=18, color=RED, weight=MEDIUM)
        result_l.next_to(left_card.get_bottom(), UP, buff=0.3)
        self.play(FadeIn(result_l, shift=UP * 0.1), run_time=0.3)

        # RIGHT panel (positive side)
        right_card = RoundedRectangle(
            width=6.0, height=4.5, corner_radius=0.2,
            fill_color=WHITE, fill_opacity=0.025,
            stroke_color=WHITE, stroke_opacity=0.05,
        )
        right_card.next_to(underline, DOWN, buff=0.35)
        right_card.set_x(3.3)

        right_title = Text("Side B", font="Pretendard",
                           font_size=28, color=TEAL, weight=BOLD)
        right_title.move_to(right_card.get_top() + DOWN * 0.35)
        self.play(FadeIn(right_card), FadeIn(right_title), run_time=0.3)

        # ... right panel content (preserves color) ...
        result_r = Text("Positive result", font="Pretendard",
                        font_size=18, color=TEAL, weight=MEDIUM)
        result_r.next_to(right_card.get_bottom(), UP, buff=0.3)
        self.play(FadeIn(result_r, shift=UP * 0.1), run_time=0.3)

        self.wait(0.01)  # DURATION_PLACEHOLDER
```

---

## Pattern 5: Token Attention

```python
from manim import *

class ManimSlide(Scene):
    def construct(self):
        self.camera.background_color = "#0B0C0E"
        TEXT = ManimColor("#EDEDEF")
        ACCENT = ManimColor("#7C7FD9")
        ACCENT_B = ManimColor("#9B9EFF")
        TEAL = ManimColor("#3CB4B4")
        MUTED = ManimColor("#9394A1")

        # Title + underline + glass card (standard)
        # ...

        # Token row: fixed-width boxes with text
        token_labels = ["tok1", "tok2", "tok3", "tok4", "tok5"]
        tokens = VGroup()
        for tl in token_labels:
            box = RoundedRectangle(
                width=1.05, height=0.65, corner_radius=0.1,
                fill_color=ACCENT, fill_opacity=0.15,
                stroke_color=ACCENT, stroke_width=1.5,
            )
            txt = Text(tl, font="Pretendard", font_size=20, color=TEXT, weight=MEDIUM)
            txt.move_to(box)
            tokens.add(VGroup(box, txt))

        tokens.arrange(RIGHT, buff=0.1)
        tokens.move_to(card.get_center() + UP * 0.8)

        # Attention arcs between token pairs
        arc_pairs = [(0, 3), (1, 4), (2, 4)]
        arcs = VGroup()
        for si, ei in arc_pairs:
            arc = ArcBetweenPoints(
                tokens[si].get_bottom() + DOWN * 0.05,
                tokens[ei].get_bottom() + DOWN * 0.05,
                angle=TAU / 5,
                color=ACCENT_B, stroke_width=1.8,
                stroke_opacity=0.45,
            )
            arcs.add(arc)

        # Combined entrance: tokens + arcs + label at once
        self.play(
            AnimationGroup(
                *[FadeIn(t, shift=UP * 0.1) for t in tokens],
                lag_ratio=0.03,
            ),
            AnimationGroup(
                *[Create(a) for a in arcs],
                lag_ratio=0.05,
            ),
            run_time=1.0,
        )

        # Chunk boundaries: vertical cut lines
        cut_indices = [2]  # cut after token index 2
        cuts = VGroup()
        for ci in cut_indices:
            mid_x = (tokens[ci].get_right()[0]
                     + tokens[ci + 1].get_left()[0]) / 2
            cut = Line(
                [mid_x, tokens[0].get_top()[1] + 0.1, 0],
                [mid_x, tokens[0].get_bottom()[1] - 1.8, 0],
                color=TEAL, stroke_width=2.5,
            )
            cuts.add(cut)

        # MoveToTarget for bulk property changes
        chunk_colors = [ACCENT, TEAL]
        chunk_ranges = [(0, 3), (3, 5)]
        for (s, e), clr in zip(chunk_ranges, chunk_colors):
            for ti in range(s, e):
                tokens[ti][0].generate_target()
                tokens[ti][0].target.set_stroke(color=clr, width=2)
                tokens[ti][0].target.set_fill(opacity=0.3)

        self.play(
            AnimationGroup(*[Create(c) for c in cuts], lag_ratio=0.15),
            *[MoveToTarget(tokens[ti][0])
              for rng in chunk_ranges for ti in range(rng[0], rng[1])],
            *[a.animate.set_stroke(opacity=0.8, width=2.5) for a in arcs],
            run_time=1.0,
        )

        self.wait(0.01)  # DURATION_PLACEHOLDER
```
