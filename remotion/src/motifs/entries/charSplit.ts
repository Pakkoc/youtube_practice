/**
 * Character-level split entrance animation.
 *
 * Each character enters from a scattered/rotated state into its final position.
 * Creates a premium "assembling" effect commonly seen in title cards
 * of high-end motion graphics and movie intros.
 *
 * Use sparingly — best for short titles (1-5 words) where each character
 * deserves individual attention.
 */
import { interpolate, spring } from "remotion";
import { SPRING_GENTLE, type SpringConfig } from "../springConfigs";

export interface CharAnimState {
  opacity: number;
  transform: string;
  filter: string;
  display: string;
}

/**
 * Get animation state for a single character in a split entrance.
 *
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param charIndex - Index of this character (0-based)
 * @param totalChars - Total number of characters
 * @param animZone - Total frames allocated for entrance
 * @param delay - Global delay offset (default 0)
 * @param config - Spring config (default SPRING_GENTLE for smooth assembly)
 */
export function charSplit(
  frame: number,
  fps: number,
  charIndex: number,
  totalChars: number,
  animZone: number,
  delay: number = 0,
  config: SpringConfig = SPRING_GENTLE,
): CharAnimState {
  if (totalChars <= 0)
    return { opacity: 1, transform: "none", filter: "none", display: "inline-block" };

  // Stagger: each char starts slightly after the previous
  const available = animZone * 0.6;
  const gap = totalChars > 1 ? available / (totalChars - 1) : 0;
  // Cap gap to prevent overly slow reveals on short strings
  const cappedGap = Math.min(gap, fps * 0.08); // Max 80ms between chars
  const charDelay = delay + charIndex * cappedGap;

  const progress = spring({
    frame: frame - charDelay,
    fps,
    config,
  });

  // Deterministic scatter direction based on character index (golden angle)
  const angle = (charIndex * 137.508) % 360;
  const rad = (angle * Math.PI) / 180;
  const scatterX = Math.cos(rad) * 30;
  const scatterY = Math.sin(rad) * 20;
  const rotation = interpolate(progress, [0, 1], [(charIndex % 2 === 0 ? -15 : 15), 0]);

  const x = interpolate(progress, [0, 1], [scatterX, 0]);
  const y = interpolate(progress, [0, 1], [scatterY, 0]);
  const scale = interpolate(progress, [0, 1], [0.6, 1]);
  const blur = interpolate(progress, [0, 1], [6, 0]);

  return {
    opacity: progress,
    transform: `translate(${x}px, ${y}px) rotate(${rotation}deg) scale(${scale})`,
    filter: blur > 0.1 ? `blur(${blur}px)` : "none",
    display: "inline-block",
  };
}
