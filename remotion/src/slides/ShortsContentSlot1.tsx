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
import { fadeSlideIn, scaleIn } from "../motifs/entries";
import { getAnimationZone, zoneDelay } from "../motifs/timing";
import { SPRING_GENTLE, SPRING_BOUNCY } from "../motifs/springConfigs";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex,
  totalSlides,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const zone = getAnimationZone(durationInFrames);

  // Crosshair icon entrance
  const iconDelay = zoneDelay(0.05, zone);
  const iconAnim = scaleIn(frame, fps, iconDelay, SPRING_BOUNCY);

  // Main text entrance
  const textDelay = zoneDelay(0.35, zone);
  const textAnim = fadeSlideIn(frame, fps, textDelay, SPRING_GENTLE);

  // Underline accent
  const lineDelay = zoneDelay(0.55, zone);
  const lineProgress = spring({
    frame: frame - lineDelay,
    fps,
    config: { damping: 20, mass: 0.6 },
  });

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
          gap: 40,
        }}
      >
        {/* Target/Crosshair icon */}
        <div
          style={{
            opacity: iconAnim.opacity,
            transform: iconAnim.transform,
          }}
        >
          <svg
            width="80"
            height="80"
            viewBox="0 0 24 24"
            fill="none"
            stroke={COLORS.TEAL}
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="6" />
            <circle cx="12" cy="12" r="2" />
            <line x1="12" y1="2" x2="12" y2="6" />
            <line x1="12" y1="18" x2="12" y2="22" />
            <line x1="2" y1="12" x2="6" y2="12" />
            <line x1="18" y1="12" x2="22" y2="12" />
          </svg>
        </div>

        {/* Main text with underline */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 16,
            opacity: textAnim.opacity,
            transform: textAnim.transform,
          }}
        >
          <span
            style={{
              fontFamily: FONT.family,
              fontSize: 52,
              fontWeight: 800,
              color: COLORS.TEXT,
              textAlign: "center",
              wordBreak: "keep-all" as const,
              letterSpacing: "-0.02em",
            }}
          >
            핵심
          </span>

          {/* Animated underline */}
          <div
            style={{
              height: 4,
              width: 120,
              background: `linear-gradient(90deg, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
              borderRadius: 2,
              transformOrigin: "center",
              transform: `scaleX(${lineProgress})`,
            }}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
