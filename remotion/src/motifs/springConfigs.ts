/**
 * Centralized spring configuration presets.
 * All templates and motifs should import from here for consistency.
 */

/** Spring config type matching Remotion's spring() config parameter. */
export type SpringConfig = {
  damping: number;
  mass: number;
  stiffness?: number;
  overshootClamping?: boolean;
};

/** Gentle spring for titles and large elements */
export const SPRING_GENTLE: SpringConfig = { damping: 15, mass: 0.8 };

/** Snappy spring for bullets and small elements */
export const SPRING_SNAPPY: SpringConfig = { damping: 20, mass: 0.6 };

/** Bouncy spring for playful/dramatic entrances */
export const SPRING_BOUNCY: SpringConfig = { damping: 8, mass: 0.6 };

/** Stiff spring for quick, decisive motions */
export const SPRING_STIFF: SpringConfig = { damping: 25, mass: 0.5 };

/** Stagger delay between consecutive items (frames at 30fps = 200ms) */
export const STAGGER_DELAY = 6;

/** Spring preset names for pickSpring() */
export type SpringPreset = "varied" | "gentle" | "energetic";

const SPRING_CYCLES: Record<SpringPreset, readonly SpringConfig[]> = {
	varied: [SPRING_GENTLE, SPRING_SNAPPY, SPRING_BOUNCY, SPRING_STIFF],
	gentle: [SPRING_GENTLE, SPRING_SNAPPY, SPRING_GENTLE, SPRING_STIFF],
	energetic: [SPRING_BOUNCY, SPRING_SNAPPY, SPRING_BOUNCY, SPRING_STIFF],
};

/** Pick a spring config by index, cycling through a preset palette. */
export function pickSpring(
	index: number,
	preset: SpringPreset = "varied",
): SpringConfig {
	const cycle = SPRING_CYCLES[preset];
	return cycle[index % cycle.length];
}
