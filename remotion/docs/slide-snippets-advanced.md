# Advanced Snippet Library (시각 어휘 확장)

> 이 스니펫은 사용 가능한 기법 예시입니다. **규칙이 아닙니다.**
> 내용에 맞게 자유롭게 조합/변형하세요. 사용 시기에 대한 규칙은 없습니다.
>
> **Safety constraints**: 모든 스니펫은 기존 import만 사용합니다.
> - No `backdropFilter` / `WebkitBackgroundClip:"text"` / `mix-blend-mode`
> - No `Math.random()` / CSS `@keyframes` / CSS `animation`
> - All timing via `spring()` + `interpolate()` only

---

## A. Animation Techniques

### A1. Counter / Odometer (숫자 롤링)

숫자가 슬롯머신처럼 자릿수별로 굴러 올라가는 효과.
**용도**: 큰 숫자 강조, KPI, 통계 (countUpProgress보다 시각적 임팩트가 큼)
**Skip**: 소수점이 많은 숫자, 텍스트 안의 인라인 숫자

```tsx
// --- Odometer: 각 자릿수가 독립적으로 rolling ---
const TARGET = 2847;  // ← 커스터마이즈
const digits = String(TARGET).split("");
const totalDigits = digits.length;

// countUpProgress로 0→1 진행률
const progress = countUpProgress(frame, fps, 1.8);  // 1.8초 동안

const CELL_H = 120;  // 한 자릿수 셀 높이 ← 커스터마이즈

<div style={{ display: "flex", gap: 4, justifyContent: "center" }}>
  {digits.map((d, i) => {
    const digit = parseInt(d);
    // 뒤쪽 자릿수일수록 먼저 완료 (오른쪽→왼쪽 settling)
    const digitDelay = (totalDigits - 1 - i) * 0.08;
    const digitProgress = interpolate(
      progress,
      [digitDelay, Math.min(digitDelay + 0.6, 1)],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
    );
    // 목표 숫자까지 전체 0-9 사이클을 돌면서 도착
    const totalScroll = digit + (totalDigits - i) * 10;  // 여러 바퀴 회전
    const currentScroll = totalScroll * digitProgress;

    return (
      <div key={i} style={{
        width: 72, height: CELL_H, overflow: "hidden",
        borderRadius: 12,
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
      }}>
        <div style={{
          transform: `translateY(${-(currentScroll % 10) * CELL_H}px)`,
          transition: "none",
        }}>
          {[0,1,2,3,4,5,6,7,8,9,0].map((n, j) => (
            <div key={j} style={{
              height: CELL_H,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 80, fontWeight: 800, fontFamily: FONT.family,
              color: COLORS.TEXT,
            }}>
              {n}
            </div>
          ))}
        </div>
      </div>
    );
  })}
</div>
```

---

### A2. Typing with Cursor (터미널 타이핑)

커서가 깜빡이며 텍스트가 한 글자씩 나타나는 효과.
**용도**: 코드/명령어, 터미널 화면, 프롬프트 입력 시각화
**Skip**: 일반 설명 텍스트, 긴 문단

```tsx
// --- Typing effect: typewriterCount + blinking cursor ---
const TEXT = "npm install @anthropic-ai/sdk";  // ← 커스터마이즈
const TYPING_DURATION = 2.0;  // seconds ← 커스터마이즈

const visibleChars = typewriterCount(frame, fps, TEXT.length, TYPING_DURATION, 0);
const displayText = TEXT.slice(0, visibleChars);

// 커서 깜빡임: 0.5초 주기 (타이핑 중에는 항상 보임)
const isTyping = visibleChars < TEXT.length;
const cursorVisible = isTyping || Math.floor(frame / (fps * 0.5)) % 2 === 0;

// 터미널 프롬프트 래퍼
<div style={{
  background: "#141618",
  borderRadius: 16,
  border: "1px solid rgba(255,255,255,0.08)",
  padding: "32px 40px",
  maxWidth: 900,
}}>
  {/* 터미널 dot 장식 */}
  <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
    {["#FF5F56","#FFBD2E","#27C93F"].map((c, i) => (
      <div key={i} style={{ width: 12, height: 12, borderRadius: 6, background: c }} />
    ))}
  </div>
  {/* 타이핑 텍스트 */}
  <div style={{
    fontFamily: "'SF Mono', 'Fira Code', monospace",
    fontSize: 32, color: "#27C93F", lineHeight: 1.6,
  }}>
    <span style={{ color: COLORS.MUTED }}>$ </span>
    <span>{displayText}</span>
    <span style={{
      opacity: cursorVisible ? 1 : 0,
      color: "#27C93F",
      marginLeft: 2,
    }}>|</span>
  </div>
</div>
```

---

### A3. Wipe Reveal (방향성 드러냄)

콘텐츠가 좌→우 또는 하→상으로 마스크가 걷히며 나타나는 효과.
**용도**: 이미지/카드/섹션의 극적 등장, 비교 전환
**Skip**: 작은 텍스트 요소 (circleReveal이 더 적합)

