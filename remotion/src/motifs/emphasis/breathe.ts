/**
 * Subtle breathing/scale oscillation effect.
 * Activates only after entrance animation completes.
 * Amplitude is intentionally tiny (±2%) to add life without distraction.
 */
import { interpolate } from "remotion";

/**
 * Returns a scale value oscillating around 1.0.
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param startAfterFrames - Frames to wait before starting (entrance duration)
 * @param amplitude - Scale amplitude (default 0.02 = ±2%)
 * @param speed - Oscillation speed in Hz (default 0.4 = gentle)
 */
export function breathe(
  frame: number,
  fps: number,
  startAfterFrames: number = 20,
  amplitude: number = 0.02,
  speed: number = 0.4,
): number {
  if (frame < startAfterFrames) return 1.0;

  const elapsed = frame - startAfterFrames;
  const fadeIn = interpolate(elapsed, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });
  const phase = Math.sin((elapsed / fps) * Math.PI * 2 * speed);
  return 1.0 + amplitude * phase * fadeIn;
}
