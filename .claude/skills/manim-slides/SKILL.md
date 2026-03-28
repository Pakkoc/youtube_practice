---
name: manim-slides
description: "Pattern library for Manim CE slide generation — design tokens, 5 copy-paste animation patterns, duration-aware design, and anti-patterns. Load when writing or reviewing Manim slides via /generate-slides."
user-invocable: false
---

# Manim Slides Pattern Library

## Activation Conditions
- **Keywords**: manim, ManimSlide, manim slide, `.py` slide, manim pattern
- **Intent Patterns**: "manim 슬라이드 작성", "manim 패턴", "Manim 디자인"
- **Working Files**: `projects/*/slides/*.py`, `features/generate_slides/manim_backend.py`
- **Content Patterns**: `class ManimSlide`, `ManimColor`, `self.camera.background_color`

## Chapters
1. [Design System](chapter-design-system.md) — Color palette, typography scale, glass card/glow recipes, spacing constants
2. [Animation Patterns](chapter-animation-patterns.md) — 5 copy-paste patterns (Vector Space, Vertical Flow, Query Search, Dual Panel, Token Attention) with decision flowchart
3. [Practical Guide](chapter-practical-guide.md) — Duration-aware design, label placement, animation combining, anti-patterns, security rules

## Relationship to Other Docs
- **Manim Scene Contract** (`.claude/commands/generate-slides.md` § Manim Scene Contract): structural rules — class name, font, colors, content zone. This skill complements (not duplicates) those rules.
- **LLM prompt** (`prompts/manim_scene_generation.txt`): prompt for GPT-5-mini pipeline. Different audience (LLM vs Claude Code agent).
- **Alignment memory** (`memory/manim-alignment.md`): historical context on v2→v3 alignment fixes.
- **Agent dispatch**: `/generate-slides` command now tells agents to read `chapter-animation-patterns.md` and `chapter-design-system.md` directly.
