/**
 * Circular orbit motion effect.
 * Returns x,y pixel offsets for an element orbiting around its resting position.
 * Use for decorative dots/rings circling a central element.
 */
import { interpolate } from "remotion";

/**
 * Returns { x, y } pixel offsets for circular orbit motion.
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param startAfterFrames - Frames to wait before starting (entrance duration)
 * @param radius - Orbit radius in pixels (default 12)
 * @param speed - Orbit speed in Hz (default 0.25)
 */
export function orbit(
  frame: number,
  fps: number,
  startAfterFrames: number = 20,
  radius: number = 12,
  speed: number = 0.25,
): { x: number; y: number } {
  if (frame < startAfterFrames) return { x: 0, y: 0 };

  const elapsed = frame - startAfterFrames;
  const fadeIn = interpolate(elapsed, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });
  const angle = (elapsed / fps) * Math.PI * 2 * speed;
  return {
    x: Math.cos(angle) * radius * fadeIn,
    y: Math.sin(angle) * radius * fadeIn,
  };
}
