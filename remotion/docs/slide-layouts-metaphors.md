# Layout: Visual Metaphors

> People pictographs, balance scales, arrow flows, icon grids.
> Use for abstract concept visualization (ratios, comparisons, processes, categories).

---

### People Row Pictograph
Row of person silhouettes with N highlighted. Use for ratio/proportion visualization (e.g., "10명 중 1명").
```tsx
const totalPeople = 10;
const highlightCount = 1; // last N highlighted
const personGap = 20;
const personWidth = 72;
const totalWidth = totalPeople * personWidth + (totalPeople - 1) * personGap;
const startX = (1920 - totalWidth) / 2;

{Array.from({ length: totalPeople }).map((_, i) => {
  const isHighlighted = i >= totalPeople - highlightCount;
  const personAnim = cascadeUp(frame, fps, i, 4, 3, pickSpring(i));
  const glowAnim = isHighlighted
    ? spring({ frame: frame - 20, fps, config: { damping: 14, mass: 0.8 } })
    : 0;
  return (
    <div key={i} style={{
      position: "absolute",
      left: startX + i * (personWidth + personGap),
      top: "50%",
      transform: "translateY(-50%)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: 4,
      ...personAnim,
    }}>
      {/* Head */}
      <div style={{
        width: 32,
        height: 32,
        borderRadius: "50%",
        background: isHighlighted ? COLORS.ACCENT : "rgba(255,255,255,0.15)",
        boxShadow: isHighlighted ? `0 0 ${20 * glowAnim}px ${COLORS.ACCENT}60` : "none",
      }} />
      {/* Body */}
      <div style={{
        width: 52,
        height: 28,
        borderRadius: "28px 28px 0 0",
        background: isHighlighted ? COLORS.ACCENT : "rgba(255,255,255,0.1)",
        boxShadow: isHighlighted ? `0 0 ${16 * glowAnim}px ${COLORS.ACCENT}40` : "none",
      }} />
    </div>
  );
})}
```

### Balance Scale
Animated scale/balance for pros vs cons comparison. Use for weighing two options.
```tsx
const leftLabel = "장점";
const rightLabel = "주의점";
const tilt = -8; // negative = left side heavier (lower)
const pivotX = 960;
const pivotY = 440; // 440 — 타이틀 공간 확보 후 수직 중심 (340-380은 상단 치우침)
const armLength = 280;
const scaleAnim = spring({ frame: frame - 6, fps, config: { damping: 12, mass: 1.2 } });
const tiltAngle = tilt * scaleAnim;

{/* Pivot post */}
<div style={{
  position: "absolute",
  left: pivotX - 3,
  top: pivotY,
  width: 6,
  height: 100,
  background: "rgba(255,255,255,0.2)",
  borderRadius: 3,
}} />
{/* Pivot dot */}
<div style={{
  position: "absolute",
  left: pivotX - 8,
  top: pivotY - 8,
  width: 16,
  height: 16,
  borderRadius: "50%",
  background: COLORS.ACCENT,
  boxShadow: `0 0 12px ${COLORS.ACCENT}60`,
}} />
{/* Arm + pans (rotate around pivot) */}
<div style={{
  position: "absolute",
  left: pivotX - armLength,
  top: pivotY - 3,
  width: armLength * 2,
  height: 6,
  background: "rgba(255,255,255,0.3)",
  borderRadius: 3,
  transformOrigin: "center center",
  transform: `rotate(${tiltAngle}deg)`,
}}>
  {/* Left pan */}
  <div style={{
    position: "absolute",
    left: -20,
    top: 20,
    width: 120,
    height: 40,
    borderRadius: "50%",
    border: "2px solid",
    borderColor: COLORS.ACCENT,
    background: `${COLORS.ACCENT}15`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  }}>
    <span style={{
      color: COLORS.ACCENT,
      fontSize: 24,
      fontFamily: FONT.family,
      fontWeight: 700,
    }}>{leftLabel}</span>
  </div>
  {/* Right pan */}
  <div style={{
    position: "absolute",
    right: -20,
    top: 20,
    width: 120,
    height: 40,
    borderRadius: "50%",
    border: "2px solid rgba(255,255,255,0.2)",
    background: "rgba(255,255,255,0.04)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  }}>
    <span style={{
      color: COLORS.MUTED,
      fontSize: 24,
      fontFamily: FONT.family,
      fontWeight: 700,
    }}>{rightLabel}</span>
  </div>
</div>
```

