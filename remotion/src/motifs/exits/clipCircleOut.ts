/**
 * Clip-path circle-closing exit animation.
 * Circle shrinks from full coverage to nothing — the reverse of circleReveal.
 * Classic iris-out transition seen in cinema and premium motion graphics.
 */
import { interpolate, spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

export function clipCircleOut(
  frame: number,
  fps: number,
  exitStart: number,
  durationInFrames: number,
  config: SpringConfig = SPRING_SNAPPY,
): { clipPath: string; opacity: number } {
  if (frame < exitStart)
    return { clipPath: "circle(75% at 50% 50%)", opacity: 1 };

  const progress = spring({
    frame: frame - exitStart,
    fps,
    config,
  });

  const radius = interpolate(progress, [0, 1], [75, 0]);

  return {
    clipPath: `circle(${radius}% at 50% 50%)`,
    opacity: 1,
  };
}
