# Motion Enhancement Patterns

> Text split reveals, clip-path reveals, exit animations, camera motion, ambient particles, blur reveal.
> All optional — use selectively for variety. NOT every slide needs all of these.

---

## When to use which

| Enhancement | Best for | Skip when |
|-------------|----------|-----------|
| **Word stagger** | Title/subtitle reveals, reading-paced buildup | List items (too many words), data-heavy slides |
| **Char split** | Short dramatic titles (1-5 words), opening/closing slides | Long text, Korean multi-byte (too many chars) |
| **Circle reveal** | Glass cards, hero content, spotlight moments | Multi-column layouts (clip cuts off columns) |
| **Inset reveal** | Full-slide content reveal, section transitions | Individual list items (too heavy per-item) |
| **Diagonal wipe** | Editorial transitions, bullet groups, comparison cards | Precision layouts with alignment needs |
| **Exit animation** | Dramatic endings, section transitions, climax slides | Short slides (<3s), information-dense slides |
| **CameraMotion** | Hold-heavy slides (big number, quote, hero title) | Diagram/chart slides (zoom distorts precision layouts) |
| **CameraPan** | Directional narrative, flow/movement slides | Static comparisons, precision charts |
| **CameraTilt** | Premium hero titles, opening/closing slides | Data-heavy slides, multi-card grids |
| **AmbientParticles** | Emotional/atmospheric slides (opening, closing, dramatic) | Data-heavy slides (particles distract from numbers/charts) |
| **GradientShift** | Emotional backgrounds, intro/outro, storytelling | Data slides, precision layouts |
| **BlurReveal** | Single hero element (title, big number, key quote) | Multi-element slides (blur on list items feels slow) |
| **float** | Icons, badges, decorative elements (bobbing feel) | Precision-aligned layouts |
| **shimmer** | Cards/panels premium sheen | Transparent background elements |
| **orbit** | Decorative dots/rings around central element | Text containers |
| **colorShift** | Keyword emphasis, state transitions | Multiple simultaneous color changes |
| **progressReveal** | Reading-pace guide, long text karaoke fill | Short titles (too fast) |

**Pacing rule**: Use at most 2-3 enhancements per slide. Don't apply all at once — subtlety is the goal.

---

## Word Stagger (word-by-word reveal)

Title/subtitle text appears word by word, guiding the viewer's reading pace.
Each word fades + slides up with a slight blur clear. The viewer's eye naturally follows the reveal order.

```tsx
import { wordStagger } from "../motifs/entries";
import { getAnimationZone } from "../motifs/timing";

const title = "AI가 만드는 영상의 미래";
const words = title.split(" ");  // or split("") for Korean char-by-char
const zone = getAnimationZone(durationInFrames);

<div>
  {words.map((word, i) => {
    const anim = wordStagger(frame, fps, i, words.length, zone, 0, SPRING_SNAPPY);
    return (
      <span key={i} style={{
        display: "inline-block",
        marginRight: 8,
        ...anim,
      }}>
        {word}
      </span>
    );
  })}
</div>
```

**Korean text**: For character-by-character reveal, use `title.split("")` instead of `split(" ")`.
**Combine with exit**: `opacity: anim.opacity * exitAnim.opacity`.
**Subtitle stagger**: Add `delay` parameter (e.g., `Math.round(zone * 0.4)`) for subtitle words to start after title.

---

## Char Split (scatter-assemble title)

Characters enter from scattered/rotated positions and assemble into the final word.
Premium movie-intro feel — use on short, impactful titles only.

```tsx
import { charSplit } from "../motifs/entries";

const title = "MOTION";
const chars = title.split("");
const zone = getAnimationZone(durationInFrames);

<div>
  {chars.map((char, i) => {
    const anim = charSplit(frame, fps, i, chars.length, zone, 0, SPRING_GENTLE);
    return (
      <span key={i} style={{
        ...anim,
        fontSize: 140,
        fontWeight: 900,
      }}>
        {char}
      </span>
    );
  })}
</div>
```

**Limit**: Best for 1-8 characters. Longer text → use wordStagger instead.

---

## Clip-Path Reveals (cinematic mask entrance)

Content revealed by animating CSS `clipPath`. The most impactful visual upgrade for minimal code.

### Circle Reveal (spotlight)

```tsx
import { circleReveal } from "../motifs/entries";

const clip = circleReveal(frame, fps, 0, SPRING_GENTLE);
// clip = { clipPath: "circle(N% at 50% 50%)", opacity: number }

<div style={{ ...clip }}>
  {/* Entire card/content block revealed as circle expands */}
</div>
```

