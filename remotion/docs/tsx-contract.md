# TSX Contract — Unified Reference

> 슬라이드(16:9), 캐러셀(4:5), 쇼츠(9:16) 공통 + 모드별 TSX 작성 규칙.
> 각 스킬(`/generate-slides`, `/generate-carousel`, `/generate-shorts-slides`)에서 참조.
> 에이전트 dispatch 시 이 파일을 프롬프트에 포함할 것.

---

## § Common Rules (모든 모드 공통)

1. **`useFonts()`**: 컴포넌트 최상단에서 반드시 호출
2. **Korean text**: 개조식 (명사형 종결 — ~임, ~것, ~방법)
3. **Inline styles only**: No CSS modules, no Tailwind
4. **No duplicate CSS properties**: TypeScript strict mode — 같은 style 객체에서 같은 키 2번 금지
5. **No `Math.random()`**: Remotion은 deterministic 렌더링
6. **Center everything**: 모든 주요 콘텐츠 중앙 정렬 (쇼츠 크롭 안전)
7. **No cross-file imports**: 슬라이드/카드 TSX 간에 상호 import 금지 (각 파일 self-contained)
8. **SVG from library**: 아이콘은 `slide-icons.md` Icon Library에서 복사. 없으면 feather icon 패턴(viewBox 0-24, stroke-based)으로 작성
9. **No empty visual slots**: 다이어그램 노드, 아이콘 그리드 등 모든 시각 요소 슬롯은 반드시 채울 것
10. **Content fidelity**: 모든 텍스트는 대본/원문에서 직접 추출. 이름, 인용, 수치를 지어내지 말 것
11. **No `background-clip: text`**: `WebkitBackgroundClip: "text"` + `WebkitTextFillColor: "transparent"` 조합 절대 금지. Remotion headless Chromium에서 글자 마스킹/깨짐 발생. 강조 텍스트는 `color: COLORS.ACCENT_BRIGHT` + `textShadow: GLOW.text` 사용

---

## § Slides Contract (16:9 Video — 1920x1080)

### Boilerplate

```tsx
import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  spring, interpolate, Easing,
} from "remotion";
import { COLORS, FONT, LAYOUT, GLOW, STYLE } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import type { FreeformProps } from "./types";
// Import motifs as needed (see § Available Imports)

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />
      <AbsoluteFill style={{
        padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
        display: "flex", flexDirection: "column",
        justifyContent: "center", alignItems: "center",
      }}>
        {/* Content */}
      </AbsoluteFill>
      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
```

### Slides-Only Rules

1. **Export**: `export const Freeform` (파이프라인이 Freeform.tsx를 덮어씀)
2. **Props**: `FreeformProps` from `./types`
3. **AnimatedBackground**: 루트 AbsoluteFill의 **첫 번째** 자식
4. **ProgressBar + SceneFade**: 루트 AbsoluteFill의 **마지막 두** 자식
5. **No CSS transitions**: `spring()`, `interpolate()` only
6. **Subtitle reserve**: 하단 360px 비워둘 것
7. **Multi-column maxWidth**: 2+ 컬럼 레이아웃은 `maxWidth: 700`. `flex: 1`이나 `width: "100%"` 금지 (쇼츠 크롭 시 잘림)
8. **Center-align charts**: bar-chart, icon-grid 등 데이터 시각화에 `alignItems: "center"` + `justifyContent: "center"` 필수
9. **No `backdropFilter`**: `backdropFilter: "blur(...)"` 금지. Glass card는 `background: "rgba(..., 0.04~0.08)"` + `border: "1px solid rgba(..., 0.08~0.22)"` + `glassCardOpacity()`로 구현
10. **Continuous connector lines**: 타임라인/플로우 연결선은 단일 `position: absolute` 연속선 사용 (개별 행 `<div>` 선 금지)
11. **Text animation**: `scaleIn`, `bounceIn`, `zoomPop`은 텍스트 컨테이너에 금지. 텍스트는 `fadeSlideIn` 또는 `cascadeUp`만 사용. scale 계열은 아이콘/배지/SVG 전용

### Layout Zone Separation (STRICT — 레이어 겹침 방지)

