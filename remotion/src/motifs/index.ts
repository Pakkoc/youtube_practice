/**
 * Motif Library — reusable animation building blocks.
 *
 * Organized into four categories:
 * - entries:      Entrance animations (fade, slide, scale, bounce, zoom, word/char split, clip-path)
 * - exits:        Exit animations (fade, scale, blur, slide, clip-path)
 * - emphasis:     In-place effects (highlight, gradient, count-up, pulse, typewriter)
 * - decorations:  Visual ornaments (glass card, lines, bars, SVG strokes, glows, rings)
 * - transitions:  Scene-level transitions (fade in/out)
 *
 * Spring configs are centralized in springConfigs.ts.
 */

// Spring configs
export {
  SPRING_GENTLE,
  SPRING_SNAPPY,
  SPRING_BOUNCY,
  SPRING_STIFF,
  STAGGER_DELAY,
  pickSpring,
} from "./springConfigs";
export type { SpringConfig, SpringPreset } from "./springConfigs";

// Entry animations
export {
  fadeSlideIn,
  scaleIn,
  fadeIn,
  slideFromLeft,
  slideFromRight,
  slideFromBottom,
  bounceIn,
  zoomPop,
  cascadeUp,
  layeredReveal,
  blurReveal,
  wordStagger,
  charSplit,
  circleReveal,
  insetReveal,
  diagonalWipe,
} from "./entries";
export type { WordAnimState, CharAnimState, ClipRevealState } from "./entries";

// Emphasis effects
export {
  highlighter,
  shiftingGradientOffset,
  parseAnimatedNumber,
  formatAnimatedNumber,
  countUpProgress,
  pulse,
  typewriterCount,
  breathe,
  stutterStep,
  penStroke,
  jitter,
  float,
  shimmer,
  orbit,
  colorShift,
  progressReveal,
} from "./emphasis";
export type { ParsedNumber } from "./emphasis";

// Decorations
export {
  glassCardOpacity,
  drawLine,
  drawBar,
  radialGlow,
  svgStrokeDraw,
  ringScale,
} from "./decorations";

// Exit animations
export {
  fadeSlideOut,
  scaleOut,
  blurOut,
  slideOutLeft,
  slideOutRight,
  clipCircleOut,
} from "./exits";

// Transitions
export { sceneFadeOpacity } from "./transitions";

// Timing utilities (duration-proportional animations)
export { getAnimationZone, staggerDelays, zoneDelay, getExitStart, exitStaggerDelays } from "./timing";