```tsx
// --- Horizontal wipe (좌→우) ---
const wipeProgress = spring({
  frame: frame - delay,  // delay ← 커스터마이즈
  fps,
  config: { damping: 20, mass: 0.8 },
});
const clipRight = interpolate(wipeProgress, [0, 1], [100, 0]);

<div style={{
  clipPath: `inset(0 ${clipRight}% 0 0)`,
  // 내부 콘텐츠
}}>
  {/* 드러날 콘텐츠 */}
</div>

// --- Vertical wipe (하→상) ---
const clipTop = interpolate(wipeProgress, [0, 1], [100, 0]);
<div style={{ clipPath: `inset(${clipTop}% 0 0 0)` }}>
  {/* 드러날 콘텐츠 */}
</div>

// --- Diagonal wipe (좌하→우상) ---
const poly = interpolate(wipeProgress, [0, 1], [0, 130]);
<div style={{
  clipPath: `polygon(0 ${poly}%, ${poly}% 0, ${poly}% 100%, 0 100%)`,
}}>
  {/* 드러날 콘텐츠 */}
</div>
```

---

### A4. Elastic Overshoot (탄성 과장 입장)

요소가 목표 지점을 넘었다가 돌아오는 "스프링 바운스" 효과.
**용도**: 강조 요소, 놀라움/wow 순간, 숫자 도착
**Skip**: 정밀 차트, 데이터 테이블 (흔들림이 가독성 해침)

```tsx
// --- Elastic: overshootClamping: false로 1.0 초과 허용 ---
const elasticScale = spring({
  frame: frame - delay,
  fps,
  config: {
    damping: 6,      // 낮을수록 더 많이 바운스 (4=극단, 8=약한)
    mass: 0.4,
    stiffness: 100,
    overshootClamping: false,  // 핵심: 1.0을 초과했다가 돌아옴
  },
});

<div style={{
  transform: `scale(${elasticScale})`,
  opacity: interpolate(elasticScale, [0, 0.5], [0, 1], { extrapolateRight: "clamp" }),
}}>
  {/* 바운스할 요소 */}
</div>

// 변형: 수평 방향 바운스 (좌측에서 들어오기)
const elasticX = spring({
  frame: frame - delay,
  fps,
  config: { damping: 7, mass: 0.5, overshootClamping: false },
});
const x = interpolate(elasticX, [0, 1], [-200, 0]);

<div style={{ transform: `translateX(${x}px)` }}>
  {/* 좌측에서 바운스하며 등장 */}
</div>
```

---

### A5. 3D Card Flip (카드 뒤집기)

카드가 Y축으로 회전하며 앞/뒷면을 보여주는 효과.
**용도**: 전/후 비교, 정답 공개, "뒤집어 보면" 메타포
**Skip**: 3개 이상 동시 사용, 짧은 슬라이드 (<3초)
**주의**: `perspective` + `rotateY`는 GPU 부하. 슬라이드당 최대 2회.

```tsx
// --- 3D Flip: front → back ---
const flipProgress = spring({
  frame: frame - delay,
  fps,
  config: { damping: 15, mass: 0.8 },
});
const rotateY = interpolate(flipProgress, [0, 1], [0, 180]);
const showBack = rotateY > 90;

<div style={{
  perspective: 1200,  // 원근감 (낮을수록 과장)
  width: 600, height: 360,  // ← 커스터마이즈
}}>
  {/* Front */}
  <div style={{
    position: "absolute", width: "100%", height: "100%",
    backfaceVisibility: "hidden",
    transform: `rotateY(${rotateY}deg)`,
    background: "rgba(255,255,255,0.04)",
    borderRadius: 20, padding: 40,
    border: "1px solid rgba(255,255,255,0.08)",
    display: "flex", alignItems: "center", justifyContent: "center",
    opacity: showBack ? 0 : 1,
  }}>
    <span style={{ fontSize: 48, fontWeight: 700, color: COLORS.TEXT }}>
      기존 방식
    </span>
  </div>
  {/* Back */}
  <div style={{
    position: "absolute", width: "100%", height: "100%",
    backfaceVisibility: "hidden",
    transform: `rotateY(${rotateY - 180}deg)`,
    background: `linear-gradient(135deg, ${COLORS.ACCENT}22, ${COLORS.TEAL}22)`,
    borderRadius: 20, padding: 40,
    border: `1px solid ${COLORS.ACCENT}44`,
    display: "flex", alignItems: "center", justifyContent: "center",
    opacity: showBack ? 1 : 0,
  }}>
    <span style={{ fontSize: 48, fontWeight: 700, color: COLORS.ACCENT_BRIGHT }}>
      새로운 방식
    </span>
  </div>
</div>
```

---

### A6. Spotlight / Dim (포커스-앤-딤)

여러 요소 중 하나만 밝히고 나머지를 어둡게 하여 순차적으로 포커스.
**용도**: 리스트 항목 순차 강조, 비교 요소 하이라이트, 단계별 설명
**Skip**: 모든 요소가 동시에 보여야 할 때

