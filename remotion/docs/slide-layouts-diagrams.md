# Layout: Diagrams & Charts

> Flow charts, bar charts, timelines, step indicators.
> All layouts shorts-safe (center-aligned, maxWidth constrained).

**⚠ 크기/배치 필수 규칙** — `tsx-contract.md` § Sizing & Centering Rules 참조:
- 노드 최소 240x80px, font-size 32px+, borderRadius 16px+
- 수직 중심 `cY = 480`, 수평 캔버스 70-80% 활용
- 화살표 strokeWidth 3px+, 화살촉 16px+
- 아래 코드 예시의 수치는 **최소 기준**이며, 그대로 복사하지 말고 콘텐츠에 맞게 키울 것

---

### A. Circle + Line Flow Diagram
**⚠ 빈도 제한: 영상 전체에서 수평 화살표 계열 합산 최대 2회.** 초과 시 `slide-layouts-metaphors.md`의 Numbered Card Row, Vertical Descent, Staircase Progress를 사용할 것.

Flow chart with connected circles (architecture, data flow).
```tsx
const nodes = ["입력", "처리", "출력"];
const nodeSize = 160;  // minimum 160px for circles
const gap = 360;       // spread across canvas
const startX = (1920 - (nodes.length * nodeSize + (nodes.length - 1) * (gap - nodeSize))) / 2;

{nodes.map((label, i) => {
  const x = startX + i * gap;
  const nodeAnim = scaleIn(frame, fps, 6 + i * 8, SPRING_BOUNCY);
  const lineProgress = i < nodes.length - 1
    ? drawLine(frame, fps, 12 + i * 8)
    : 0;
  return (
    <React.Fragment key={i}>
      {/* Connection line */}
      {i < nodes.length - 1 && (
        <div style={{
          position: "absolute",
          left: x + nodeSize,
          top: "50%",
          width: gap - nodeSize,
          height: 3,
          background: `linear-gradient(90deg, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
          transformOrigin: "left center",
          transform: `scaleX(${lineProgress})`,
          boxShadow: GLOW.bar,
        }} />
      )}
      {/* Node circle */}
      <div style={{
        position: "absolute",
        left: x,
        top: "50%",
        transform: `translateY(-50%) scale(${nodeAnim.opacity})`,
        opacity: nodeAnim.opacity,
        width: nodeSize,
        height: nodeSize,
        borderRadius: "50%",
        border: `2.5px solid ${COLORS.ACCENT}`,
        background: COLORS.CODE_BG,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}>
        <span style={{
          color: COLORS.TEXT,
          fontSize: 32,
          fontFamily: FONT.family,
          fontWeight: 600,
        }}>{label}</span>
      </div>
    </React.Fragment>
  );
})}
```

### B. Horizontal Bar Chart
Animated horizontal bars for comparison/ranking.
```tsx
const bars = [
  { label: "항목 A", value: 85, color: COLORS.ACCENT },
  { label: "항목 B", value: 62, color: COLORS.TEAL },
  { label: "항목 C", value: 40, color: COLORS.ACCENT_BRIGHT },
];
const maxBarWidth = 600;

{bars.map((bar, i) => {
  const barProgress = drawBar(frame, fps, 10 + i * 6);
  const labelAnim = fadeSlideIn(frame, fps, 6 + i * 6, SPRING_SNAPPY);
  return (
    <div key={i} style={{
      display: "flex",
      alignItems: "center",
      gap: 20,
      marginBottom: 28,
      ...labelAnim,
    }}>
      <span style={{
        width: 120,
        textAlign: "right",
        color: COLORS.MUTED,
        fontSize: FONT.bullet.size,
        fontFamily: FONT.family,
        fontWeight: FONT.bullet.weight,
      }}>{bar.label}</span>
      <div style={{
        width: maxBarWidth,
        height: 28,
        background: "rgba(255,255,255,0.05)",
        borderRadius: 14,
        overflow: "hidden",
      }}>
        <div style={{
          width: `${bar.value}%`,
          height: "100%",
          background: bar.color,
          borderRadius: 14,
          transformOrigin: "left center",
          transform: `scaleX(${barProgress})`,
          boxShadow: `0 0 12px ${bar.color}40`,
        }} />
      </div>
      <span style={{
        color: COLORS.TEXT,
        fontSize: 34,
        fontFamily: FONT.family,
        fontWeight: 700,
      }}>{Math.round(bar.value * barProgress)}%</span>
    </div>
  );
})}
```

### C. Vertical Timeline
Dots + single continuous vertical line + labels for chronological content.
Uses a single `position: absolute` line (NOT per-row individual lines).
```tsx
const events = [
  { year: "2020", text: "시작", color: COLORS.ACCENT },
  { year: "2022", text: "성장", color: COLORS.TEAL },
  { year: "2024", text: "도약", color: COLORS.ACCENT_BRIGHT },
];

