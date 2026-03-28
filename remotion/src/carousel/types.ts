/**
 * Types for the Carousel (card news) composition.
 * Static 1080x1350 (4:5) PNG cards for Instagram carousel.
 * Freeform TSX only — template mode removed.
 */

/** Shared color config passed from Python */
export interface CarouselColors {
  background: string;
  accent: string;
  text: string;
}

/** Freeform card props — LLM-generated TSX (Remotion-AI mode) */
export interface FreeformCardProps extends Record<string, unknown> {
  cardIndex: number;
  totalCards: number;
  colors: CarouselColors;
  backgroundImage?: string;
  /** Theme preset name (e.g. "dark", "quiet-luxury"). Used for THEME_PRESETS lookup. */
  themeName?: string;
}

/** Layout constants for 1080x1350 canvas */
export const CAROUSEL_LAYOUT = {
  width: 1080,
  height: 1350,
  padding: { top: 80, right: 72, bottom: 80, left: 72 },
  contentWidth: 1080 - 72 * 2, // 936
} as const;
