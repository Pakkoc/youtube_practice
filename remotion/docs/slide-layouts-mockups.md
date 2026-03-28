# Layout: UI Mockups

> App windows, chat UIs, service panels, callouts, badges.
> Use for product/service UX explanation slides.

---

### A. Document Frame
Mockup of a document/editor interface.
```tsx
const frameAnim = scaleIn(frame, fps, 6, SPRING_GENTLE);
<div style={{
  width: 700,
  borderRadius: 16,
  overflow: "hidden",
  border: `1px solid rgba(255,255,255,0.1)`,
  background: COLORS.CODE_BG,
  ...frameAnim,
}}>
  {/* Title bar */}
  <div style={{
    padding: "12px 16px",
    display: "flex",
    gap: 8,
    borderBottom: "1px solid rgba(255,255,255,0.06)",
  }}>
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F57" }} />
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FEBC2E" }} />
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28C840" }} />
  </div>
  {/* Content area */}
  <div style={{ padding: "24px 28px" }}>
    {/* Add document content lines here */}
  </div>
</div>
```

### B. App Window Chat Mockup
macOS-style window with chat bubbles. Use for AI/chatbot service UX topics.
```tsx
const windowAnim = scaleIn(frame, fps, 4, SPRING_GENTLE);

const messages = [
  { role: "user" as const, text: "사용자 메시지" },
  { role: "ai" as const, text: "AI 응답 메시지" },
];

{/* Window container */}
<div style={{
  width: 640,
  borderRadius: 16,
  overflow: "hidden",
  border: `1px solid rgba(255,255,255,0.1)`,
  background: COLORS.CODE_BG,
  ...windowAnim,
}}>
  {/* macOS title bar */}
  <div style={{
    padding: "12px 16px",
    display: "flex",
    gap: 8,
    borderBottom: "1px solid rgba(255,255,255,0.06)",
  }}>
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F57" }} />
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FEBC2E" }} />
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28C840" }} />
  </div>
  {/* Chat area */}
  <div style={{ padding: "24px 28px", display: "flex", flexDirection: "column", gap: 16 }}>
    {messages.map((msg, i) => {
      const bubbleAnim = fadeSlideIn(frame, fps, 10 + i * 8, SPRING_SNAPPY);
      const isUser = msg.role === "user";
      return (
        <div key={i} style={{
          display: "flex",
          justifyContent: isUser ? "flex-end" : "flex-start",
          ...bubbleAnim,
        }}>
          <div style={{
            padding: "12px 20px",
            borderRadius: 16,
            maxWidth: "75%",
            background: isUser ? COLORS.ACCENT : "rgba(255,255,255,0.08)",
            color: isUser ? "#000" : COLORS.TEXT,
            fontSize: 28,
            fontFamily: FONT.family,
            fontWeight: 500,
            lineHeight: "1.5",
          }}>{msg.text}</div>
        </div>
      );
    })}
  </div>
  {/* Input bar */}
  <div style={{
    padding: "12px 28px 16px",
    borderTop: "1px solid rgba(255,255,255,0.06)",
  }}>
    <div style={{
      height: 40,
      borderRadius: 20,
      background: "rgba(255,255,255,0.06)",
      border: "1px solid rgba(255,255,255,0.1)",
    }} />
  </div>
</div>
```

### C. App Window Service Mockup
Window with action buttons/cards instead of chat. Use for structured AI service UX.
```tsx
const windowAnim = scaleIn(frame, fps, 4, SPRING_GENTLE);

const actions = [
  { icon: "document", label: "계약서 분석하기" },
  { icon: "search", label: "법적 리스크 확인" },
  { icon: "target", label: "조항 해석 도우미" },
];

{/* Window container */}
<div style={{
  width: 520,
  borderRadius: 16,
  overflow: "hidden",
  border: `1px solid ${COLORS.ACCENT}40`,
  background: `linear-gradient(180deg, rgba(0,255,136,0.06) 0%, ${COLORS.CODE_BG} 100%)`,
}}>
  {/* Header */}
  <div style={{
    padding: "20px 28px 12px",
    ...windowAnim,
  }}>
    <span style={{
      color: COLORS.ACCENT,
      fontSize: 28,
      fontFamily: FONT.family,
      fontWeight: 700,
    }}>나의 서비스</span>
  </div>
  {/* Action cards */}
  <div style={{ padding: "8px 28px 28px", display: "flex", flexDirection: "column", gap: 12 }}>
    {actions.map((action, i) => {
      const cardAnim = fadeSlideIn(frame, fps, 8 + i * 6, SPRING_SNAPPY);
      return (
        <div key={i} style={{
          padding: "14px 20px",
          borderRadius: 12,
          border: `1px solid rgba(255,255,255,0.08)`,
          background: "rgba(255,255,255,0.04)",
          display: "flex",
          alignItems: "center",
          gap: 12,
          ...cardAnim,
        }}>
          {/* Insert icon SVG here */}
          <span style={{
            color: COLORS.TEXT,
            fontSize: 26,
            fontFamily: FONT.family,
            fontWeight: 500,
          }}>{action.label}</span>
        </div>
      );
    })}
  </div>
</div>
```

