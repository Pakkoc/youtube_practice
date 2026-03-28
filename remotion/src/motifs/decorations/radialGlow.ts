/**
 * Radial glow fade-in.
 * Radial background glow with fade-in animation.
 */
import { interpolate } from "remotion";

/** Returns glow opacity (0 to targetOpacity). */
export function radialGlow(
  frame: number,
  fps: number,
  durationSeconds: number = 0.8,
  targetOpacity: number = 0.3,
): number {
  return interpolate(frame, [0, fps * durationSeconds], [0, targetOpacity], {
    extrapolateRight: "clamp",
  });
}
