/**
 * Vertical bar draw animation (scaleY).
 * Vertical bar draw animation using scaleY spring.
 */
import { spring } from "remotion";
import { SPRING_GENTLE, type SpringConfig } from "../springConfigs";

/** Returns scaleY progress (0 to 1) for a vertical bar draw. */
export function drawBar(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_GENTLE,
): number {
  return spring({ frame: frame - delay, fps, config });
}
