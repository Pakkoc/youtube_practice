/**
 * Clip-path based reveal animations.
 *
 * Content is revealed by animating CSS clip-path from hidden to fully visible.
 * These create cinematic transitions that feel more "editorial" than simple fades:
 *
 * - circleReveal: Expanding circle from center (spotlight effect)
 * - insetReveal: Shrinking inset rectangle (frame-in effect)
 * - diagonalWipe: Diagonal wipe across the element
 *
 * These are the CSS equivalent of After Effects track mattes —
 * the most impactful visual upgrade for minimal code complexity.
 */
import { interpolate, spring } from "remotion";
import { SPRING_GENTLE, SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

export interface ClipRevealState {
  clipPath: string;
  opacity: number;
}

/**
 * Expanding circle reveal from center (or custom origin).
 * Content appears as if a spotlight is opening on it.
 */
export function circleReveal(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_GENTLE,
  /** Origin as "X% Y%" — default "50% 50%" (center) */
  origin: string = "50% 50%",
): ClipRevealState {
  const progress = spring({ frame: frame - delay, fps, config });

  // Circle radius goes from 0% to 75% (enough to cover full element)
  const radius = interpolate(progress, [0, 1], [0, 75]);
  // Slight fade for first 20% of animation to soften the edge
  const opacity = interpolate(progress, [0, 0.2, 1], [0, 1, 1]);

  return {
    clipPath: `circle(${radius}% at ${origin})`,
    opacity,
  };
}

/**
 * Inset rectangle reveal — frame closes in from edges.
 * Creates an elegant "curtain opening" or "frame-in" effect.
 */
export function insetReveal(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_SNAPPY,
): ClipRevealState {
  const progress = spring({ frame: frame - delay, fps, config });

  // Inset goes from 50% (fully hidden) to 0% (fully visible)
  const inset = interpolate(progress, [0, 1], [50, 0]);
  // Add slight rounding during animation for premium feel
  const round = interpolate(progress, [0, 0.5, 1], [30, 15, 0]);

  return {
    clipPath: `inset(${inset}% round ${round}px)`,
    opacity: 1,
  };
}

/**
 * Diagonal wipe reveal — content appears from one corner to the opposite.
 * The most editorial of the three — feels like a page turn.
 *
 * @param direction - "topLeft" (default) or "topRight"
 */
export function diagonalWipe(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_GENTLE,
  direction: "topLeft" | "topRight" = "topLeft",
): ClipRevealState {
  const progress = spring({ frame: frame - delay, fps, config });

  // Animate polygon points to create diagonal sweep
  // The wipe travels from one corner to the diagonal opposite
  const p = interpolate(progress, [0, 1], [0, 150]); // overshoot to 150% ensures full coverage

  let clipPath: string;
  if (direction === "topLeft") {
    // Wipe from top-left to bottom-right
    clipPath = `polygon(0% 0%, ${p}% 0%, 0% ${p}%)`;
    if (p > 100) {
      clipPath = `polygon(0% 0%, 100% 0%, 100% ${p - 100}%, ${p - 100}% 100%, 0% 100%)`;
    }
    if (p >= 150) {
      clipPath = "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)";
    }
  } else {
    // Wipe from top-right to bottom-left
    clipPath = `polygon(100% 0%, ${100 - p}% 0%, 100% ${p}%)`;
    if (p > 100) {
      clipPath = `polygon(100% 0%, 0% 0%, 0% ${p - 100}%, ${100 - (p - 100)}% 100%, 100% 100%)`;
    }
    if (p >= 150) {
      clipPath = "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)";
    }
  }

  const opacity = interpolate(progress, [0, 0.1, 1], [0, 1, 1]);

  return {
    clipPath,
    opacity,
  };
}