```tsx
// --- Spotlight: rolling focus window ---
const ITEMS = ["기획", "디자인", "개발", "테스트", "배포"];  // ← 커스터마이즈
const FOCUS_DURATION = fps * 1.2;  // 각 아이템에 포커스 머무는 시간
const zone = getAnimationZone(durationInFrames, { fps });
const delays = staggerDelays(ITEMS.length, zone, { minGap: 4 });

{ITEMS.map((item, i) => {
  // 각 아이템의 포커스 시점 계산
  const itemDelay = delays[i];
  const nextDelay = i < ITEMS.length - 1 ? delays[i + 1] : durationInFrames;

  // 이 아이템이 포커스 중인지
  const isFocused = frame >= itemDelay && frame < nextDelay;

  // smooth opacity transition
  const focusOpacity = spring({
    frame: frame - itemDelay,
    fps,
    config: SPRING_SNAPPY,
  });
  const dimOpacity = isFocused
    ? interpolate(focusOpacity, [0, 1], [0.2, 1])
    : interpolate(focusOpacity, [0, 1], [0.2, 0.2]);

  // 포커스 시 약간 scale up
  const focusScale = isFocused
    ? interpolate(focusOpacity, [0, 1], [0.95, 1.05])
    : 1.0;

  return (
    <div key={i} style={{
      opacity: frame < delays[0] ? 0 : dimOpacity,
      transform: `scale(${focusScale})`,
      padding: "20px 32px",
      borderRadius: 16,
      background: isFocused ? "rgba(124,127,217,0.12)" : "rgba(255,255,255,0.02)",
      border: isFocused ? "1px solid rgba(124,127,217,0.3)" : "1px solid rgba(255,255,255,0.06)",
      fontSize: 40, fontWeight: 600, color: COLORS.TEXT,
      fontFamily: FONT.family,
    }}>
      {item}
    </div>
  );
})}
```

---

## B. Shape Vocabulary

### B1. Hexagon (정육각형)

**용도**: 기술/네트워크 노드, 카테고리 아이콘 배경, 벌집 그리드
**Skip**: 단순 아이콘 배경 (circle이 더 자연스러운 경우)

```tsx
// --- Hexagon SVG (flatTop 방향) ---
// size ← 커스터마이즈 (viewBox 100x100 기준)
<svg width={100} height={100} viewBox="0 0 100 100">
  <polygon
    points="50,2 93,25 93,75 50,98 7,75 7,25"
    fill={`${COLORS.ACCENT}22`}
    stroke={COLORS.ACCENT}
    strokeWidth={2}
  />
  {/* 중앙 텍스트/아이콘 추가 가능 */}
</svg>

// --- Hexagon clipPath (카드 마스킹용) ---
<div style={{
  width: 200, height: 200,
  clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
  background: `linear-gradient(135deg, ${COLORS.ACCENT}33, ${COLORS.TEAL}33)`,
  display: "flex", alignItems: "center", justifyContent: "center",
}}>
  {/* 클리핑된 콘텐츠 */}
</div>

// --- Hexagon grid (벌집 배치, 3열) ---
const HEX_SIZE = 100;
const ROW_HEIGHT = HEX_SIZE * 0.87;  // sin(60deg) * size
const COL_WIDTH = HEX_SIZE * 0.75;

{items.map((item, i) => {
  const row = Math.floor(i / 3);
  const col = i % 3;
  const offsetX = row % 2 === 1 ? COL_WIDTH / 2 : 0;  // 홀수 행 offset
  return (
    <div key={i} style={{
      position: "absolute",
      left: col * COL_WIDTH + offsetX + 200,  // ← 시작 위치 커스터마이즈
      top: row * ROW_HEIGHT + 300,
      width: HEX_SIZE, height: HEX_SIZE,
      clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
      background: `${COLORS.ACCENT}22`,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 24, color: COLORS.TEXT, fontFamily: FONT.family,
    }}>
      {item}
    </div>
  );
})}
```

---

### B2. Diamond (다이아몬드)

**용도**: 의사결정 포인트, 조건 분기, 중요도 강조 마커
**Skip**: 넓은 텍스트가 필요할 때 (대각선 공간이 좁음)

```tsx
// --- Diamond (CSS rotate) ---
<div style={{
  width: 100, height: 100,
  transform: "rotate(45deg)",
  background: `${COLORS.TEAL}22`,
  border: `2px solid ${COLORS.TEAL}`,
  borderRadius: 8,
  display: "flex", alignItems: "center", justifyContent: "center",
}}>
  <span style={{
    transform: "rotate(-45deg)",  // 텍스트 원위치
    fontSize: 28, fontWeight: 700, color: COLORS.TEAL,
  }}>
    Y/N
  </span>
</div>

// --- Diamond SVG ---
<svg width={80} height={80} viewBox="0 0 80 80">
  <polygon
    points="40,4 76,40 40,76 4,40"
    fill="none"
    stroke={COLORS.ACCENT_BRIGHT}
    strokeWidth={2.5}
  />
</svg>
```

---

### B3. Blob (유기적 형태)

**용도**: 배경 장식, 부드러운 이미지 프레임, 감성적 분위기
**Skip**: 데이터/정밀 다이어그램 (blob은 장식적)

