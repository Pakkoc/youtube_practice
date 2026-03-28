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
import { glassCardOpacity } from "../motifs/decorations";
import { getAnimationZone, zoneDelay } from "../motifs/timing";
import { SPRING_GENTLE, SPRING_SNAPPY, SPRING_BOUNCY } from "../motifs/springConfigs";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex,
  totalSlides,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const zone = getAnimationZone(durationInFrames);

  const STRUCK_RED = "rgba(255,107,107,0.5)";

  // Brain icon entrance
  const brainDelay = zoneDelay(0, zone);
  const brainAnim = scaleIn(frame, fps, brainDelay, SPRING_BOUNCY);

  // Refresh arrow animation
  const arrowDelay = zoneDelay(0.15, zone);
  const arrowRotate = spring({
    frame: frame - arrowDelay,
    fps,
    config: { damping: 12, mass: 0.7 },
  });

  // Glass card entrance
  const cardDelay = zoneDelay(0.25, zone);
  const cardOp = glassCardOpacity(frame, fps, 0.6);

  // Left label (crossed out) entrance
  const leftDelay = zoneDelay(0.4, zone);
  const leftAnim = fadeSlideIn(frame, fps, leftDelay, SPRING_GENTLE);

  // Right label (highlighted) entrance
  const rightDelay = zoneDelay(0.55, zone);
  const rightAnim = fadeSlideIn(frame, fps, rightDelay, SPRING_SNAPPY);

  // Main text entrance
  const mainDelay = zoneDelay(0.7, zone);
  const mainAnim = fadeSlideIn(frame, fps, mainDelay, SPRING_GENTLE);

  // Strikethrough animation for left label
  const strikeDelay = zoneDelay(0.5, zone);
  const strikeProgress = spring({
    frame: frame - strikeDelay,
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
          gap: 44,
        }}
      >
        {/* Brain icon with refresh arrow */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            opacity: brainAnim.opacity,
            transform: brainAnim.transform,
          }}
        >
          {/* Brain SVG */}
          <svg
            width="90"
            height="90"
            viewBox="0 0 24 24"
            fill="none"
            stroke={COLORS.TEAL}
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 2a5 5 0 015 5c0 .91-.26 1.76-.7 2.5" />
            <path d="M7 7a5 5 0 00-.7 2.5" />
            <path d="M12 2a5 5 0 00-5 5" />
            <path d="M17.3 9.5A5 5 0 0119 13a4.97 4.97 0 01-2 4" />
            <path d="M6.7 9.5A5 5 0 005 13a4.97 4.97 0 002 4" />
            <path d="M17 17a5 5 0 01-5 5 5 5 0 01-5-5" />
            <line x1="12" y1="22" x2="12" y2="12" />
          </svg>

          {/* Refresh arrow overlay */}
          <div
            style={{
              transform: `rotate(${interpolate(arrowRotate, [0, 1], [-180, 0])}deg)`,
              opacity: arrowRotate,
            }}
          >
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke={COLORS.ACCENT_BRIGHT}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
            </svg>
          </div>
        </div>

        {/* Glass card with reframe message */}
        <div
          style={{
            width: "100%",
            maxWidth: 800,
            background: "rgba(255,255,255,0.04)",
            border: `1px solid rgba(255,255,255,${0.08 * cardOp})`,
            borderRadius: 24,
            padding: "40px 40px",
            opacity: cardOp,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 36,
          }}
        >
          {/* Two-column comparison */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 48,
              width: "100%",
            }}
          >
            {/* Left: Crossed out */}
            <div
              style={{
                opacity: leftAnim.opacity,
                transform: leftAnim.transform,
                position: "relative",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontFamily: FONT.family,
                  fontSize: 32,
                  fontWeight: 700,
                  color: COLORS.MUTED,
                  wordBreak: "keep-all" as const,
                  opacity: 0.6,
                }}
              >
                기억 삭제
              </div>
              {/* Strikethrough */}
              <div
                style={{
                  position: "absolute",
                  left: -4,
                  right: -4,
                  top: "50%",
                  height: 3,
                  background: STRUCK_RED,
                  borderRadius: 2,
                  transformOrigin: "left center",
                  transform: `scaleX(${strikeProgress})`,
                }}
              />
            </div>

            {/* Arrow divider */}
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke={COLORS.ACCENT}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>

            {/* Right: Highlighted */}
            <div
              style={{
                opacity: rightAnim.opacity,
                transform: rightAnim.transform,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontFamily: FONT.family,
                  fontSize: 36,
                  fontWeight: 800,
                  color: COLORS.TEAL,
                  wordBreak: "keep-all" as const,
                }}
              >
                집중력 리셋
              </div>
              {/* Teal underline accent */}
              <div
                style={{
                  width: "100%",
                  height: 3,
                  background: COLORS.TEAL,
                  borderRadius: 2,
                  marginTop: 6,
                  opacity: 0.6,
                }}
              />
            </div>
          </div>
        </div>

        {/* Main reframe text */}
        <div
          style={{
            opacity: mainAnim.opacity,
            transform: mainAnim.transform,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontFamily: FONT.family,
              fontSize: 36,
              fontWeight: 800,
              color: COLORS.TEXT,
              lineHeight: 1.4,
              wordBreak: "keep-all" as const,
            }}
          >
            compact는{" "}
            <span style={{ color: COLORS.TEAL }}>집중력을 리셋</span>
            하는 것
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
