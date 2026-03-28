# Slide Patterns Reference

> Index file. Sub-documents contain copy-paste ready code.
> This file is read by Claude Code during `/generate-slides` Step 4 (Write TSX).

## Anti-pattern: 표면 명사 시각화

대본에 등장하는 명사(문서, 영상, 앱 등)를 곧바로 목업/아이콘으로 그리면 **맥락이 빠진 껍데기**가 됩니다.

| 대본 의도 | 잘못된 시각화 | 올바른 시각화 |
|-----------|-------------|-------------|
| "영상을 만든 **계기**" (동기 서술) | 영상 파일 목업 | 3단계 여정 흐름 (경험→강의→제작) |
| "A가 B보다 **좋은 이유**" (비교) | A 로고 단독 표시 | A vs B 비교 레이아웃 |
| "X란 **무엇인가**" (정의) | X 스크린샷 | 개념 도해 (아이콘+설명) |

**원칙**: 문단의 화행(동기? 비교? 정의? 감정?)을 먼저 파악하고, 그에 맞는 레이아웃을 선택할 것.

## Quick Reference

| Need | File | Section |
|------|------|---------|
| SVG 아이콘 복사 | [slide-icons.md](slide-icons.md) | Icon Library (28 icons) |
| 레이아웃 인덱스 | [slide-layouts.md](slide-layouts.md) | 4개 서브파일 라우팅 (아래 참고) |
| 차트/타임라인/스텝 | [slide-layouts-diagrams.md](slide-layouts-diagrams.md) | Circle Flow, Bar Chart, Timeline, Step Indicator |
| UI 목업 (채팅/앱) | [slide-layouts-mockups.md](slide-layouts-mockups.md) | Document Frame, Chat Mockup, Service Mockup, Side-by-Side Compare, Warning Callout, Badge/Pill |
| 시각 은유 (피플/저울) | [slide-layouts-metaphors.md](slide-layouts-metaphors.md) | People Row, Balance Scale, Arrow Flow, Icon Grid (3x2) |
| 보조/쇼츠 | [slide-layouts-extras.md](slide-layouts-extras.md) | Progress Bar, Icon+Text Grid (1x4), SVG Stroke Draw, Shorts-Safe variants |
| **모션 강화** | [slide-patterns-motion.md](slide-patterns-motion.md) | WordStagger, CharSplit, ClipReveal(3종), Exit(6종), CameraMotion, AmbientParticles, BlurReveal, Spring Decision Guide |
| **타이포그래피** | [typography-patterns.md](typography-patterns.md) | Word Carousel, Text Highlight, Typewriter Text |
| **예제 뱅크** | [slide-examples.md](slide-examples.md) | 10개 complete TSX 예제 (content type별 few-shot) |
| **고급 스니펫** | [slide-snippets-advanced.md](slide-snippets-advanced.md) | 카운터, 타이핑, 와이프, 헥사곤, 비대칭 구도, 라인차트, 전환 변형 |
| 모션 패턴 | 이 파일 | VOX-Style Motion Patterns |
| 공유 헬퍼 | 이 파일 | Shared Helper Pattern |

---

## Anti-pattern: 수평 화살표 플로우 반복 (ㅁ→ㅁ→ㅁ wall)

**가장 빈번한 위반.** "A가 B를 거쳐 C가 된다" 형태의 대본이 나오면 자동으로 수평 박스 3개 + SVG 화살표 조합을 꺼내는 경향이 있다. 이 패턴이 영상 전체에서 2회를 초과하면 시각적 단조로움이 극심해진다.

**빈도 상한**: 영상 전체에서 Arrow Flow (수평 박스+화살표) 계열 **최대 2회**. Circle+Line Flow, Labeled Arrow Flow, Branch Flow의 수평 화살표 변형 모두 합산.

| 대본 의도 | ❌ 매번 하는 것 | ✅ 대체 시각화 |
|-----------|---------------|--------------|
| "A → B → C" 인과/순서 | 수평 3-box + SVG 화살표 | **Numbered Card Row**, Vertical Descent, Staircase Progress |
| "입력 → 처리 → 출력" | Circle + Line Flow | **Funnel/Pyramid**, Layered Cards, Transform Split |
| "단계별 진행" | Step-flow boxes | **Step Indicator**, Numbered Card Row, Vertical Descent |
| "분기/팬아웃" | Fan-out 화살표 | **Annotated Hub**, Icon Grid, Radial layout |
| "순환/반복" | 4-box rectangular cycle | Cycle Flow (기존, 적정), **Concentric layout** |

