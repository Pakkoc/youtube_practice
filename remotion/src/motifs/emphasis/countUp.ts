/**
 * Count-up animation engine for numeric values.
 * Animates numeric values from 0 to target.
 */
import { interpolate, Easing } from "remotion";

export interface ParsedNumber {
  prefix: string;
  value: number;
  suffix: string;
  decimals: number;
  useCommas: boolean;
}

/**
 * Extract the numeric core from strings like "73%", "1,200만", "약 500명".
 * Returns null if no number found.
 */
export function parseAnimatedNumber(str: string): ParsedNumber | null {
  const match = str.match(/^(.*?)([\d,]+\.?\d*)(.*?)$/);
  if (!match) return null;

  const [, prefix, numStr, suffix] = match;
  const useCommas = numStr.includes(",");
  const cleanNum = numStr.replace(/,/g, "");
  const value = parseFloat(cleanNum);
  if (isNaN(value) || value === 0) return null;

  const dotIndex = cleanNum.indexOf(".");
  const decimals = dotIndex >= 0 ? cleanNum.length - dotIndex - 1 : 0;

  return { prefix, value, suffix, decimals, useCommas };
}

/** Format the animated number back to display string with commas/decimals. */
export function formatAnimatedNumber(parsed: ParsedNumber, progress: number): string {
  const current = parsed.value * progress;

  let formatted: string;
  if (parsed.decimals > 0) {
    formatted = current.toFixed(parsed.decimals);
  } else {
    formatted = Math.round(current).toString();
  }

  if (parsed.useCommas) {
    const [intPart, decPart] = formatted.split(".");
    formatted = parseInt(intPart).toLocaleString("en-US");
    if (decPart) formatted += "." + decPart;
  }

  return parsed.prefix + formatted + parsed.suffix;
}

/**
 * Returns count-up progress (0 to 1) with ease-out cubic.
 * Duration in seconds controls how long the count-up takes.
 */
export function countUpProgress(
  frame: number,
  fps: number,
  durationSeconds: number = 1.2,
): number {
  return interpolate(frame, [0, fps * durationSeconds], [0, 1], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
}
