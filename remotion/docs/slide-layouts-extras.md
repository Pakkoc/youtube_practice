# Layout: Extras & Shorts-Safe

> Progress bars, icon grids (1x4), SVG animation, shorts-safe overrides.

---

### Animated Progress Bar (inline)
```tsx
const progress = drawBar(frame, fps, 8);
<div style={{ width: "80%", maxWidth: 600, margin: "24px auto" }}>
  <div style={{
    height: 8,
    borderRadius: 4,
    background: "rgba(255,255,255,0.06)",
    overflow: "hidden",
  }}>
    <div style={{
      height: "100%",
      width: "75%",
      background: `linear-gradient(90deg, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
      borderRadius: 4,
      transformOrigin: "left center",
      transform: `scaleX(${progress})`,
      boxShadow: GLOW.bar,
    }} />
  </div>
</div>
```

### Icon + Text Grid (1x4 row)
```tsx
const items = [
  { icon: "star", label: "품질" },
  { icon: "lightning", label: "속도" },
  { icon: "cloud", label: "확장성" },
  { icon: "checkmark", label: "안정성" },
];
<div style={{
  display: "flex",
  gap: 48,
  justifyContent: "center",
}}>
  {items.map((item, i) => {
    const a = cascadeUp(frame, fps, i, 8, STAGGER_DELAY, SPRING_BOUNCY);
    return (
      <div key={i} style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        ...a,
      }}>
        <div style={{
          width: 64,
          height: 64,
          borderRadius: 16,
          background: GLOW.highlightBg,
          border: `1px solid ${GLOW.highlightBorder}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          {/* Insert appropriate SVG icon here */}
        </div>
        <span style={{
          color: COLORS.TEXT,
          fontSize: 32,
          fontFamily: FONT.family,
          fontWeight: 600,
        }}>{item.label}</span>
      </div>
    );
  })}
</div>
```

### SVG Stroke Draw Animation
```tsx
const totalLength = 200; // approximate path length
const dashOffset = svgStrokeDraw(frame, fps, totalLength, 6); // (frame, fps, totalLength, delay)
<svg width="200" height="200" viewBox="0 0 100 100" fill="none"
     stroke={COLORS.ACCENT} strokeWidth="2" strokeLinecap="round">
  <circle cx="50" cy="50" r="40"
    strokeDasharray={totalLength}
    strokeDashoffset={dashOffset}
  />
</svg>
```

---

## Shorts-Safe Patterns

These patterns enforce center alignment and width constraints for 9:16 shorts cropping safety.

### Center-Aligned Bar Chart (Shorts-Safe)

Multi-column/bar layouts MUST use this centering pattern.
Max width 700px ensures content survives 9:16 shorts cropping.

```tsx
{/* Container: center-aligned, max-width constrained */}
<div style={{
  display: "flex",
  flexDirection: "column",
  gap: 40,
  width: "100%",
  maxWidth: 700,
  alignItems: "center",
}}>
  {bars.map((bar, i) => (
    <div key={i} style={{
      display: "flex",
      alignItems: "center",
      gap: 20,
      justifyContent: "center",  // <- CRITICAL for center alignment
      width: "100%",
    }}>
      <div style={{ width: 200, textAlign: "right" as const }}>
        <span style={{ color: bar.color, fontSize: 30, fontFamily: FONT.family, fontWeight: 700 }}>
          {bar.label}
        </span>
      </div>
      <div style={{ width: 520, height: 32, background: "rgba(255,255,255,0.05)", borderRadius: 16, overflow: "hidden" }}>
        <div style={{
          width: `${bar.value}%`,
          height: "100%",
          background: bar.color,
          borderRadius: 16,
          transformOrigin: "left center",
          transform: `scaleX(${drawBar(frame, fps, 8 + i * 8)})`,
        }} />
      </div>
    </div>
  ))}
</div>
```

### Shorts-Safe Split Compare

Two-column comparison with fixed widths (not flex:1).
maxWidth 700px + explicit column widths = shorts crop safe.

```tsx
<div style={{
  display: "flex",
  gap: 40,
  alignItems: "stretch",
  justifyContent: "center",
  maxWidth: 700,  // <- NOT width: "100%"
}}>
  {/* Left column */}
  <div style={{ width: 280, padding: "36px 24px", /* ... */ }}>
    {/* content */}
  </div>
  {/* Divider or VS */}
  <div style={{ display: "flex", alignItems: "center" }}>
    <span>VS</span>
  </div>
  {/* Right column */}
  <div style={{ width: 280, padding: "36px 24px", /* ... */ }}>
    {/* content */}
  </div>
</div>
```

### Continuous Vertical Timeline (Shorts-Safe)

Timeline with a single continuous line (NOT per-row individual lines).
Individual per-row lines break when dot sizes differ or row heights vary.

```tsx
{/* Timeline container: position relative for absolute line */}
<div style={{ position: "relative", display: "flex", flexDirection: "column" }}>
  {/* Single continuous vertical line (absolute positioned) */}
  <div style={{
    position: "absolute",
    left: 7,  // center of 14px dot
    top: 7,
    width: 2,
    height: "calc(100% - 14px)",  // or fixed px based on row count
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
        }} />
        {/* Content */}
        <div>
          <span style={{ fontSize: 34, fontWeight: 700, color: event.color }}>{event.year}</span>
          <span style={{ fontSize: 32, color: COLORS.TEXT, marginLeft: 16 }}>{event.label}</span>
        </div>
      </div>
    );
  })}
</div>
```
