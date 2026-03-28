/**
 * Directional drift without zoom — single-axis pan motion.
 *
 * Similar to CameraMotion but without scale — pure translate in one direction.
 * Adds a sense of movement/flow to hold-phase content.
 */
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

interface CameraPanProps {
  children: React.ReactNode;
  /** Frame count for entrance animations (camera stays still during entrance) */
  entranceFrames?: number;
  /** Pan direction (default "right") */
  direction?: "left" | "right" | "up" | "down";
  /** Pan distance in pixels (default 8) */
  distance?: number;
}

export const CameraPan: React.FC<CameraPanProps> = ({
  children,
  entranceFrames = 30,
  direction = "right",
  distance = 8,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const holdStart = entranceFrames;
  const holdEnd = Math.max(holdStart + 1, durationInFrames);

  const progress = interpolate(frame, [holdStart, holdEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  let translateX = 0;
  let translateY = 0;

  switch (direction) {
    case "right":
      translateX = progress * distance;
      break;
    case "left":
      translateX = progress * -distance;
      break;
    case "up":
      translateY = progress * -distance;
      break;
    case "down":
      translateY = progress * distance;
      break;
  }

  return (
    <AbsoluteFill
      style={{
        transform: `translate(${translateX}px, ${translateY}px)`,
        willChange: "transform",
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
