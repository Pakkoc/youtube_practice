/**
 * Color transition progress (0 to 1).
 * Returns a normalized value for use with Remotion's interpolateColors().
 * Example: interpolateColors(colorShift(...), [0,1], ["#gray", "#accent"])
 */
import { interpolate, Easing } from "remotion";

/**
 * Returns 0-1 progress for smooth color transition.
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param delay - Delay in frames before transition starts (default 0)
 * @param durationSeconds - Transition duration in seconds (default 0.8)
 */
export function colorShift(
  frame: number,
  fps: number,
  delay: number = 0,
  durationSeconds: number = 0.8,
): number {
  const durationFrames = Math.round(fps * durationSeconds);
  return interpolate(frame, [delay, delay + durationFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.ease),
  });
}
