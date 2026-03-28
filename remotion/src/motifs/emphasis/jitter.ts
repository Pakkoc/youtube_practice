/**
 * Deterministic micro-jitter for intentional imperfection.
 * Uses golden-angle phase separation so consecutive seeds are uncorrelated.
 * ~2s period at 30fps — reads as gentle breathing, not shaking.
 */
export function jitter(
	frame: number,
	seed: number,
	amplitude: number = 1.0,
): number {
	return Math.sin(frame * 0.1 + seed * 137.5) * amplitude;
}
