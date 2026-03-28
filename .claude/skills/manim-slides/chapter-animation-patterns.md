# Animation Patterns

5 production-proven patterns from project 007. Each includes a decision trigger and key techniques.

## Decision Flowchart

```
Content type?
├─ Coordinate/scatter data, vector similarity  → Pattern 1: Vector Space (030)
├─ Sequential steps, pipeline, transformation  → Pattern 2: Vertical Flow (050)
├─ Search, nearest neighbor, retrieval         → Pattern 3: Query Search (051)
├─ Side-by-side comparison, A vs B             → Pattern 4: Dual Panel (095)
└─ Token/sequence processing, attention        → Pattern 5: Token Attention (096)
```

---

## Pattern 1: Vector Space

**When**: Coordinate data, vector similarity, clustering, embedding visualization.
**Source**: 030.py (2D vector space with clusters and cosine angles)

**Key techniques:**
- Axes inside glass card: `x_range=[-4,4], y_range=[-2.5,2.5], x_length=11.5, y_length=4.5`
- Glow + Arrow + Dot triplet per data point with color coding (ACCENT_B)
- Cosine similarity angle: `Angle(Line(...), Line(...))` between two vectors
- Staggered animation: `AnimationGroup(*[GrowArrow(g[1]) for g in grp], lag_ratio=0.15)`
- Cluster labels at semantic positions (not centered)

→ Full code: `chapter-animation-patterns-code.md` § Pattern 1

---

## Pattern 2: Vertical Step Flow

**When**: Sequential steps, pipeline stages, data transformation process.
**Source**: 050.py (RAG pipeline: document → chunk → embed → store)

**Key techniques:**
- Vertical top-to-bottom flow: source → arrow → transform → arrow → destination
- Combined step labels: `"1  Step Name"` next to arrows (not separate)
- `ReplacementTransform` for showing data transformation between stages
- Color-coded stages: ACCENT → ACCENT_B → TEAL for progression
- Destination glow: `Circle(radius=0.4, fill_opacity=0.1)` behind final card

→ Full code: `chapter-animation-patterns-code.md` § Pattern 2

---

## Pattern 3: Query Search

**When**: Search, retrieval, nearest neighbor, embedding lookup.
**Source**: 051.py (RAG search: query vector → distance lines → nearest highlight → LLM)

**Key techniques:**
- `DashedLine` for distance visualization (subtle `stroke_opacity=0.25`, `dash_length=0.08`)
- `GrowFromCenter` for query vector dramatic entrance with prominent glow
- `np.sqrt` for distance computation (only `numpy` is allowed as extra import)
- Sequential highlight loop: enlarge dot + brighten glow + solid connection line
- `FadeOut(dist_lines)` cleanup after highlight

→ Full code: `chapter-animation-patterns-code.md` § Pattern 3

---

## Pattern 4: Dual Panel Comparison

**When**: Side-by-side comparison, A vs B, before/after.
**Source**: 095.py (일반 RAG vs Late Chunking)

**Key techniques:**
- `DashedLine` center divider (`stroke_opacity=0.3`)
- `set_x(-3.3)` / `set_x(3.3)` for symmetric panel positioning
- Contrasting animation: left side grays out (`.set_fill(color=DIM, opacity=0.15)`), right side preserves color
- Panel title at `card.get_top() + DOWN * 0.35`
- Optional extra colors: `DIM` for disabled, `RED` for negative

→ Full code: `chapter-animation-patterns-code.md` § Pattern 4

---

## Pattern 5: Token Attention

**When**: Token/sequence processing, attention mechanism, chunking with context.
**Source**: 096.py (token row + attention arcs + chunk boundaries + MoveToTarget)

**Key techniques:**
- Fixed-width token boxes (`width=1.05`) for uniform row
- `ArcBetweenPoints` with `angle=TAU/5` for attention arcs
- Chunk boundary: compute `mid_x` between adjacent tokens for vertical cut lines
- `generate_target()` + `MoveToTarget()` for bulk recoloring without recreating objects
- Combined animation: cuts + recoloring + arc emphasis in single `play()` call

→ Full code: `chapter-animation-patterns-code.md` § Pattern 5
