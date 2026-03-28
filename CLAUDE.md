# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI video automation system -- generates YouTube videos end-to-end from a script (`script.txt`). Covers slide generation, TTS synthesis, and subtitle compositing.

**API-Only mode**: cloud APIs only, no GPU required (ElevenLabs TTS, Remotion slides). B-roll and avatar are disabled.

## Model & API Versions

**WARNING: All API calls use OpenAI GPT-5 family. Never put Claude models in code!**

- **Use**: `gpt-5`, `gpt-5.4-mini`, `gpt-5.1` (high-quality tasks)
- **Never use**: Claude models or deprecated models (`gpt-4.1`, `gpt-4-turbo`, `gpt-5-mini`, `gpt-5-nano`)

**GPT-5 API spec** (`shared/api/claude.py` -> `ask()`):
- **Chat Completions API** (`client.chat.completions.create()`)
- Use **`max_completion_tokens`** (`max_tokens` returns 400 error on GPT-5)
- **Never pass `temperature`** -- not supported by GPT-5 family

## Working Style

- **Scope control**: If asked about 1 item, answer only that. Do not explain all related items.
- **"Let's discuss"** = conversation only, no code. **"Implement it"** = write code immediately.
- **E2E auto-proceed**: "make video", "make shorts" etc. -- proceed mechanically through sub-steps without asking. Only ask when context is ambiguous.

## Verification

Before declaring a feature complete:

1. **Self-review**: Re-check changed files (missing return, type safety, no stubs)
2. **Lint & Type check**: `ruff check .` + `npx tsc --noEmit` (TSX). **Lint before every commit.**
3. **Test**: Run relevant `pytest`, fix failures
4. **FSD imports**: Run `lint-imports` on multi-file changes
5. **"Check it", "Test it" = actual runtime test.** Never declare done with static analysis only.

## Architecture -- Feature-Sliced Design (FSD)

```
app/        -> CLI entry, config singleton, provider DI
pipelines/  -> workflow orchestration
features/   -> individual capabilities (generate_tts, generate_slides, burn_subtitles, ...)
entities/   -> Pydantic domain models (Project, Script, Slide, AudioClip, Video, ...)
shared/     -> utilities, API clients, ffmpeg wrapper, config schema
```

**Import rule:** Upper -> Lower only. `import-linter` enforces: `app` -> `pipelines` -> `features` -> `entities` -> `shared`.

**Remotion rendering layer** (`remotion/src/`):
```
slides/    -> 16:9 longform video slides (Freeform TSX)
shorts/    -> 9:16 shorts slides + HookTitle + StyledSubtitle
carousel/  -> Instagram carousel cards
design/    -> shared design tokens, themes, fonts, animations
motifs/    -> reusable motion patterns (snippet library)
```

## Commands

**Requires:** Python >= 3.13. Env vars: copy `.env.example` -> `.env`.

```bash
# Install
uv sync                            # base deps
uv sync --extra dev                # ruff, mypy, pytest, import-linter
cd remotion && npm install && cd .. # Remotion rendering deps

# Pipelines (default profile = api, no CONFIG_PROFILE needed)
uv run video-automation pipeline script-to-video --input script.txt --project my-video
uv run video-automation pipeline script-to-shorts --input script.txt --project my-shorts
uv run video-automation pipeline video-to-shorts --project my-shorts
uv run video-automation pipeline script-to-carousel --input script.txt --project my-carousel
uv run video-automation pipeline add-subtitles --input video.mp4 --project my-video

# Quality
ruff check . && ruff format .
mypy app shared entities
lint-imports
pytest
```

## Skill Dispatch Guide

| Command | Purpose |
|---------|---------|
| `/generate-video <project>` | E2E: script -> final_video.mp4 (16:9) |
| `/generate-shorts <project>` | All shorts (script/CC/external video auto-detect) |
| `/carousel-copywriting <project>` | Carousel copy design + self-evaluation |
| `/generate-carousel <project>` | Carousel card TSX + visual review |
| `/generate-script <project>` | All scripts (longform/shorts/CC auto-detect) |

### User request -> Command mapping

| User request | Command |
|-------------|---------|
| "make video", "E2E", "run pipeline" | `/generate-video` |
| "make shorts" (any type) | `/generate-shorts` |
| "carousel copy/text planning" | `/carousel-copywriting` |
| "make carousel" | `/generate-carousel` |
| "make script" | `/generate-script` |

## Workshop Notes

- **Default profile is `api`** -- no need to prefix commands with `CONFIG_PROFILE=api`.
- **B-roll and avatar are disabled** in this workshop build.
- **Required API keys**: `OPENAI_API_KEY`, `ELEVENLABS_API_KEY` (in `.env`)

## Knowledge Management

- **Rules**: `.claude/rules/` -- domain-specific rules (pipeline, rendering)
- **Skills**: `.claude/commands/` -- verified repeatable procedures