타이틀과 다이어그램/플로우가 동일 수직 영역에서 겹치는 문제가 반복 발생함.

**핵심 원칙**: Boilerplate의 centered AbsoluteFill(`justifyContent: "center"`)은 콘텐츠를 수직 중앙(~480px)에 배치한다. 이 안에 타이틀을 넣으면서, 동시에 바깥에 `position: "absolute"`로 노드/다이어그램을 중앙 부근에 배치하면 텍스트가 겹친다.

**패턴별 해결책:**

1. **타이틀 + 다이어그램 (별도 영역)**: 타이틀은 centered AbsoluteFill에서 빼고 `position: "absolute"` + 명시적 `top`으로 상단 배치. 다이어그램 노드는 `cY = 560` 이하에 배치.
```tsx
// GOOD: 타이틀 상단 고정, 다이어그램 중앙~하단
<AbsoluteFill>
  <AnimatedBackground backgroundImage={backgroundImage} />
  <div style={{
    position: "absolute", left: 0, right: 0, top: LAYOUT.padding.top + 60,
    display: "flex", justifyContent: "center",
  }}>
    <h1 style={{ ... }}>타이틀 텍스트</h1>
  </div>
  {/* 다이어그램 노드들: position absolute, top: CY - NODE_H/2 */}
  <ProgressBar ... /><SceneFade />
</AbsoluteFill>

// BAD: 타이틀이 centered AbsoluteFill 안에서 중앙 배치 + 노드도 중앙
<AbsoluteFill>
  <AnimatedBackground backgroundImage={backgroundImage} />
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
    <h1>타이틀 텍스트</h1>  {/* ← 수직 중앙 ~480px */}
  </AbsoluteFill>
  <div style={{ position: "absolute", top: 435 }}>노드</div>  {/* ← 겹침! */}
</AbsoluteFill>
```

2. **모든 콘텐츠가 flex 레이아웃**: 다이어그램 없이 텍스트/카드만 있으면 centered AbsoluteFill 안에 모두 배치 (boilerplate 그대로 사용).

3. **자가 검증**: 코드 작성 후 "centered AbsoluteFill 안 요소"와 "position: absolute 요소"의 수직 좌표가 겹치지 않는지 반드시 확인.

---

### Sizing & Centering Rules (STRICT — 반복 위반 금지)

다이어그램/플로우/차트가 **작고 한쪽으로 치우치는 문제**가 반복 발생함. 아래 수치를 반드시 준수할 것.

**1. 노드/카드 최소 크기**

| 요소 | 최소 width | 최소 height | 최소 font-size | 최소 borderRadius |
|------|-----------|------------|---------------|------------------|
| 다이어그램 노드 | 240px | 80px | 32px | 16px |
| 배지/태그 | 120px | 48px | 26px | 12px |
| 아이콘 컨테이너 | 88px | 88px | — | 20px |
| 플로우 원형 노드 | 160px (diameter) | 160px | 28px | 50% |

**2. 수직 중심: `cY = 500`**
- 1920x1080 캔버스에서 시각적 중심은 `cY = 500` (상단 타이틀 + 하단 progress bar 감안)
- `cY = 420`, `cY = 430` 등 위로 치우치면 안 됨
- cycle-flow 삼각형/사각형의 중심점도 `cY = 500` 기준

**3. 수평 분포: 캔버스 70-80% 활용**
- 수평 노드 배치 시 좌우 여백 150-250px 유지 (전체 1920px 중 ~1400-1600px 사용)
- 3-4 노드 수평: `gap = 350-440px`
- 5 노드 수평: `gap = 280-340px`
- cycle-flow: `hSpan ≥ 260`, `vSpan ≥ 140`

**4. SVG 화살표 최소 크기**
- strokeWidth: 3px 이상
- 화살촉: 16px 이상 (`sz = 16`, polygon `±8`)
- `interpolate()` inputRange는 반드시 오름차순 (descending 금지)

**5. Absolute 타이틀 센터링 (STRICT — 반복 위반 금지)**

