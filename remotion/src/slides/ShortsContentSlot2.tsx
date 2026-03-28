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
import { drawBar } from "../motifs/decorations";
import { getAnimationZone, zoneDelay, staggerDelays } from "../motifs/timing";
import {
  SPRING_GENTLE,
  SPRING_SNAPPY,
  SPRING_BOUNCY,
} from "../motifs/springConfigs";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex,
  totalSlides,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const zone = getAnimationZone(durationInFrames);

  const bars = [
    { label: "1주차", pct: 0.6, color: COLORS.MUTED, value: "60%" },
    { label: "2주차", pct: 0.8, color: COLORS.ACCENT, value: "80%" },
    { label: "3주차", pct: 0.95, color: COLORS.TEAL, value: "95%" },
  ];

  // Trending Up icon entrance
  const iconDelay = zoneDelay(0, zone);
  const iconAnim = scaleIn(frame, fps, iconDelay, SPRING_BOUNCY);

  // Title entrance
  const titleDelay = zoneDelay(0.15, zone);
  const titleAnim = fadeSlideIn(frame, fps, titleDelay, SPRING_GENTLE);

  // Staggered bar delays
  const barDelays = staggerDelays(bars.length, zone, {
    offset: Math.round(zone * 0.3),
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
        {/* Trending Up SVG icon */}
        <div style={{ ...iconAnim }}>
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
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
            <polyline points="17 6 23 6 23 12" />
          </svg>
        </div>

        {/* Label */}
        <div
          style={{
            opacity: titleAnim.opacity,
            transform: titleAnim.transform,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontFamily: FONT.family,
              fontSize: 30,
              fontWeight: 700,
              color: COLORS.TEXT,
              lineHeight: 1.4,
              wordBreak: "keep-all" as const,
            }}
          >
            규칙 추가할수록 정확도 향상
          </div>
        </div>

        {/* Horizontal bar chart */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 28,
            width: "100%",
            maxWidth: 700,
          }}
        >
          {bars.map((bar, i) => {
            const barProgress = drawBar(
              frame,
              fps,
              barDelays[i],
              SPRING_SNAPPY,
            );
            const labelAnim = fadeSlideIn(
              frame,
              fps,
              barDelays[i],
              SPRING_GENTLE,
            );

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 20,
                  opacity: labelAnim.opacity,
                  transform: labelAnim.transform,
                }}
              >
                {/* Week label */}
                <div
                  style={{
                    fontFamily: FONT.family,
                    fontSize: 26,
                    fontWeight: 600,
                    color: COLORS.MUTED,
                    minWidth: 100,
                    textAlign: "right",
                    whiteSpace: "nowrap" as const,
                  }}
                >
                  {bar.label}
                </div>

                {/* Bar track */}
                <div
                  style={{
                    flex: 1,
                    height: 36,
                    background: "rgba(255,255,255,0.04)",
                    borderRadius: 8,
                    overflow: "hidden",
                    position: "relative",
                  }}
                >
                  {/* Bar fill */}
                  <div
                    style={{
                      width: `${bar.pct * 100}%`,
                      height: "100%",
                      background: bar.color,
                      borderRadius: 8,
                      transformOrigin: "left",
                      transform: `scaleX(${barProgress})`,
                      opacity: 0.85,
                    }}
                  />
                </div>

                {/* Percentage label */}
                <div
                  style={{
                    fontFamily: FONT.family,
                    fontSize: 26,
                    fontWeight: 700,
                    color: bar.color,
                    minWidth: 60,
                    whiteSpace: "nowrap" as const,
                  }}
                >
                  {bar.value}
                </div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