### Labeled Arrow Flow
**⚠ 빈도 제한: 영상 전체에서 수평 화살표 계열 합산 최대 2회.** 초과 시 아래 Numbered Card Row, Vertical Descent, Staircase Progress를 사용할 것.

Icon/label -> arrow -> icon/label chain. Use for process/concept flow (user -> service -> result).
```tsx
const nodes = [
  { label: "사용자", iconColor: COLORS.TEXT },
  { label: "AI 분석", iconColor: COLORS.ACCENT },
  { label: "결과", iconColor: COLORS.TEAL },
];
const nodeGap = 240;
const startX = (1920 - (nodes.length - 1) * nodeGap) / 2;

{nodes.map((node, i) => {
  const nodeAnim = scaleIn(frame, fps, 6 + i * 8, SPRING_BOUNCY);
  const arrowP = i < nodes.length - 1
    ? drawLine(frame, fps, 14 + i * 8)
    : 0;
  return (
    <React.Fragment key={i}>
      {/* Node */}
      <div style={{
        position: "absolute",
        left: startX + i * nodeGap - 40,
        top: "50%",
        transform: "translateY(-50%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        ...nodeAnim,
      }}>
        <div style={{
          width: 80,
          height: 80,
          borderRadius: "50%",
          border: `2px solid ${node.iconColor}40`,
          background: `${node.iconColor}10`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          {/* Insert SVG icon */}
        </div>
        <span style={{
          color: node.iconColor,
          fontSize: 28,
          fontFamily: FONT.family,
          fontWeight: 600,
        }}>{node.label}</span>
      </div>
      {/* Arrow */}
      {i < nodes.length - 1 && (
        <div style={{
          position: "absolute",
          left: startX + i * nodeGap + 60,
          top: "50%",
          transform: "translateY(-50%)",
          display: "flex",
          alignItems: "center",
        }}>
          <div style={{
            width: nodeGap - 140,
            height: 3,
            background: `linear-gradient(90deg, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
            transformOrigin: "left center",
            transform: `scaleX(${arrowP})`,
            boxShadow: GLOW.bar,
          }} />
          <svg width="16" height="16" viewBox="0 0 16 16" style={{
            opacity: arrowP,
            marginLeft: -2,
          }}>
            <path d="M6 3l5 5-5 5" fill="none" stroke={COLORS.TEAL} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      )}
    </React.Fragment>
  );
})}
```

### Numbered Card Row ★ (Arrow Flow 대체 — 순서/인과)
Glass cards with large accent numbers. Sequence implied by number, no arrows needed.
Ideal for: "A → B → C" type content, step-by-step progression, cause-and-effect chains.
```tsx
const steps = [
  { num: "01", label: "이해", desc: "개념을 파악하는 단계" },
  { num: "02", label: "납득", desc: "논리적으로 수용", },
  { num: "03", label: "설계", desc: "실제 구현 단계" },
];
const cardW = 340, cardGap = 48;
const totalW = steps.length * cardW + (steps.length - 1) * cardGap;
const startX = (1920 - totalW) / 2;
const zone = getAnimationZone(durationInFrames);
const delays = staggerDelays(steps.length, zone);

