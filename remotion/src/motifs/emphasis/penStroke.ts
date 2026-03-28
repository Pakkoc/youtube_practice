/**
 * Pen-stroke highlighter with hand-drawn wobble.
 * Returns progress (0→1 for scaleX) and wobble (±px Y displacement).
 */
import {spring} from "remotion";
import type {SpringConfig} from "../springConfigs";

export function penStroke(
	frame: number,
	fps: number,
	delay: number = 0,
	config: SpringConfig = {damping: 22, mass: 0.7},
): {progress: number; wobble: number} {
	const progress = spring({frame: frame - delay, fps, config});
	const wobble = Math.sin(progress * Math.PI * 2.5) * 1.5;
	return {progress, wobble};
}
