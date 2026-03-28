/**
 * Subtle virtual camera motion — adds cinematic feel to static slides.
 *
 * Applies a gentle zoom-in (1.0 -> 1.025) and micro-drift over the slide's
 * hold phase. Only activates after entrance animations complete (entranceFrames).
 * The effect is intentionally subtle to avoid distracting from content.
 */
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

interface CameraMotionProps {
  children: React.ReactNode;
  /** Frame count for entrance animations (camera stays still during entrance) */
  entranceFrames?: number;
  /** Maximum zoom scale (default 1.025 = 2.5% zoom) */
  maxZoom?: number;
  /** Horizontal drift in pixels (default 4) */
  driftX?: number;
  /** Vertical drift in pixels (default 3) */
  driftY?: number;
}

export const CameraMotion: React.FC<CameraMotionProps> = ({
  children,
  entranceFrames = 30,
  maxZoom = 1.025,
  driftX = 4,
  driftY = 3,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Only animate during hold phase (after entrance, before exit)
  const holdStart = entranceFrames;
  const holdEnd = Math.max(holdStart + 1, durationInFrames);

  const progress = interpolate(frame, [holdStart, holdEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(progress, [0, 1], [1.0, maxZoom]);
  const translateX = interpolate(progress, [0, 1], [0, driftX]);
  const translateY = interpolate(progress, [0, 1], [0, -driftY]);

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
        willChange: "transform",
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
