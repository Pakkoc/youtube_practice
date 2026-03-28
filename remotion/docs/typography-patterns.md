# Typography Patterns

> 3가지 텍스트 애니메이션 레시피. 새 motif 없이 기존 프리미티브 조합.
> 각 패턴은 독립적 — 필요한 것만 참조.

---

## Word Carousel (blur crossfade 텍스트 순환)

단어 배열이 blur crossfade로 순환합니다. 고정 위치에서 키워드가 교대로 나타나는 효과.

**용도**: 관련 개념 순환 강조, 키워드 교대 ("생산성 → 효율성 → 혁신")
**금지**: 모든 항목이 동시에 보여야 할 때 (icon-grid 사용)

```tsx
import { interpolate } from "remotion";

const words = ["생산성", "효율성", "혁신"];
const framesPerWord = Math.round(fps * 1.5);  // 1.5초 per word
const currentIdx = Math.floor(frame / framesPerWord) % words.length;
const wordFrame = frame % framesPerWord;

// Fade-in (0-20%) + Hold (20-80%) + Fade-out (80-100%)
const opacity = interpolate(wordFrame, [0, framesPerWord * 0.2, framesPerWord * 0.8, framesPerWord], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
const blur = interpolate(wordFrame, [0, framesPerWord * 0.2, framesPerWord * 0.8, framesPerWord], [8, 0, 0, 8], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

// 고정 너비 컨테이너 (가장 긴 단어 기준)
<div style={{ position: "relative", minWidth: 300, textAlign: "center" }}>
  {/* 가장 긴 단어로 너비 확보 (투명) */}
  <span style={{ visibility: "hidden", fontSize: 64, fontWeight: 800, fontFamily: FONT.family }}>
    {words.reduce((a, b) => a.length > b.length ? a : b)}
  </span>
  {/* 실제 표시 단어 */}
  <span style={{
    position: "absolute", left: 0, right: 0, top: 0,
    fontSize: 64, fontWeight: 800, fontFamily: FONT.family,
    color: COLORS.ACCENT_BRIGHT,
    opacity,
    filter: `blur(${blur}px)`,
  }}>
    {words[currentIdx]}
  </span>
</div>
```

**핵심**: `visibility: "hidden"` span으로 고정 너비 확보 → 단어 교체 시 레이아웃 점프 방지.

---

## Text Highlight (2-layer 하이라이트 스윕)

텍스트 등장 후 핵심 구문 아래 하이라이트 바가 스윕합니다.

**용도**: 등장 후 1-2개 핵심 구문 강조
**금지**: 슬라이드당 3개 초과 하이라이트

```tsx
import { highlighter } from "../motifs/emphasis";
import { fadeSlideIn } from "../motifs/entries";
import { getAnimationZone, zoneDelay } from "../motifs/timing";

const zone = getAnimationZone(durationInFrames);
const textDelay = zoneDelay(0.1, zone);
const highlightDelay = zoneDelay(0.4, zone);  // 텍스트 등장 후 하이라이트

const textAnim = fadeSlideIn(frame, fps, textDelay, SPRING_GENTLE);
const hlProgress = highlighter(frame, fps, highlightDelay);

<div style={{ position: "relative", display: "inline-block", ...textAnim }}>
  {/* Base text (항상 보임) */}
  <span style={{
    fontSize: 48, fontWeight: 700, fontFamily: FONT.family,
    color: COLORS.TEXT,
  }}>
    AI 시대의 <span style={{ position: "relative" }}>
      핵심 역량
      {/* Highlight bar overlay */}
      <div style={{
        position: "absolute",
        left: -4, right: -4, bottom: 2,
        height: 14,
        background: `${COLORS.ACCENT}30`,
        borderRadius: 4,
        transformOrigin: "left center",
        transform: `scaleX(${hlProgress})`,
      }} />
    </span>은 맥락 설계
  </span>
</div>
```

**핵심**: `position: "relative"` wrapper + `position: "absolute"` highlight bar. `transformOrigin: "left center"`로 좌→우 스윕.

---

## Typewriter Text (문자열 슬라이싱 + 블링킹 커서)

기존 `typewriterCount()` → `text.slice(0, charCount)`로 텍스트 타이핑 효과.

**용도**: 터미널/코드 출력, AI 생성 텍스트, 극적 텍스트 공개
**금지**: 긴 문단 (너무 느림), 리스트 (stagger 사용)

```tsx
import { typewriterCount } from "../motifs/emphasis";
import { getAnimationZone, zoneDelay } from "../motifs/timing";

const zone = getAnimationZone(durationInFrames);
const text = "AI가 당신의 업무를 자동화합니다";
const twDelay = zoneDelay(0.2, zone);
const charCount = typewriterCount(frame, fps, text.length, 2.0, twDelay);

// 블링킹 커서: 0.5초 주기 깜빡 (부드러운 보간 대신 의도적 깜빡)
const cursorVisible = Math.floor(frame / Math.round(fps * 0.5)) % 2 === 0;

<div style={{
  fontFamily: "'Pretendard', monospace",
  fontSize: 40, fontWeight: 600,
  color: COLORS.TEXT,
}}>
  {text.slice(0, charCount)}
  <span style={{
    color: COLORS.ACCENT_BRIGHT,
    opacity: charCount < text.length ? (cursorVisible ? 1 : 0) : 0,
  }}>|</span>
</div>
```

**한국어 호환**: `String.prototype.slice`는 UTF-16 코드 유닛 기준. 한글 1글자 = 1유닛이므로 정상 동작.
**커서 숨김**: 타이핑 완료 후 커서 사라짐 (`charCount < text.length` 체크).
**monospace 느낌**: `fontFamily`에 monospace fallback 추가하면 터미널 느낌.
