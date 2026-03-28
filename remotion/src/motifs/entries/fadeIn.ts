/**
 * Fade-in only animation.
 */
import { spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

export function fadeIn(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_SNAPPY,
): { opacity: number } {
  const progress = spring({ frame: frame - delay, fps, config });
  return { opacity: progress };
}
