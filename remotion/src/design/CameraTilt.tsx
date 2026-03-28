/**
 * Subtle 3D perspective tilt oscillation.
 *
 * Applies gentle rotateX/Y wobble with CSS perspective for a premium feel.
 * Uses sine-wave oscillation (not linear drift) for natural, cinematic motion.
 */
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

interface CameraTiltProps {
  children: React.ReactNode;
  /** Frame count for entrance animations (tilt stays neutral during entrance) */
  entranceFrames?: number;
  /** Max X-axis rotation in degrees (default 1.5) */
  maxRotateX?: number;
  /** Max Y-axis rotation in degrees (default 2) */
  maxRotateY?: number;
  /** Perspective distance in pixels (default 1200) */
  perspective?: number;
}

export const CameraTilt: React.FC<CameraTiltProps> = ({
  children,
  entranceFrames = 30,
  maxRotateX = 1.5,
  maxRotateY = 2,
  perspective = 1200,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const holdStart = entranceFrames;

  // Fade-in ramp so tilt starts gradually
  const fadeIn = interpolate(frame, [holdStart, holdStart + fps * 0.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Gentle sine oscillation at different frequencies for natural feel
  const elapsed = Math.max(0, frame - holdStart);
  const rotateX = Math.sin((elapsed / fps) * Math.PI * 2 * 0.15) * maxRotateX * fadeIn;
  const rotateY = Math.sin((elapsed / fps) * Math.PI * 2 * 0.2) * maxRotateY * fadeIn;

  return (
    <AbsoluteFill
      style={{
        perspective,
      }}
    >
      <AbsoluteFill
        style={{
          transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
          willChange: "transform",
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
