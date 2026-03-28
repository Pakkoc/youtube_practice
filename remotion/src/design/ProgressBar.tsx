/**
 * Minimal progress bar at the bottom of each slide.
 * Shows current position within the video (slideIndex / totalSlides).
 * Fades in with the slide content.
 */
import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS } from "./theme";

interface ProgressBarProps {
  slideIndex?: number;
  totalSlides?: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  slideIndex,
  totalSlides,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (slideIndex == null || !totalSlides || totalSlides <= 1) return null;

  const progress = Math.min(slideIndex / totalSlides, 1);

  // Bar draws from left to right
  const drawProgress = spring({
    frame: frame - 8,
    fps,
    config: { damping: 25, mass: 0.8 },
  });

  // Fade in
  const opacity = interpolate(frame, [4, fps * 0.4], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: 3,
        background: "rgba(255,255,255,0.06)",
        opacity,
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${progress * 100}%`,
          background: `linear-gradient(90deg, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
          boxShadow: `0 0 8px rgba(124,127,217,0.4)`,
          transform: `scaleX(${drawProgress})`,
          transformOrigin: "left center",
          borderRadius: "0 2px 2px 0",
        }}
      />
    </div>
  );
};