`position: "absolute"` 타이틀이 화면 중앙에 오지 않는 문제가 반복 발생함. absolute 요소에 `textAlign: "center"`만 넣으면 요소 자체는 `left: 0` + auto-width(shrink-to-fit)이므로 왼쪽 정렬된다.

```tsx
// GOOD: absolute 타이틀 — left: 0, right: 0으로 전폭 확보 후 textAlign 적용
<div style={{
  position: "absolute", top: LAYOUT.padding.top + 20,
  left: 0, right: 0,  // ← 필수! 전폭 확보
  display: "flex", justifyContent: "center",
}}>
  <h1 style={{ textAlign: "center", ... }}>타이틀</h1>
</div>

// BAD: left/right/width 없는 absolute → 왼쪽으로 치우침
<div style={{ position: "absolute", top: LAYOUT.padding.top + 20, textAlign: "center" }}>
  <h1>타이틀</h1>  {/* ← 왼쪽 정렬됨! */}
</div>
```

**6. 다이어그램 좌우 대칭 검증 (STRICT)**

수평 배치 다이어그램에서 시각적 중심점이 캔버스 중심(x=960)과 일치해야 함.

```
대칭 공식: (가장 왼쪽 요소 중심 + 가장 오른쪽 요소 중심) / 2 = 960

예: srcX=400, tgtX=1520 → 중심=(400+1520)/2=960 ✓
예: srcX=420, tgtX=1200 → 중심=(420+1200)/2=810 ✗ (150px 왼쪽 치우침)
```

Fan-out/Branch 패턴: source와 branch 그룹의 중심도 960 기준 대칭이어야 함.

**7. 자가 검증 (에이전트 필수)**
코드 작성 후 아래를 확인:
- [ ] 가장 작은 노드가 240x80px 이상인가?
- [ ] cY가 480-520 범위인가?
- [ ] 가장 왼쪽 노드 x ≥ 150, 가장 오른쪽 노드 x+nW ≤ 1770인가?
- [ ] 라벨 font-size가 32px 이상인가?
- [ ] **레이어 겹침 없음**: centered AbsoluteFill 안 요소와 position:absolute 요소가 같은 수직 영역을 차지하지 않는가?
- [ ] **Absolute 타이틀**: `position: "absolute"` 타이틀에 `left: 0, right: 0` 또는 `width: "100%"` 있는가?
- [ ] **좌우 대칭**: 수평 다이어그램의 시각 중심 = 960px인가?
- [ ] **수평 화살표 빈도**: 영상 전체에서 수평 화살표 계열이 2회를 초과하지 않는가?

**8. Layout Centering Checklist (레이아웃별 필수 검증)**

아래 3가지 레이아웃에서 정렬 오류가 반복 발생. 해당 레이아웃 사용 시 반드시 검증할 것.

| 레이아웃 | 변수 | 허용 범위 | 검증 공식 |
|---------|------|----------|----------|
| Vertical Descent | `startY` | `(1080 - totalH) / 2 ± 40` | **절대 720 사용 금지** — 반드시 1080 기준 |
| Vertical Descent | `dotX` | 660-740 | `(dotX - 8) + (contentWidth + 48) / 2 ≈ 960` |
| Balance Scale | `pivotY` | 420-460 | 팬 하단 ~ annotation 간격 ≥ 60px |
| Hub-Satellite | `hubY` | **490-520** (420-440 금지) | 모든 위성: `hubY + sin(angle)*orbitR - nH/2 ≥ 180` |
| Hub-Satellite | — | — | `hubY + orbitR ≤ 800` (하단 여유) |

> **Hub-Satellite 반복 사고**: hubY=420~440 + angle=270 위성 → 위성이 y=160~180에 배치되어 타이틀(y=100~150)과 겹침. 프로젝트 011에서 7회 발생. hubY는 반드시 490 이상으로 설정할 것.

---

## § Carousel Contract (4:5 Static — 1080x1350)

### Boilerplate

