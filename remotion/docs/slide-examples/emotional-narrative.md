# Emotional Narrative — 감성/서사 슬라이드

## 언제 사용

스토리텔링, 극적 전환, 감성적 메시지, 변화의 순간, 깨달음.
인용문 한 줄이 슬라이드 전체를 채우는 경우. 데이터·차트 슬라이드에는 부적합.

## 핵심 기법

- `blurReveal` + `blurOut` — 시네마틱 등장/퇴장 쌍 (인용문 히어로 1개)
- `CameraMotion` — 홀드 구간 줌+드리프트 (정적인 슬라이드에 생동감 부여)
- `GradientShift` — 감성 배경 색상 순환 (분위기 조성)
- `breathe` — 장식 요소에 자연스러운 호흡 스케일 (아이콘 전용)
- `shiftingGradientOffset` — 강조 단어 사이클링 그라디언트
- `SPRING_GENTLE` — 사색적·공감적 분위기 (감성 슬라이드 전용 프리셋)
- `fadeSlideIn` — 화자/출처 텍스트 등장 (SPRING_GENTLE, 늦은 진입)
- `getAnimationZone` + `zoneDelay` — 하드코딩 프레임 없이 타이밍 관리
- `getExitStart` — 퇴장 타이밍 계산

## TSX

