/**
 * Fade + slide-up entrance animation.
 * Returns { opacity, transform } to spread into style.
 */
import { interpolate, spring } from "remotion";
import { SPRING_GENTLE, type SpringConfig } from "../springConfigs";

export function fadeSlideIn(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_GENTLE,
): { opacity: number; transform: string } {
  const progress = spring({ frame: frame - delay, fps, config });
  return {
    opacity: progress,
    transform: `translateY(${interpolate(progress, [0, 1], [30, 0])}px)`,
  };
}
