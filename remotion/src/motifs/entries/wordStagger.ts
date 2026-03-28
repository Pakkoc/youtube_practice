/**
 * Word-by-word stagger reveal.
 *
 * Splits text into words and returns per-word animation state.
 * Each word enters sequentially with spring-based opacity + translateY,
 * creating the effect of text "being typed" word by word.
 *
 * The viewer's eye naturally follows the reveal order, keeping attention
 * locked on the slide content as it builds up.
 */
import { interpolate, spring } from "remotion";
import { SPRING_SNAPPY, type SpringConfig } from "../springConfigs";

export interface WordAnimState {
  opacity: number;
  transform: string;
  filter: string;
}

/**
 * Get animation state for a single word in a staggered sequence.
 *
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param wordIndex - Index of this word (0-based)
 * @param totalWords - Total number of words
 * @param animZone - Total frames allocated for entrance
 * @param delay - Global delay offset (default 0)
 * @param config - Spring config (default SPRING_SNAPPY)
 */
export function wordStagger(
  frame: number,
  fps: number,
  wordIndex: number,
  totalWords: number,
  animZone: number,
  delay: number = 0,
  config: SpringConfig = SPRING_SNAPPY,
): WordAnimState {
  if (totalWords <= 0) return { opacity: 1, transform: "none", filter: "none" };

  // Reserve 30% of zone for last word's spring to settle
  const available = animZone * 0.7;
  const gap = totalWords > 1 ? available / (totalWords - 1) : 0;
  const wordDelay = delay + wordIndex * gap;

  const progress = spring({
    frame: frame - wordDelay,
    fps,
    config,
  });

  const y = interpolate(progress, [0, 1], [18, 0]);
  const blur = interpolate(progress, [0, 1], [4, 0]);

  return {
    opacity: progress,
    transform: `translateY(${y}px)`,
    filter: blur > 0.1 ? `blur(${blur}px)` : "none",
  };
}
