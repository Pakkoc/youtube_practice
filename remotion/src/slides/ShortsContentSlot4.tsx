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
import { getAnimationZone, zoneDelay } from "../motifs/timing";
import { SPRING_GENTLE, SPRING_SNAPPY, SPRING_BOUNCY } from "../motifs/springConfigs";
import { countUpProgress } from "../motifs/emphasis";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex,
  totalSlides,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const zone = getAnimationZone(durationInFrames);

  const GAUGE_GREEN = "#3CB4B4";
  const GAUGE_BG = "rgba(255,255,255,0.06)";

  // Big number entrance
  const numDelay = zoneDelay(0, zone);
  const numAnim = fadeSlideIn(frame, fps, numDelay, SPRING_SNAPPY);

  // Count-up for the 50%
  const countDelay = zoneDelay(0.05, zone);
  const countProgress = countUpProgress(frame, fps, 1.0);
  const displayNum = Math.round(interpolate(countProgress, [0, 1], [0, 50]));

  // Gauge bar entrance
  const gaugeDelay = zoneDelay(0.15, zone);
  const gaugeProgress = drawBar(frame, fps, gaugeDelay);

  // Flag/marker entrance
  const markerDelay = zoneDelay(0.4, zone);
  const markerAnim = scaleIn(frame, fps, markerDelay, SPRING_BOUNCY);

  // Label text entrance
  const labelDelay = zoneDelay(0.3, zone);
  const labelAnim = fadeSlideIn(frame, fps, labelDelay, SPRING_GENTLE);

  // Action text entrance
  const actionDelay = zoneDelay(0.55, zone);
  const actionAnim = fadeSlideIn(frame, fps, actionDelay, SPRING_GENTLE);

  // Tip text entrance
  const tipDelay = zoneDelay(0.7, zone);
  const tipAnim = fadeSlideIn(frame, fps, tipDelay, SPRING_GENTLE);

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
        {/* Big "50%" number */}
        <div
          style={{
            opacity: numAnim.opacity,
            transform: numAnim.transform,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontFamily: FONT.family,
              fontSize: 96,
              fontWeight: 800,
              color: GAUGE_GREEN,
              lineHeight: 1.0,
              letterSpacing: "-0.04em",
            }}
          >
            {displayNum}%
          </div>
        </div>

        {/* Label above gauge */}
        <div
          style={{
            opacity: labelAnim.opacity,
            transform: labelAnim.transform,
          }}
        >
          <div
            style={{
              fontFamily: FONT.family,
              fontSize: 22,
              fontWeight: 600,
              color: COLORS.MUTED,
              letterSpacing: "0.04em",
              wordBreak: "keep-all" as const,
            }}
          >
            기억 공간 사용량
          </div>
        </div>

        {/* Gauge bar */}
        <div
          style={{
            width: "85%",
            maxWidth: 700,
            position: "relative",
          }}
        >
          {/* Background track */}
          <div
            style={{
              height: 28,
              borderRadius: 14,
              background: GAUGE_BG,
              overflow: "hidden",
              position: "relative",
            }}
          >
            {/* Filled portion (50%) */}
            <div
              style={{
                height: "100%",
                width: "50%",
                background: `linear-gradient(90deg, ${COLORS.ACCENT}, ${GAUGE_GREEN})`,
                borderRadius: 14,
                transformOrigin: "left center",
                transform: `scaleX(${gaugeProgress})`,
                boxShadow: `0 0 12px ${GAUGE_GREEN}60`,
              }}
            />
          </div>

          {/* Tick marks */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginTop: 8,
              paddingLeft: 2,
              paddingRight: 2,
            }}
          >
            {[0, 25, 50, 75, 100].map((tick) => (
              <div
                key={tick}
                style={{
                  fontFamily: FONT.family,
                  fontSize: 14,
                  fontWeight: 500,
                  color: tick === 50 ? GAUGE_GREEN : `${COLORS.MUTED}80`,
                }}
              >
                {tick}
              </div>
            ))}
          </div>

          {/* Flag marker at 50% */}
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: -36,
              transform: `translateX(-50%)`,
              opacity: markerAnim.opacity,
            }}
          >
            <div
              style={{
                transform: markerAnim.transform,
              }}
            >
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill={GAUGE_GREEN}
                stroke="none"
              >
                <path d="M12 2L8 8h8L12 2z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Action text */}
        <div
          style={{
            opacity: actionAnim.opacity,
            transform: actionAnim.transform,
            textAlign: "center",
            marginTop: 12,
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
            반쯤 찼을 때{" "}
            <span style={{ color: GAUGE_GREEN }}>한 번씩 정리</span>
          </div>
        </div>

        {/* Practical tip */}
        <div
          style={{
            opacity: tipAnim.opacity,
            transform: tipAnim.transform,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontFamily: FONT.family,
              fontSize: 24,
              fontWeight: 600,
              color: COLORS.MUTED,
              lineHeight: 1.4,
              wordBreak: "keep-all" as const,
            }}
          >
            /compact 한 번이면 충분
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