```tsx
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
import { CameraMotion } from "../design/CameraMotion";
import { GradientShift } from "../design/GradientShift";
import { blurReveal, fadeSlideIn } from "../motifs/entries";
import { blurOut } from "../motifs/exits";
import { breathe, shiftingGradientOffset } from "../motifs/emphasis";
import {
  getAnimationZone, zoneDelay, getExitStart,
} from "../motifs/timing";
import { SPRING_GENTLE, SPRING_SNAPPY } from "../motifs/springConfigs";
import type { FreeformProps } from "./types";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // --- 타이밍 ---
  const zone = getAnimationZone(durationInFrames, { fps });
  const exitStart = getExitStart(durationInFrames, { fps });

  // --- 아이콘: 전구 SVG (깨달음) ---
  const iconDelay = zoneDelay(0.0, zone);
  const iconAnim = fadeSlideIn(frame, fps, iconDelay, SPRING_GENTLE);
  const iconExit = blurOut(frame, fps, exitStart, durationInFrames);
  // breathe: 아이콘에만 사용, 홀드 구간 호흡 스케일
  const iconScale = breathe(frame, fps, zone, 0.04, 0.28);

  // --- 인용문 히어로: blurReveal ---
  const quoteDelay = zoneDelay(0.18, zone);
  const quoteAnim = blurReveal(frame, fps, quoteDelay, SPRING_GENTLE);
  const quoteExit = blurOut(frame, fps, exitStart, durationInFrames);

  // --- 강조 단어 그라디언트 (사이클링) ---
  const gradOffset = shiftingGradientOffset(frame, 200);

  // --- 구분선: 빠른 등장 ---
  const dividerDelay = zoneDelay(0.48, zone);
  const dividerAnim = fadeSlideIn(frame, fps, dividerDelay, SPRING_SNAPPY);
  const dividerExit = blurOut(frame, fps, exitStart, durationInFrames);

  // --- 화자/출처: 늦게 등장 ---
  const sourceDelay = zoneDelay(0.62, zone);
  const sourceAnim = fadeSlideIn(frame, fps, sourceDelay, SPRING_GENTLE);
  const sourceExit = blurOut(frame, fps, exitStart, durationInFrames);

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />

      {/* 감성 배경 그라디언트 순환 */}
      <GradientShift
        speed={0.08}
        direction={135}
        colors={[
          "rgba(124,127,217,0.07)",
          "rgba(60,180,180,0.05)",
          "rgba(155,158,255,0.06)",
        ]}
      />

      <CameraMotion entranceFrames={zone} maxZoom={1.02} driftX={4} driftY={3}>
        <AbsoluteFill style={{
          padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}>

          {/* 전구 SVG 아이콘 (깨달음) */}
          <div style={{
            opacity: iconAnim.opacity * iconExit.opacity,
            transform: `${iconAnim.transform ?? ""} scale(${iconScale}) ${iconExit.transform ?? ""}`.trim(),
            filter: iconExit.filter,
            marginBottom: 44,
          }}>
            <svg
              width={68} height={68}
              viewBox="0 0 24 24"
              fill="none"
              stroke={COLORS.ACCENT_BRIGHT}
              strokeWidth={1.6}
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="9" y1="18" x2="15" y2="18" />
              <line x1="10" y1="22" x2="14" y2="22" />
              <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14" />
            </svg>
          </div>

          {/* 인용문 히어로 */}
          <div style={{
            ...quoteAnim,
            opacity: quoteAnim.opacity * quoteExit.opacity,
            filter: [quoteAnim.filter, quoteExit.filter].filter(Boolean).join(" ") || undefined,
            transform: `${quoteAnim.transform ?? ""} ${quoteExit.transform ?? ""}`.trim() || undefined,
            maxWidth: 1120,
            textAlign: "center",
            marginBottom: 36,
          }}>
            {/* 따옴표 장식 */}
            <span style={{
              fontSize: 80,
              fontWeight: 800,
              fontFamily: FONT.family,
              color: `rgba(124,127,217,0.25)`,
              lineHeight: 0.6,
              display: "block",
              marginBottom: 8,
              letterSpacing: "-0.04em",
            }}>
              "
            </span>

            <p style={{
              fontSize: 52,
              fontWeight: 700,
              fontFamily: FONT.family,
              lineHeight: 1.25,
              color: COLORS.TEXT,
              margin: 0,
              wordBreak: "keep-all",
              letterSpacing: "-0.03em",
            }}>
              기술이 바뀌는 것이 아니라,{" "}
              <span style={{
                background: `linear-gradient(${gradOffset}deg, ${COLORS.ACCENT_BRIGHT}, ${COLORS.TEAL}, ${COLORS.ACCENT_BRIGHT})`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}>
                우리가 바뀌는 것
              </span>
              임
            </p>
          </div>

          {/* 구분선 */}
          <div style={{
            opacity: dividerAnim.opacity * dividerExit.opacity,
            transform: `${dividerAnim.transform ?? ""} ${dividerExit.transform ?? ""}`.trim() || undefined,
            filter: dividerExit.filter,
            marginBottom: 28,
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}>
            <div style={{ width: 48, height: 1, background: `rgba(124,127,217,0.35)` }} />
            <div style={{
              width: 6, height: 6, borderRadius: "50%",
              backgroundColor: COLORS.ACCENT,
              boxShadow: "0 0 8px rgba(124,127,217,0.6)",
            }} />
            <div style={{ width: 48, height: 1, background: `rgba(124,127,217,0.35)` }} />
          </div>

          {/* 화자/출처 */}
          <div style={{
            opacity: sourceAnim.opacity * sourceExit.opacity,
            transform: `${sourceAnim.transform ?? ""} ${sourceExit.transform ?? ""}`.trim() || undefined,
            filter: sourceExit.filter,
            textAlign: "center",
          }}>
            <span style={{
              fontSize: FONT.subtitle.size,
              fontWeight: 500,
              fontFamily: FONT.family,
              color: COLORS.MUTED,
              letterSpacing: "0.01em",
            }}>
              변화를 두려워하는 이들에게 — 2025
            </span>
          </div>

        </AbsoluteFill>
      </CameraMotion>

      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
```

## 변형 팁

- 인용문이 짧으면 (15자 이내) fontSize를 72-80px로 올리고 `charSplit`으로 교체 가능
- 배경 이미지 있을 때 `GradientShift` colors의 alpha를 0.04~0.05로 낮출 것
- 슬라이드가 5초 이상이면 `breathe`의 속도(speed) 인자를 0.22로 낮춰 호흡 주기 늘리기
- 아이콘을 하트로 교체: `<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />`
- 극적 전환점 슬라이드: `GradientShift` colors에 붉은 계열(`rgba(217,80,80,0.06)`) 추가
