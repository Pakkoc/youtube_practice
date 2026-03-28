/**
 * Progressive disclosure by information layer.
 * Unlike cascadeUp (uniform stagger), layeredReveal uses a large gap
 * between layers (reading time) and a small gap within a layer.
 */
import {spring, interpolate} from "remotion";
import {SPRING_GENTLE, type SpringConfig} from "../springConfigs";

interface LayeredRevealOptions {
	/** First layer start frame (default 0) */
	baseDelay?: number;
	/** Gap between layers in frames — reading time (default 12 = 400ms @30fps) */
	layerGap?: number;
	/** Gap between items within a layer (default 4 = 133ms @30fps) */
	itemStagger?: number;
	/** Item index within the layer (default 0) */
	itemIndex?: number;
	/** Spring config (default SPRING_GENTLE) */
	config?: SpringConfig;
	/** translateY distance in px (default 25) */
	distance?: number;
}

export function layeredReveal(
	frame: number,
	fps: number,
	layer: number,
	options: LayeredRevealOptions = {},
): {opacity: number; transform: string} {
	const {
		baseDelay = 0,
		layerGap = 12,
		itemStagger = 4,
		itemIndex = 0,
		config = SPRING_GENTLE,
		distance = 25,
	} = options;
	const delay = baseDelay + layer * layerGap + itemIndex * itemStagger;
	const progress = spring({frame: frame - delay, fps, config});
	return {
		opacity: progress,
		transform: `translateY(${interpolate(progress, [0, 1], [distance, 0])}px)`,
	};
}