```tsx
// --- Blob SVG: 3가지 변형 (deterministic, no Math.random) ---

// 변형 1: 둥근 blob
<svg width={200} height={200} viewBox="0 0 200 200">
  <path
    d="M40,100 C40,30 80,10 120,30 C160,50 180,80 170,120 C160,160 120,190 80,170 C40,150 40,170 40,100Z"
    fill={`${COLORS.ACCENT}15`}
    stroke={`${COLORS.ACCENT}30`}
    strokeWidth={1.5}
  />
</svg>

// 변형 2: 넓은 blob
<svg width={300} height={180} viewBox="0 0 300 180">
  <path
    d="M30,90 C30,30 90,10 150,20 C210,30 270,50 270,90 C270,130 220,170 150,160 C80,150 30,150 30,90Z"
    fill={`${COLORS.TEAL}12`}
  />
</svg>

// 변형 3: 각진 blob (더 역동적)
<svg width={200} height={200} viewBox="0 0 200 200">
  <path
    d="M50,80 C60,20 110,5 150,40 C190,75 195,110 160,150 C125,190 70,185 40,150 C10,115 40,140 50,80Z"
    fill={`${COLORS.ACCENT_BRIGHT}10`}
    stroke={`${COLORS.ACCENT_BRIGHT}20`}
    strokeWidth={1}
  />
</svg>
```

---

### B4. Bracket / Brace (중괄호)

**용도**: "이것들을 묶으면" 그룹핑, 코드 메타포, 분류 시각화
**Skip**: 단순 리스트 (icon-grid가 더 적합)

```tsx
// --- Curly brace SVG (왼쪽, 높이 커스터마이즈) ---
const BRACE_H = 300;  // ← 묶을 영역 높이에 맞게
<svg width={40} height={BRACE_H} viewBox={`0 0 40 ${BRACE_H}`}>
  <path
    d={`M35,8 C20,8 20,${BRACE_H/2-20} 5,${BRACE_H/2} C20,${BRACE_H/2+20} 20,${BRACE_H-8} 35,${BRACE_H-8}`}
    fill="none"
    stroke={COLORS.ACCENT}
    strokeWidth={2.5}
    strokeLinecap="round"
  />
</svg>

// --- 오른쪽 brace (mirror) ---
<svg width={40} height={BRACE_H} viewBox={`0 0 40 ${BRACE_H}`} style={{ transform: "scaleX(-1)" }}>
  {/* 동일한 path */}
</svg>

// --- 사용 예: 왼쪽 항목들 + brace + 오른쪽 결과 ---
<div style={{ display: "flex", alignItems: "center", gap: 20 }}>
  <div>{/* 왼쪽 항목 리스트 */}</div>
  <svg>{/* brace */}</svg>
  <div>{/* = 결과 */}</div>
</div>
```

---

### B5. Arrow Variations (화살표 변형)

**용도**: 흐름/방향 표현 시 기존 얇은 화살표 대신 시각적 변화
**Skip**: 기본 arrow로 충분한 경우

```tsx
// --- Thick chevron arrow ---
<svg width={60} height={40} viewBox="0 0 60 40">
  <path
    d="M5,20 L40,20 M30,8 L45,20 L30,32"
    fill="none"
    stroke={COLORS.ACCENT}
    strokeWidth={4}
    strokeLinecap="round"
    strokeLinejoin="round"
  />
</svg>

// --- Curved arc arrow (위로 휘는) ---
<svg width={200} height={80} viewBox="0 0 200 80">
  <path
    d="M20,60 C20,10 180,10 180,60"
    fill="none"
    stroke={COLORS.TEAL}
    strokeWidth={3}
    strokeLinecap="round"
    markerEnd="url(#arrowhead)"
  />
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill={COLORS.TEAL} />
    </marker>
  </defs>
</svg>

// --- Looping return arrow (되돌아오는 화살표) ---
<svg width={120} height={100} viewBox="0 0 120 100">
  <path
    d="M20,80 C20,20 100,20 100,50 C100,70 60,70 60,50"
    fill="none"
    stroke={COLORS.ACCENT_BRIGHT}
    strokeWidth={3}
    strokeLinecap="round"
    markerEnd="url(#returnArrow)"
  />
  <defs>
    <marker id="returnArrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill={COLORS.ACCENT_BRIGHT} />
    </marker>
  </defs>
</svg>
```

---

## C. Composition Patterns

### C1. Off-Center Hero (삼등분 구도)

**용도**: 시각적 긴장감, 역동적 첫인상, 비대칭 미학
**Skip**: 차트/다이어그램 (정확한 정렬이 필요한 경우)

