/**
 * Marp-style slide background with dark content card.
 *
 * Layer stack (back to front):
 *   1. Vertical gradient (dark teal → dark purple) — outer frame
 *   2. Dark content card (#0B0C0E, rounded corners, drop shadow)
 *      └─ B-roll image (optional, semi-transparent, clipped to card)
 *
 * Text content is rendered by each template ON TOP of this component.
 */
import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { COLORS } from "./theme";

/**
 * Marp CleanShot X gradient (matches config gradient_start / gradient_end).
 * Top: dark teal rgb(10,35,50) → Bottom: dark purple rgb(30,15,60)
 */
const GRADIENT_TOP = "rgb(10, 35, 50)";
const GRADIENT_BOTTOM = "rgb(30, 15, 60)";

/** Card margin from screen edges (px). Matches Marp stylize padding=80 scaled. */
const CARD_MARGIN = { top: 48, right: 56, bottom: 48, left: 56 };
const CARD_RADIUS = 20;

interface AnimatedBackgroundProps {
  /** Intensity (kept for API compat, currently unused). */
  intensity?: number;
  /** Show grid dots (kept for API compat, currently unused). */
  showGrid?: boolean;
  /** B-roll image filename in public/ (e.g. "_bg_001.png"). */
  backgroundImage?: string;
}

export const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({
  backgroundImage,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Gradient fade-in
  const fadeIn = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Card entrance
  const cardOpacity = interpolate(frame, [0, fps * 0.3], [0, 1], {
    extrapolateRight: "clamp",
  });
  const cardScale = spring({
    frame,
    fps,
    config: { damping: 30, mass: 0.8 },
  });

  // B-roll image inside card
  const imgFadeIn = interpolate(frame, [fps * 0.3, fps * 1.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const imgScale = interpolate(frame, [0, durationInFrames], [1.02, 1.08], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {/* 1. Marp-style vertical gradient (outer frame) */}
      <AbsoluteFill
        style={{
          opacity: fadeIn,
          background: `linear-gradient(180deg, ${GRADIENT_TOP} 0%, ${GRADIENT_BOTTOM} 100%)`,
        }}
      />

      {/* 2. Dark content card with optional B-roll image inside */}
      <AbsoluteFill
        style={{
          padding: `${CARD_MARGIN.top}px ${CARD_MARGIN.right}px ${CARD_MARGIN.bottom}px ${CARD_MARGIN.left}px`,
          opacity: cardOpacity,
          transform: `scale(${0.97 + 0.03 * cardScale})`,
        }}
      >
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "100%",
            backgroundColor: COLORS.BG,
            borderRadius: CARD_RADIUS,
            overflow: "hidden",
            boxShadow:
              "0 8px 40px rgba(0,0,0,0.6), 0 2px 8px rgba(0,0,0,0.3)",
            border: "1px solid rgba(255,255,255,0.04)",
          }}
        >
          {/* B-roll image inside card — semi-transparent */}
          {backgroundImage && (
            <Img
              src={staticFile(backgroundImage)}
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
                opacity: 0.1 * imgFadeIn,
                filter: "saturate(0.7)",
                transform: `scale(${imgScale})`,
              }}
            />
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
