/**
 * Bouncy entrance animation (damping:8 for overshoot).
 */
import { interpolate, spring } from "remotion";
import { SPRING_BOUNCY, type SpringConfig } from "../springConfigs";

export function bounceIn(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_BOUNCY,
): { opacity: number; transform: string } {
  const progress = spring({ frame: frame - delay, fps, config });
  return {
    opacity: Math.min(progress * 2, 1),
    transform: `scale(${Math.min(interpolate(progress, [0, 1], [0.3, 1]), 1)})`,
  };
}
