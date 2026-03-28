# Carousel Patterns Reference

> This file is read by Claude Code during `/generate-carousel` Step 4 (Write TSX).
> All patterns are copy-paste ready. **No animation** — these are static still images.

## Related Files (선택적 로드)

**필요한 파일만 읽을 것** — Card Table의 Layout 컬럼을 보고 해당 패턴이 포함된 파일만 로드.

| File | When to Read | Contents |
|------|-------------|----------|
| `carousel-patterns-layouts.md` | Layout A-I 사용 시 (거의 항상) | Base patterns A-I + Common Elements (663줄) |
| `carousel-patterns-layouts-extended.md` | Layout J-W 사용 시 | Extended patterns J-W (1040줄) |
| `carousel-patterns-ql.md` | Theme = quiet-luxury | QL 테마 전용 패턴 (815줄) |
| `carousel-patterns-fills.md` | 배경 장식/이미지 패턴 필요 시 | Background, Decoration, Fill Strategies (321줄) |
| `carousel-patterns-icons.md` | SVG 아이콘 필요 시 | Inline SVG Icon Library (117줄) |

---

## Layout Pattern Index (23종)

카드 테이블 작성 후 이 인덱스를 보고 필요한 파일만 선택적으로 로드.

### Base Patterns A-I → `carousel-patterns-layouts.md`

| ID | Name | Best For |
|----|------|----------|
| A | Cover Card | 첫 장. 중앙 타이틀 + radial glow |
| B | Icon Grid (2x2/1x3) | 기능 소개, 장점 나열 |
| C | Numbered List | 단계별 설명, 순서가 있는 항목 |
| D | Split Top/Bottom | 큰 숫자/비주얼 + 설명 |
| E | Quote Card | 인용문, 핵심 메시지 강조 |
| F | Bar Chart | 수치 비교, 성과 시각화 |
| G | Donut Chart | 비율, 구성 비교 |
| H | Before/After | 전후 비교, 변화 시각화 |
| I | CTA Ending | 마지막 장. 행동 촉구 + 핸들 |

### Extended Patterns J-W → `carousel-patterns-layouts-extended.md`

| ID | Name | Best For |
|----|------|----------|
| J | Stat Dashboard | KPI 그리드, 핵심 지표 |
| K | Progress Tracker | 로드맵, 완료율 |
| L | Ranking List | Top-N 순위 |
| M | Code Snippet | 개발자 튜토리얼, API 예시 |
| N | Terminal Output | CLI 데모, 설치 가이드 |
| O | Feature Matrix | 기능 비교표 (체크/X) |
| P | Pros & Cons | 장단점 이중 패널 |
| Q | Big Number | 단일 임팩트 수치 강조 |
| R | Highlight Box | 핵심 포인트 강조 박스 |
| S | Testimonial | 후기, 추천사 |
| T | Timeline | 시간순 이벤트 |
| U | Split Image+Text | 풀블리드 이미지 + 텍스트 |
| V | Accordion/FAQ | Q&A, FAQ |
| W | Chapter Divider | 섹션 구분 |

### Quiet Luxury Patterns QL-A~F → `carousel-patterns-ql.md`

다크 A-I의 화이트 테마 변형. Theme=quiet-luxury일 때만 로드.

---

## Canvas & Layout

- **Canvas**: 1080 x 1350 (4:5 ratio, Instagram carousel)
- **Padding**: top 80, right 72, bottom 80, left 72
- **Content width**: 936px (1080 - 72*2)
- **Bottom 80px**: Reserved for PageDots (do NOT place content below y=1270)
- **Safe area**: y=80 to y=1270, x=72 to x=1008

```
┌──────────────────────────┐  1080
│     padding-top: 80      │
│  ┌──────────────────┐    │
│  │                  │    │  ← content area (936 x 1190)
│  │   Card Content   │    │
│  │                  │    │
│  └──────────────────┘    │
│     ● ● ━━ ● ●          │  ← PageDots (bottom: 40)
│     padding-bottom: 80   │
└──────────────────────────┘  1350
```

---

## Vertical Space Management

Cards must look **visually dense and centered**, never top-heavy with empty bottom space.

### Rule 1: Content wrapper must center vertically

Use `position: absolute` with inset padding and `justifyContent: "center"` for all card content.

