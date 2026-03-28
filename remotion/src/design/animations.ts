/**
 * Shared animation presets for slide templates.
 *
 * This file re-exports from the motifs library for backwards compatibility.
 * New code should import directly from "../motifs" instead.
 */

// Spring configs
export {
  SPRING_GENTLE,
  SPRING_SNAPPY,
  SPRING_BOUNCY,
  SPRING_STIFF,
  STAGGER_DELAY,
} from "../motifs/springConfigs";

// Entry animations (existing)
export { fadeSlideIn } from "../motifs/entries/fadeSlideIn";
export { scaleIn } from "../motifs/entries/scaleIn";
export { fadeIn } from "../motifs/entries/fadeIn";
export { slideFromLeft } from "../motifs/entries/slideFromLeft";
export { slideFromRight } from "../motifs/entries/slideFromRight";

// New entry animations
export { slideFromBottom } from "../motifs/entries/slideFromBottom";
export { bounceIn } from "../motifs/entries/bounceIn";
export { zoomPop } from "../motifs/entries/zoomPop";
export { cascadeUp } from "../motifs/entries/cascadeUp";

/**
 * Vertical line draw-down animation.
 * Returns a scaleY value (0 to 1).
 */
export { drawBar as drawDown } from "../motifs/decorations/drawBar";