**핵심 원칙**: 순서/인과를 전달할 때 반드시 화살표가 필요한 것이 아니다. **번호**(01→02→03), **수직 위치**(위→아래), **크기 변화**(큰→작은), **색상 그라데이션**, **계단식 배치**만으로도 순서를 충분히 전달할 수 있다. 화살표는 명시적 방향성이 핵심인 경우(데이터 파이프라인, 아키텍처 다이어그램)에만 사용할 것.

---

## Anti-pattern: Centered AbsoluteFill + position:absolute 겹침

Centered AbsoluteFill(`justifyContent: "center"`)은 콘텐츠를 수직 중앙(~480px)에 배치한다. 이 안에 타이틀을 넣으면서 동시에 바깥에 `position: "absolute"`로 노드/다이어그램을 중앙 부근에 배치하면 텍스트가 겹친다.

타이틀 + 다이어그램 패턴에서는 타이틀도 `position: "absolute"` + 명시적 `top`으로 상단에 고정하고, centered AbsoluteFill을 사용하지 않는다.

---

## Anti-pattern: svgStrokeDraw arrow tip (inputRange crash)

`svgStrokeDraw` returns `offset` that goes from `len` (hidden) → `0` (fully drawn).
When calculating arrow tip opacity, **NEVER** use descending inputRange:

```tsx
// BAD — crashes: "inputRange must be strictly monotonically increasing"
const tipOp = interpolate(offset, [len * 0.15, 0], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

// GOOD — ascending inputRange, reversed outputRange
const tipOp = interpolate(offset, [0, len * 0.15], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
```

Logic: offset=0 means fully drawn → tip visible (1). offset≥len*0.15 → tip hidden (0).

---

## Common Patterns

### Accent word (solid color + glow)
```tsx
// ⚠ WebkitBackgroundClip:"text" + WebkitTextFillColor:"transparent" 절대 금지
// Remotion headless Chromium에서 글자 마스킹/깨짐 발생 (background-clip:text 렌더링 버그)
// 대신 솔리드 컬러 + textShadow glow 조합 사용
<span style={{
  color: COLORS.ACCENT_BRIGHT,
  textShadow: GLOW.text,
  fontWeight: 800,
}}>{word}</span>
```

### Animated underline
```tsx
const lineP = spring({ frame: frame - 6, fps, config: { damping: 20, mass: 0.6 } });
<div style={{
  height: 3,
  background: `linear-gradient(90deg, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
  boxShadow: GLOW.bar,
  transformOrigin: "center",
  transform: `scaleX(${lineP})`,
  width: "60%", margin: "16px auto 0", borderRadius: 2,
}} />
```

### Glass card
```tsx
// NOTE: NEVER use backdropFilter: "blur(...)". It blurs the background/animations behind the card.
// Glass effect = semi-transparent bg + subtle border + glassCardOpacity() only.
const cardOp = glassCardOpacity(frame, fps, 0.6);
<div style={{
  background: `rgba(255,255,255,0.04)`,
  border: `1px solid rgba(255,255,255,${0.06 * cardOp})`,
  borderRadius: 16, padding: "40px 48px",
  opacity: cardOp,
}} />
```

### Staggered items
```tsx
{items.map((item, i) => {
  const d = 10 + i * STAGGER_DELAY;
  const a = fadeSlideIn(frame, fps, d, SPRING_SNAPPY);
  return <div key={i} style={{ ...a }}>{item}</div>;
})}
```

### Korean-safe card (icon + label + description)
```tsx
import { STYLE, LAYOUT } from "../design/theme";

// Card with minWidth — prevents Korean text mid-word break
<div style={{ minWidth: LAYOUT.card.minWidth, textAlign: "center" }}>
  {/* icon */}
  <span style={{ ...STYLE.cardLabel, color: COLORS.ACCENT }}>라벨 텍스트</span>
  <span style={{ ...STYLE.cardDesc }}>부연 설명 텍스트</span>
