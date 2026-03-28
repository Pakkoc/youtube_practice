---
paths: "cc-content/**"
---

# CC Shorts Content Pipeline

Educational Claude Code shorts for non-developers. Card DB -> script -> render.

**Two tracks:** Evergreen (`cc-001`~`cc-035`) | Auto-Update (release detection)

**3 script formats:** Translator | Flow diagram | Situation card

**CC-specific commands:** `/generate-script cc-002` (CC auto-detect) | `/generate-shorts cc-002` (CC auto-detect) | `/detect-releases`

**Workflow:**
```bash
/generate-script cc-002             # Step 1: CC auto-detect -> script generation
uv run video-automation pipeline script-to-shorts ...  # Step 2: Scene split + TTS
/generate-shorts cc-002             # Step 3: CC auto-detect -> Hook titles + TSX
uv run video-automation pipeline script-to-shorts ...  # Step 4: Render
```
