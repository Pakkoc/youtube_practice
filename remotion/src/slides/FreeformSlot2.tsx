import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
} from "remotion";
import { COLORS, FONT, LAYOUT, GLOW } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import { wordStagger, scaleIn, fadeSlideIn } from "../motifs/entries";
import { fadeSlideOut } from "../motifs/exits";
import { shiftingGradientOffset } from "../motifs/emphasis";
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

  const badgeAnim = scaleIn(frame, fps, zoneDelay(0.05, zone), SPRING_BOUNCY);

  const title = "데이터 격차";
  const words = title.split("");
  const gradOff = shiftingGradientOffset(frame, 120);

  const subtitleAnim = fadeSlideIn(frame, fps, zoneDelay(0.4, zone), SPRING_GENTLE);
  const subtitleExit = fadeSlideOut(frame, fps, exitStart, durationInFrames);

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />
      <AbsoluteFill style={{
        padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: 28,
      }}>

        {/* Section badge */}
        <div style={{
          position: "absolute",
          top: LAYOUT.padding.top,
          left: LAYOUT.padding.left,
          display: "flex", alignItems: "center", gap: 8,
          ...badgeAnim,
        }}>
          <div style={{
            background: COLORS.ACCENT, color: "#fff",
            fontSize: 18, fontWeight: 800, fontFamily: FONT.family,
            width: 32, height: 32, borderRadius: 8,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>J</div>
          <span style={{
            color: COLORS.MUTED, fontSize: 20, fontFamily: FONT.family,
            fontWeight: 600, letterSpacing: "0.08em",
          }}>데이터 격차</span>
        </div>

        <div style={{ textAlign: "center" }}>
          {words.map((char, i) => {
            const a = wordStagger(frame, fps, i, words.length, zone, 0, SPRING_SNAPPY);
            return (
              <span key={i} style={{
                display: "inline-block",
                fontSize: 72,
                fontWeight: 800,
                fontFamily: FONT.family,
                letterSpacing: "-0.03em",
                backgroundImage: `linear-gradient(90deg, ${COLORS.ACCENT_BRIGHT}, ${COLORS.TEAL}, ${COLORS.ACCENT_BRIGHT})`,
                backgroundSize: "200% 100%",
                backgroundPosition: `${gradOff}% 0`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                ...a,
              }}>
                {char}
              </span>
            );
          })}
        </div>

        <div style={{
          opacity: subtitleAnim.opacity * subtitleExit.opacity,
          transform: `${subtitleAnim.transform} ${subtitleExit.transform}`,
          textAlign: "center",
          maxWidth: 700,
        }}>
          <p style={{
            margin: 0, fontSize: 34, fontWeight: 500,
            fontFamily: FONT.family, color: COLORS.MUTED,
            lineHeight: 1.4, wordBreak: "keep-all",
          }}>
            단순히 "많이 쓴다"가 포인트가 아님
          </p>
        </div>

      </AbsoluteFill>
      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