```tsx
// DO — centered content wrapper (standard pattern for every card)
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 32,
}}>
  {/* Card content */}
</div>

// DON'T — top-positioned absolute div (content clusters at top, empty bottom)
<div style={{
  position: "absolute",
  top: 200,
  left: 72,
  right: 72,
}}>
  {/* Content hangs from top, leaving dead space below */}
</div>
```

### Rule 2: NEVER use `flex: 1` on content containers

`flex: 1` forces a child to expand and fill remaining space, creating unwanted gaps.

```tsx
// BAD — flex: 1 expands panel beyond content needs
<div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
  <span>Short text</span>  {/* → huge gap below */}
</div>

// GOOD — let content determine its own height
<div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
  <span>Short text</span>  {/* → no wasted space */}
</div>
```

### Rule 3: Grid uses `auto` rows, not `1fr`

`gridTemplateRows: "1fr 1fr 1fr"` forces equal row heights regardless of content.

```tsx
// BAD — equal rows stretch to fill container
<div style={{ display: "grid", gridTemplateRows: "1fr 1fr 1fr", gap: 20 }}>

// GOOD — rows size to their content (just omit gridTemplateRows)
<div style={{ display: "grid", gap: 20 }}>
```

### Rule 4: Content-light cards scale up typography

If a card has only 2-3 text elements, increase font sizes 1.5x from baseline:

| Element | Normal size | Content-light size |
|---------|------------|-------------------|
| Title | 40-48px | 56-64px |
| Body text | 22-26px | 32-36px |
| Label/badge | 16-20px | 24-28px |

---

## Component Boilerplate

Every card TSX file MUST follow this structure:

```tsx
import React from "react";
import { AbsoluteFill } from "remotion";
import { COLORS, FONT, GLOW } from "../design/theme";
import { useFonts } from "../design/fonts";
import type { FreeformCardProps } from "./types";
import { CAROUSEL_LAYOUT } from "./types";
import { PageDots } from "./CoverCard";

export const FreeformCard: React.FC<FreeformCardProps> = ({
  cardIndex,
  totalCards,
  colors,
  backgroundImage,
}) => {
  useFonts();

  return (
    <AbsoluteFill style={{ backgroundColor: colors.background }}>
      {/* Background image (optional) */}
      {backgroundImage && (
        <AbsoluteFill>
          <img
            src={`/${backgroundImage}`}
            style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.2 }}
          />
        </AbsoluteFill>
      )}

      {/* Content wrapper — vertically centered */}
      <div style={{
        position: "absolute",
        top: 80, left: 72, right: 72, bottom: 80,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: 32,
      }}>
        {/* === Card content here === */}
      </div>

      {/* PageDots — ALWAYS last child */}
      <PageDots
        current={cardIndex}
        total={totalCards}
        accent={colors.accent}
        muted={`${colors.text}33`}
      />
    </AbsoluteFill>
  );
};
```

### Rules

1. **Component name**: Always `FreeformCard` (file is overwritten per card)
2. **`useFonts()`**: Must call at top of component
3. **`PageDots`**: Must be the last child of root `AbsoluteFill`
4. **No animation**: No `useCurrentFrame`, `spring`, `interpolate`, `AnimatedBackground`, `SceneFade`, `ProgressBar`, motifs
5. **Inline styles only**: No CSS modules, no external stylesheets
6. **Korean text**: Use concise bullet-style (개조식), not full sentences
7. **Colors**: Use `colors.background`, `colors.accent`, `colors.text` from props. Use `COLORS.*` for secondary tones

---

## Font Size Guide (Carousel)

| Element | Size | Weight |
|---------|------|--------|
| Card title | 40-56px | 800 |
| Section title | 28-36px | 700 |
| Body text | 22-26px | 500 |
| Badge / label | 16-20px | 600 |
| Big number | 72-96px | 800 |
| Caption / muted | 18-20px | 400 |
| CTA button | 22px | 700 |

---

## Prohibited (Static Cards Only)

These are for animated video slides and must NOT be used in carousel cards:

- `useCurrentFrame()`, `useVideoConfig()`
- `spring()`, `interpolate()`
- `AnimatedBackground`, `SceneFade`, `ProgressBar`
- Any import from `../motifs/`
- Any import from `../design/animations`
- CSS `transition`, `animation`, `@keyframes`
- `Sequence`, `Series` from remotion

---

## Quiet Luxury Theme

> **Quiet Luxury 패턴은 별도 파일로 분리되었습니다:**
> `remotion/docs/carousel-patterns-ql.md`
>
> QL 테마 캐러셀 생성 시 해당 파일을 추가로 참조하세요.