Custom origin: `circleReveal(frame, fps, 0, SPRING_GENTLE, "30% 40%")` — spotlight from top-left.

### Inset Reveal (frame-in)

```tsx
import { insetReveal } from "../motifs/entries";

const clip = insetReveal(frame, fps, 0, SPRING_SNAPPY);
// clip = { clipPath: "inset(N% round Npx)", opacity: 1 }

<div style={{ ...clip }}>
  {/* Content appears as frame closes in from edges */}
</div>
```

### Diagonal Wipe

> **사용 제한**: 풀스크린 컨테이너(AbsoluteFill 직속 래퍼)에만 사용.
> 개별 텍스트, 카드, 리스트 아이템에 적용하면 대각선이 글자/아이콘을 잘라서 부자연스러움.
> 텍스트/카드 블록 reveal에는 `insetReveal` 또는 `fadeSlideIn`을 사용할 것.

```tsx
import { diagonalWipe } from "../motifs/entries";

const clip = diagonalWipe(frame, fps, 0, SPRING_GENTLE, "topLeft");
// direction: "topLeft" or "topRight"

// GOOD: 풀스크린 섹션 전환
<AbsoluteFill style={{ ...clip }}>
  {/* Full-screen content swept in diagonally */}
</AbsoluteFill>

// BAD: 개별 카드/텍스트에 적용 — 대각선이 글자를 자름
// <div style={{ ...clip }}><h1>제목</h1></div>  ← 금지
```

---

## Exit Animation (per-element)

Elements gracefully leave before SceneFade. More polished than abrupt black cut.

### 6 exit types (choose by slide mood)

| Exit | Feel | Best for |
|------|------|----------|
| `fadeSlideOut` | Gentle fade + slide down | Default, information slides |
| `scaleOut` | Shrink + fade | Titles, hero elements |
| `blurOut` | Blur dissolve + scale up | Dreamy, cinematic transitions (pairs with blurReveal) |
| `slideOutLeft` | Slide left + fade | Directional flow, "moving forward" |
| `slideOutRight` | Slide right + fade | Directional flow, paired with slideFromLeft entrance |
| `clipCircleOut` | Iris-out (circle closes) | Dramatic endings (pairs with circleReveal) |

```tsx
import { getExitStart, exitStaggerDelays } from "../motifs/timing";
import { fadeSlideOut } from "../motifs/exits/fadeSlideOut";
import { scaleOut } from "../motifs/exits/scaleOut";
import { blurOut } from "../motifs/exits/blurOut";
import { slideOutLeft } from "../motifs/exits/slideOutLeft";
import { slideOutRight } from "../motifs/exits/slideOutRight";
import { clipCircleOut } from "../motifs/exits/clipCircleOut";

const zone = getAnimationZone(durationInFrames);
const exitStart = getExitStart(durationInFrames);

// Title: scale-out
const titleExit = scaleOut(frame, fps, exitStart, durationInFrames);

// Items: reverse stagger (last item exits first)
const itemExitDelays = exitStaggerDelays(items.length, exitStart, durationInFrames);

// Combine with entrance animation:
<div style={{
  ...titleAnim,
  opacity: titleAnim.opacity * titleExit.opacity,
  transform: `${titleAnim.transform ?? ""} ${titleExit.transform}`,
}}>
```

### blurOut (cinematic dissolve)
```tsx
const exit = blurOut(frame, fps, exitStart, durationInFrames);
// Returns { opacity, transform: "scale(N)", filter: "blur(Npx)" }
<div style={{
  ...entryAnim,
  opacity: entryAnim.opacity * exit.opacity,
  transform: `${entryAnim.transform ?? ""} ${exit.transform}`,
  filter: exit.filter,
}}>
```

### clipCircleOut (iris-out)
```tsx
const exit = clipCircleOut(frame, fps, exitStart, durationInFrames);
// Returns { clipPath: "circle(N% at 50% 50%)", opacity: 1 }
<div style={{
  ...entryAnim,
  clipPath: frame >= exitStart ? exit.clipPath : undefined,
}}>
```

**Key**: Multiply entry opacity with exit opacity. Concatenate transforms. For clip-path exits, apply conditionally (`frame >= exitStart`).

---

## CameraMotion (subtle zoom + drift)

Wraps content in a slow zoom-in during hold phase. Adds cinematic depth.

