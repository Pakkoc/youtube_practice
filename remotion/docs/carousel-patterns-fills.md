# Carousel Patterns — Fills, Backgrounds & Image Integration

> Background/decoration patterns, content fill strategies, and image integration patterns.
> Part of the carousel patterns suite — see `carousel-patterns.md` for the index.

---

## Background & Decoration Patterns

Use these to fill empty space and add visual depth. All are static — no animation imports.

### Subtle Dot Grid

Faint dot pattern for texture behind content. Place as a sibling of the content wrapper.

```tsx
{/* Dot grid background — place before content wrapper */}
<div style={{ position: "absolute", top: 120, left: 100, right: 100, bottom: 120, display: "flex", flexWrap: "wrap" as const, gap: 60, justifyContent: "center", alignContent: "center", opacity: 0.12 }}>
  {Array.from({ length: 24 }).map((_, i) => (
    <div key={i} style={{ width: 6, height: 6, borderRadius: 3, background: colors.text }} />
  ))}
</div>
```

### Corner Accent Lines

L-shaped lines at two corners for subtle framing.

```tsx
{/* Top-left corner accent */}
<div style={{ position: "absolute", top: 48, left: 48, width: 60, height: 60 }}>
  <div style={{ position: "absolute", top: 0, left: 0, width: 60, height: 2, background: `${colors.accent}40` }} />
  <div style={{ position: "absolute", top: 0, left: 0, width: 2, height: 60, background: `${colors.accent}40` }} />
</div>
{/* Bottom-right corner accent */}
<div style={{ position: "absolute", bottom: 100, right: 48, width: 60, height: 60 }}>
  <div style={{ position: "absolute", bottom: 0, right: 0, width: 60, height: 2, background: `${colors.accent}40` }} />
  <div style={{ position: "absolute", bottom: 0, right: 0, width: 2, height: 60, background: `${colors.accent}40` }} />
</div>
```

### Radial Glow (General Purpose)

Not just for covers — use behind any key content area to add depth.

```tsx
{/* Radial glow — adjust position via `at X% Y%` */}
<AbsoluteFill style={{
  background: `radial-gradient(ellipse 50% 35% at 50% 45%, ${colors.accent}25 0%, transparent 70%)`,
}} />
```

### Side Accent Bar

Thin vertical gradient line on the left edge.

```tsx
{/* Left accent bar */}
<div style={{
  position: "absolute",
  top: 120,
  left: 0,
  width: 4,
  height: 300,
  borderRadius: 2,
  background: `linear-gradient(180deg, ${colors.accent}, ${colors.accent}00)`,
}} />
```

### Floating Accent Shapes

2-3 abstract circles at low opacity for visual depth. Place behind content.

```tsx
{/* Floating accent shapes — behind content */}
<div style={{ position: "absolute", top: 180, right: 60, width: 200, height: 200, borderRadius: "50%", background: `${colors.accent}08`, filter: "blur(40px)" }} />
<div style={{ position: "absolute", bottom: 220, left: 40, width: 140, height: 140, borderRadius: "50%", background: `${COLORS.TEAL}06`, filter: "blur(30px)" }} />
```

---

## Content Fill Strategies

### Density Classification

For each card, count **substantive content items** (bullet points, data values, icon-label pairs, image blocks). Title/subtitle alone don't count.

| Items (excl. title) | Density | Strategy |
|---------------------|---------|----------|
| 1-2 | **Low — PROBLEM** | **Merge or add image** (see below) |
| 3-4 | Medium | Center layout, standard fonts, add background decoration |
| 5+ | High | Center layout, standard fonts, decorations optional |

### Low-density cards: Merge or Fill

**A sparse card with huge empty space is the #1 visual quality killer.** The 1080x1350 canvas is tall — 2-3 text items clustered at the top with 60%+ dead space below looks unfinished. Before scaling fonts or centering, use these solutions:

#### Strategy 1: Merge with adjacent card (preferred)

If two neighboring cards each have 1-2 items, combine them into one denser card.

**Examples:**
- Card A "동시 입력" (1 item) + Card B "자동 재연결" (1 item) → merged "실시간 동기화" icon-grid card (2 features side-by-side = 4 items total)
- Card C "제한사항" (3 short title-only items) → too sparse as standalone → merge as a note section into another card, or combine with CTA

**Rule: 꽉 찬 7장이 허전한 10장보다 낫다.**

#### Strategy 2: Fill with searched image

When merging isn't possible (topics too different), add a relevant image to fill 40-60% of card area.

- Use patterns J/K/L/M from § Image Integration Patterns below
- Good candidates: UI screenshots, product mockups, diagrams, stock photos
- Image occupies visual space while sparse text sits alongside or above/below

```tsx
{/* Example: sparse numbered list (2 items) + image block fills the card */}
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 32,
}}>
  {/* Title + 2 numbered items */}
  <div>...</div>
  {/* Image block fills remaining space */}
  <div style={{
    width: "100%",
    height: 400,
    borderRadius: 20,
    overflow: "hidden",
    border: "1px solid rgba(255,255,255,0.08)",
  }}>
    <Img
      src={staticFile("carousel_img_004.jpg")}
      style={{ width: "100%", height: "100%", objectFit: "cover" }}
    />
  </div>
</div>
```

#### Strategy 3: Scale up (last resort)

Only when merge is impossible AND no relevant image exists:

- Center content vertically (`justifyContent: "center"`)
- Scale fonts 1.5x from baseline (title 56-64px, body 32-36px)
- Add a background decoration (radial glow, dot grid, or floating shapes)
- Example: a single quote, a big stat + context, a CTA

