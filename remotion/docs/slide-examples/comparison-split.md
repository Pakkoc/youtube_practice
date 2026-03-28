# Comparison Split — 비교/대비 슬라이드

## 언제 사용

A vs B 비교, 장단점, before/after, 기존 방식 vs 새 방식.

## TSX

```tsx
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
import type { FreeformProps } from "./types";
import { fadeSlideIn, cascadeUp, insetReveal } from "../motifs/entries";
import { scaleOut } from "../motifs/exits/scaleOut";
import { getAnimationZone, zoneDelay, staggerDelays, getExitStart } from "../motifs/timing";
import { SPRING_STIFF, SPRING_SNAPPY } from "../motifs/springConfigs";
import { colorShift, drawLine } from "../motifs/decorations";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const zone = getAnimationZone(durationInFrames);
  const exitStart = getExitStart(durationInFrames);

  // ── 타이틀 ──────────────────────────────────────────────────
  const titleAnim = fadeSlideIn(frame, fps, zoneDelay(0, zone), SPRING_STIFF);
  const titleExit = scaleOut(frame, fps, exitStart, durationInFrames);

  // ── 비교 컨테이너 (insetReveal) ──────────────────────────────
  const containerClip = insetReveal(frame, fps, zoneDelay(0.1, zone), SPRING_STIFF);

  // ── 중앙 구분선 ──────────────────────────────────────────────
  const dividerProgress = drawLine(frame, fps, zoneDelay(0.15, zone));

  // ── 왼쪽 컬럼 불릿 (기존 방식) ───────────────────────────────
  const leftBullets = ["수작업 반복 작업", "느린 처리 속도", "높은 인건비"];
  const leftDelays = staggerDelays(leftBullets.length, zone, { offset: zoneDelay(0.3, zone) });

  // ── 오른쪽 컬럼 (새로운 방식) ────────────────────────────────
  const rightBullets = ["AI 자동화 처리", "실시간 대용량 처리", "비용 90% 절감"];
  const rightDelays = staggerDelays(rightBullets.length, zone, { offset: zoneDelay(0.4, zone) });

  // ── colorShift (회색 → 액센트) ───────────────────────────────
  const csProgress = colorShift(frame, fps, zoneDelay(0.35, zone), 0.9);
  const rightTitleColor = interpolateColors(csProgress, [0, 1], [COLORS.MUTED, COLORS.ACCENT]);
  const rightBorderColor = interpolateColors(csProgress, [0, 1], ["rgba(147,148,161,0.25)", "rgba(124,127,217,0.55)"]);
  const rightBgColor = interpolateColors(csProgress, [0, 1], ["rgba(28,30,33,0.5)", "rgba(124,127,217,0.07)"]);

  // ── 컨테이너 exit ─────────────────────────────────────────────
  const containerExit = scaleOut(frame, fps, exitStart, durationInFrames);

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

        {/* 타이틀 */}
        <div style={{
          marginBottom: 48,
          opacity: titleAnim.opacity * titleExit.opacity,
          transform: `${titleAnim.transform} ${titleExit.transform}`,
        }}>
          <h1 style={{
            color: COLORS.TEXT,
            fontSize: FONT.title.size - 8,
            fontWeight: FONT.title.weight,
            fontFamily: FONT.family,
            letterSpacing: FONT.title.letterSpacing,
            margin: 0,
            textAlign: "center",
          }}>
            무엇이 달라졌는가
          </h1>
        </div>

        {/* 비교 컨테이너 */}
        <div style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "stretch",
          gap: 0,
          position: "relative",
          opacity: containerClip.opacity * containerExit.opacity,
          clipPath: containerClip.clipPath,
          transform: containerExit.transform,
        }}>

          {/* ── 왼쪽: 기존 방식 ── */}
          <div style={{
            maxWidth: 700,
            width: 560,
            padding: "40px 44px",
            borderRadius: "20px 0 0 20px",
            background: "rgba(28,30,33,0.7)",
            border: "1px solid rgba(147,148,161,0.18)",
            borderRight: "none",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}>
            {/* 아이콘 — 과거/느림 */}
            <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke={COLORS.MUTED} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 16 }}>
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            <h2 style={{
              color: COLORS.MUTED,
              fontSize: 34,
              fontWeight: 700,
              fontFamily: FONT.family,
              margin: "0 0 28px 0",
              textAlign: "center",
              letterSpacing: "-0.02em",
            }}>
              기존 방식
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 18, width: "100%" }}>
              {leftBullets.map((text, i) => {
                const anim = cascadeUp(frame, fps, i, leftDelays[0], leftDelays[1] - leftDelays[0], SPRING_SNAPPY);
                return (
                  <div key={i} style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    opacity: anim.opacity,
                    transform: anim.transform,
                  }}>
                    <div style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      backgroundColor: COLORS.MUTED,
                      flexShrink: 0,
                    }} />
                    <span style={{
                      color: COLORS.MUTED,
                      fontSize: 32,
                      fontWeight: 500,
                      fontFamily: FONT.family,
                      wordBreak: "keep-all",
                    }}>
                      {text}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ── 중앙 구분선 ── */}
          <div style={{
            width: 2,
            background: COLORS.MUTED,
            opacity: 0.3,
            position: "relative",
            overflow: "hidden",
            alignSelf: "stretch",
          }}>
            <div style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              background: `linear-gradient(180deg, ${COLORS.ACCENT} 0%, ${COLORS.TEAL} 100%)`,
              transformOrigin: "top",
              scaleY: dividerProgress,
              opacity: dividerProgress > 0 ? 1 : 0,
            }} />
          </div>

          {/* ── 오른쪽: 새로운 방식 ── */}
          <div style={{
            maxWidth: 700,
            width: 560,
            padding: "40px 44px",
            borderRadius: "0 20px 20px 0",
            background: rightBgColor,
            border: `1px solid ${rightBorderColor}`,
            borderLeft: "none",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}>
            {/* 아이콘 — AI/빠름 */}
            <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke={rightTitleColor} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 16 }}>
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
            <h2 style={{
              color: rightTitleColor,
              fontSize: 34,
              fontWeight: 700,
              fontFamily: FONT.family,
              margin: "0 0 28px 0",
              textAlign: "center",
              letterSpacing: "-0.02em",
              textShadow: csProgress > 0.7 ? GLOW.text : "none",
            }}>
              새로운 방식
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 18, width: "100%" }}>
              {rightBullets.map((text, i) => {
                const anim = cascadeUp(frame, fps, i, rightDelays[0], rightDelays[1] - rightDelays[0], SPRING_STIFF);
                return (
                  <div key={i} style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    opacity: anim.opacity,
                    transform: anim.transform,
                  }}>
                    <div style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      backgroundColor: rightTitleColor,
                      flexShrink: 0,
                    }} />
                    <span style={{
                      color: COLORS.TEXT,
                      fontSize: 32,
                      fontWeight: 500,
                      fontFamily: FONT.family,
                      wordBreak: "keep-all",
                    }}>
                      {text}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      </AbsoluteFill>
      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
```

## 핵심 기법

- `insetReveal` — 비교 컨테이너 전체를 프레임-인 방식으로 극적으로 등장
- `colorShift` + `interpolateColors` — 오른쪽 컬럼 제목·테두리·배경이 회색 → 액센트로 전환
- `drawLine` — 중앙 구분선이 위에서 아래로 그려지는 애니메이션 (scaleY on inner div)
- `cascadeUp` — 각 컬럼의 불릿 항목 순차 등장
- `scaleOut` — 타이틀·컨테이너 동시 shrink 퇴장
- `SPRING_STIFF` — 결단력 있는 권위적인 느낌 (비교 슬라이드에 적합)
- `getAnimationZone` + `zoneDelay` + `staggerDelays` — 하드코딩 프레임 없음
