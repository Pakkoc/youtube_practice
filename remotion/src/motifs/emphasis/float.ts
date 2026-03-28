/**
 * Floating Y-axis oscillation effect.
 * Activates only after entrance animation completes.
 * Returns a pixel offset for translateY — elements gently bob up and down.
 */
import { interpolate } from "remotion";

/**
 * Returns a Y pixel offset oscillating around 0.
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param startAfterFrames - Frames to wait before starting (entrance duration)
 * @param amplitude - Pixel amplitude (default 6 = ±6px)
 * @param speed - Oscillation speed in Hz (default 0.35 = gentle)
 */
export function float(
  frame: number,
  fps: number,
  startAfterFrames: number = 20,
  amplitude: number = 6,
  speed: number = 0.35,
): number {
  if (frame < startAfterFrames) return 0;

  const elapsed = frame - startAfterFrames;
  const fadeIn = interpolate(elapsed, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });
  const phase = Math.sin((elapsed / fps) * Math.PI * 2 * speed);
  return amplitude * phase * fadeIn;
}