```tsx
// --- Rule of thirds: 좌상단 1/3 + 우하단 보조 ---
<AbsoluteFill>
  <AnimatedBackground backgroundImage={backgroundImage} />

  {/* 메인 콘텐츠: 좌상단 1/3 교차점 */}
  <div style={{
    position: "absolute",
    left: 100, top: 200,  // 1920의 약 1/3 지점 근처
    maxWidth: 900,
  }}>
    {/* 강조 바 */}
    <div style={{
      width: 60, height: 6, borderRadius: 3,
      background: COLORS.ACCENT, marginBottom: 24,
    }} />
    <div style={{
      fontSize: 72, fontWeight: 800, lineHeight: 1.15,
      color: COLORS.TEXT, fontFamily: FONT.family,
      wordBreak: "keep-all",
    }}>
      메인 타이틀이 여기에
    </div>
    <div style={{
      fontSize: 36, fontWeight: 500, lineHeight: 1.4,
      color: COLORS.MUTED, fontFamily: FONT.family,
      marginTop: 20,
    }}>
      보조 설명 텍스트
    </div>
  </div>

  {/* 보조 비주얼: 우하단 */}
  <div style={{
    position: "absolute",
    right: 120, bottom: 200,
    opacity: 0.6,
  }}>
    {/* 보조 그래픽, 아이콘, 또는 장식 */}
  </div>

  <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
  <SceneFade />
</AbsoluteFill>
```

---

### C2. Scale Contrast (극대+극소 대비)

**용도**: 핵심 메시지 강조, 숫자와 맥락의 시각적 위계
**Skip**: 모든 요소가 동등한 중요도일 때

```tsx
// --- 극대 숫자 + 극소 맥락 ---
<div style={{
  display: "flex", flexDirection: "column",
  alignItems: "center", gap: 8,
}}>
  {/* 거대한 숫자 */}
  <div style={{
    fontSize: 200,  // 극대
    fontWeight: 900, lineHeight: 1.0,
    color: COLORS.ACCENT_BRIGHT,
    fontFamily: FONT.family,
    textShadow: GLOW.text,
  }}>
    73%
  </div>

  {/* 극소 맥락 라벨들 */}
  <div style={{
    display: "flex", gap: 24, alignItems: "center",
  }}>
    <span style={{
      fontSize: 24,  // 극소 (200과의 대비 = 8:1)
      fontWeight: 500, color: COLORS.MUTED,
      fontFamily: FONT.family,
      textTransform: "uppercase" as const,
      letterSpacing: "0.15em",
    }}>
      productivity increase
    </span>
    <div style={{
      width: 1, height: 20,
      background: "rgba(255,255,255,0.2)",
    }} />
    <span style={{
      fontSize: 24, fontWeight: 500,
      color: COLORS.TEAL, fontFamily: FONT.family,
    }}>
      2024 Q4
    </span>
  </div>
</div>
```

---

### C3. Overlapping Cards (겹침 카드)

**용도**: 깊이감, 레이어 구조 시각화, 옵션/카테고리 나열
**Skip**: 2개 이하 항목 (겹침 효과가 무의미)

```tsx
// --- Z-stacked cards with stagger entrance ---
const CARDS = [
  { title: "기본", color: COLORS.MUTED },
  { title: "프로", color: COLORS.ACCENT },
  { title: "엔터프라이즈", color: COLORS.TEAL },
];

const zone = getAnimationZone(durationInFrames, { fps });
const delays = staggerDelays(CARDS.length, zone, { minGap: 6 });

{CARDS.map((card, i) => {
  const anim = fadeSlideIn(frame, fps, delays[i], SPRING_SNAPPY);
  return (
    <div key={i} style={{
      position: "absolute",
      left: 400 + i * 40,   // 우측으로 40px씩 offset
      top: 300 + i * 25,    // 아래로 25px씩 offset
      width: 500, height: 300,
      borderRadius: 20, padding: 40,
      background: i === CARDS.length - 1
        ? `linear-gradient(135deg, ${card.color}22, ${card.color}11)`
        : "rgba(255,255,255,0.03)",
      border: `1px solid ${card.color}33`,
      boxShadow: `0 8px 32px rgba(0,0,0,${0.2 + i * 0.1})`,
      zIndex: i,  // 뒤에서부터 앞으로
      ...anim,
    }}>
      <div style={{
        fontSize: 36, fontWeight: 700,
        color: card.color, fontFamily: FONT.family,
      }}>
        {card.title}
      </div>
    </div>
  );
})}
```

---

### C4. Edge-Aligned Content (한쪽 정렬)

**용도**: 에디토리얼 느낌, 여백 활용, 인용문+시각 조합
**Skip**: 차트/다이어그램 (중앙 배치가 더 적합)

```tsx
// --- Left-edge: 콘텐츠가 왼쪽에 밀착, 오른쪽 60% 여백 ---
<AbsoluteFill>
  <AnimatedBackground backgroundImage={backgroundImage} />

  {/* 왼쪽 강조 바 */}
  <div style={{
    position: "absolute", left: 0, top: 200, bottom: 200,
    width: 6, background: COLORS.ACCENT,
    boxShadow: GLOW.bar,
  }} />

  {/* 콘텐츠: 왼쪽 40%에 배치 */}
  <div style={{
    position: "absolute",
    left: 40, top: 220,
    maxWidth: 700,  // 1920의 ~37%
  }}>
    <div style={{
      fontSize: 64, fontWeight: 800, lineHeight: 1.15,
      color: COLORS.TEXT, fontFamily: FONT.family,
      wordBreak: "keep-all",
    }}>
      핵심 메시지
    </div>
    <div style={{
      fontSize: 32, fontWeight: 500, lineHeight: 1.5,
      color: COLORS.MUTED, fontFamily: FONT.family,
      marginTop: 24,
    }}>
      상세 설명이 여기에 위치합니다. 오른쪽의 넓은 여백이 시각적 호흡을 제공합니다.
    </div>
  </div>

  {/* 오른쪽 여백은 의도적으로 비움 (또는 반투명 장식) */}

  <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
  <SceneFade />
</AbsoluteFill>
```

