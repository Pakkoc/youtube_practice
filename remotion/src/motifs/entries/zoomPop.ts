/**
 * Zoom pop entrance: scale 0 -> 1.08 -> 1 (overshoot then settle).
 */
import { interpolate, spring } from "remotion";
import { SPRING_BOUNCY, type SpringConfig } from "../springConfigs";

export function zoomPop(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_BOUNCY,
): { opacity: number; transform: string } {
  const progress = spring({ frame: frame - delay, fps, config });
  // Overshoot: goes to 1.08 then settles at 1.0
  const scale = Math.min(interpolate(progress, [0, 0.7, 1], [0, 1.08, 1]), 1.08);
  return {
    opacity: Math.min(progress * 2.5, 1),
    transform: `scale(${scale})`,
  };
}