```tsx
import React from "react";
import { AbsoluteFill } from "remotion";
import { COLORS, FONT, GLOW, THEME_PRESETS } from "../design/theme";
// quiet-luxury: import { QUIET_LUXURY, QL_SHADOW, THEME_PRESETS } from "../design/theme";
import { useFonts } from "../design/fonts";
import type { FreeformCardProps } from "./types";
import { CAROUSEL_LAYOUT } from "./types";
import { PageDots } from "./CoverCard";

export const FreeformCard: React.FC<FreeformCardProps> = ({
  cardIndex, totalCards, colors, backgroundImage, themeName,
}) => {
  useFonts();

  return (
    <AbsoluteFill style={{ backgroundColor: colors.background }}>
      {backgroundImage && (
        <AbsoluteFill>
          <img src={`/${backgroundImage}`}
            style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.2 }} />
        </AbsoluteFill>
      )}
      {/* Card content */}
      <PageDots current={cardIndex} total={totalCards}
        accent={colors.accent} muted={`${colors.text}33`} />
    </AbsoluteFill>
  );
};
```

### Carousel-Only Rules

1. **Export**: `export const FreeformCard`
2. **Props**: `FreeformCardProps` from `./types`
3. **PageDots**: 루트 AbsoluteFill의 **마지막** 자식
4. **NO animation**: `useCurrentFrame`, `spring`, `interpolate`, `AnimatedBackground`, `SceneFade`, `ProgressBar`, motifs import 모두 금지
5. **Content safe area**: y=80 ~ y=1270, x=72 ~ x=1008 (하단 80px는 PageDots 영역)
6. **Canvas**: 1080x1350 (`CAROUSEL_LAYOUT.width/height`)

### Theme System

**Dark (기본):**
```
colors.background  = "#0B0C0E"   (config에서 주입)
colors.accent      = "#7C7FD9"
colors.text        = "#EDEDEF"
COLORS.TEAL        = "#3CB4B4"
COLORS.ACCENT_BRIGHT = "#9B9EFF"
COLORS.MUTED       = "#9394A1"
```

**Quiet Luxury:**
```
QUIET_LUXURY.BG            = "#FFFFFF"
QUIET_LUXURY.TEXT           = "#1A1A1A"
QUIET_LUXURY.ACCENT         = "#2C2C2C"
QUIET_LUXURY.ACCENT_WARM    = "#8B7355"   (taupe)
QUIET_LUXURY.ACCENT_COOL    = "#6B7B8D"   (slate)
QUIET_LUXURY.SURFACE        = "#F7F7F5"
QUIET_LUXURY.SURFACE_WARM   = "#F5F0EB"
QL_SHADOW.card              = "0 2px 20px rgba(0,0,0,0.06)"
```

QL Rules: 50%+ 여백, 좌측 정렬 기본, glow/glass/backdropFilter 금지, flat surface + QL_SHADOW, Weight 대비(800 vs 300), SVG strokeWidth: 1, 매 카드 2+ 변경(히어로 위치, 온도, 악센트)

### Font Sizes (Carousel)

```
Card title:    40-56px, weight 800
Section title: 28-36px, weight 700
Body text:     22-26px, weight 500
Badge/label:   16-20px, weight 600
Big number:    72-96px, weight 800
```

---

## § Shorts Contract (9:16 Video — 1080x1920)

### Boilerplate

