import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolateColors,
} from "remotion";
import { COLORS, FONT, LAYOUT, GLOW } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import { CameraPan } from "../design/CameraPan";
import { circleReveal, fadeSlideIn } from "../motifs/entries";
import { clipCircleOut } from "../motifs/exits";
import { drawLine } from "../motifs/decorations";
import { colorShift } from "../motifs/emphasis";
import {
  getAnimationZone, zoneDelay, getExitStart,
} from "../motifs/timing";
import { SPRING_STIFF, SPRING_SNAPPY, SPRING_GENTLE } from "../motifs/springConfigs";
import type { FreeformProps } from "./types";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const zone = getAnimationZone(durationInFrames);
  const exitStart = getExitStart(durationInFrames);

  const containerClip = circleReveal(frame, fps, zoneDelay(0.05, zone), SPRING_STIFF);
  const containerExit = clipCircleOut(frame, fps, exitStart, durationInFrames);

  const dividerProgress = drawLine(frame, fps, zoneDelay(0.15, zone));

  const leftAnim = fadeSlideIn(frame, fps, zoneDelay(0.2, zone), SPRING_SNAPPY);
  const rightAnim = fadeSlideIn(frame, fps, zoneDelay(0.3, zone), SPRING_STIFF);

  const cs = colorShift(frame, fps, zoneDelay(0.35, zone), 0.9);
  const rightColor = interpolateColors(cs, [0, 1], [COLORS.MUTED, COLORS.TEAL]);

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />
      <CameraPan entranceFrames={zone} direction="right" distance={6}>
        <AbsoluteFill style={{
          padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}>

          <div style={{
            display: "flex", gap: 0, position: "relative",
            clipPath: frame >= exitStart ? containerExit.clipPath : containerClip.clipPath,
            opacity: containerClip.opacity,
          }}>

            {/* Left: labor cost */}
            <div style={{
              maxWidth: 700, width: 480, padding: "48px 44px",
              borderRadius: "20px 0 0 20px",
              background: `${COLORS.ACCENT}08`,
              border: `1px solid ${COLORS.ACCENT}25`,
              borderRight: "none",
              display: "flex", flexDirection: "column",
              alignItems: "center", gap: 24,
              ...leftAnim,
            }}>
              <svg width={48} height={48} viewBox="0 0 24 24" fill="none" stroke={COLORS.ACCENT} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
              <span style={{ fontSize: 38, fontWeight: 800, fontFamily: FONT.family, color: COLORS.ACCENT }}>
                인건비
              </span>
              <div style={{
                padding: "10px 20px", borderRadius: 20,
                background: `${COLORS.ACCENT}15`, border: `1px solid ${COLORS.ACCENT}25`,
              }}>
                <span style={{ fontSize: 28, fontWeight: 600, fontFamily: FONT.family, color: COLORS.ACCENT }}>
                  수배 이상
                </span>
              </div>
            </div>

            {/* Divider */}
            <div style={{
              width: 2, background: COLORS.MUTED, opacity: 0.3,
              position: "relative", overflow: "hidden", alignSelf: "stretch",
            }}>
              <div style={{
                position: "absolute", top: 0, left: 0,
                width: "100%", height: "100%",
                background: `linear-gradient(180deg, ${COLORS.ACCENT}, ${COLORS.TEAL})`,
                transformOrigin: "top",
                transform: `scaleY(${dividerProgress})`,
                opacity: dividerProgress > 0 ? 1 : 0,
              }} />
            </div>

            {/* Right: token cost */}
            <div style={{
              maxWidth: 700, width: 480, padding: "48px 44px",
              borderRadius: "0 20px 20px 0",
              background: `rgba(60,180,180,${0.03 + cs * 0.05})`,
              border: `1px solid rgba(60,180,180,${0.15 + cs * 0.25})`,
              borderLeft: "none",
              display: "flex", flexDirection: "column",
              alignItems: "center", gap: 24,
              ...rightAnim,
            }}>
              <svg width={48} height={48} viewBox="0 0 24 24" fill="none" stroke={rightColor} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              <span style={{
                fontSize: 38, fontWeight: 800, fontFamily: FONT.family,
                color: rightColor,
                textShadow: cs > 0.7 ? `0 0 12px rgba(60,180,180,0.4)` : "none",
              }}>
                토큰 비용
              </span>
              <div style={{
                padding: "10px 20px", borderRadius: 20,
                background: `${COLORS.TEAL}15`, border: `1px solid ${COLORS.TEAL}30`,
              }}>
                <span style={{ fontSize: 28, fontWeight: 600, fontFamily: FONT.family, color: COLORS.TEAL }}>
                  대체 가능
                </span>
              </div>
            </div>

          </div>

        </AbsoluteFill>
      </CameraPan>
      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
