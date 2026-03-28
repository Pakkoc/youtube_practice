/**
 * Decorative ring scale-up animation.
 * Decorative ring with scale-up spring animation.
 */
import { spring } from "remotion";

/** Returns ring progress (0 to 1) for scale and opacity. */
export function ringScale(
  frame: number,
  fps: number,
  delay: number = 3,
  config = { damping: 25, mass: 1.0 },
): number {
  return spring({ frame: frame - delay, fps, config });
}