```tsx
import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  spring, interpolate, Easing,
} from "remotion";
import { COLORS, FONT } from "../design/theme";
import { useFonts } from "../design/fonts";
import { SHORTS_CONTENT } from "../shorts/types";
import type { FreeformProps } from "./types";
// Import motifs as needed (see § Available Imports)

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  return (
    <AbsoluteFill style={{
      width: SHORTS_CONTENT.width, height: SHORTS_CONTENT.height,
      backgroundColor: "transparent",
    }}>
      <AbsoluteFill style={{
        padding: "60px 48px 200px 48px",
        display: "flex", flexDirection: "column",
        justifyContent: "center", alignItems: "center",
      }}>
        {/* Content */}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

### Shorts-Only Rules

1. **Export**: `export const Freeform`
2. **Props**: `FreeformProps` from `./types`
3. **NO AnimatedBackground / ProgressBar / SceneFade**: `ShortsSlideWrapper`가 chrome 담당
4. **Content zone**: 1080x1360 — overflow 금지
5. **Bottom padding**: 200px (자막 영역)
6. **backgroundColor**: `"transparent"` (Wrapper가 배경 제어)
7. **2-column maxWidth**: 각 컬럼 480px 이내
8. **Font limits**: 제목 ≤56px, 본문 ≤36px, 보조 ≤24px
9. **No CSS transitions**: `spring()`, `interpolate()` only

### CC Shorts (Claude Code 교육 쇼츠)

일반 Shorts 규칙에 추가로 적용되는 제약:

1. **Padding**: `"140px 48px 340px 48px"` (일반 Shorts `"60px 48px 200px 48px"`와 다름)
2. **1080x1080 중앙 배치**: 콘텐츠를 가운데 정사각형 영역에 자연스럽게 배치 (테두리 없음)
3. **Usable content**: ~984px x ~880px (padding 제외)
4. **3가지 포맷 패턴**: translator(좌우비교), flow(세로흐름도), situation(카드플립) — `cc-content/docs/cc-shorts-patterns.md` 참조
5. **포맷 패턴은 핵심 슬라이드만**: 도입/마무리는 일반 쇼츠 레이아웃 사용

```
1080x1920 전체 프레임
┌─────────────────────┐
│   Hook Title Zone    │ 0-280px
├─────────────────────┤
│   상단 여백 140px     │ 280-420px (padding-top)
│                     │
│   1080x1080 콘텐츠   │ 420-1500px ← CC Shorts 콘텐츠
│                     │
│   하단 여백 + 자막    │ 1500-1640px (padding-bottom 340px)
├─────────────────────┤
│   데드존              │ 1640-1920px
└─────────────────────┘
```

---

## § Available Imports (Slides + Shorts 전용)

캐러셀에서는 사용 금지. 슬라이드/쇼츠에서만 사용.

### ⚠ Import Quick Reference (함수 → 모듈 매핑)

**에이전트가 함수를 잘못된 모듈에서 import하는 실수가 반복됨. 아래 표를 반드시 참조.**

| 함수 | 올바른 import 경로 | ❌ 자주 틀리는 경로 |
|------|-------------------|-------------------|
| `drawBar` | `../motifs/decorations` | ~~`../motifs/emphasis`~~ |
| `drawLine` | `../motifs/decorations` | ~~`../motifs/emphasis`~~ |
| `svgStrokeDraw` | `../motifs/decorations` | ~~`../motifs/entries`~~ |
| `glassCardOpacity` | `../motifs/decorations` | ~~`../motifs/emphasis`~~ |
| `countUpProgress` | `../motifs/emphasis` | ~~`../motifs/decorations`~~ |
| `cascadeUp` | `../motifs/entries` | ~~`../motifs/emphasis`~~ |
| `getAnimationZone` | `../motifs/timing` | ~~`../motifs/entries`~~ |

**모듈별 전체 export 목록:**

| 모듈 | exports |
|------|---------|
| `entries` | fadeSlideIn, scaleIn, fadeIn, slideFromLeft, slideFromRight, slideFromBottom, bounceIn, zoomPop, cascadeUp, layeredReveal, blurReveal, wordStagger, charSplit, circleReveal, insetReveal, diagonalWipe |
| `exits` | fadeSlideOut, scaleOut, blurOut, slideOutLeft, slideOutRight, clipCircleOut |
| `emphasis` | highlighter, shiftingGradientOffset, countUpProgress, parseAnimatedNumber, formatAnimatedNumber, pulse, typewriterCount, breathe, stutterStep, penStroke, jitter, float, shimmer, orbit, colorShift, progressReveal |
| `decorations` | glassCardOpacity, **drawBar**, **drawLine**, svgStrokeDraw, radialGlow, ringScale |
| `timing` | getAnimationZone, staggerDelays, zoneDelay, getExitStart, exitStaggerDelays |
| `springConfigs` | SPRING_GENTLE, SPRING_SNAPPY, SPRING_BOUNCY, SPRING_STIFF, STAGGER_DELAY, pickSpring |
| `transitions` | sceneFadeOpacity |

---

### Entry animations — return `{ opacity: number; transform: string }`
```tsx
import { fadeSlideIn, scaleIn, fadeIn, slideFromLeft, slideFromRight,
         slideFromBottom, bounceIn, zoomPop, cascadeUp,
         layeredReveal, blurReveal } from "../motifs/entries";
