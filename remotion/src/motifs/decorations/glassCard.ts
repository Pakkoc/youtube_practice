/**
 * Glassmorphism card fade-in.
 * Glassmorphism card with blur and opacity animation.
 */
import { interpolate } from "remotion";

/** Returns opacity for a glass card effect (0 to 1). */
export function glassCardOpacity(
  frame: number,
  fps: number,
  durationSeconds: number = 0.3,
): number {
  return interpolate(frame, [0, fps * durationSeconds], [0, 1], {
    extrapolateRight: "clamp",
  });
}
