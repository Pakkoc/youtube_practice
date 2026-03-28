/**
 * Typewriter effect: reveals characters one by one.
 * Returns the number of characters to show at the current frame.
 */
import { interpolate, Easing } from "remotion";

/**
 * @param totalChars - Total number of characters in the text
 * @param durationSeconds - How long the typing takes
 * @returns Number of characters visible at the current frame
 */
export function typewriterCount(
  frame: number,
  fps: number,
  totalChars: number,
  durationSeconds: number = 1.5,
  delay: number = 0,
): number {
  const progress = interpolate(
    frame - delay,
    [0, fps * durationSeconds],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.linear },
  );
  return Math.floor(progress * totalChars);
}
