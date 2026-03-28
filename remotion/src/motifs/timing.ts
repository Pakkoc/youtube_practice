/**
 * Duration-proportional animation timing utilities.
 *
 * Uses an adaptive ratio that guarantees a minimum "hold" period
 * (completed state visible) at the end of every slide:
 *   ≤3s → 0.5  (50% entrance, 50% hold)
 *   ≤5s → 0.65 (65% entrance, 35% hold)
 *   ≥10s → 0.5 (50% entrance, 50% hold)
 *   5~10s → linear 0.65→0.5
 *
 * Additionally, a minimum hold of 0.5s (15 frames @30fps) is always reserved
 * so the audience can read the completed slide even on very short durations.
 */

interface AnimZoneOptions {
  /** Override the adaptive ratio with a fixed value (0-1) */
  ratio?: number;
  /** Minimum entrance frames, clamped (default 30 = 1s @30fps) */
  minFrames?: number;
  /** Maximum entrance frames, clamped (default 600 = 20s @30fps) */
  maxFrames?: number;
  /** Frames-per-second, needed for adaptive ratio (default 30) */
  fps?: number;
  /** Minimum hold frames reserved at the end (default 15 = 0.5s @30fps) */
  minHoldFrames?: number;
}

/**
 * Adaptive ratio — always reserves hold time for the completed state.
 *
 *   ≤3s  → 0.50  (short slides: half entrance, half hold)
 *   5s   → 0.65  (moderate entrance, 35% hold)
 *   ≥10s → 0.50  (long slides: generous hold)
 *   3~5s → linear 0.50→0.65
 *   5~10s → linear 0.65→0.50
 */
function adaptiveRatio(durationInFrames: number, fps: number): number {
  const sec = durationInFrames / fps;
  if (sec <= 3) return 0.5;
  if (sec <= 5) return 0.5 + ((sec - 3) / 2) * 0.15;
  if (sec >= 10) return 0.5;
  // Linear interpolation: 5s→0.65, 10s→0.5
  return 0.65 - ((sec - 5) / 5) * 0.15;
}

/**
 * Calculate the number of frames available for entrance animations.
 *
 * Guarantees a minimum hold period at the end so the completed slide
 * is visible to the audience before transitioning.
 *
 * @param durationInFrames - Total slide duration from useVideoConfig()
 * @param options - Tuning knobs
 * @returns Frame count for the animation zone
 */
export function getAnimationZone(
  durationInFrames: number,
  options?: AnimZoneOptions,
): number {
  const fps = options?.fps ?? 30;
  const ratio = options?.ratio ?? adaptiveRatio(durationInFrames, fps);
  const minFrames = options?.minFrames ?? 30;
  const maxFrames = options?.maxFrames ?? 600;
  const minHoldFrames = options?.minHoldFrames ?? 15;

  const raw = Math.round(durationInFrames * ratio);
  // Never exceed (duration - minHold) so the completed state is always visible
  const holdCap = Math.max(minFrames, durationInFrames - minHoldFrames);
  return Math.max(minFrames, Math.min(maxFrames, raw, holdCap));
}

interface StaggerOptions {
  /** Frame offset before the first item appears (default 0) */
  offset?: number;
  /** Minimum gap between items in frames (default 3) */
  minGap?: number;
  /** Maximum gap between items in frames (default 60 = 2s @30fps) */
  maxGap?: number;
  /** Frames reserved at end for last spring to settle (default 20) */
  settleFrames?: number;
}

/**
 * Distribute N items evenly across the animation zone.
 *
 * @param itemCount - Number of items to stagger
 * @param animZone - Total entrance frames from getAnimationZone()
 * @param options - Tuning knobs
 * @returns Array of frame delays, one per item
 */
export function staggerDelays(
  itemCount: number,
  animZone: number,
  options?: StaggerOptions,
): number[] {
  if (itemCount <= 0) return [];
  if (itemCount === 1) return [options?.offset ?? 0];

  const offset = options?.offset ?? 0;
  const minGap = options?.minGap ?? 3;
  const maxGap = options?.maxGap ?? 60;
  const settleFrames = options?.settleFrames ?? 20;

  const available = Math.max(0, animZone - offset - settleFrames);
  const rawGap = available / (itemCount - 1);
  const gap = Math.max(minGap, Math.min(maxGap, Math.round(rawGap)));

  return Array.from({ length: itemCount }, (_, i) =>
    Math.round(offset + i * gap),
  );
}

/**
 * Map a normalized position (0-1) to a frame delay within the animation zone.
 * Useful for single elements that should appear at a specific point in the entrance.
 *
 * @param position - 0 = start of zone, 1 = end of zone
 * @param animZone - Total entrance frames from getAnimationZone()
 * @returns Frame delay
 */
export function zoneDelay(position: number, animZone: number): number {
  return Math.round(Math.max(0, Math.min(1, position)) * animZone);
}

/* ── Exit Animation Timing ───────────────────────────────────── */

/**
 * Calculate the frame at which exit animations should begin.
 * Exit zone occupies the last 15% of slide duration (capped at 0.8s).
 * Items should start exiting at this frame and finish by durationInFrames.
 *
 * @param durationInFrames - Total slide duration
 * @param options - Tuning knobs
 * @returns Frame number where exit begins
 */
export function getExitStart(
  durationInFrames: number,
  options?: { fps?: number; exitRatio?: number; maxExitSeconds?: number },
): number {
  const fps = options?.fps ?? 30;
  const exitRatio = options?.exitRatio ?? 0.15;
  const maxExitSeconds = options?.maxExitSeconds ?? 0.8;

  const maxExitFrames = Math.round(fps * maxExitSeconds);
  const rawExitFrames = Math.round(durationInFrames * exitRatio);
  const exitFrames = Math.min(rawExitFrames, maxExitFrames);

  // Don't exit on very short slides (< 2s)
  if (durationInFrames < fps * 2) return durationInFrames;

  return durationInFrames - exitFrames;
}

/**
 * Distribute N items' exit delays across the exit zone (reverse stagger).
 * Last items exit first (reverse of entrance order).
 *
 * @param itemCount - Number of items to stagger
 * @param exitStart - Frame where exit begins (from getExitStart)
 * @param durationInFrames - Total slide duration
 * @returns Array of frame numbers where each item's exit begins
 */
export function exitStaggerDelays(
  itemCount: number,
  exitStart: number,
  durationInFrames: number,
): number[] {
  if (itemCount <= 0) return [];
  if (itemCount === 1) return [exitStart];

  const exitZone = durationInFrames - exitStart;
  // Reserve 40% of exit zone for the last item to settle
  const available = Math.max(0, exitZone * 0.6);
  const gap = available / (itemCount - 1);

  // Reverse order: last item exits first
  return Array.from({ length: itemCount }, (_, i) =>
    Math.round(exitStart + (itemCount - 1 - i) * gap),
  );
}