{steps.map((step, i) => {
  const cardOp = glassCardOpacity(frame, fps, 0.6);
  const anim = fadeSlideIn(frame, fps, delays[i], pickSpring(i));
  return (
    <div key={i} style={{
      position: "absolute",
      left: startX + i * (cardW + cardGap),
      top: 300, width: cardW,
      background: "rgba(255,255,255,0.04)",
      border: `1px solid rgba(255,255,255,${0.06 * cardOp})`,
      borderRadius: 20, padding: "36px 32px",
      opacity: cardOp, ...anim,
    }}>
      <span style={{
        color: COLORS.ACCENT_BRIGHT, fontSize: 56, fontWeight: 800,
        fontFamily: FONT.family, lineHeight: 1,
        display: "block", textShadow: GLOW.text,
      }}>{step.num}</span>
      <h3 style={{
        color: COLORS.TEXT, fontSize: 32, fontWeight: 700,
        fontFamily: FONT.family, margin: "16px 0 8px",
      }}>{step.label}</h3>
      <p style={{
        color: COLORS.MUTED, fontSize: 24, fontWeight: 400,
        fontFamily: FONT.family, wordBreak: "keep-all" as const, margin: 0,
      }}>{step.desc}</p>
    </div>
  );
})}
```

**Variants**:
- **2 items**: Increase `cardW` to 440 for more breathing room
- **4 items**: Reduce `cardW` to 280, `cardGap` to 32
- **Without descriptions**: Omit `desc`, reduce card height, add accent icon instead

### Vertical Descent ★ (Arrow Flow 대체 — 순서/인과)
Items cascading vertically with accent dots and connecting gradient line on the left.
Ideal for: sequential processes, cause-effect chains, progressive steps without horizontal arrows.
```tsx
const items = [
  { label: "이해", desc: "개념을 파악하는 단계", color: COLORS.ACCENT },
  { label: "납득", desc: "논리적으로 수용하는 단계", color: COLORS.TEAL },
  { label: "설계", desc: "실제로 구현하는 단계", color: COLORS.ACCENT_BRIGHT },
];
const itemH = 88, itemGap = 36;
const totalH = items.length * itemH + (items.length - 1) * itemGap;
const startY = (1080 - totalH) / 2 + 20; // 반드시 1080 사용 (720 사용 금지!)
const dotX = 680; // dot+content 블록을 x=960 기준 수평 중심 정렬 (560은 좌측 치우침)
const zone = getAnimationZone(durationInFrames);

{/* Continuous connecting line (left side) */}
<div style={{
  position: "absolute",
  left: dotX, top: startY + itemH / 2,
  width: 3, height: totalH - itemH,
  background: `linear-gradient(to bottom, ${COLORS.ACCENT}, ${COLORS.TEAL}, ${COLORS.ACCENT_BRIGHT})`,
  transformOrigin: "top center",
  transform: `scaleY(${drawLine(frame, fps, zoneDelay(0.05, zone))})`,
  borderRadius: 2,
}} />

{items.map((item, i) => {
  const y = startY + i * (itemH + itemGap);
  const anim = fadeSlideIn(frame, fps, zoneDelay(0.15 + i * 0.2, zone), pickSpring(i));
  const dotAnim = scaleIn(frame, fps, zoneDelay(0.1 + i * 0.2, zone), SPRING_BOUNCY);
  return (
    <React.Fragment key={i}>
      {/* Accent dot */}
      <div style={{
        position: "absolute",
        left: dotX - 7, top: y + itemH / 2 - 8,
        width: 16, height: 16, borderRadius: "50%",
        background: item.color,
        boxShadow: `0 0 12px ${item.color}60`,
        ...dotAnim,
      }} />
      {/* Content */}
      <div style={{
        position: "absolute",
        left: dotX + 40, top: y,
        width: 560, minHeight: itemH,
        display: "flex", flexDirection: "column", justifyContent: "center",
        ...anim,
      }}>
        <span style={{
          color: item.color, fontSize: 36, fontWeight: 700,
          fontFamily: FONT.family,
        }}>{item.label}</span>
        <span style={{
          color: COLORS.MUTED, fontSize: 24, fontWeight: 400,
          fontFamily: FONT.family, wordBreak: "keep-all" as const, marginTop: 4,
        }}>{item.desc}</span>
      </div>
    </React.Fragment>
  );
})}
```

### Annotated Hub ★ (Fan-out/관계 대체)
Central concept with satellite items radiating outward. Implied connection by proximity, with optional subtle connecting lines.
Ideal for: concept + properties, central idea + branches, replacing fan-out arrow patterns.
```tsx
const center = { label: "핵심 개념" };
const satellites = [
  { label: "속성 A", angle: 210, color: COLORS.ACCENT },
  { label: "속성 B", angle: 330, color: COLORS.TEAL },
  { label: "속성 C", angle: 90, color: COLORS.ACCENT_BRIGHT },
];
// ⚠ hubY 범위: 490-520 필수. 420-440은 angle=270 위성이 타이틀과 겹침 (실제 사고 발생)
// 검증: 모든 위성에 대해 hubY + sin(angle)*orbitR - nH/2 ≥ 180 확인
const hubX = 960, hubY = 500, hubR = 88, orbitR = 300;
const zone = getAnimationZone(durationInFrames);

