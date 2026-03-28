/**
 * Quantize a smooth 0→1 progress into discrete steps.
 * Wrapping a spring with stutterStep(spring(...), 8) gives a ~12fps stutter
 * feel at 30fps, mimicking VOX-style stop-motion editing.
 */
export function stutterStep(progress: number, steps: number = 8): number {
	if (steps <= 0) return progress;
	return Math.floor(progress * steps) / steps;
}
