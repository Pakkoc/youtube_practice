/**
 * Blur-out exit animation.
 * Content blurs and fades, reversing the blurReveal entrance.
 * Creates a dreamy, cinematic dissolve feel.
 */
import { interpolate, spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

export function blurOut(
  frame: number,
  fps: number,
  exitStart: number,
  durationInFrames: number,
  config: SpringConfig = SPRING_SNAPPY,
): { opacity: number; transform: string; filter: string } {
  if (frame < exitStart)
    return { opacity: 1, transform: "scale(1)", filter: "none" };

  const progress = spring({
    frame: frame - exitStart,
    fps,
    config,
  });

  const blur = interpolate(progress, [0, 1], [0, 10]);
  const scale = interpolate(progress, [0, 1], [1, 1.04]);

  return {
    opacity: interpolate(progress, [0, 1], [1, 0]),
    transform: `scale(${scale})`,
    filter: `blur(${blur}px)`,
  };
}
