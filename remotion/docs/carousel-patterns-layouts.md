# Carousel Patterns — Layout Patterns & Common Elements

> Base layout patterns A-I and reusable common elements for carousel cards.
> Extended patterns J-W: see `carousel-patterns-layouts-extended.md`.
> Part of the carousel patterns suite — see `carousel-patterns.md` for the index.

---

## Layout Patterns

### A. Cover Card
Big centered title + subtitle, radial glow background.

```tsx
{/* Radial glow */}
<AbsoluteFill
  style={{
    background: `radial-gradient(ellipse 60% 40% at 50% 50%, ${colors.accent}33 0%, transparent 70%)`,
  }}
/>

{/* Content type badge */}
<div style={{
  position: "absolute",
  top: 80,
  left: 72,
  fontSize: 20,
  fontWeight: 600,
  fontFamily: FONT.family,
  color: colors.accent,
  letterSpacing: "0.12em",
  textTransform: "uppercase" as const,
}}>
  AI AUTOMATION
</div>

{/* Centered title */}
<AbsoluteFill style={{
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  padding: "80px 72px",
  textAlign: "center" as const,
}}>
  <div style={{
    fontSize: 56,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    lineHeight: 1.15,
    letterSpacing: "-0.03em",
    marginBottom: 28,
  }}>
    Main Title Here
  </div>
  <div style={{ width: 80, height: 3, background: colors.accent, borderRadius: 2, marginBottom: 24 }} />
  <div style={{
    fontSize: 24,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}99`,
    lineHeight: 1.5,
  }}>
    Subtitle description
  </div>
</AbsoluteFill>
```

### B. Icon Grid (2x2 or 1x3)
Grid of icon + label + description. **Must include description text** in each cell (not just a label).

```tsx
const items = [
  { icon: "lightning", label: "Fast", desc: "10x faster than manual" },
  { icon: "checkmark", label: "Reliable", desc: "99.9% uptime guarantee" },
  { icon: "gear", label: "Flexible", desc: "Fully customizable" },
  { icon: "star", label: "Premium", desc: "Enterprise-grade quality" },
];

