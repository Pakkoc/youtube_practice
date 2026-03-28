# Shorts Layout Diagram (1080 x 1920)

> Source of truth: `remotion/src/shorts/types.ts`
> Last updated: 2026-03-17

## Full Canvas (1080 x 1920)

```
 0px ┌─────────────────────────────────────────────────┐
     │                 HOOK ZONE (480px)                │
     │              backgroundColor: #0f0f0f            │
     │                                                  │
     │  ┌──────────────────────────────────────────┐    │
     │  │  padding-left: 40    padding-right: 40   │    │
     │  │  SAFE_WIDTH = 1000px (1080 - 40*2)       │    │
     │  │                                          │    │
     │  │  ┌─ Layer 1: Category ──────────────┐    │    │
     │  │  │  "샘호트만 : AI 엔지니어의 시선"   │    │    │
     │  │  │  26px, NanumGaramYeonkkot         │    │    │
     │  │  │  RIGHT-aligned, opacity 0.55      │    │    │
     │  │  │  marginBottom: 2px                │    │    │
     │  │  └───────────────────────────────────┘    │    │
     │  │                                          │    │
     │  │  ┌─ Layer 2: Main Hook ─────────────┐    │    │
     │  │  │    "/init 자동 세팅"               │    │    │
     │  │  │    200px base → auto-scale         │    │    │
     │  │  │    Pretendard Black w900           │    │    │
     │  │  │    CENTER-aligned                  │    │    │
     │  │  │    color: accentColor (#A2FFEB)    │    │    │
     │  │  │    5-layer neon glow               │    │    │
     │  │  │    lineHeight: 0.95                │    │    │
     │  │  │    letterSpacing: -0.03em          │    │    │
     │  │  │    wordBreak: keep-all             │    │    │
     │  │  │    HEIGHT BUDGET: 346px max        │    │    │
     │  │  └───────────────────────────────────┘    │    │
     │  │                                          │    │
     │  │  ┌─ Layer 3: Sub Detail ────────────┐    │    │
     │  │  │  "(프로젝트 초기화 명령어)"       │    │    │
     │  │  │  48px, NanumGaramYeonkkot          │    │    │
     │  │  │  CENTER-aligned, opacity 0.8       │    │    │
     │  │  │  marginTop: -2px                   │    │    │
     │  │  └───────────────────────────────────┘    │    │
     │  │                                          │    │
     │  └──────────────────────────────────────────┘    │
     │                                                  │
480px ├──────────────────────────────────────────────────┤
     │░░░░░░░░░ TOP GRADIENT (80px) ░░░░░░░░░░░░░░░░░░│
     │░░░░ rgba(15,15,15,0.7) → transparent ░░░░░░░░░░│
560px │──────────────────────────────────────────────────│
     │                                                  │
     │          VIDEO / CONTENT ZONE (1280px)           │
     │          1080 x 1280, objectFit: cover           │
     │                                                  │
     │     ┌────── Video mode ──────┐                   │
     │     │  <OffthreadVideo>      │                   │
     │     │  cover crops 16:9      │                   │
     │     └────────────────────────┘                   │
     │     ┌────── Slide mode ──────┐                   │
     │     │  <ContentComponent>    │                   │
     │     │  TSX freeform slide    │                   │
     │     └────────────────────────┘                   │
     │                                                  │
     │  ╔════════════════════════════════════════════╗   │
     │  ║          SUBTITLE (at y=1400)              ║   │
     │  ║  left: 48px (safeZone)  right: 48px        ║   │
     │  ║  3-word chunks, 48px, Pretendard Bold      ║   │
     │  ║  active word: accentColor, scale 1.1       ║   │
     │  ║  inactive: #FFFFFF                         ║   │
     │  ║  textShadow for readability                ║   │
     │  ╚════════════════════════════════════════════╝   │
     │                                                  │
1680px│░░░░░░░░ BOTTOM GRADIENT (80px) ░░░░░░░░░░░░░░░░│
     │░░░░ transparent → rgba(15,15,15,0.7) ░░░░░░░░░░│
1760px├──────────────────────────────────────────────────┤
     │              DEAD ZONE (160px)                   │
     │              backgroundColor: #0f0f0f            │
1920px└──────────────────────────────────────────────────┘
```

## Layout Constants (`types.ts`)

```typescript
SHORTS_LAYOUT = {
  hookZoneHeight: 480,      // Hook zone: 0 → 480
  videoY:         480,      // Video/Content start
  videoWidth:     1080,     // Full width
  videoHeight:    1280,     // 480 → 1760
  subtitleY:      1400,     // Subtitle overlay position
  safeZone:       { left: 48, right: 48 },
}

SHORTS_CONTENT = {
  width:  1080,             // = videoWidth
  height: 1280,             // = videoHeight
  top:    480,              // = videoY
}

SHORTS_BRANDING = {
  channelName: "샘호트만 : AI 엔지니어의 시선",
}
```

## Hook Zone Height Budget (480px)

```
  480px total
  ├── Category:    26px + 2px margin  =  28px
  ├── Main Hook:   variable           ≤ 346px (HEIGHT BUDGET)
  ├── Sub Detail:  48px - 2px margin  =  46px
  └── Breathing:                      =  60px (flexbox center distributes)
```

## Font Auto-Scaling Algorithm

```
Input:  text string + baseFontSize (200px)
Output: scaled fontSize (80px ~ 200px)

1. Estimate pixel width per character:
   - Korean/CJK (U+3000~9FFF, AC00~D7AF): fontSize × 0.92
   - Space:                                 fontSize × 0.25
   - Latin/digits/symbols:                  fontSize × 0.55

2. Calculate line count:
   lines = ceil(estimatedWidth / SAFE_WIDTH)    // SAFE_WIDTH = 1000px

3. Calculate total height:
   totalHeight = lines × fontSize × LINE_HEIGHT  // LINE_HEIGHT = 0.95

4. If totalHeight > 346px → shrink by 10%, repeat
   Floor: 80px minimum
```

## Z-Order (front to back)

```
 z-index  Layer
 ───────  ──────────────────────────────
  top     HookTitle (position: absolute, top: 0)
   │      Top gradient (pointerEvents: none)
   │      Bottom gradient (pointerEvents: none)
   │      StyledSubtitle (position: absolute, top: 1400)
  bottom  Video/Content (position: absolute, top: 480)
          AbsoluteFill background (#0f0f0f)
```

## Two Composition Modes

```
┌─────────────────────────┬──────────────────────────────┐
│   ShortsComposition     │   ShortsSlideWrapper         │
│   (Video mode)          │   (Slide mode)               │
├─────────────────────────┼──────────────────────────────┤
│ OffthreadVideo          │ ContentComponent (TSX)       │
│ objectFit: cover        │ FreeformProps injected       │
│ videoSrc required       │ slideIndex / totalSlides     │
│ Used by video_to_shorts │ Used by script_to_shorts     │
└─────────────────────────┴──────────────────────────────┘

Shared layers: HookTitle + StyledSubtitle + gradients
```

## Neon Glow Effect (Main Hook)

```css
text-shadow:
  0 0 12px  {accentColor}DD,    /* inner glow — sharp */
  0 0 28px  {accentColor}66,    /* mid glow */
  0 0 56px  {accentColor}33,    /* outer glow */
  0 0 80px  {accentColor}1A,    /* far glow — faint */
  0 2px 10px rgba(0,0,0,0.95);  /* drop shadow — depth */
```
