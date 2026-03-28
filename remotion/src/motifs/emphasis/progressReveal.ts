/**
 * Left-to-right text color fill (karaoke-style progress).
 * Returns 0-100 percentage for use as a CSS gradient stop.
 * Example: background: linear-gradient(90deg, activeColor ${p}%, inactiveColor ${p}%)
 *          + WebkitBackgroundClip: "text"
 *
 * Internally delegates to colorShift (same eased interpolation, scaled to 0-100).
 */
import { colorShift } from "./colorShift";

/**
 * Returns 0-100 progress percentage for text fill reveal.
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param delay - Delay in frames before reveal starts (default 0)
 * @param durationSeconds - Total reveal duration in seconds (default 2.0)
 */
export function progressReveal(
  frame: number,
  fps: number,
  delay: number = 0,
  durationSeconds: number = 2.0,
): number {
  return colorShift(frame, fps, delay, durationSeconds) * 100;
}