// fadeSlideIn(frame, fps, delayFrames, springConfig?)
// cascadeUp(frame, fps, itemIndex, baseDelay?, stagger?, config?)
// layeredReveal(frame, fps, layer, { baseDelay?, layerGap?, itemStagger?, itemIndex?, config?, distance? })
// blurReveal(frame, fps, delay?, config?) -> { opacity, filter: "blur(Npx)", transform: "scale(N)" }
```

### Text split reveals — word/character level entrance
```tsx
import { wordStagger } from "../motifs/entries";
// wordStagger(frame, fps, wordIndex, totalWords, animZone, delay?, config?)
// -> { opacity, transform, filter }
// Word-by-word reveal: each word enters sequentially with blur+slide-up.
// Use for titles/subtitles where reading pace guides attention.

import { charSplit } from "../motifs/entries";
// charSplit(frame, fps, charIndex, totalChars, animZone, delay?, config?)
// -> { opacity, transform, filter, display:"inline-block" }
// Character scatter-assemble: each char enters from a scattered/rotated position.
// Premium feel — use sparingly on short titles (1-5 words).
```

### Clip-path reveals — cinematic mask entrance
```tsx
import { circleReveal, insetReveal, diagonalWipe } from "../motifs/entries";
// circleReveal(frame, fps, delay?, config?, origin?) -> { clipPath, opacity }
//   Expanding circle from center (spotlight effect). origin="50% 50%" default.
// insetReveal(frame, fps, delay?, config?) -> { clipPath, opacity }
//   Shrinking inset rectangle (frame-in / curtain-opening effect).
// diagonalWipe(frame, fps, delay?, config?, direction?) -> { clipPath, opacity }
//   Diagonal sweep. direction="topLeft" (default) or "topRight".
//   ⚠️ 풀스크린 컨테이너 전용. 개별 텍스트/카드/아이템에 사용 금지 (대각선이 글자를 자름).
```

### Exit animations — return `{ opacity: number; transform: string }`
```tsx
import { fadeSlideOut, scaleOut, blurOut, slideOutLeft,
         slideOutRight, clipCircleOut } from "../motifs/exits";
// fadeSlideOut(frame, fps, exitStart, durationInFrames, config?) — fade + slide-down
// scaleOut(frame, fps, exitStart, durationInFrames, config?) — shrink + fade
// blurOut(frame, fps, exitStart, durationInFrames, config?) -> { opacity, transform, filter }
//   Cinematic blur dissolve. Pairs well with blurReveal entrance.
// slideOutLeft(frame, fps, exitStart, durationInFrames, config?) — slide left + fade
// slideOutRight(frame, fps, exitStart, durationInFrames, config?) — slide right + fade
// clipCircleOut(frame, fps, exitStart, durationInFrames, config?) -> { clipPath, opacity }
//   Iris-out (circle shrinks to nothing). Pairs with circleReveal entrance.
```

### Exit timing
```tsx
import { getExitStart, exitStaggerDelays } from "../motifs/timing";
// getExitStart(durationInFrames, { fps?, exitRatio?, maxExitSeconds? }) -> frame number
// exitStaggerDelays(itemCount, exitStart, durationInFrames) -> frame[] (reverse order)
```

### Scene-level components
```tsx
import { CameraMotion } from "../design/CameraMotion";
// <CameraMotion entranceFrames={zone} maxZoom={1.025} driftX={4} driftY={3}>...children</CameraMotion>

import { CameraPan } from "../design/CameraPan";
// <CameraPan entranceFrames={zone} direction="right" distance={8}>...children</CameraPan>
//   Pure translate drift (no zoom). direction: "left"|"right"|"up"|"down".

import { CameraTilt } from "../design/CameraTilt";
// <CameraTilt entranceFrames={zone} maxRotateX={1.5} maxRotateY={2} perspective={1200}>...children</CameraTilt>
//   Subtle 3D perspective oscillation. Premium cinematic feel.

import { AmbientParticles } from "../design/AmbientParticles";
// <AmbientParticles count={6} opacity={0.08} color="rgba(124,127,217,1)" />