{/* Timeline container: position relative for absolute line */}
<div style={{ position: "relative", display: "flex", flexDirection: "column" }}>
  {/* Single continuous vertical line (absolute positioned) */}
  <div style={{
    position: "absolute",
    left: 7,  // center of 14px dot
    top: 7,
    width: 2,
    height: "calc(100% - 14px)",
    background: `linear-gradient(to bottom, ${COLORS.MUTED}, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
    transform: `scaleY(${drawLine(frame, fps, 4)})`,
    transformOrigin: "top center",
  }} />
  {/* Timeline rows */}
  {events.map((event, i) => {
    const rowAnim = cascadeUp(frame, fps, i, 8, 6, pickSpring(i));
    return (
      <div key={i} style={{
        display: "flex",
        alignItems: "center",
        gap: 24,
        marginBottom: i < events.length - 1 ? 52 : 0,
        ...rowAnim,
      }}>
        {/* Dot */}
        <div style={{
          width: 14, height: 14, borderRadius: "50%",
          background: event.color, flexShrink: 0,
          boxShadow: `0 0 12px ${event.color}60`,
        }} />
        {/* Content */}
        <div>
          <span style={{
            color: event.color,
            fontSize: 32,
            fontFamily: FONT.family,
            fontWeight: 700,
            marginRight: 16,
          }}>{event.year}</span>
          <span style={{
            color: COLORS.TEXT,
            fontSize: FONT.bullet.size,
            fontFamily: FONT.family,
            fontWeight: FONT.bullet.weight,
          }}>{event.text}</span>
        </div>
      </div>
    );
  })}
</div>
```

### D. Step Indicator
"Step X of Y" with progress dots and glowing current step. Perfect for tutorial/how-to content.
```tsx
const currentStep = 2;
const totalSteps = 5;
const stepTitle = "프로젝트 설정";

const titleAnim = fadeSlideIn(frame, fps, 4, SPRING_GENTLE);
const badgeAnim = scaleIn(frame, fps, 8, SPRING_BOUNCY);
const barProgress = drawBar(frame, fps, 12);

{/* Step badge */}
<div style={{
  display: "flex",
  alignItems: "center",
  gap: 12,
  marginBottom: 32,
  ...badgeAnim,
}}>
  <div style={{
    background: COLORS.ACCENT,
    color: "#fff",
    fontSize: 26,
    fontWeight: 800,
    fontFamily: FONT.family,
    padding: "8px 20px",
    borderRadius: 24,
    boxShadow: `0 0 16px ${COLORS.ACCENT}50`,
  }}>STEP {currentStep}</div>
  <span style={{
    color: COLORS.MUTED,
    fontSize: 28,
    fontFamily: FONT.family,
    fontWeight: 500,
  }}>of {totalSteps}</span>
</div>

{/* Step title */}
<h1 style={{
  color: COLORS.TEXT,
  fontSize: FONT.title.size,
  fontWeight: FONT.title.weight,
  fontFamily: FONT.family,
  letterSpacing: FONT.title.letterSpacing,
  lineHeight: FONT.title.lineHeight,
  margin: 0,
  marginBottom: 40,
  ...titleAnim,
}}>{stepTitle}</h1>

{/* Progress dots */}
<div style={{
  display: "flex",
  gap: 16,
  alignItems: "center",
  marginBottom: 24,
}}>
  {Array.from({ length: totalSteps }).map((_, i) => {
    const dotAnim = scaleIn(frame, fps, 14 + i * 3, SPRING_SNAPPY);
    const isCurrent = i + 1 === currentStep;
    const isPast = i + 1 < currentStep;
    return (
      <div key={i} style={{
        width: isCurrent ? 16 : 10,
        height: isCurrent ? 16 : 10,
        borderRadius: "50%",
        background: isPast ? COLORS.ACCENT : isCurrent ? COLORS.ACCENT_BRIGHT : "rgba(255,255,255,0.15)",
        boxShadow: isCurrent ? `0 0 12px ${COLORS.ACCENT_BRIGHT}80` : "none",
        transition: "none",
        ...dotAnim,
      }} />
    );
  })}
</div>

{/* Progress bar */}
<div style={{
  width: 400,
  height: 4,
  borderRadius: 2,
  background: "rgba(255,255,255,0.06)",
  overflow: "hidden",
}}>
  <div style={{
    height: "100%",
    width: `${(currentStep / totalSteps) * 100}%`,
    background: `linear-gradient(90deg, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
    borderRadius: 2,
    transformOrigin: "left center",
    transform: `scaleX(${barProgress})`,
    boxShadow: GLOW.bar,
  }} />
</div>
```

---

### E. Cycle Flow Diagram
Nodes arranged in a clockwise loop with animated directional arrows.
Ideal for: feedback loops, iterative processes, PDCA cycles, continuous improvement, recurring workflows.
Uses SVG overlay for arrows + absolute-positioned div nodes (full 1920x1080 canvas).

**Frequency note**: Cycle flows are high-value for educational content — 이해도를 크게 높이므로, 빈도 제한 없이 적극 활용할 것.
```tsx
// Data — change labels/colors as needed. Supports 3-5 nodes.
const cycleNodes = [
  { label: "계획", color: COLORS.ACCENT },
  { label: "실행", color: COLORS.TEAL },
  { label: "검증", color: COLORS.ACCENT_BRIGHT },
  { label: "개선", color: COLORS.ACCENT },
];
const centerText = "반복"; // optional center label — set to "" to hide

// Layout constants
const nW = 164, nH = 58, aGap = 14; // node size + arrow gap from edge
const cX = 960, cY = 450; // cycle center (above subtitle zone)
const hSpan = 230, vSpan = 120; // half-width, half-height of rectangle

// Node positions — clockwise from top-left
const cPos = [
  { x: cX - hSpan, y: cY - vSpan },
  { x: cX + hSpan, y: cY - vSpan },
  { x: cX + hSpan, y: cY + vSpan },
  { x: cX - hSpan, y: cY + vSpan },
];

// Arrow connections (node edge → next node edge)
const dirs: Array<"r"|"d"|"l"|"u"> = ["r", "d", "l", "u"];
const cArrows = [
  { x1: cPos[0].x+nW/2+aGap, y1: cPos[0].y,           x2: cPos[1].x-nW/2-aGap, y2: cPos[1].y },
  { x1: cPos[1].x,           y1: cPos[1].y+nH/2+aGap,  x2: cPos[2].x,           y2: cPos[2].y-nH/2-aGap },
  { x1: cPos[2].x-nW/2-aGap, y1: cPos[2].y,           x2: cPos[3].x+nW/2+aGap, y2: cPos[3].y },
  { x1: cPos[3].x,           y1: cPos[3].y-nH/2-aGap,  x2: cPos[0].x,           y2: cPos[0].y+nH/2+aGap },
];

// Arrowhead triangle helper (axis-aligned directions)
const tipSz = 10;
const tipPts = (x: number, y: number, d: "r"|"d"|"l"|"u") => {
  if (d === "r") return `${x},${y} ${x-tipSz},${y-tipSz/2} ${x-tipSz},${y+tipSz/2}`;
  if (d === "d") return `${x},${y} ${x-tipSz/2},${y-tipSz} ${x+tipSz/2},${y-tipSz}`;
  if (d === "l") return `${x},${y} ${x+tipSz},${y-tipSz/2} ${x+tipSz},${y+tipSz/2}`;
  return `${x},${y} ${x-tipSz/2},${y+tipSz} ${x+tipSz/2},${y+tipSz}`;
};

{/* SVG arrow overlay — full canvas */}
<svg viewBox="0 0 1920 1080" style={{
  position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none",
}}>
  {cArrows.map((a, i) => {
    const len = Math.hypot(a.x2 - a.x1, a.y2 - a.y1);
    const offset = svgStrokeDraw(frame, fps, len, 12 + i * 8);
    const tipOp = interpolate(offset, [len * 0.15, 0], [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <React.Fragment key={`ca-${i}`}>
        <line x1={a.x1} y1={a.y1} x2={a.x2} y2={a.y2}
          stroke={cycleNodes[i].color} strokeWidth={2.5}
          strokeDasharray={len} strokeDashoffset={offset} />
        <polygon points={tipPts(a.x2, a.y2, dirs[i])}
          fill={cycleNodes[i].color} opacity={tipOp} />
      </React.Fragment>
    );
  })}
</svg>

{/* Cycle nodes */}
{cycleNodes.map((node, i) => {
  const na = scaleIn(frame, fps, 4 + i * 6, SPRING_BOUNCY);
  return (
    <div key={i} style={{
      position: "absolute",
      left: cPos[i].x - nW / 2, top: cPos[i].y - nH / 2,
      width: nW, height: nH, borderRadius: 14,
      border: `2px solid ${node.color}`,
      background: COLORS.CODE_BG,
      display: "flex", alignItems: "center", justifyContent: "center",
      boxShadow: `0 0 16px ${node.color}30`,
      ...na,
    }}>
      <span style={{
        color: COLORS.TEXT, fontSize: 32,
        fontFamily: FONT.family, fontWeight: 600,
      }}>{node.label}</span>
    </div>
  );
})}

{/* Center label (optional) */}
{centerText && (() => {
  const cAnim = fadeSlideIn(frame, fps, 28, SPRING_GENTLE);
  return (
    <div style={{
      position: "absolute",
      left: cX - 52, top: cY - 24,
      width: 104, height: 48, borderRadius: 24,
      background: `${COLORS.ACCENT}18`,
      border: `1px solid ${COLORS.ACCENT}40`,
      display: "flex", alignItems: "center", justifyContent: "center",
      ...cAnim,
    }}>
      <span style={{
        color: COLORS.ACCENT_BRIGHT, fontSize: 26,
        fontFamily: FONT.family, fontWeight: 700,
      }}>{centerText}</span>
    </div>
  );
})()}
```

**3-node variant** (triangle): Change `cPos` to 3 positions and `cArrows`/`dirs` accordingly:
```tsx
const cPos = [
  { x: cX, y: cY - vSpan },           // top center
  { x: cX + hSpan, y: cY + vSpan },   // bottom-right
  { x: cX - hSpan, y: cY + vSpan },   // bottom-left
];
// Arrows: top→BR (diagonal), BR→BL (horizontal left), BL→top (diagonal)
// Use generic tipPts with angle calculation (see Branch-Merge pattern below)
```

---

### F. Branch-Merge Flow Diagram
One node fans out to multiple branches, then merges back into one.
Ideal for: decision trees, parallel processing, multi-path evaluation, input→output mapping.
Uses SVG overlay for diagonal arrows + absolute-positioned div nodes.

**Frequency note**: Branch-merge flows are high-value for educational content — 분기/합류 구조를 직관적으로 전달하므로, 적극 활용할 것.
```tsx
// Data
const sourceLabel = "입력";
const targetLabel = "종합";
const branches = [
  { label: "경로 A", color: COLORS.ACCENT },
  { label: "경로 B", color: COLORS.TEAL },
  { label: "경로 C", color: COLORS.ACCENT_BRIGHT },
];

// Layout
const nW = 160, nH = 56, aGap = 16;
const cY = 450;
const srcX = 340, branchX = 920, tgtX = 1580;
const vSpace = 100; // vertical gap between branch centers

const srcPos = { x: srcX, y: cY };
const tgtPos = { x: tgtX, y: cY };
const bStartY = cY - (branches.length - 1) * vSpace / 2;
const bPos = branches.map((_, i) => ({ x: branchX, y: bStartY + i * vSpace }));

// Generic arrowhead for any angle (works for diagonal arrows)
const tipSz = 10;
const genTip = (x2: number, y2: number, x1: number, y1: number) => {
  const l = Math.hypot(x2 - x1, y2 - y1);
  const ux = (x2 - x1) / l, uy = (y2 - y1) / l;
  const px = -uy, py = ux;
  const w = 0.4;
  return `${x2},${y2} ${x2-ux*tipSz+px*tipSz*w},${y2-uy*tipSz+py*tipSz*w} ${x2-ux*tipSz-px*tipSz*w},${y2-uy*tipSz-py*tipSz*w}`;
};

// Arrow lines: source→branches (fan-out) + branches→target (fan-in)
const fanOut = bPos.map(bp => ({
  x1: srcPos.x + nW / 2 + aGap, y1: srcPos.y,
  x2: bp.x - nW / 2 - aGap,    y2: bp.y,
}));
const fanIn = bPos.map(bp => ({
  x1: bp.x + nW / 2 + aGap,    y1: bp.y,
  x2: tgtPos.x - nW / 2 - aGap, y2: tgtPos.y,
}));
const allArrows = [...fanOut, ...fanIn];

{/* SVG arrow overlay */}
<svg viewBox="0 0 1920 1080" style={{
  position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none",
}}>
  {allArrows.map((a, i) => {
    const len = Math.hypot(a.x2 - a.x1, a.y2 - a.y1);
    const isFanIn = i >= branches.length;
    const delay = isFanIn ? 18 + (i - branches.length) * 5 : 8 + i * 5;
    const offset = svgStrokeDraw(frame, fps, len, delay);
    const tOp = interpolate(offset, [len * 0.15, 0], [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const color = branches[i % branches.length].color;
    return (
      <React.Fragment key={`ba-${i}`}>
        <line x1={a.x1} y1={a.y1} x2={a.x2} y2={a.y2}
          stroke={color} strokeWidth={2} opacity={0.7}
          strokeDasharray={len} strokeDashoffset={offset} />
        <polygon points={genTip(a.x2, a.y2, a.x1, a.y1)}
          fill={color} opacity={tOp * 0.9} />
      </React.Fragment>
    );
  })}
</svg>

{/* Source node */}
{(() => {
  const a = scaleIn(frame, fps, 2, SPRING_BOUNCY);
  return (
    <div style={{
      position: "absolute",
      left: srcPos.x - nW / 2, top: srcPos.y - nH / 2,
      width: nW, height: nH, borderRadius: 14,
      border: `2px solid ${COLORS.ACCENT}`,
      background: COLORS.CODE_BG,
      display: "flex", alignItems: "center", justifyContent: "center",
      boxShadow: `0 0 16px ${COLORS.ACCENT}30`,
      ...a,
    }}>
      <span style={{
        color: COLORS.TEXT, fontSize: 32, fontFamily: FONT.family, fontWeight: 600,
      }}>{sourceLabel}</span>
    </div>
  );
})()}

{/* Branch nodes */}
{branches.map((b, i) => {
  const a = scaleIn(frame, fps, 10 + i * 5, SPRING_BOUNCY);
  return (
    <div key={i} style={{
      position: "absolute",
      left: bPos[i].x - nW / 2, top: bPos[i].y - nH / 2,
      width: nW, height: nH, borderRadius: 14,
      border: `2px solid ${b.color}`,
      background: COLORS.CODE_BG,
      display: "flex", alignItems: "center", justifyContent: "center",
      boxShadow: `0 0 16px ${b.color}30`,
      ...a,
    }}>
      <span style={{
        color: COLORS.TEXT, fontSize: 32, fontFamily: FONT.family, fontWeight: 600,
      }}>{b.label}</span>
    </div>
  );
})}

{/* Target node */}
{(() => {
  const a = scaleIn(frame, fps, 26, SPRING_BOUNCY);
  return (
    <div style={{
      position: "absolute",
      left: tgtPos.x - nW / 2, top: tgtPos.y - nH / 2,
      width: nW, height: nH, borderRadius: 14,
      border: `2px solid ${COLORS.TEAL}`,
      background: COLORS.CODE_BG,
      display: "flex", alignItems: "center", justifyContent: "center",
      boxShadow: `0 0 16px ${COLORS.TEAL}30`,
      ...a,
    }}>
      <span style={{
        color: COLORS.TEXT, fontSize: 32, fontFamily: FONT.family, fontWeight: 600,
      }}>{targetLabel}</span>
    </div>
  );
})()}
```

**Variants**:
- **2 branches**: Change `branches` array to 2 items, increase `vSpace` to 140 for visual balance
- **4+ branches**: Reduce `vSpace` to 80, reduce `nH` to 48 to fit within subtitle zone
- **Multi-stage**: Chain two Branch-Merge patterns (source → branches → mid-merge → branches2 → target) by adjusting X positions
