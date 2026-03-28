/**
 * SVG stroke draw animation via strokeDashoffset.
 * Animates SVG paths via strokeDashoffset for draw-on effects.
 */
import { interpolate, spring } from "remotion";

/**
 * Returns strokeDashoffset for an SVG path draw animation.
 * @param totalLength - Total stroke dash length (e.g. 120)
 */
export function svgStrokeDraw(
  frame: number,
  fps: number,
  totalLength: number,
  delay: number = 0,
  config = { damping: 20, mass: 0.8 },
): number {
  const progress = spring({ frame: frame - delay, fps, config });
  return interpolate(progress, [0, 1], [totalLength, 0]);
}