</div>
```

### Count-up number
```tsx
const parsed = parseAnimatedNumber("73%");
const p = countUpProgress(frame, fps, 1.2);
const display = formatAnimatedNumber(parsed, p);
```

---

## Duration-Proportional Timing

All entrance animations must scale with slide duration. **Hardcoded frame delays are forbidden** in Freeform TSX.

`getAnimationZone` uses an **adaptive ratio**: short slides (≤5s) use 100% of duration for animations, long slides (≥10s) use 50%, with linear interpolation in between.

### Import

```tsx
import { getAnimationZone, staggerDelays, zoneDelay } from "../motifs/timing";
```

### Usage

```tsx
const { fps, durationInFrames } = useVideoConfig();
const zone = getAnimationZone(durationInFrames);

// Single element at 30% of entrance zone
const subtitleDelay = zoneDelay(0.3, zone);
const subtitleAnim = fadeSlideIn(frame, fps, subtitleDelay);

// List of N items spread across zone
const delays = staggerDelays(items.length, zone, { offset: Math.round(zone * 0.2) });
items.map((item, i) => {
  const anim = fadeSlideIn(frame, fps, delays[i]);
  // ...
});
```

### Rules

1. Call `getAnimationZone(durationInFrames)` once per component
2. Use `zoneDelay(position, zone)` for single elements (position 0-1)
3. Use `staggerDelays(count, zone, options)` for lists
4. Never use literal frame numbers (e.g., `delay: 10`, `frame - 6`)
5. Micro-timing offsets within a single element (e.g., marker highlight +6 after parent) remain as small fixed offsets relative to the parent delay

---

## VOX-Style Motion Patterns

These patterns use the VOX-inspired motifs (`stutterStep`, `penStroke`, `jitter`, `layeredReveal`, `pickSpring`) to create organic, editorial motion.

### Progressive Disclosure (점진적 공개)

Use `layeredReveal` for 3-layer information hierarchy: title -> main visual -> details.

```tsx
import { layeredReveal } from "../motifs/entries";

// Layer 0: Title (appears immediately)
const titleAnim = layeredReveal(frame, fps, 0);

// Layer 1: Main visual (appears 400ms later -- reading time)
const visualAnim = layeredReveal(frame, fps, 1);

// Layer 2: Detail items (800ms later, staggered within layer)
{details.map((item, i) => {
  const a = layeredReveal(frame, fps, 2, { itemIndex: i });
  return <div key={i} style={{ ...a }}>{item}</div>;
})}
```

### Stutter Effect (스터터 / 12fps 느낌)

Wrap any spring with `stutterStep` for stop-motion editorial feel.

```tsx
import { stutterStep } from "../motifs/emphasis";

const raw = spring({ frame: frame - 6, fps, config: SPRING_SNAPPY });
const stepped = stutterStep(raw, 8); // 8 discrete steps
// Use stepped for opacity, translateY, scaleX, etc.
<div style={{ opacity: stepped, transform: `translateY(${(1 - stepped) * 30}px)` }}>
  ...
</div>
```

### Pen Highlighter (펜 하이라이터)

Replace `highlighter()` with `penStroke()` for hand-drawn feel.

```tsx
import { penStroke } from "../motifs/emphasis";

const pen = penStroke(frame, fps, 10); // delay 10 frames
<div style={{
  position: "absolute",
  left: 0, right: 0, bottom: 2,
  height: 12,
  background: `${COLORS.ACCENT}30`,
  borderRadius: 4,
  transformOrigin: "left center",
  transform: `scaleX(${pen.progress}) translateY(${pen.wobble}px)`,
}} />
```

### Intentional Imperfection (의도적 불완전)

Add `jitter` to bullet dots, icons, or card positions for organic feel.

```tsx
import { jitter } from "../motifs/emphasis";

{items.map((item, i) => (
  <div key={i} style={{
    transform: `translate(${jitter(frame, i, 0.8)}px, ${jitter(frame, i + 100, 0.6)}px)`,
  }}>
    {/* Bullet dot or icon */}
  </div>
))}
```

### Spring Variety (스프링 다양성)

Use `pickSpring` so adjacent items get different spring configs automatically.

```tsx
import { pickSpring } from "../motifs/springConfigs";

