/**
 * Marker-pen highlighter draw effect (scaleX from left).
 * Draws a marker-pen highlight behind text using scaleX spring.
 */
import { spring } from "remotion";

export function highlighter(
  frame: number,
  fps: number,
  delay: number = 0,
  config = { damping: 25, mass: 0.6 },
): number {
  return spring({ frame: frame - delay, fps, config });
}
