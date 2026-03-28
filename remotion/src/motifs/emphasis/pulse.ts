/**
 * Pulsing glow effect using sine wave.
 * Sine-wave pulsing glow for emphasis elements.
 */
import { interpolate } from "remotion";

/**
 * Returns a pulsing intensity value (0 to ~0.45).
 * @param baseIntensity - Base glow level (default 0.3)
 * @param amplitude - Pulse amplitude (default 0.15)
 * @param speed - Pulse speed multiplier (default 0.8)
 */
export function pulse(
  frame: number,
  fps: number,
  baseIntensity: number = 0.3,
  amplitude: number = 0.15,
  speed: number = 0.8,
): number {
  const fadeIn = interpolate(frame, [0, fps * 0.6], [0, 1], {
    extrapolateRight: "clamp",
  });
  const phase = Math.sin((frame / fps) * Math.PI * speed);
  return (baseIntensity + amplitude * phase) * fadeIn;
}