```tsx
import { CameraMotion } from "../design/CameraMotion";

// Wrap the content layer (between AnimatedBackground and ProgressBar)
<AnimatedBackground backgroundImage={backgroundImage} />
<CameraMotion entranceFrames={zone} maxZoom={1.02}>
  <AbsoluteFill style={{ /* content */ }}>
    {/* ... slide content ... */}
  </AbsoluteFill>
</CameraMotion>
<ProgressBar ... />
<SceneFade />
```

**Props**: `maxZoom` (1.02 = subtle, 1.04 = noticeable), `driftX`/`driftY` (px).
ProgressBar and SceneFade stay OUTSIDE CameraMotion (they shouldn't zoom).

---

## AmbientParticles (floating light dots)

Semi-transparent dots drifting upward. Creates "alive" atmosphere.

```tsx
import { AmbientParticles } from "../design/AmbientParticles";

// Place after AnimatedBackground, before content
<AnimatedBackground backgroundImage={backgroundImage} />
<AmbientParticles count={5} opacity={0.06} />
{/* content layers */}
```

**Props**: `count` (4-8), `opacity` (0.05-0.1), `color` (default accent).
Uses deterministic seeded positioning (no Math.random).

---

## BlurReveal (blur-to-sharp entrance)

Premium text reveal — starts blurred and sharpens. Use for ONE hero element per slide.

```tsx
import { blurReveal } from "../motifs/entries/blurReveal";

const heroAnim = blurReveal(frame, fps, zoneDelay(0.1, zone), SPRING_GENTLE);
// Returns { opacity, filter: "blur(Npx)", transform: "scale(N)" }

<div style={{
  fontSize: 64, fontWeight: 800,
  ...heroAnim,  // spread all three properties
}}>
  Hero Text
</div>
```

**Combine with exit**: `opacity: heroAnim.opacity * heroExit.opacity`.
Don't use on list items — the blur-per-item feels sluggish.

---

## CameraPan (directional drift)

Pure translate without zoom. Adds directional movement to hold-phase content.

```tsx
import { CameraPan } from "../design/CameraPan";

// Wrap content layer (between AnimatedBackground and ProgressBar)
<AnimatedBackground backgroundImage={backgroundImage} />
<CameraPan entranceFrames={zone} direction="right" distance={8}>
  <AbsoluteFill style={{ /* content */ }}>
    {/* ... slide content ... */}
  </AbsoluteFill>
</CameraPan>
<ProgressBar ... />
<SceneFade />
```

**Props**: `direction` ("left" | "right" | "up" | "down"), `distance` (px, default 8).
Use "right" for forward-flow narrative, "up" for ascending/growth content.

---

## CameraTilt (3D perspective oscillation)

Subtle 3D tilt wobble using CSS perspective. Premium cinematic feel.

```tsx
import { CameraTilt } from "../design/CameraTilt";

<AnimatedBackground backgroundImage={backgroundImage} />
<CameraTilt entranceFrames={zone} maxRotateX={1.5} maxRotateY={2}>
  <AbsoluteFill style={{ /* content */ }}>
    {/* ... slide content ... */}
  </AbsoluteFill>
</CameraTilt>
<ProgressBar ... />
<SceneFade />
```

**Props**: `maxRotateX`/`maxRotateY` (degrees), `perspective` (px, default 1200).
Uses sine-wave oscillation, not linear drift — gentle back-and-forth.

---

## Continuous Motion (float, shimmer, orbit)

Subtle ongoing animation that activates after entrance and runs throughout the hold phase.

### float (vertical bob)

```tsx
import { float } from "../motifs/emphasis";

// Icon bobbing gently
<div style={{
  transform: `translateY(${float(frame, fps, zone, 6, 0.35)}px)`,
}}>
  <svg>...</svg>
</div>
```

### shimmer (light-streak sweep)

```tsx
import { shimmer } from "../motifs/emphasis";

// Sheen sweeping across a card
<div style={{
  padding: 24, borderRadius: 16,
  background: "rgba(124,127,217,0.08)",
  ...shimmer(frame, fps, zone),
}}>
  Card content
</div>
```

**Note**: shimmer returns `{ background, backgroundSize, backgroundPosition }` — spread it onto the element. The shimmer's background will override the element's background, so use on overlay divs or combine carefully.

### orbit (circular path)

```tsx
import { orbit } from "../motifs/emphasis";

// Decorative ring orbiting around a central icon
const o = orbit(frame, fps, zone, 12, 0.25);
<div style={{
  transform: `translate(${o.x}px, ${o.y}px)`,
  width: 8, height: 8, borderRadius: "50%",
  backgroundColor: COLORS.ACCENT,
  opacity: 0.4,
}}>
</div>
```

---

## GradientShift (ambient gradient cycling)

Slow-cycling gradient overlay for atmospheric depth. Place after AnimatedBackground.

```tsx
import { GradientShift } from "../design/GradientShift";

<AnimatedBackground backgroundImage={backgroundImage} />
<GradientShift speed={0.1} direction={135} />
{/* content layers */}
```

**Props**: `colors` (array, default accent/teal/bright at low alpha), `speed` (Hz), `direction` (degrees).
Uses deterministic frame-based cycling with fade-in/out.

---

## Spring Preset Decision Guide

Choose the right spring for the content's emotional intent, not just its visual weight.

### Preset Feel

| Preset | Feel | Settle Time | 시청자 인상 |
|--------|------|-------------|-------------|
| `SPRING_GENTLE` | 커튼이 열리듯 부드러운 등장 | ~600ms | "중요한, 신중한" |
| `SPRING_SNAPPY` | 카드 뒤집히듯 빠른 배치 | ~300ms | "팩트, 다음으로" |
| `SPRING_BOUNCY` | 튕기며 과도하게 갔다 돌아옴 | ~500ms | "놀라운, 흥미로운" |
| `SPRING_STIFF` | 감속 없이 즉각 도착 | ~200ms | "핵심, 집중" |

### Content → Spring 매핑

```
제목/히어로 텍스트?    → SPRING_GENTLE (읽기 속도, 무게감)
불릿 항목?            → SPRING_SNAPPY (효율적 연속)
큰 숫자/통계?         → SPRING_BOUNCY (놀라움, wow)
경고/핵심 정보?       → SPRING_STIFF (긴급, 권위)
차트 바?              → SPRING_SNAPPY (깔끔, 전문적)
감성/스토리?          → SPRING_GENTLE (분위기, 공감)
CTA/행동 유도?        → SPRING_BOUNCY (흥분, 참여)
다이어그램 노드?      → pickSpring("varied") (시각적 다양성)
```

### Font Size + Spring 페어링

- `fontSize >= 64px` → GENTLE/STIFF만 (큰 텍스트 reflow 방지)
- `fontSize 36-63px` → 모든 preset OK
- `fontSize <= 35px` → SNAPPY/BOUNCY 권장
- 아이콘/배지 → BOUNCY 항상 OK

### pickSpring 프리셋

| Preset | 순환 | 용도 |
|--------|------|------|
| `"varied"` | GENTLE → SNAPPY → BOUNCY → STIFF | 기본값, 다양한 목록 |
| `"gentle"` | GENTLE → SNAPPY → GENTLE → STIFF | 감성/서사 콘텐츠 (BOUNCY 제외) |
| `"energetic"` | BOUNCY → SNAPPY → BOUNCY → STIFF | 데이터/비교 강조 (BOUNCY 2배) |

```tsx
// pickSpring(i) — 기본 varied 순환
{items.map((item, i) => {
  const config = pickSpring(i);           // gentle → snappy → bouncy → stiff → ...
  const anim = fadeSlideIn(frame, fps, delays[i], config);
  return <div key={i} style={{ ...anim }}>{item}</div>;
})}

// pickSpring(i, "gentle") — 감성 슬라이드
const config = pickSpring(i, "gentle");   // BOUNCY 빠지고 GENTLE 2회

// pickSpring(i, "energetic") — 데이터 강조
const config = pickSpring(i, "energetic"); // BOUNCY 2회로 역동적
```

---

## Color Transitions (colorShift, progressReveal)

### colorShift (interpolateColors companion)

```tsx
import { colorShift } from "../motifs/emphasis";
import { interpolateColors } from "remotion";

// Keyword changes color from gray to accent
const progress = colorShift(frame, fps, zone, 0.8);
const color = interpolateColors(progress, [0, 1], [COLORS.MUTED, COLORS.ACCENT]);

<span style={{ color }}>keyword</span>
```

### progressReveal (karaoke text fill)

```tsx
import { progressReveal } from "../motifs/emphasis";

// Text fills left-to-right with active color
const p = progressReveal(frame, fps, zone, 2.0);

<span style={{
  background: `linear-gradient(90deg, ${COLORS.ACCENT} ${p}%, ${COLORS.MUTED} ${p}%)`,
  WebkitBackgroundClip: "text",
  WebkitTextFillColor: "transparent",
  backgroundClip: "text",
}}>
  Long sentence that reveals progressively
</span>
```
