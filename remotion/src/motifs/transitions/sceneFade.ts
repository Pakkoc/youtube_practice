/**
 * Scene fade logic as a pure function.
 * Returns overlay opacity for entrance/exit black fade.
 */
import { interpolate } from "remotion";

const FADE_DURATION = 0.3;

/**
 * Returns black overlay opacity (0 to 1) for smooth scene transitions.
 * High at start (entrance reveal), low in middle, high at end (exit).
 */
export function sceneFadeOpacity(
  frame: number,
  fps: number,
  durationInFrames: number,
  fadeDuration: number = FADE_DURATION,
): number {
  const fadeFrames = Math.round(fps * fadeDuration);

  const fadeInOpacity = interpolate(frame, [0, fadeFrames], [1, 0], {
    extrapolateRight: "clamp",
  });

  const fadeOutOpacity = interpolate(
    frame,
    [durationInFrames - fadeFrames, durationInFrames],
    [0, 1],
    { extrapolateLeft: "clamp" },
  );

  return Math.max(fadeInOpacity, fadeOutOpacity);
}
