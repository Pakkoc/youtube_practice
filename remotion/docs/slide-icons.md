# SVG Icon Library

> Copy-paste ready SVG icons for Freeform slides.
> All icons are 80x80, viewBox 0-24, feather icon conventions (stroke-based). Exception: "(filled)" variants use fill for emphasis.

---

## SVG Stroke Animation Safety

When using `svgStrokeDraw()` with `strokeDasharray` for drawing animation:
- `strokeDasharray` value MUST equal or slightly exceed the actual SVG path perimeter
- Triangle (`M60 10 L110 100 L10 100 Z` in 120x110 viewBox): perimeter ~ 306px -> use `310`
- Circle (r=10): perimeter ~ 63px -> use `65`
- Simple line: use the line length directly
- **If unsure, overestimate by 5%** -- excess dasharray is invisible, but deficit shows missing segments

---

## Icon Entry Animation

```tsx
const iconAnim = scaleIn(frame, fps, 8, SPRING_BOUNCY);
<div style={{ ...iconAnim }}>
  {/* SVG icon here */}
</div>
```

---

## Icons

**Star**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.TEAL} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
</svg>
```

**Lightning**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT_BRIGHT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
</svg>
```

**Checkmark Circle**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.TEAL} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/>
</svg>
```

**Arrow Right**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M5 12h14M12 5l7 7-7 7"/>
</svg>
```

**Document**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.MUTED} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
</svg>
```

**Code Brackets**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT_BRIGHT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
</svg>
```

**Cloud**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.TEAL} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M18 10h-1.26A8 8 0 109 20h9a5 5 0 000-10z"/>
</svg>
```

**Search**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.MUTED} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>
```

**Warning Triangle**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
</svg>
```

**Play Circle**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/>
</svg>
```

**Gear / Settings**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.MUTED} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
</svg>
```

**Users / People**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.TEAL} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
</svg>
```

**Arrow Up**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT_BRIGHT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M12 19V5"/><path d="M5 12l7-7 7 7"/>
</svg>
```

**Arrow Down**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.MUTED} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M12 5v14"/><path d="M19 12l-7 7-7-7"/>
</svg>
```

**Triangle (Warning, stroke-animated)**
```tsx
// Perimeter: ~306px. Use strokeDasharray="310" for animation.
<svg width="80" height="80" viewBox="0 0 120 110">
  <path d="M60 10 L110 100 L10 100 Z" fill="none" stroke="#FF6B6B" strokeWidth="3" strokeLinejoin="round"
    strokeDasharray="310" strokeDashoffset={svgStrokeDraw(frame, fps, 310, 4)} />
</svg>
```

**Heart**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/>
</svg>
```

**Target / Crosshair**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.TEAL} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
</svg>
```

**Trending Up**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.TEAL} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
</svg>
```

**Trending Down**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#FF6B6B" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>
</svg>
```

**Robot / AI**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><line x1="12" y1="7" x2="12" y2="11"/><line x1="8" y1="16" x2="8" y2="16.01"/><line x1="16" y1="16" x2="16" y2="16.01"/>
</svg>
```

**Chat Bubble**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
</svg>
```

**Chat Bubble (filled, for emphasis)**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill={COLORS.ACCENT} stroke="none">
  <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
  <line x1="8" y1="10" x2="16" y2="10" stroke="#000" strokeWidth="2" strokeLinecap="round"/>
  <line x1="8" y1="14" x2="13" y2="14" stroke="#000" strokeWidth="2" strokeLinecap="round"/>
</svg>
```

**X Circle (Close / Dismiss)**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.MUTED} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
</svg>
```

**Person (single silhouette)**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.TEXT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>
</svg>
```

**Balance Scale**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.TEAL} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <line x1="12" y1="3" x2="12" y2="21"/><line x1="4" y1="7" x2="20" y2="7"/><path d="M4 7l2 6h0a3 3 0 006 0h0l2-6"/><path d="M14 7l2 6h0a3 3 0 006 0h0l2-6"/><line x1="10" y1="21" x2="14" y2="21"/>
</svg>
```

**Clipboard / Form**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/>
</svg>
```

**Question Circle**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT_BRIGHT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>
</svg>
```

**Bookmark / Save**
```tsx
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
  <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/>
</svg>
```
