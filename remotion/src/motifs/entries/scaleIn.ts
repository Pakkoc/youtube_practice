/**
 * Scale-up entrance animation.
 * Returns { opacity, transform } to spread into style.
 */
import { interpolate, spring } from "remotion";
import { SPRING_GENTLE, type SpringConfig } from "../springConfigs";

export function scaleIn(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_GENTLE,
): { opacity: number; transform: string } {
  const progress = spring({ frame: frame - delay, fps, config });
  return {
    opacity: progress,
    transform: `scale(${Math.min(interpolate(progress, [0, 1], [0.5, 1]), 1)})`,
  };
}