---

### C5. Uneven Split (비대칭 분할, 70/30)

**용도**: 주요 콘텐츠+보조 패널, 텍스트+데이터 조합
**Skip**: 동등한 비교 (50/50 split-compare가 더 적합)

```tsx
// --- 70/30 split: 왼쪽 메인, 오른쪽 사이드바 ---
<div style={{
  display: "flex",
  width: 1680,  // 1920 - padding 양쪽 120
  height: 600,
  gap: 32,
}}>
  {/* 메인 패널 (70%) */}
  <div style={{
    width: 1140,  // 약 70%
    borderRadius: 20, padding: "40px 48px",
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
  }}>
    {/* 주요 콘텐츠 */}
  </div>

  {/* 사이드 패널 (30%) */}
  <div style={{
    width: 508,  // 약 30%
    borderRadius: 20, padding: "40px 32px",
    background: `linear-gradient(180deg, ${COLORS.ACCENT}11, ${COLORS.ACCENT}06)`,
    border: `1px solid ${COLORS.ACCENT}22`,
    display: "flex", flexDirection: "column",
    gap: 24,
  }}>
    {/* 보조 정보, 통계, 하이라이트 */}
  </div>
</div>
```

---

## D. Data Visualization

### D1. Animated Line Chart (선형 차트)

**용도**: 추세, 시간에 따른 변화, 성장률
**Skip**: 카테고리 비교 (bar chart가 더 적합)

```tsx
// --- Line chart: SVG polyline + strokeDash animation ---
const DATA = [20, 35, 28, 55, 42, 68, 85, 73];  // ← 커스터마이즈
const CHART_W = 800;
const CHART_H = 400;
const PADDING = 40;

// 데이터 → 좌표 변환
const maxVal = Math.max(...DATA);
const points = DATA.map((v, i) => {
  const x = PADDING + (i / (DATA.length - 1)) * (CHART_W - PADDING * 2);
  const y = CHART_H - PADDING - (v / maxVal) * (CHART_H - PADDING * 2);
  return `${x},${y}`;
}).join(" ");

// 선 길이 추정 (직선 근사)
const totalLength = 1500;  // 대략적 총 길이 (정확도보다 시각 효과 우선)
const drawProgress = spring({ frame, fps, config: SPRING_GENTLE });
const dashOffset = totalLength * (1 - drawProgress);

<svg width={CHART_W} height={CHART_H} style={{ overflow: "visible" }}>
  {/* 그리드 라인 */}
  {[0.25, 0.5, 0.75, 1].map((ratio, i) => {
    const y = CHART_H - PADDING - ratio * (CHART_H - PADDING * 2);
    return (
      <line key={i}
        x1={PADDING} y1={y} x2={CHART_W - PADDING} y2={y}
        stroke="rgba(255,255,255,0.06)" strokeWidth={1}
      />
    );
  })}

  {/* 선 (stroke-dash 애니메이션) */}
  <polyline
    points={points}
    fill="none"
    stroke={COLORS.ACCENT}
    strokeWidth={3}
    strokeLinecap="round"
    strokeLinejoin="round"
    strokeDasharray={totalLength}
    strokeDashoffset={dashOffset}
  />

  {/* 데이터 포인트 */}
  {DATA.map((v, i) => {
    const x = PADDING + (i / (DATA.length - 1)) * (CHART_W - PADDING * 2);
    const y = CHART_H - PADDING - (v / maxVal) * (CHART_H - PADDING * 2);
    const dotScale = spring({
      frame: frame - 10 - i * 4,  // 순차 등장
      fps,
      config: SPRING_BOUNCY,
    });
    return (
      <circle key={i}
        cx={x} cy={y} r={6}
        fill={COLORS.ACCENT_BRIGHT}
        transform={`scale(${dotScale})`}
        style={{ transformOrigin: `${x}px ${y}px` }}
      />
    );
  })}
</svg>
```

---

### D2. Semi-Circular Gauge (반원 게이지)

**용도**: 달성률, 점수, 퍼포먼스 지표, 온도/속도 메타포
**Skip**: 정확한 수치 비교 (bar chart가 더 적합)

