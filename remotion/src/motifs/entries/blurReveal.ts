/**
 * Blur-to-sharp entrance animation.
 * Content starts heavily blurred and gradually sharpens while fading in.
 * Premium feel — often used in high-end motion graphics for text reveals.
 */
import { interpolate, spring } from "remotion";
import { SPRING_GENTLE, type SpringConfig } from "../springConfigs";

export function blurReveal(
  frame: number,
  fps: number,
  delay: number = 0,
  config: SpringConfig = SPRING_GENTLE,
): { opacity: number; filter: string; transform: string } {
  const progress = spring({ frame: frame - delay, fps, config });
  const blur = interpolate(progress, [0, 1], [12, 0]);
  const scale = interpolate(progress, [0, 1], [1.04, 1]);

  return {
    opacity: progress,
    filter: `blur(${blur}px)`,
    transform: `scale(${scale})`,
  };
}
