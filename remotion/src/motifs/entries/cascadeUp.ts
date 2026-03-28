/**
 * Cascade-up utility: staggered fadeSlideIn for a list of items.
 * Returns animation style for the i-th item.
 */
import { fadeSlideIn } from "./fadeSlideIn";
import { SPRING_GENTLE, STAGGER_DELAY, type SpringConfig } from "../springConfigs";

export function cascadeUp(
  frame: number,
  fps: number,
  itemIndex: number,
  baseDelay: number = 0,
  stagger: number = STAGGER_DELAY,
  config: SpringConfig = SPRING_GENTLE,
): { opacity: number; transform: string } {
  return fadeSlideIn(frame, fps, baseDelay + itemIndex * stagger, config);
}