{/* Center hub */}
{(() => {
  const a = scaleIn(frame, fps, zoneDelay(0, zone), SPRING_BOUNCY);
  return (
    <div style={{
      position: "absolute",
      left: hubX - hubR, top: hubY - hubR,
      width: hubR * 2, height: hubR * 2, borderRadius: "50%",
      background: COLORS.CODE_BG,
      border: `3px solid ${COLORS.ACCENT}`,
      boxShadow: `0 0 24px ${COLORS.ACCENT}40`,
      display: "flex", alignItems: "center", justifyContent: "center",
      ...a,
    }}>
      <span style={{
        color: COLORS.TEXT, fontSize: 32, fontWeight: 700,
        fontFamily: FONT.family, textAlign: "center" as const,
      }}>{center.label}</span>
    </div>
  );
})()}

{/* Subtle connecting lines */}
<svg viewBox="0 0 1920 1080" style={{
  position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none",
}}>
  {satellites.map((sat, i) => {
    const rad = (sat.angle * Math.PI) / 180;
    const ex = hubX + Math.cos(rad) * hubR;
    const ey = hubY + Math.sin(rad) * hubR;
    const sx = hubX + Math.cos(rad) * orbitR;
    const sy = hubY + Math.sin(rad) * orbitR;
    const len = orbitR - hubR;
    const offset = svgStrokeDraw(frame, fps, len, zoneDelay(0.2 + i * 0.12, zone));
    return (
      <line key={i}
        x1={ex} y1={ey} x2={sx} y2={sy}
        stroke={sat.color} strokeWidth={2} opacity={0.4}
        strokeDasharray={len} strokeDashoffset={offset}
      />
    );
  })}
</svg>

{/* Satellite nodes */}
{satellites.map((sat, i) => {
  const rad = (sat.angle * Math.PI) / 180;
  const sx = hubX + Math.cos(rad) * orbitR;
  const sy = hubY + Math.sin(rad) * orbitR;
  const nW = 180, nH = 64;
  const a = fadeSlideIn(frame, fps, zoneDelay(0.3 + i * 0.12, zone), pickSpring(i));
  return (
    <div key={i} style={{
      position: "absolute",
      left: sx - nW / 2, top: sy - nH / 2,
      width: nW, height: nH, borderRadius: 16,
      background: COLORS.CODE_BG,
      border: `2px solid ${sat.color}`,
      display: "flex", alignItems: "center", justifyContent: "center",
      boxShadow: `0 0 12px ${sat.color}30`,
      ...a,
    }}>
      <span style={{
        color: COLORS.TEXT, fontSize: 28, fontWeight: 600,
        fontFamily: FONT.family,
      }}>{sat.label}</span>
    </div>
  );
})}
```

**Variants**:
- **4 satellites**: Use angles 45, 135, 225, 315 for even distribution
- **5 satellites**: Use angles 90, 162, 234, 306, 378 (pentagon)
- **Without lines**: Remove SVG overlay, proximity alone implies connection

### Staircase Progress ★ (Arrow Flow 대체 — 진행/발전)
Diagonal stepping pattern — each card lower-right of the previous. Progression implied by position.
Ideal for: evolution, improvement, level-up sequences, replacing linear arrow flows.
```tsx
const steps = [
  { label: "입력", color: COLORS.ACCENT },
  { label: "처리", color: COLORS.TEAL },
  { label: "출력", color: COLORS.ACCENT_BRIGHT },
];
const stepW = 300, stepH = 88;
const offsetX = stepW + 40, offsetY = 110;
const totalW = stepW + (steps.length - 1) * offsetX;
const startX = (1920 - totalW) / 2;
const startY = 240;
const zone = getAnimationZone(durationInFrames);