{/* Centered content wrapper */}
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
}}>
  {/* Section title (optional) */}
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    marginBottom: 40,
    textAlign: "center" as const,
  }}>
    Section Title
  </div>

  {/* Grid — NO flex: 1, NO gridTemplateRows: "1fr" */}
  <div style={{
    display: "flex",
    flexWrap: "wrap" as const,
    gap: 24,
    justifyContent: "center",
  }}>
    {items.map((item, i) => (
      <div key={i} style={{
        width: 430,
        padding: "40px 32px",
        background: "rgba(255,255,255,0.04)",
        borderRadius: 20,
        border: `1px solid rgba(255,255,255,0.08)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
      }}>
        {/* SVG icon here (60x60) */}
        <div style={{
          fontSize: 24,
          fontWeight: 700,
          fontFamily: FONT.family,
          color: colors.text,
          textAlign: "center" as const,
        }}>
          {item.label}
        </div>
        <div style={{
          fontSize: 18,
          fontWeight: 400,
          fontFamily: FONT.family,
          color: `${colors.text}88`,
          textAlign: "center" as const,
          lineHeight: 1.4,
        }}>
          {item.desc}
        </div>
      </div>
    ))}
  </div>
</div>
```

### C. Numbered List
Ordered list with accent number badges.

```tsx
const listItems = [
  "First item description",
  "Second item description",
  "Third item description",
];

<div style={{
  position: "absolute",
  top: 240,
  left: 72,
  right: 72,
  display: "flex",
  flexDirection: "column",
  gap: 32,
}}>
  {listItems.map((text, i) => (
    <div key={i} style={{
      display: "flex",
      alignItems: "flex-start",
      gap: 24,
    }}>
      <div style={{
        minWidth: 52,
        height: 52,
        borderRadius: 16,
        background: `${colors.accent}20`,
        border: `1px solid ${colors.accent}40`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 24,
        fontWeight: 800,
        fontFamily: FONT.family,
        color: colors.accent,
      }}>
        {i + 1}
      </div>
      <div style={{
        fontSize: 26,
        fontWeight: 500,
        fontFamily: FONT.family,
        color: colors.text,
        lineHeight: 1.5,
        paddingTop: 8,
      }}>
        {text}
      </div>
    </div>
  ))}
</div>
```

### D. Split Top/Bottom
Top half = visual/stat, bottom half = explanation.

```tsx
{/* Top section — big number or visual */}
<div style={{
  position: "absolute",
  top: 80,
  left: 72,
  right: 72,
  height: 500,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
}}>
  <div style={{
    fontSize: 96,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.accent,
    letterSpacing: "-0.04em",
  }}>
    87%
  </div>
  <div style={{
    fontSize: 22,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: COLORS.MUTED,
    marginTop: 12,
  }}>
    Customer satisfaction
  </div>
</div>

{/* Divider */}
<div style={{
  position: "absolute",
  top: 620,
  left: 120,
  right: 120,
  height: 1,
  background: `${colors.text}15`,
}} />

{/* Bottom section — explanation */}
<div style={{
  position: "absolute",
  top: 660,
  left: 72,
  right: 72,
  bottom: 100,
}}>
  <div style={{
    fontSize: 26,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}CC`,
    lineHeight: 1.6,
  }}>
    Explanation text here with more details about the statistic shown above.
  </div>
</div>
```

### E. Quote Card
Glass card with large emphasized text. **Vertically centered** with corner accent decoration.

```tsx
{/* Corner accents for framing */}
<div style={{ position: "absolute", top: 48, left: 48, width: 60, height: 60 }}>
  <div style={{ position: "absolute", top: 0, left: 0, width: 60, height: 2, background: `${colors.accent}40` }} />
  <div style={{ position: "absolute", top: 0, left: 0, width: 2, height: 60, background: `${colors.accent}40` }} />
</div>
<div style={{ position: "absolute", bottom: 100, right: 48, width: 60, height: 60 }}>
  <div style={{ position: "absolute", bottom: 0, right: 0, width: 60, height: 2, background: `${colors.accent}40` }} />
  <div style={{ position: "absolute", bottom: 0, right: 0, width: 2, height: 60, background: `${colors.accent}40` }} />
</div>

{/* Centered content wrapper */}
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
}}>
  {/* Glass card */}
  <div style={{
    padding: "56px 44px",
    background: "rgba(255,255,255,0.04)",
    borderRadius: 24,
    border: `1px solid rgba(255,255,255,0.08)`,
  }}>
    {/* SVG quote mark */}
    <svg width="48" height="48" viewBox="0 0 24 24" fill={`${colors.accent}40`}>
      <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/>
      <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/>
    </svg>

    <div style={{
      fontSize: 38,
      fontWeight: 700,
      fontFamily: FONT.family,
      color: colors.text,
      lineHeight: 1.5,
      marginTop: 28,
    }}>
      The quoted text goes here with emphasis.
    </div>

    <div style={{
      fontSize: 22,
      fontWeight: 500,
      fontFamily: FONT.family,
      color: COLORS.MUTED,
      marginTop: 24,
    }}>
      — Attribution
    </div>
  </div>
</div>
```

### F. Horizontal Bar Chart (Static)
Static horizontal bars for comparison/ranking. **Vertically centered** with bottom insight text.

```tsx
const bars = [
  { label: "Item A", value: 85, color: colors.accent },
  { label: "Item B", value: 62, color: COLORS.TEAL },
  { label: "Item C", value: 40, color: COLORS.ACCENT_BRIGHT },
];

{/* Centered content wrapper — NO flex: 1 on bars container */}
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 32,
}}>
  {/* Title */}
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
  }}>
    Chart Title
  </div>

  {/* Bars — natural height, no flex: 1 */}
  <div style={{
    display: "flex",
    flexDirection: "column",
    gap: 36,
  }}>
    {bars.map((bar, i) => (
      <div key={i} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 22,
          fontFamily: FONT.family,
          fontWeight: 600,
        }}>
          <span style={{ color: colors.text }}>{bar.label}</span>
          <span style={{ color: bar.color }}>{bar.value}%</span>
        </div>
        <div style={{
          width: "100%",
          height: 24,
          background: "rgba(255,255,255,0.05)",
          borderRadius: 12,
          overflow: "hidden",
        }}>
          <div style={{
            width: `${bar.value}%`,
            height: "100%",
            background: bar.color,
            borderRadius: 12,
            boxShadow: `0 0 12px ${bar.color}40`,
          }} />
        </div>
      </div>
    ))}
  </div>

  {/* Bottom insight text — fills vertical space */}
  <div style={{
    fontSize: 20,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}88`,
    lineHeight: 1.5,
    marginTop: 8,
  }}>
    Key insight or summary about the data shown above.
  </div>
</div>
```

### G. Donut Chart
SVG circle-based donut chart.

```tsx
const percentage = 73;
const radius = 120;
const circumference = 2 * Math.PI * radius;
const filled = circumference * (percentage / 100);

<div style={{
  position: "absolute",
  top: 200,
  left: 0,
  right: 0,
  display: "flex",
  justifyContent: "center",
}}>
  <div style={{ position: "relative", width: 280, height: 280 }}>
    <svg width="280" height="280" viewBox="0 0 280 280">
      {/* Background circle */}
      <circle cx="140" cy="140" r={radius} fill="none"
        stroke="rgba(255,255,255,0.06)" strokeWidth="20" />
      {/* Filled arc */}
      <circle cx="140" cy="140" r={radius} fill="none"
        stroke={colors.accent} strokeWidth="20"
        strokeLinecap="round"
        strokeDasharray={`${filled} ${circumference - filled}`}
        strokeDashoffset={circumference * 0.25}
        style={{ filter: `drop-shadow(0 0 8px ${colors.accent}60)` }}
      />
    </svg>
    {/* Center text */}
    <div style={{
      position: "absolute",
      inset: 0,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
    }}>
      <div style={{
        fontSize: 56,
        fontWeight: 800,
        fontFamily: FONT.family,
        color: colors.text,
      }}>
        {percentage}%
      </div>
      <div style={{
        fontSize: 18,
        fontWeight: 500,
        fontFamily: FONT.family,
        color: COLORS.MUTED,
      }}>
        Completion
      </div>
    </div>
  </div>
</div>
```

### H. Before/After Comparison
Side-by-side comparison. **Vertically centered**, no `flex: 1`, larger fonts.

```tsx
{/* Centered content wrapper */}
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 32,
}}>
  {/* Title */}
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    textAlign: "center" as const,
  }}>
    Comparison Title
  </div>

  {/* Panels — width: "48%" instead of flex: 1 */}
  <div style={{
    display: "flex",
    gap: 24,
  }}>
    {/* Before */}
    <div style={{
      width: "48%",
      padding: "36px 28px",
      background: "rgba(255,80,80,0.06)",
      borderRadius: 20,
      border: "1px solid rgba(255,80,80,0.15)",
    }}>
      <div style={{
        fontSize: 20,
        fontWeight: 700,
        fontFamily: FONT.family,
        color: "#FF6B6B",
        marginBottom: 24,
        letterSpacing: "0.08em",
      }}>
        BEFORE
      </div>
      {/* Items — fontSize: 22, gap: 16 */}
    </div>

    {/* After */}
    <div style={{
      width: "48%",
      padding: "36px 28px",
      background: `${COLORS.TEAL}08`,
      borderRadius: 20,
      border: `1px solid ${COLORS.TEAL}20`,
    }}>
      <div style={{
        fontSize: 20,
        fontWeight: 700,
        fontFamily: FONT.family,
        color: COLORS.TEAL,
        marginBottom: 24,
        letterSpacing: "0.08em",
      }}>
        AFTER
      </div>
      {/* Items — fontSize: 22, gap: 16 */}
    </div>
  </div>
</div>
```

### I. CTA Ending Card
Call-to-action with handle/link.

```tsx
<AbsoluteFill style={{
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  padding: "80px 72px",
  textAlign: "center" as const,
}}>
  {/* Icon or emoji */}
  <div style={{ fontSize: 64, marginBottom: 32 }}>
    {/* SVG icon */}
  </div>

  <div style={{
    fontSize: 44,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    lineHeight: 1.3,
    marginBottom: 24,
  }}>
    CTA Title
  </div>

  <div style={{
    fontSize: 22,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}88`,
    lineHeight: 1.5,
    marginBottom: 40,
  }}>
    Supporting description text
  </div>

  {/* Button-like CTA */}
  <div style={{
    padding: "16px 48px",
    background: colors.accent,
    borderRadius: 50,
    fontSize: 22,
    fontWeight: 700,
    fontFamily: FONT.family,
    color: "#FFFFFF",
    boxShadow: `0 0 20px ${colors.accent}50`,
  }}>
    Follow @handle
  </div>
