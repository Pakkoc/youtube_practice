/**
 * Design tokens — 3-Layer Design System.
 *
 *   Layer 1: Shared constants (FONT, LAYOUT) — theme-independent
 *   Layer 2: Theme presets (THEME_PRESETS) — bundled per-series tokens
 *   Layer 3: Per-card override (FreeformCardProps.colors) — runtime
 *
 * New theme 추가: THEME_PRESETS에 엔트리 1개 추가로 완료.
 */

export const COLORS = {
  BG: "#0B0C0E",
  TEXT: "#EDEDEF",
  ACCENT: "#7C7FD9",
  ACCENT_BRIGHT: "#9B9EFF",
  MUTED: "#9394A1",
  CODE_BG: "#1C1E21",
  CODE_BORDER: "#222326",
  PRE_BG: "#131416",
  TEAL: "#3CB4B4",
} as const;

/** Reusable glow/highlight styles */
export const GLOW = {
  /** Accent text glow */
  text: `0 0 20px rgba(124,127,217,0.5), 0 0 40px rgba(124,127,217,0.2)`,
  /** Subtle accent underline/bar glow */
  bar: `0 0 12px rgba(124,127,217,0.6)`,
  /** Highlight box behind bold words */
  highlightBg: "rgba(124,127,217,0.15)",
  highlightBorder: "rgba(124,127,217,0.3)",
} as const;

export const FONT = {
  family: "'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif",
  title: {
    size: 88,
    weight: 800 as const,
    letterSpacing: "-0.04em",
    lineHeight: 1.1,
  },
  bullet: {
    size: 44,
    weight: 500 as const,
    lineHeight: 1.25,
  },
  subtitle: {
    size: 36,
    weight: 500 as const,
    lineHeight: 1.4,
  },
  bigNumber: {
    size: 140,
    weight: 800 as const,
    lineHeight: 1.0,
  },
  context: {
    size: 40,
    weight: 500 as const,
    lineHeight: 1.4,
  },
} as const;

/** Quiet Luxury theme — white-based, minimal, premium feel */
export const QUIET_LUXURY = {
  BG: "#FFFFFF",
  TEXT: "#1A1A1A",
  TEXT_SECONDARY: "#555555",
  ACCENT: "#2C2C2C",
  ACCENT_WARM: "#8B7355",
  ACCENT_COOL: "#6B7B8D",
  MUTED: "#999999",
  BORDER: "#E5E5E5",
  SURFACE: "#F7F7F5",
  SURFACE_WARM: "#F5F0EB",
  CODE_BG: "#F2F2F2",
} as const;

/** Quiet Luxury shadows — subtle, no glow */
export const QL_SHADOW = {
  card: "0 2px 20px rgba(0,0,0,0.06)",
  text: "none",
  elevated: "0 8px 32px rgba(0,0,0,0.08)",
} as const;

export const LAYOUT = {
  padding: { top: 80, right: 100, bottom: 80, left: 100 },
  bulletPaddingLeft: 50,
  bulletDotSize: 12,
  bulletMarginBottom: 28,
  /** Bottom 1/3 reserved for subtitles */
  subtitleReserved: 360,
  /** Multi-column card minimum widths (Korean text safe) */
  card: { minWidth: 200, descMinWidth: 240 },
} as const;

/**
 * Style presets for Korean text safety.
 * Spread into inline styles: style={{...STYLE.cardLabel}}
 *
 * - cardLabel: 짧은 라벨 (whiteSpace: nowrap → 한 줄 강제)
 * - cardDesc:  부연 설명 (wordBreak: keep-all → 한글 단어 중간 절단 방지)
 * - cardBody:  카드/칼럼 본문 (wordBreak: keep-all)
 */
export const STYLE = {
  cardLabel: {
    fontFamily: FONT.family,
    fontSize: 32,
    fontWeight: 600 as const,
    color: COLORS.TEXT,
    whiteSpace: "nowrap" as const,
    textAlign: "center" as const,
  },
  cardDesc: {
    fontFamily: FONT.family,
    fontSize: 24,
    fontWeight: 400 as const,
    color: COLORS.MUTED,
    textAlign: "center" as const,
    lineHeight: 1.4,
    wordBreak: "keep-all" as const,
  },
  cardBody: {
    fontFamily: FONT.family,
    fontSize: 28,
    fontWeight: 500 as const,
    color: COLORS.TEXT,
    wordBreak: "keep-all" as const,
    lineHeight: 1.35,
  },
} as const;

// ─── Layer 2: Theme Presets ──────────────────────────────────

/**
 * Bundled theme preset — references Layer 1 constants above.
 * 새 테마 추가 시 colors/shadow 상수를 정의하고 여기에 엔트리 추가.
 */
export const THEME_PRESETS = {
  dark: {
    name: "Dark Tech",
    colors: COLORS,
    shadow: GLOW,
    typography: { titleWeight: 800 as const, bodyWeight: 500 as const, letterSpacing: "-0.04em" },
    effects: { glow: true, glass: true, gradients: true },
  },
  "quiet-luxury": {
    name: "Quiet Luxury",
    colors: QUIET_LUXURY,
    shadow: QL_SHADOW,
    typography: { titleWeight: 800 as const, bodyWeight: 300 as const, letterSpacing: "-0.03em" },
    effects: { glow: false, glass: false, gradients: false },
  },
} as const;

/** Available theme names */
export type ThemeName = keyof typeof THEME_PRESETS;
