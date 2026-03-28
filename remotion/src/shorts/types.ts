/**
 * Types for the Shorts/Reels composition.
 */

export interface ShortsWordTimestamp {
  word: string;
  startFrame: number;
  endFrame: number;
}

export interface ShortsCompositionProps extends Record<string, unknown> {
  durationInFrames?: number;
  hookTitle: string;
  hookTitleLine2?: string;
  subDetail?: string;
  videoSrc: string;
  words: ShortsWordTimestamp[];
  accentColor?: string;
  backgroundColor?: string;
  hookFontSize?: number;
  subtitleFontSize?: number;
}

/** Props for ShortsSlideWrapper — TSX slide content instead of video */
export interface ShortsSlideCompositionProps extends Record<string, unknown> {
  durationInFrames?: number;
  hookTitle: string;
  hookTitleLine2?: string;
  subDetail?: string;
  words: ShortsWordTimestamp[];
  accentColor?: string;
  backgroundColor?: string;
  hookFontSize?: number;
  subtitleFontSize?: number;
  slideIndex?: number;
  totalSlides?: number;
}

/** Layout constants — sandwich: dark hook zone / video (cover) / dark dead zone */
export const SHORTS_LAYOUT = {
  hookZoneHeight: 480,
  videoY: 480,
  videoWidth: 1080,
  videoHeight: 1280,
  subtitleY: 1400,
  safeZone: { left: 48, right: 48 },
} as const;

/** Content zone dimensions for shorts slide TSX content */
export const SHORTS_CONTENT = {
  width: 1080,
  height: 1280,
  top: 480,
} as const;

/** Channel branding — fixed across all shorts */
export const SHORTS_BRANDING = {
  channelName: "샘호트만 : AI 엔지니어의 시선",
  seriesName: "Claude Code 왕기초",
} as const;
