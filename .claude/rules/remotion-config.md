---
paths:
  - "remotion/**/*.{ts,tsx}"
  - "features/generate_slides/**/*.py"
---

# Remotion & Slides Configuration

## Slides (Freeform TSX + Manim CE)

- **Freeform TSX** (default): Claude Code writes TSX directly using `slide-generation` skill (long-form: `chapter-longform-tsx.md`, shorts: `chapter-shorts-tsx.md`)
- **Manim CE**: Claude Code decides mode for math/algorithm content in `slide-generation` skill (`chapter-longform-tsx.md`)
- Pattern: `remotion/docs/slide-patterns.md` + `slide-layouts-*.md`

## B-roll Backends

- `flux2_klein` -- FLUX.2 Klein 4B (local GPU)
- `nanobanana` -- Gemini image gen/edit (API)
- `flux_kontext` -- Flux Kontext + LoRA (img2img, requires reference image)

## Config (Profile System)

`shared/config/schema.py` (`AppConfig`) -> `config/config.{profile}.yaml`. Access: `app/config.py:get_config()`.

- **Default profile: `base`** -> loads `config.base.yaml` (NOT `config.yaml`!)
- `CONFIG_PROFILE`: `base` | `api` | `asmr` | `shorts`
- Load order: profile YAML -> `_apply_env_overrides()` -> `apply_pipeline_overrides()`
