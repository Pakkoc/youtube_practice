/**
 * Shifting gradient for accent words.
 * Returns backgroundPosition offset for a cycling gradient effect.
 * Cycling gradient effect for accent word emphasis.
 */

/** Returns gradient offset percentage (0-360) cycling every `loopFrames` frames. */
export function shiftingGradientOffset(
  frame: number,
  loopFrames: number = 120,
): number {
  return (frame % loopFrames) * 3;
}