import { GradientShift } from "../design/GradientShift";
// <GradientShift speed={0.1} direction={135} colors={["rgba(124,127,217,0.08)", ...]} />
//   Ambient gradient cycling overlay. Place after AnimatedBackground.
```

### Emphasis — return numbers for animation progress
```tsx
import { highlighter, shiftingGradientOffset, countUpProgress,
         parseAnimatedNumber, formatAnimatedNumber,
         pulse, typewriterCount, breathe,
         stutterStep, penStroke, jitter } from "../motifs/emphasis";
// highlighter(frame, fps, delay?) -> 0-1 (scaleX)
// countUpProgress(frame, fps, durationSec?) -> 0-1
// parseAnimatedNumber("73%") -> { prefix, value, suffix, decimals, useCommas }
// formatAnimatedNumber(parsed, progress) -> "73%"
// pulse(frame, fps, base?, amp?, speed?) -> 0-0.45
// typewriterCount(frame, fps, totalChars, durSec?, delay?) -> char count
//   Usage: text.slice(0, typewriterCount(...)) for typing effect. 한글 호환 (1글자=1유닛).
//   Cursor: Math.floor(frame / Math.round(fps*0.5)) % 2 for blinking "|"
// breathe(frame, fps, startAfterFrames?, amp?, speed?) -> scale ~1.0
//   ⚠ startAfterFrames는 **프레임 수** (초 아님). 20 = 20프레임. 0.6 넣으면 즉시 시작됨
//   짧은 슬라이드(≤3초)에서는 사용 자제 — pulse() 권장
// shiftingGradientOffset(frame, loopFrames?) -> 0-360
// stutterStep(progress, steps?) -> stepped 0-1 (VOX 12fps feel)
// penStroke(frame, fps, delay?, config?) -> { progress: 0-1, wobble: px }
// jitter(frame, seed, amplitude?) -> px offset (deterministic imperfection)
// float(frame, fps, startAfter?, amplitude?, speed?) -> Y px offset (bobbing motion)
// shimmer(frame, fps, startAfter?, width?, speed?, color?) -> { background, backgroundSize, backgroundPosition }
// orbit(frame, fps, startAfter?, radius?, speed?) -> { x: number, y: number } (circular path)
// colorShift(frame, fps, delay?, durationSec?) -> 0-1 (for interpolateColors)
// progressReveal(frame, fps, delay?, durationSec?) -> 0-100 (gradient stop % for text fill)
```

### Decorations — return numbers
```tsx
import { glassCardOpacity, drawBar, drawLine, radialGlow,
         svgStrokeDraw, ringScale } from "../motifs/decorations";
// glassCardOpacity(frame, fps, durSec?) -> 0-1
// drawBar(frame, fps, delay?) -> 0-1 scaleY
// drawLine(frame, fps, delay?) -> 0-1 scaleX
// radialGlow(frame, fps, durSec?, targetOpacity?) -> 0-target
// svgStrokeDraw(frame, fps, totalLength, delay?) -> strokeDashoffset
// ringScale(frame, fps, delay?) -> 0-1
```

### Spring configs
```tsx
import { SPRING_GENTLE, SPRING_SNAPPY, SPRING_BOUNCY, SPRING_STIFF,
         STAGGER_DELAY, pickSpring } from "../motifs/springConfigs";
