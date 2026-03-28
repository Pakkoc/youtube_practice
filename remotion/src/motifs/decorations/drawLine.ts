/**
 * Horizontal line draw animation (scaleX from left or center).
 * Horizontal line draw animation using scaleX spring.
 */
import { spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

/** Returns scaleX progress (0 to 1) for a horizontal line draw. */
export function drawLine(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_SNAPPY,
): number {
  return spring({ frame: frame - delay, fps, config });
}