```tsx
// --- Semi-circular gauge with animated fill ---
const VALUE = 73;    // 0~100 ← 커스터마이즈
const RADIUS = 140;
const STROKE_W = 20;
const CX = 180;
const CY = 180;

// 반원 arc path
const arcLength = Math.PI * RADIUS;  // 반원 둘레
const fillProgress = countUpProgress(frame, fps, 1.5);
const fillLength = arcLength * (VALUE / 100) * fillProgress;
const emptyLength = arcLength - fillLength;

// 색상 구간 (green/yellow/red)
const gaugeColor = VALUE >= 70 ? COLORS.TEAL : VALUE >= 40 ? "#FFBD2E" : "#FF5F56";

<svg width={360} height={200} viewBox="0 0 360 200">
  {/* 배경 트랙 */}
  <path
    d={`M ${CX - RADIUS},${CY} A ${RADIUS},${RADIUS} 0 0,1 ${CX + RADIUS},${CY}`}
    fill="none"
    stroke="rgba(255,255,255,0.06)"
    strokeWidth={STROKE_W}
    strokeLinecap="round"
  />
  {/* 채워지는 부분 */}
  <path
    d={`M ${CX - RADIUS},${CY} A ${RADIUS},${RADIUS} 0 0,1 ${CX + RADIUS},${CY}`}
    fill="none"
    stroke={gaugeColor}
    strokeWidth={STROKE_W}
    strokeLinecap="round"
    strokeDasharray={`${fillLength} ${emptyLength}`}
  />
  {/* 중앙 숫자 */}
  <text
    x={CX} y={CY - 20}
    textAnchor="middle"
    fontSize={64} fontWeight={800}
    fontFamily={FONT.family}
    fill={COLORS.TEXT}
  >
    {Math.round(VALUE * fillProgress)}
  </text>
  <text
    x={CX} y={CY + 10}
    textAnchor="middle"
    fontSize={24} fontWeight={500}
    fontFamily={FONT.family}
    fill={COLORS.MUTED}
  >
    점
  </text>
</svg>
```

---

### D3. Comparison Matrix (비교 매트릭스)

**용도**: 기능 비교표, 플랜 비교, 체크리스트 그리드
**Skip**: 2개 이하 항목 (split-compare가 더 적합)

```tsx
// --- Comparison matrix: staggered cell reveal ---
const COLS = ["Free", "Pro", "Enterprise"];
const ROWS = ["API 호출", "모델 선택", "우선 지원", "SLA"];
const DATA = [
  [true, true, true],
  [false, true, true],
  [false, false, true],
  [false, true, true],
];

const zone = getAnimationZone(durationInFrames, { fps });
const totalCells = ROWS.length * COLS.length;

<div style={{
  display: "grid",
  gridTemplateColumns: `180px repeat(${COLS.length}, 160px)`,
  gap: 4,
}}>
  {/* 헤더 행 */}
  <div /> {/* 빈 코너 */}
  {COLS.map((col, ci) => {
    const headerAnim = fadeSlideIn(frame, fps, ci * 4, SPRING_SNAPPY);
    return (
      <div key={ci} style={{
        padding: "16px 8px", textAlign: "center",
        fontSize: 28, fontWeight: 700, color: COLORS.ACCENT_BRIGHT,
        fontFamily: FONT.family,
        ...headerAnim,
      }}>
        {col}
      </div>
    );
  })}
  {/* 데이터 행 */}
  {ROWS.map((row, ri) => (
    <React.Fragment key={ri}>
      <div style={{
        padding: "16px 12px",
        fontSize: 26, fontWeight: 600, color: COLORS.TEXT,
        fontFamily: FONT.family,
        display: "flex", alignItems: "center",
      }}>
        {row}
      </div>
      {DATA[ri].map((val, ci) => {
        const cellIdx = ri * COLS.length + ci;
        const cellDelay = 12 + cellIdx * 3;  // 순차 등장
        const cellAnim = scaleIn(frame, fps, cellDelay, SPRING_SNAPPY);
        return (
          <div key={ci} style={{
            padding: 16,
            display: "flex", alignItems: "center", justifyContent: "center",
            background: val ? `${COLORS.TEAL}11` : "rgba(255,255,255,0.02)",
            borderRadius: 12,
            ...cellAnim,
          }}>
            {/* Checkmark or X */}
            <svg width={28} height={28} viewBox="0 0 24 24">
              {val ? (
                <path d="M5 13l4 4L19 7" fill="none" stroke={COLORS.TEAL} strokeWidth={2.5} strokeLinecap="round" />
              ) : (
                <path d="M6 6l12 12M18 6L6 18" fill="none" stroke={COLORS.MUTED} strokeWidth={2} strokeLinecap="round" />
              )}
            </svg>
          </div>
        );
      })}
    </React.Fragment>
  ))}
</div>
```

---

### D4. Segmented Donut (다중 세그먼트 도넛)

**용도**: 비율 분포, 카테고리 점유율, 다중 항목 비교
**Skip**: 2개 이하 세그먼트 (semi-circular gauge가 더 적합)