// SPRING_GENTLE:  { damping: 15, mass: 0.8 }
// SPRING_SNAPPY:  { damping: 20, mass: 0.6 }
// SPRING_BOUNCY:  { damping: 8,  mass: 0.6 }
// SPRING_STIFF:   { damping: 25, mass: 0.5 }
// STAGGER_DELAY = 6 frames
// pickSpring(index, preset?) -> cycling SpringConfig
```

### Transitions
```tsx
import { sceneFadeOpacity } from "../motifs/transitions";
// sceneFadeOpacity(frame, fps, durationInFrames, fadeDur?) -> 0-1
```

---

## § Design System Reference

### Colors (Slides + Shorts 공통)
```
COLORS.BG            = "#0B0C0E"
COLORS.TEXT           = "#EDEDEF"
COLORS.ACCENT         = "#7C7FD9"
COLORS.ACCENT_BRIGHT  = "#9B9EFF"
COLORS.MUTED          = "#9394A1"
COLORS.TEAL           = "#3CB4B4"
COLORS.CODE_BG        = "#1C1E21"
```

### Fonts
```
FONT.family    = "'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif"
FONT.title     = { size: 88, weight: 800, letterSpacing: "-0.04em", lineHeight: 1.1 }
FONT.bullet    = { size: 44, weight: 500, lineHeight: 1.25 }
FONT.subtitle  = { size: 36, weight: 500, lineHeight: 1.4 }
FONT.bigNumber = { size: 140, weight: 800, lineHeight: 1.0 }
FONT.context   = { size: 40, weight: 500, lineHeight: 1.4 }
```

### Layout (Slides)
```
LAYOUT.padding           = { top: 80, right: 100, bottom: 80, left: 100 }
LAYOUT.subtitleReserved  = 360
LAYOUT.bulletPaddingLeft = 50
LAYOUT.bulletDotSize     = 12
LAYOUT.bulletMarginBottom = 28
LAYOUT.card.minWidth     = 200
LAYOUT.card.descMinWidth = 240
```

### Style Presets (Korean text safe)
```
STYLE.cardLabel  = { fontSize:32, fontWeight:600, whiteSpace:"nowrap", textAlign:"center" }
STYLE.cardDesc   = { fontSize:24, fontWeight:400, wordBreak:"keep-all", textAlign:"center" }
STYLE.cardBody   = { fontSize:28, fontWeight:500, wordBreak:"keep-all" }
```

### Glow
```
GLOW.text            = "0 0 20px rgba(124,127,217,0.5), 0 0 40px rgba(124,127,217,0.2)"
GLOW.bar             = "0 0 12px rgba(124,127,217,0.6)"
GLOW.highlightBg     = "rgba(124,127,217,0.15)"
GLOW.highlightBorder = "rgba(124,127,217,0.3)"
```

---

## § Agent Dispatch Rules (공통)

### Batch Sizing

| 총 개수 | 배치 수 | 전략 |
|---------|---------|------|
| 1-6 | 1 (순차) | 에이전트 없이 직접 작성 |
| 7-12 | 2 | 2개 병렬 배치 |
| 13-18 | 3 | 3개 병렬 배치 |
| 19+ | 4 | 4개 병렬 배치 |

### Agent Prompt Template

각 배치 에이전트에 전달할 정보:
1. **전체 Slide/Card Table** (ALL 항목, 이 에이전트 담당분 표시)
2. **담당 번호** — 명시적 리스트 (예: "slides 1, 2, 3, 4, 5")
3. **Art Direction 요약** — Step 2 결과
4. **이 TSX Contract** — 해당 모드의 § 섹션 + § Common Rules
5. **패턴 레퍼런스 경로** — 에이전트가 직접 읽도록 파일 경로 전달
6. **대본/원문** — 해당 배치가 다루는 paragraph/script 내용

### Agent Rules (에이전트 프롬프트에 포함)
- Table을 정확히 따를 것. 레이아웃 재계획/변경 금지
- 각 paragraph/section 파일을 읽어 실제 텍스트 추출
- 모든 TSX/카드에 SVG 또는 structured visual 1개 이상 포함
- 슬라이드/카드 간 cross-file import 금지
- 작성 후 type check: 해당 slot 파일에 복사 → `cd remotion && npx tsc --noEmit`

**모든 배치 에이전트를 단일 메시지에서 동시 실행** (병렬성 보장).

---

## § Common TSX Issues

- Duplicate style properties (같은 객체에 `transform` 2번)
- Wrong import paths (Available Imports 목록 외 경로 사용)
- Animation in carousel (carousel은 animation 일체 금지)
- `backdropFilter: "blur"` in slides (렌더링 시 배경 깨짐)
- `WebkitBackgroundClip: "text"` + `WebkitTextFillColor: "transparent"` (글자 마스킹/깨짐 — 솔리드 컬러 + GLOW.text 사용)
- `strokeDasharray` < path perimeter (SVG stroke 애니메이션 불완전)
