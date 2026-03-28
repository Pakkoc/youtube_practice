/**
 * Slide from bottom entrance (translateY 40 -> 0).
 */
import { interpolate, spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

export function slideFromBottom(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_SNAPPY,
): { opacity: number; transform: string } {
  const progress = spring({ frame: frame - delay, fps, config });
  return {
    opacity: progress,
    transform: `translateY(${interpolate(progress, [0, 1], [40, 0])}px)`,
  };
}
