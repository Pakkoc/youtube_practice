/**
 * Slide-out-right exit animation.
 * Content slides to the right and fades.
 */
import { interpolate, spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

export function slideOutRight(
  frame: number,
  fps: number,
  exitStart: number,
  durationInFrames: number,
  config: SpringConfig = SPRING_SNAPPY,
): { opacity: number; transform: string } {
  if (frame < exitStart) return { opacity: 1, transform: "translateX(0px)" };

  const progress = spring({
    frame: frame - exitStart,
    fps,
    config,
  });

  return {
    opacity: interpolate(progress, [0, 1], [1, 0]),
    transform: `translateX(${interpolate(progress, [0, 1], [0, 50])}px)`,
  };
}