{items.map((item, i) => {
  const config = pickSpring(i); // cycles: gentle -> snappy -> bouncy -> stiff
  const anim = fadeSlideIn(frame, fps, 8 + i * 6, config);
  return <div key={i} style={{ ...anim }}>{item}</div>;
})}
```

### Text Animation Rule

텍스트 컨테이너에 `scaleIn`, `bounceIn`, `zoomPop` 등 scale 계열 애니메이션을 사용하면 scale(0.5→1.0) 과정에서 텍스트 줄바꿈이 변경되어 시각적 불쾌감(text reflow)이 발생합니다.

- **텍스트 (통째로)**: `fadeSlideIn` 또는 `cascadeUp`만 사용 (opacity + translateY)
- **텍스트 (단어별 등장)**: `wordStagger` — 각 단어를 `display: "inline-block"`으로 감싸서 순차 reveal
- **텍스트 (글자별 등장)**: `charSplit` — 짧은 제목(1-5단어)에만 사용. 각 글자가 흩어진 상태에서 조합
- **콘텐츠 블록 reveal**: `circleReveal`, `insetReveal` — 카드/섹션 전체를 clip-path로 reveal
- **전체 화면 전환 전용**: `diagonalWipe` — **풀스크린 컨테이너에만** 사용. 개별 텍스트, 카드, 아이콘에 적용 금지 (대각선이 글자/요소를 잘라서 부자연스러움)
- **아이콘/배지/SVG**: `scaleIn`, `bounceIn`, `zoomPop` 사용 가능

```tsx
// GOOD: 텍스트에 fadeSlideIn
const titleAnim = fadeSlideIn(frame, fps, 0, SPRING_GENTLE);
<h1 style={{ ...titleAnim }}>제목 텍스트</h1>

// GOOD: 단어별 순차 등장 (wordStagger)
const words = title.split(" ");
{words.map((word, i) => {
  const a = wordStagger(frame, fps, i, words.length, zone, 0, SPRING_SNAPPY);
  return <span key={i} style={{ display: "inline-block", marginRight: 8, ...a }}>{word}</span>;
})}

// GOOD: 카드를 clip-path로 reveal
const clip = circleReveal(frame, fps, 0, SPRING_GENTLE);
<div style={{ ...clip }}>{cardContent}</div>

// GOOD: 아이콘에 scaleIn
const iconAnim = scaleIn(frame, fps, 6);
<div style={{ width: 64, height: 64, ...iconAnim }}>{svgIcon}</div>

// BAD: 텍스트에 scaleIn → reflow 발생
const titleAnim = scaleIn(frame, fps, 0);
<h1 style={{ ...titleAnim }}>긴 제목 텍스트가 줄바꿈됨</h1>
```

---

## Shared Helper Pattern

When 3+ slides share the same visual element, define a helper function at the top of each file:

```tsx
// -- Reusable helpers (copy to each slide that uses them) --

const SectionBadge: React.FC<{
  number: string; label: string; frame: number; fps: number;
}> = ({ number, label, frame, fps }) => {
  const anim = fadeSlideIn(frame, fps, 4, SPRING_STIFF);
  return (
    <div style={{
      position: "absolute",
      top: LAYOUT.padding.top,
      left: LAYOUT.padding.left,
      display: "flex", alignItems: "center", gap: 8,
      ...anim,
    }}>
      <div style={{
        background: COLORS.ACCENT, color: "#fff",
        fontSize: 18, fontWeight: 800, fontFamily: FONT.family,
        width: 32, height: 32, borderRadius: 8,
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>{number}</div>
      <span style={{
        color: COLORS.MUTED, fontSize: 20, fontFamily: FONT.family,
        fontWeight: 600, textTransform: "uppercase" as const,
        letterSpacing: "0.08em",
      }}>{label}</span>
    </div>
  );
};

const IconLabel: React.FC<{
  icon: React.ReactNode; label: string; frame: number; fps: number; delay: number;
}> = ({ icon, label, frame, fps, delay }) => {
  const a = cascadeUp(frame, fps, 0, delay, STAGGER_DELAY, SPRING_BOUNCY);
  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center", gap: 12, ...a,
    }}>
      <div style={{
        width: 64, height: 64, borderRadius: 16,
        background: GLOW.highlightBg, border: `1px solid ${GLOW.highlightBorder}`,
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>{icon}</div>
      <span style={{
        color: COLORS.TEXT, fontSize: 24, fontFamily: FONT.family, fontWeight: 600,
      }}>{label}</span>
    </div>
  );
};
```
