/**
 * Full-screen black overlay for smooth slide transitions.
 * Renders on top of all content — add as the LAST child of each template.
 *
 * - First 0.3s: black fades away (reveal)
 * - Last 0.3s: black fades in (exit)
 */
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

/** Fade duration in seconds */
const FADE_DURATION = 0.3;

export const SceneFade: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Limit fade to at most 25% of total duration so short slides stay visible
  const maxFadeFrames = Math.floor(durationInFrames * 0.25);
  const fadeFrames = Math.min(Math.round(fps * FADE_DURATION), maxFadeFrames);

  // Entrance: black overlay 1 → 0
  const fadeInOpacity = interpolate(frame, [0, fadeFrames], [1, 0], {
    extrapolateRight: "clamp",
  });

  // Exit: black overlay 0 → 1
  const fadeOutOpacity = interpolate(
    frame,
    [durationInFrames - fadeFrames, durationInFrames],
    [0, 1],
    { extrapolateLeft: "clamp" },
  );

  const opacity = Math.max(fadeInOpacity, fadeOutOpacity);

  if (opacity <= 0.001) return null;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "black",
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};
