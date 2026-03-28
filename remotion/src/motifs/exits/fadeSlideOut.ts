/**
 * Fade + slide-down exit animation.
 * Mirror of fadeSlideIn — content slides down and fades out.
 */
import { interpolate, spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

/**
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param exitStart - Frame where this item's exit begins
 * @param durationInFrames - Total slide duration
 * @param config - Spring config (default SPRING_SNAPPY for quick exit)
 */
export function fadeSlideOut(
  frame: number,
  fps: number,
  exitStart: number,
  durationInFrames: number,
  config: SpringConfig = SPRING_SNAPPY,
): { opacity: number; transform: string } {
  if (frame < exitStart) return { opacity: 1, transform: "translateY(0px)" };

  const progress = spring({
    frame: frame - exitStart,
    fps,
    config,
  });

  return {
    opacity: interpolate(progress, [0, 1], [1, 0]),
    transform: `translateY(${interpolate(progress, [0, 1], [0, 25])}px)`,
  };
}