</AbsoluteFill>
```

---

## Common Elements

### Section Badge
Small labeled badge for category/section marker.

```tsx
<div style={{
  display: "inline-flex",
  padding: "6px 16px",
  background: `${colors.accent}15`,
  border: `1px solid ${colors.accent}30`,
  borderRadius: 20,
  fontSize: 16,
  fontWeight: 600,
  fontFamily: FONT.family,
  color: colors.accent,
  letterSpacing: "0.06em",
}}>
  SECTION 01
</div>
```

### Glass Card
Frosted glass container for grouped content.

```tsx
<div style={{
  padding: "36px 32px",
  background: "rgba(255,255,255,0.04)",
  borderRadius: 20,
  border: "1px solid rgba(255,255,255,0.08)",
  backdropFilter: "blur(10px)",
}}>
  {/* Content */}
</div>
```

### Gradient Text
Accent gradient applied to key text.

```tsx
<div style={{
  fontSize: 48,
  fontWeight: 800,
  fontFamily: FONT.family,
  backgroundImage: `linear-gradient(135deg, ${colors.accent}, ${COLORS.TEAL})`,
  backgroundClip: "text",
  WebkitBackgroundClip: "text",
  WebkitTextFillColor: "transparent",
}}>
  Gradient Text
</div>
```

### Accent Divider Line

```tsx
<div style={{
  width: 80,
  height: 3,
  background: `linear-gradient(90deg, ${colors.accent}, ${colors.accent}44)`,
  borderRadius: 2,
}} />
```
