import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
} from "remotion";
import { COLORS, FONT, LAYOUT, GLOW, STYLE } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import { cascadeUp, scaleIn, fadeSlideIn } from "../motifs/entries";
import { scaleOut } from "../motifs/exits";
import { float } from "../motifs/emphasis";
import { glassCardOpacity } from "../motifs/decorations";
import {
  getAnimationZone, zoneDelay, staggerDelays, getExitStart, exitStaggerDelays,
} from "../motifs/timing";
import { SPRING_SNAPPY, SPRING_GENTLE, SPRING_BOUNCY, pickSpring } from "../motifs/springConfigs";
import type { FreeformProps } from "./types";

const ITEMS = [
  {
    label: "영상 자동화",
    color: COLORS.ACCENT,
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/>
      </svg>
    ),
  },
  {
    label: "Skills 고도화",
    color: COLORS.TEAL,
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
      </svg>
    ),
  },
  {
    label: "카드뉴스 생성",
    color: COLORS.ACCENT_BRIGHT,
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="12" y1="3" x2="12" y2="21"/>
      </svg>
    ),
  },
  {
    label: "커뮤니티 콘텐츠",
    color: "#34D399",
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 00-3-3.87"/>
        <path d="M16 3.13a4 4 0 010 7.75"/>
      </svg>
    ),
  },
];

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const zone = getAnimationZone(durationInFrames);
  const exitStart = getExitStart(durationInFrames);

  const titleAnim = fadeSlideIn(frame, fps, zoneDelay(0, zone), SPRING_GENTLE);
  const titleExit = scaleOut(frame, fps, exitStart, durationInFrames);

  const itemDelays = staggerDelays(ITEMS.length, zone, { offset: zoneDelay(0.15, zone) });
  const itemExitDelays = exitStaggerDelays(ITEMS.length, exitStart, durationInFrames);

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
          marginBottom: 48,
          opacity: titleAnim.opacity * titleExit.opacity,
          transform: `${titleAnim.transform} ${titleExit.transform}`,
          textAlign: "center",
        }}>
          <h2 style={{
            margin: 0, fontSize: 44, fontWeight: 800,
            fontFamily: FONT.family, color: COLORS.TEXT,
            letterSpacing: "-0.03em",
          }}>
            이 토큰으로 운영되는 것들
          </h2>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 280px)",
          gridTemplateRows: "repeat(2, auto)",
          gap: "24px 28px",
          maxWidth: 700,
          justifyContent: "center",
        }}>
          {ITEMS.map((item, i) => {
            const cardAnim = cascadeUp(frame, fps, i, itemDelays[0], itemDelays[1] - itemDelays[0], pickSpring(i, "energetic"));
            const cardExit = scaleOut(frame, fps, itemExitDelays[i], durationInFrames);
            const iconAnim = scaleIn(frame, fps, itemDelays[i], SPRING_BOUNCY);
            const floatY = float(frame, fps, zone, 4, 0.3 + i * 0.06);

            return (
              <div key={i} style={{
                borderRadius: 20,
                border: `1px solid ${item.color}30`,
                background: `${item.color}0C`,
                padding: "28px 24px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 14,
                opacity: cardAnim.opacity * cardExit.opacity,
                transform: `${cardAnim.transform} ${cardExit.transform}`,
              }}>
                <div style={{
                  width: 72, height: 72, borderRadius: 18,
                  border: `1px solid ${item.color}30`,
                  background: `${item.color}15`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  color: item.color,
                  opacity: iconAnim.opacity,
                  transform: `${iconAnim.transform} translateY(${floatY}px)`,
                }}>
                  {item.icon}
                </div>
                <span style={{
                  ...STYLE.cardLabel,
                  fontFamily: FONT.family,
                  color: COLORS.TEXT,
                  fontSize: 28,
                  fontWeight: 700,
                }}>
                  {item.label}
                </span>
              </div>
            );
          })}
        </div>

      </AbsoluteFill>
      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
