/**
 * Scale-down exit animation.
 * Content shrinks slightly and fades out.
 */
import { interpolate, spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

export function scaleOut(
  frame: number,
  fps: number,
  exitStart: number,
  durationInFrames: number,
  config: SpringConfig = SPRING_SNAPPY,
): { opacity: number; transform: string } {
  if (frame < exitStart) return { opacity: 1, transform: "scale(1)" };

  const progress = spring({
    frame: frame - exitStart,
    fps,
    config,
  });

  return {
    opacity: interpolate(progress, [0, 1], [1, 0]),
    transform: `scale(${interpolate(progress, [0, 1], [1, 0.92])})`,
  };
}
