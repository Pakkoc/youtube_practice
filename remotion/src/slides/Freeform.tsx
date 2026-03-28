import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
} from "remotion";
import { COLORS, FONT } from "../design/theme";
import { useFonts } from "../design/fonts";
import { SHORTS_CONTENT } from "../shorts/types";
import type { FreeformProps } from "./types";
import { fadeSlideIn, fadeIn } from "../motifs/entries";
import { getAnimationZone, zoneDelay } from "../motifs/timing";
import { SPRING_BOUNCY, SPRING_GENTLE } from "../motifs/springConfigs";

/**
 * Slide 021 (4.13s) - Scale contrast: "많이" (dimmed) vs "핵심만 정확하게" (TEAL, prominent)
 * Elastic overshoot entrance for key phrase
 */
export const Freeform: React.FC<FreeformProps> = ({
  slideIndex,
  totalSlides,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const zone = getAnimationZone(durationInFrames);

  // "많이" appears first (large, muted, crossed out)
  const wrongDelay = zoneDelay(0.05, zone);
  const wrongAnim = fadeSlideIn(frame, fps, wrongDelay, SPRING_GENTLE);

  // Strike-through line draws across "많이"
  const strikeDelay = zoneDelay(0.3, zone);
  const strikeProgress = spring({
    frame: frame - strikeDelay,
    fps,
    config: { damping: 18, mass: 0.6 },
  });

  // "핵심만 정확하게" enters with elastic overshoot
  const rightDelay = zoneDelay(0.4, zone);
  const rightProgress = spring({
    frame: frame - rightDelay,
    fps,
    config: { damping: 6, mass: 0.6, overshootClamping: false },
  });
  const rightOpacity = interpolate(rightProgress, [0, 0.3], [0, 1], {
    extrapolateRight: "clamp",
  });
  const rightScale = interpolate(rightProgress, [0, 1], [0.4, 1]);

  // "많이" dims when "핵심만" appears
  const dimProgress = spring({
    frame: frame - rightDelay,
    fps,
    config: { damping: 20, mass: 0.8 },
  });
  const wrongDim = interpolate(dimProgress, [0, 1], [1, 0.3]);

  return (
    <AbsoluteFill
      style={{
        width: SHORTS_CONTENT.width,
        height: SHORTS_CONTENT.height,
        backgroundColor: "transparent",
      }}
    >
      <AbsoluteFill
        style={{
          padding: "140px 48px 340px 48px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          gap: 48,
        }}
      >
        {/* "많이" - large, muted, gets crossed out */}
        <div
          style={{
            position: "relative",
            opacity: wrongAnim.opacity * wrongDim,
            transform: wrongAnim.transform,
          }}
        >
          <span
            style={{
              fontFamily: FONT.family,
              fontSize: 88,
              fontWeight: 800,
              color: COLORS.MUTED,
              letterSpacing: "-0.03em",
            }}
          >
            {"많이"}
          </span>

          {/* Strike-through line */}
          <div
            style={{
              position: "absolute",
              top: "52%",
              left: -8,
              right: -8,
              height: 4,
              borderRadius: 2,
              background: "#FF6B6B",
              transformOrigin: "left center",
              transform: `scaleX(${strikeProgress})`,
            }}
          />
        </div>

        {/* Divider arrow */}
        <div
          style={{
            opacity: rightOpacity,
            transform: `scale(${interpolate(rightProgress, [0, 1], [0.5, 1])})`,
          }}
        >
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke={COLORS.TEAL}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="12" y1="5" x2="12" y2="19" />
            <polyline points="19 12 12 19 5 12" />
          </svg>
        </div>

        {/* "핵심만 정확하게" - prominent TEAL, elastic entrance */}
        <div
          style={{
            opacity: rightOpacity,
            transform: `scale(${rightScale})`,
            textAlign: "center",
          }}
        >
          <span
            style={{
              fontFamily: FONT.family,
              fontSize: 60,
              fontWeight: 800,
              color: COLORS.TEAL,
              letterSpacing: "-0.03em",
              wordBreak: "keep-all" as const,
              textShadow: `0 0 30px rgba(60,180,180,0.4)`,
            }}
          >
            {"핵심만 정확하게"}
          </span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