### D. Side-by-Side App Compare
Two windows side-by-side (e.g., "Chat UI" vs "Button UI"). Use for UX pattern comparison.
```tsx
const panels = [
  { title: "채팅 UI", highlight: false, content: "window" as const },
  { title: "버튼 UI", highlight: true, content: "cards" as const },
];

<div style={{
  display: "flex",
  gap: 40,
  justifyContent: "center",
  maxWidth: 800,
}}>
  {panels.map((panel, i) => {
    const panelAnim = fadeSlideIn(frame, fps, 6 + i * 8, SPRING_SNAPPY);
    const isHighlighted = panel.highlight;
    return (
      <div key={i} style={{
        width: 360,
        display: "flex",
        flexDirection: "column",
        gap: 20,
        alignItems: "center",
        ...panelAnim,
      }}>
        {/* Panel title */}
        <span style={{
          fontSize: 34,
          fontFamily: FONT.family,
          fontWeight: 800,
          color: isHighlighted ? COLORS.ACCENT : COLORS.TEXT,
        }}>{panel.title}</span>
        {/* Panel window */}
        <div style={{
          width: "100%",
          minHeight: 240,
          borderRadius: 16,
          border: `1px solid ${isHighlighted ? COLORS.ACCENT + "60" : "rgba(255,255,255,0.1)"}`,
          background: isHighlighted
            ? `linear-gradient(180deg, rgba(0,255,136,0.06) 0%, ${COLORS.CODE_BG} 100%)`
            : COLORS.CODE_BG,
          padding: 24,
        }}>
          {/* Fill with chat bubbles or action cards */}
        </div>
        {/* Caption below */}
        <div style={{
          padding: "10px 24px",
          borderRadius: 12,
          background: isHighlighted ? `${COLORS.ACCENT}15` : "rgba(255,255,255,0.04)",
          border: `1px solid ${isHighlighted ? COLORS.ACCENT + "30" : "rgba(255,255,255,0.06)"}`,
        }}>
          <span style={{
            color: isHighlighted ? COLORS.ACCENT : COLORS.MUTED,
            fontSize: 28,
            fontFamily: FONT.family,
            fontWeight: 600,
          }}>{isHighlighted ? "아, 이거 누르면 되는구나!" : "뭘 써야 할지 모름"}</span>
        </div>
      </div>
    );
  })}
</div>
```

### E. Warning Callout
Highlighted callout box for important messages.
```tsx
const calloutAnim = fadeSlideIn(frame, fps, 8, SPRING_SNAPPY);
<div style={{
  display: "flex",
  gap: 16,
  padding: "24px 32px",
  borderRadius: 12,
  border: `1px solid rgba(245,158,11,0.3)`,
  background: "rgba(245,158,11,0.08)",
  maxWidth: 800,
  ...calloutAnim,
}}>
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 2 }}>
    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>
  <span style={{
    color: COLORS.TEXT,
    fontSize: FONT.bullet.size,
    fontFamily: FONT.family,
    fontWeight: FONT.bullet.weight,
    lineHeight: String(FONT.bullet.lineHeight),
  }}>주의할 내용</span>
</div>
```

### F. Badge / Pill
Section label badge for top-left corner.
```tsx
const badgeAnim = fadeSlideIn(frame, fps, 4, SPRING_STIFF);
<div style={{
  position: "absolute",
  top: LAYOUT.padding.top,
  left: LAYOUT.padding.left,
  display: "flex",
  alignItems: "center",
  gap: 8,
  ...badgeAnim,
}}>
  <div style={{
    background: COLORS.ACCENT,
    color: "#fff",
    fontSize: 24,
    fontWeight: 800,
    fontFamily: FONT.family,
    width: 32,
    height: 32,
    borderRadius: 8,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  }}>01</div>
  <span style={{
    color: COLORS.MUTED,
    fontSize: 26,
    fontFamily: FONT.family,
    fontWeight: 600,
    textTransform: "uppercase" as const,
    letterSpacing: "0.08em",
  }}>SECTION LABEL</span>
</div>
```