```tsx
// --- Segmented donut with staggered arc reveal ---
const SEGMENTS = [
  { label: "GPT", value: 45, color: COLORS.ACCENT },
  { label: "Claude", value: 30, color: COLORS.TEAL },
  { label: "Gemini", value: 15, color: COLORS.ACCENT_BRIGHT },
  { label: "Others", value: 10, color: COLORS.MUTED },
];

const RADIUS = 120;
const STROKE_W = 32;
const CX = 200;
const CY = 200;
const circumference = 2 * Math.PI * RADIUS;

// 각 세그먼트 시작/길이 계산
let accumulated = 0;
const segmentData = SEGMENTS.map((seg, i) => {
  const start = accumulated;
  accumulated += seg.value;
  return { ...seg, startPct: start, lengthPct: seg.value };
});

{segmentData.map((seg, i) => {
  const segDelay = i * 8;  // stagger
  const segProgress = spring({
    frame: frame - segDelay,
    fps,
    config: SPRING_SNAPPY,
  });
  const dashLength = (seg.lengthPct / 100) * circumference * segProgress;
  const gapLength = circumference - dashLength;
  const rotation = (seg.startPct / 100) * 360 - 90;  // -90 = 12시 시작

  return (
    <circle key={i}
      cx={CX} cy={CY} r={RADIUS}
      fill="none"
      stroke={seg.color}
      strokeWidth={STROKE_W}
      strokeDasharray={`${dashLength} ${gapLength}`}
      strokeLinecap="round"
      transform={`rotate(${rotation} ${CX} ${CY})`}
    />
  );
})}

{/* 중앙 라벨 */}
<text x={CX} y={CY} textAnchor="middle" dominantBaseline="middle"
  fontSize={48} fontWeight={800} fontFamily={FONT.family} fill={COLORS.TEXT}>
  100%
</text>
```

---

## E. Transition Variations

### E1. Cross-Dissolve (교차 디졸브)

**용도**: 한 슬라이드 내에서 콘텐츠 A→B 부드러운 전환
**Skip**: 씬 경계 전환 (SceneFade가 담당)

```tsx
// --- Cross-dissolve: 두 콘텐츠가 겹치며 교체 ---
const SWITCH_FRAME = Math.floor(durationInFrames * 0.5);  // 전환 시점
const OVERLAP = Math.floor(fps * 0.4);  // 겹침 구간 (0.4초)

const contentAOpacity = interpolate(
  frame,
  [SWITCH_FRAME - OVERLAP, SWITCH_FRAME],
  [1, 0],
  { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
);
const contentBOpacity = interpolate(
  frame,
  [SWITCH_FRAME, SWITCH_FRAME + OVERLAP],
  [0, 1],
  { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
);

{/* Content A */}
<AbsoluteFill style={{ opacity: contentAOpacity }}>
  {/* 첫 번째 콘텐츠 */}
</AbsoluteFill>

{/* Content B */}
<AbsoluteFill style={{ opacity: contentBOpacity }}>
  {/* 두 번째 콘텐츠 */}
</AbsoluteFill>
```

---

### E2. Wipe Transition (와이프 전환)

**용도**: 콘텐츠 교체에 방향성 부여, 에디토리얼 느낌
**Skip**: 미묘한 전환이 필요할 때 (cross-dissolve가 더 적합)

```tsx
// --- Wipe: 새 콘텐츠가 왼쪽에서 밀고 들어옴 ---
const SWITCH_FRAME = Math.floor(durationInFrames * 0.5);
const wipeSpring = spring({
  frame: frame - SWITCH_FRAME,
  fps,
  config: { damping: 18, mass: 0.7 },
});
const wipeX = interpolate(wipeSpring, [0, 1], [100, 0]);

{/* Content A (밀려나는 기존) */}
<AbsoluteFill style={{
  clipPath: `inset(0 0 0 ${100 - wipeX}%)`,
}}>
  {/* 첫 번째 콘텐츠 */}
</AbsoluteFill>

{/* Content B (밀고 들어오는 신규) */}
<AbsoluteFill style={{
  clipPath: `inset(0 ${wipeX}% 0 0)`,
}}>
  {/* 두 번째 콘텐츠 */}
</AbsoluteFill>
```

---

### E3. Zoom-Through (줌 통과)

**용도**: "다음 레벨로" 진입감, 세부사항으로 다이브, 극적 전환
**Skip**: 정밀 정보 슬라이드 (줌이 가독성 해침)

```tsx
// --- Zoom-through: 기존 콘텐츠가 확대되며 사라지고 새 콘텐츠 등장 ---
const SWITCH_FRAME = Math.floor(durationInFrames * 0.5);
const zoomProgress = spring({
  frame: frame - SWITCH_FRAME,
  fps,
  config: { damping: 15, mass: 0.8 },
});

const outScale = interpolate(zoomProgress, [0, 1], [1, 1.5]);
const outOpacity = interpolate(zoomProgress, [0, 0.6], [1, 0], {
  extrapolateRight: "clamp",
});
const inScale = interpolate(zoomProgress, [0, 1], [0.7, 1]);
const inOpacity = interpolate(zoomProgress, [0.3, 1], [0, 1], {
  extrapolateLeft: "clamp",
});

{/* Content A (확대되며 퇴장) */}
<AbsoluteFill style={{
  transform: `scale(${outScale})`,
  opacity: outOpacity,
}}>
  {/* 첫 번째 콘텐츠 */}
</AbsoluteFill>

{/* Content B (축소 상태에서 등장) */}
<AbsoluteFill style={{
  transform: `scale(${inScale})`,
  opacity: inOpacity,
}}>
  {/* 두 번째 콘텐츠 */}
</AbsoluteFill>
```