{steps.map((step, i) => {
  const x = startX + i * offsetX;
  const y = startY + i * offsetY;
  const anim = fadeSlideIn(frame, fps, zoneDelay(0.1 + i * 0.2, zone), pickSpring(i));
  return (
    <div key={i} style={{
      position: "absolute", left: x, top: y,
      width: stepW, height: stepH, borderRadius: 16,
      background: COLORS.CODE_BG,
      border: `2px solid ${step.color}`,
      display: "flex", alignItems: "center", justifyContent: "center",
      boxShadow: `0 0 16px ${step.color}30`,
      ...anim,
    }}>
      <span style={{
        color: step.color, fontSize: 20, fontWeight: 600,
        fontFamily: FONT.family, marginRight: 12, opacity: 0.6,
      }}>{String(i + 1).padStart(2, "0")}</span>
      <span style={{
        color: COLORS.TEXT, fontSize: 32, fontWeight: 600,
        fontFamily: FONT.family,
      }}>{step.label}</span>
    </div>
  );
})}
```

**Variants**:
- **Ascending** (default): Each step lower-right (progress = advancement)
- **Descending**: Negative `offsetY` — each step upper-right (funnel-narrowing feel)
- **4-5 steps**: Reduce `stepW` to 240, `offsetY` to 80

---

### Icon Grid (3x2 / 2x3)
Grid of icon cards with badge overlay. Use for category/service overview.
```tsx
const items = [
  { label: "법률 상담", icon: "document" },
  { label: "의료 서비스", icon: "heart" },
  { label: "교육 플랫폼", icon: "star" },
  { label: "쇼핑 서비스", icon: "cloud" },
  { label: "고객 지원", icon: "users" },
  { label: "금융 서비스", icon: "trending" },
];
const cols = 3;
const cellSize = 140;
const cellGap = 32;
const gridWidth = cols * cellSize + (cols - 1) * cellGap;

<div style={{
  display: "flex",
  flexWrap: "wrap",
  gap: cellGap,
  justifyContent: "center",
  maxWidth: gridWidth,
}}>
  {items.map((item, i) => {
    const cardAnim = cascadeUp(frame, fps, i, 6, 4, pickSpring(i));
    return (
      <div key={i} style={{
        width: cellSize,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        ...cardAnim,
      }}>
        {/* Icon circle */}
        <div style={{
          position: "relative",
          width: 80,
          height: 80,
          borderRadius: "50%",
          background: "rgba(255,255,255,0.06)",
          border: "1px solid rgba(255,255,255,0.1)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          {/* Insert SVG icon here */}
          {/* Badge dot (top-right) */}
          <div style={{
            position: "absolute",
            top: -4,
            right: -4,
            width: 24,
            height: 24,
            borderRadius: "50%",
            background: COLORS.ACCENT,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14"/>
              <path d="M12 5v14"/>
            </svg>
          </div>
        </div>
        {/* Label */}
        <span style={{
          color: COLORS.TEXT,
          fontSize: 26,
          fontFamily: FONT.family,
          fontWeight: 600,
          textAlign: "center" as const,
        }}>{item.label}</span>
      </div>
    );
  })}
</div>
```
