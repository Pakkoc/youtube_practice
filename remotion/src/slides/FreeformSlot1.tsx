import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  spring, interpolate,
} from "remotion";
import { COLORS, FONT, LAYOUT, GLOW } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import { insetReveal, fadeSlideIn, scaleIn } from "../motifs/entries";
import { blurOut } from "../motifs/exits";
import { svgStrokeDraw } from "../motifs/decorations";
import {
  getAnimationZone, zoneDelay, getExitStart,
} from "../motifs/timing";
import { SPRING_SNAPPY, SPRING_GENTLE, SPRING_BOUNCY } from "../motifs/springConfigs";
import type { FreeformProps } from "./types";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const zone = getAnimationZone(durationInFrames);
  const exitStart = getExitStart(durationInFrames);

  const clipAnim = insetReveal(frame, fps, zoneDelay(0.05, zone), SPRING_SNAPPY);
  const exitAnim = blurOut(frame, fps, exitStart, durationInFrames);

  const cY = 480;
  const nW = 240, nH = 80;

  // Two person nodes diverging over time
  const userAX = 320, userBX = 320;
  const userAY = cY - 80, userBY = cY + 80;

  // Time arrow right
  const endAX = 1200, endBX = 1200;
  const endAY = cY - 180; // diverges up (more data)
  const endBY = cY + 180; // diverges down (less data)

  // Data result
  const dataX = 1500;

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />
      <AbsoluteFill style={{
        padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}>

        <div style={{
          position: "absolute",
          top: LAYOUT.padding.top + 10,
          left: 0, right: 0,
          textAlign: "center",
          ...fadeSlideIn(frame, fps, zoneDelay(0, zone), SPRING_GENTLE),
        }}>
          <span style={{
            fontSize: 36, fontWeight: 700, fontFamily: FONT.family, color: COLORS.MUTED,
          }}>
            시간이 지날수록 벌어지는 격차
          </span>
        </div>

        <div style={{
          ...clipAnim,
          opacity: clipAnim.opacity * exitAnim.opacity,
          filter: exitAnim.filter,
          transform: exitAnim.transform,
          position: "relative",
          width: 1920, height: 1080,
        }}>

          {/* SVG diverging lines */}
          <svg viewBox="0 0 1920 1080" style={{
            position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none",
          }}>
            {/* Top line (investor) - diverges up */}
            {(() => {
              const pathD = `M${userAX + nW / 2} ${userAY} Q${(userAX + endAX) / 2} ${userAY} ${endAX} ${endAY}`;
              const len = 600;
              const offset = svgStrokeDraw(frame, fps, len, zoneDelay(0.2, zone));
              return (
                <path d={pathD} fill="none" stroke={COLORS.TEAL} strokeWidth={3}
                  strokeDasharray={len} strokeDashoffset={offset} opacity={0.7} />
              );
            })()}
            {/* Bottom line (saver) - stays flat or diverges down */}
            {(() => {
              const pathD = `M${userBX + nW / 2} ${userBY} Q${(userBX + endBX) / 2} ${userBY} ${endBX} ${endBY}`;
              const len = 600;
              const offset = svgStrokeDraw(frame, fps, len, zoneDelay(0.25, zone));
              return (
                <path d={pathD} fill="none" stroke={COLORS.MUTED} strokeWidth={3}
                  strokeDasharray={len} strokeDashoffset={offset} opacity={0.4} />
              );
            })()}
          </svg>

          {/* User A: many tokens */}
          {(() => {
            const a = scaleIn(frame, fps, zoneDelay(0.1, zone), SPRING_BOUNCY);
            return (
              <div style={{
                position: "absolute",
                left: userAX - nW / 2, top: userAY - nH / 2,
                width: nW, height: nH, borderRadius: 16,
                border: `2px solid ${COLORS.TEAL}`,
                background: COLORS.CODE_BG,
                display: "flex", alignItems: "center", justifyContent: "center",
                boxShadow: `0 0 16px ${COLORS.TEAL}30`,
                ...a,
              }}>
                <span style={{ color: COLORS.TEAL, fontSize: 30, fontFamily: FONT.family, fontWeight: 700 }}>
                  많이 쓰는 사람
                </span>
              </div>
            );
          })()}

          {/* User B: few tokens */}
          {(() => {
            const a = scaleIn(frame, fps, zoneDelay(0.15, zone), SPRING_SNAPPY);
            return (
              <div style={{
                position: "absolute",
                left: userBX - nW / 2, top: userBY - nH / 2,
                width: nW, height: nH, borderRadius: 16,
                border: `2px solid ${COLORS.MUTED}88`,
                background: COLORS.CODE_BG,
                display: "flex", alignItems: "center", justifyContent: "center",
                ...a,
              }}>
                <span style={{ color: COLORS.MUTED, fontSize: 30, fontFamily: FONT.family, fontWeight: 700 }}>
                  아끼는 사람
                </span>
              </div>
            );
          })()}

          {/* Gap label: data */}
          {(() => {
            const a = fadeSlideIn(frame, fps, zoneDelay(0.55, zone), SPRING_GENTLE);
            return (
              <div style={{
                position: "absolute",
                left: endAX + 40, top: cY - 30,
                ...a,
              }}>
                <div style={{
                  padding: "12px 28px", borderRadius: 16,
                  background: `${COLORS.ACCENT_BRIGHT}15`,
                  border: `1px solid ${COLORS.ACCENT_BRIGHT}30`,
                }}>
                  <span style={{
                    fontSize: 36, fontWeight: 800, fontFamily: FONT.family,
                    color: COLORS.ACCENT_BRIGHT,
                  }}>
                    = 데이터
                  </span>
                </div>
              </div>
            );
          })()}

          {/* Time axis label */}
          {(() => {
            const a = fadeSlideIn(frame, fps, zoneDelay(0.4, zone), SPRING_SNAPPY);
            return (
              <div style={{
                position: "absolute",
                bottom: LAYOUT.padding.bottom + 380,
                left: 0, right: 0,
                textAlign: "center",
                ...a,
              }}>
                <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke={COLORS.MUTED} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: 8, verticalAlign: "middle" }}>
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
                <span style={{ fontSize: 26, fontWeight: 500, fontFamily: FONT.family, color: COLORS.MUTED }}>
                  시간
                </span>
              </div>
            );
          })()}

        </div>

      </AbsoluteFill>
      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