### Medium density (3-4 items)
- Use centered vertical layout with standard font sizes
- Add at least one background decoration for visual depth
- Example: title + 3 bullet points, icon grid with 4 items

### High density (5+ items)
- Use centered vertical layout with standard font sizes
- Background decorations optional (content already fills the space)
- Example: numbered list with 6 items, comparison with many points

**Always apply:** centered vertical wrapper + no `flex: 1` + no `gridTemplateRows: "1fr"`.

---

## Image Integration Patterns

Cards can include searched/downloaded images from `remotion/public/`. These files are copied there before rendering.

### J. Background Image (Full Card)

Subtle background behind all content. Good for covers, stats, quotes.

**IMPORTANT:** Use `Img` + `staticFile()` from remotion (not `<img src="/...">`). Add to import: `import { AbsoluteFill, Img, staticFile } from "remotion";`

```tsx
{/* Background image — 10-15% opacity, behind content */}
<AbsoluteFill style={{ overflow: "hidden" }}>
  <Img
    src={staticFile("img_001.jpg")}
    style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.12, filter: "saturate(0.5)" }}
  />
</AbsoluteFill>
```

### J-AI. AI-Generated Cinematic Background

AI(NanoBanana/Gemini)로 생성한 시네마틱 배경 이미지. `backgroundImage` prop으로 전달되며, 다크 그라디언트 오버레이로 텍스트 가독성 확보.

**사용 시점**: Cover, CTA, Quote, 저밀도 카드 (3-5장/캐러셀). copy_deck.md에 `image_prompt`가 있는 카드만 적용.

**렌더링 파이프라인이 `backgroundImage` prop을 자동 주입**하므로, TSX에서는 prop을 받아 처리하면 됨.

```tsx
// import에 Img, staticFile 필수
import { AbsoluteFill, Img, staticFile } from "remotion";

// props에서 backgroundImage 받기
const { cardIndex, totalCards, colors, backgroundImage } = props;

// 배경 레이어 (AbsoluteFill의 첫 번째 자식으로)
{backgroundImage && (
  <AbsoluteFill style={{ overflow: "hidden" }}>
    <Img
      src={staticFile(backgroundImage)}
      style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.15, filter: "saturate(0.6)" }}
    />
  </AbsoluteFill>
)}
{/* 다크 그라디언트 오버레이 — 하단 텍스트 가독성 확보 */}
{backgroundImage && (
  <AbsoluteFill style={{
    background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.5) 50%, transparent 100%)",
  }} />
)}
```

**적용 기준 (copy_deck.md에서 `image_prompt` 부여)**:

| 카드 유형 | 배경 이미지 | 이유 |
|-----------|------------|------|
| Cover | 항상 | 첫인상, 스크롤 멈춤 |
| CTA (마지막) | 항상 | 행동 유도 임팩트 |
| Quote / 감정 카드 | 강력 추천 | 분위기 강화 |
| 저밀도 (1-2 아이템) | 추천 | 빈 공간 해결 |
| 고밀도 (5+ 아이템) | 절대 안됨 | 가독성 방해 |
| 차트/데이터 | 안됨 | 시각적 간섭 |

### K. Rounded Image Block

Product photo, screenshot, or scene. Place within the content area.

```tsx
{/* Rounded image block — use within content wrapper */}
<div style={{
  width: "100%",
  height: 340,
  borderRadius: 20,
  overflow: "hidden",
  border: "1px solid rgba(255,255,255,0.08)",
}}>
  <Img
    src={staticFile("img_013.jpg")}
    style={{ width: "100%", height: "100%", objectFit: "cover" }}
  />
</div>
```

### L. Circular Image

Avatar-style or product close-up. Centered or side-placed.

```tsx
{/* Circular image */}
<div style={{
  width: 200,
  height: 200,
  borderRadius: "50%",
  overflow: "hidden",
  border: `3px solid ${colors.accent}30`,
  flexShrink: 0,
}}>
  <Img
    src={staticFile("img_010.jpg")}
    style={{ width: "100%", height: "100%", objectFit: "cover" }}
  />
</div>
```

### M. Image with Gradient Overlay

Image with a gradient fade for text overlay on top.

```tsx
{/* Image with bottom gradient */}
<div style={{ position: "relative", width: "100%", height: 400, borderRadius: 20, overflow: "hidden" }}>
  <Img
    src={staticFile("img_005.jpg")}
    style={{ width: "100%", height: "100%", objectFit: "cover" }}
  />
  <div style={{
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: "60%",
    background: `linear-gradient(transparent, ${colors.background})`,
  }} />
  <div style={{
    position: "absolute",
    bottom: 24,
    left: 24,
    right: 24,
    fontSize: 24,
    fontWeight: 700,
    fontFamily: FONT.family,
    color: colors.text,
  }}>
    Caption text over image
  </div>
</div>
```

### Image File Naming

- Location: `remotion/public/` (copied before rendering, cleaned after)
- Naming: `carousel_img_NNN.jpg` (NNN = card number)
- Source: downloaded via `search_images_serperdev()` + `_resize_image_to_4_5()`
- **Not all cards need images** — select 3-5 cards where images add real value

### When to Use Images

| Card Type | Image Style | Example |
|-----------|------------|---------|
| Cover | J. Background 15% | 주제 관련 분위기 사진 |
| Stats/Numbers | J. Background 15% | 업무/비즈니스 배경 |
| Case Study | K. Rounded Block | 제품 사진, 결과물 스크린샷 |
| Quote | J. Background 10% | 관련 인물/장면 |
| Before/After | K. Rounded Block | 비교 대상 사진 |
| CTA | M. Gradient Overlay | 행동 유도 관련 이미지 |
