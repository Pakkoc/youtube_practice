# Hero Intro — 극적 도입 슬라이드

## 언제 사용

인트로, 오프닝, 핵심 메시지 강조, 영상 제목 등장. 첫 슬라이드에 적합.
짧고 강렬한 제목(1-5 단어)이 있을 때 사용. 긴 텍스트 목록에는 부적합.

## 핵심 기법

- `charSplit` — 글자 scatter→assemble (짧은 제목 전용, 1-8자)
- `CameraTilt` — 3D 원근 미세 틸트 (premium 히어로 슬라이드 전용)
- `AmbientParticles` — 부유 파티클 (감성·분위기용, 데이터 슬라이드에는 사용 금지)
- `fadeSlideIn` + `SPRING_GENTLE` — 부제 등장 (대형 텍스트는 GENTLE/STIFF만)
- `shiftingGradientOffset` — 강조 단어에 사이클링 그라디언트
- `blurOut` — 시네마틱 블러 디졸브 퇴장
- `getAnimationZone` + `zoneDelay` — 하드코딩 프레임 없이 타이밍 관리

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
import { CameraTilt } from "../design/CameraTilt";
import { AmbientParticles } from "../design/AmbientParticles";
import { charSplit, fadeSlideIn } from "../motifs/entries";
import { blurOut } from "../motifs/exits";
import { shiftingGradientOffset } from "../motifs/emphasis";
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

  // --- 아이콘: 번개 SVG (circleReveal 느낌으로 fadeSlideIn) ---
  const iconDelay = zoneDelay(0.0, zone);
  const iconAnim = fadeSlideIn(frame, fps, iconDelay, SPRING_GENTLE);
  const iconExit = blurOut(frame, fps, exitStart, durationInFrames);

  // --- 제목: 글자 scatter-assemble ---
  const title = "AI 혁명의 시작";
  const chars = title.split("");
  const charDelay = zoneDelay(0.12, zone);

  // --- 부제: fadeSlideIn ---
  const subtitleDelay = zoneDelay(0.55, zone);
  const subtitleAnim = fadeSlideIn(frame, fps, subtitleDelay, SPRING_GENTLE);
  const subtitleExit = blurOut(frame, fps, exitStart, durationInFrames);

  // --- 강조 단어 그라디언트 (사이클링) ---
  const gradOffset = shiftingGradientOffset(frame, 180);

  // --- 하단 레이블: 빠른 등장 ---
  const labelDelay = zoneDelay(0.72, zone);
  const labelAnim = fadeSlideIn(frame, fps, labelDelay, SPRING_SNAPPY);

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />
      <AmbientParticles count={6} opacity={0.07} color="rgba(124,127,217,1)" />

      <CameraTilt entranceFrames={zone} maxRotateX={1.5} maxRotateY={2} perspective={1200}>
        <AbsoluteFill style={{
          padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}>

          {/* 번개 SVG 아이콘 */}
          <div style={{
            marginBottom: 36,
            opacity: iconAnim.opacity * iconExit.opacity,
            transform: `${iconAnim.transform} ${iconExit.transform}`,
            filter: iconExit.filter,
          }}>
            <svg
              width={72} height={72}
              viewBox="0 0 24 24"
              fill="none"
              stroke={COLORS.ACCENT_BRIGHT}
              strokeWidth={1.8}
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          </div>

          {/* 제목: charSplit scatter-assemble */}
          <div style={{
            display: "flex",
            flexDirection: "row",
            flexWrap: "wrap",
            justifyContent: "center",
            alignItems: "center",
            marginBottom: 32,
            lineHeight: 1.1,
          }}>
            {chars.map((char, i) => {
              const anim = charSplit(frame, fps, i, chars.length, zone, charDelay, SPRING_GENTLE);
              const exit = blurOut(frame, fps, exitStart, durationInFrames);
              // 공백은 그대로 렌더
              if (char === " ") {
                return <span key={i} style={{ display: "inline-block", width: 28 }} />;
              }
              return (
                <span
                  key={i}
                  style={{
                    ...anim,
                    opacity: anim.opacity * exit.opacity,
                    filter: [anim.filter, exit.filter].filter(Boolean).join(" ") || undefined,
                    fontSize: FONT.title.size,
                    fontWeight: FONT.title.weight,
                    fontFamily: FONT.family,
                    letterSpacing: FONT.title.letterSpacing,
                    color: COLORS.TEXT,
                    textShadow: GLOW.text,
                  }}
                >
                  {char}
                </span>
              );
            })}
          </div>

          {/* 강조 단어: 사이클링 그라디언트 */}
          <div style={{
            marginBottom: 40,
            opacity: subtitleAnim.opacity * subtitleExit.opacity,
            transform: `${subtitleAnim.transform} ${subtitleExit.transform}`,
            filter: subtitleExit.filter,
          }}>
            <span style={{
              fontSize: 40,
              fontWeight: 700,
              fontFamily: FONT.family,
              background: `linear-gradient(${gradOffset}deg, ${COLORS.ACCENT_BRIGHT}, ${COLORS.TEAL}, ${COLORS.ACCENT_BRIGHT})`,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              letterSpacing: "-0.02em",
            }}>
              생성형 AI · 자동화 · 미래
            </span>
          </div>

          {/* 부제 텍스트 */}
          <div style={{
            opacity: subtitleAnim.opacity * subtitleExit.opacity,
            transform: `${subtitleAnim.transform} ${subtitleExit.transform}`,
            filter: subtitleExit.filter,
            maxWidth: 900,
            textAlign: "center",
          }}>
            <p style={{
              fontSize: FONT.subtitle.size,
              fontWeight: FONT.subtitle.weight,
              fontFamily: FONT.family,
              lineHeight: FONT.subtitle.lineHeight,
              color: COLORS.MUTED,
              margin: 0,
              wordBreak: "keep-all",
            }}>
              2025년, AI는 영상 제작의 패러다임을 바꾸고 있음
            </p>
          </div>

          {/* 하단 레이블 배지 */}
          <div style={{
            marginTop: 48,
            opacity: labelAnim.opacity,
            transform: labelAnim.transform,
          }}>
            <div style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              padding: "10px 24px",
              borderRadius: 40,
              border: `1px solid rgba(124,127,217,0.3)`,
              background: "rgba(124,127,217,0.08)",
            }}>
              <div style={{
                width: 8, height: 8, borderRadius: "50%",
                backgroundColor: COLORS.ACCENT_BRIGHT,
                boxShadow: "0 0 8px rgba(155,158,255,0.8)",
              }} />
              <span style={{
                fontSize: 28,
                fontWeight: 600,
                fontFamily: FONT.family,
                color: COLORS.ACCENT_BRIGHT,
                letterSpacing: "0.04em",
              }}>
                EPISODE 01
              </span>
            </div>
          </div>

        </AbsoluteFill>
      </CameraTilt>

      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
```

## 변형 팁

- 제목이 8자 초과이면 `charSplit` → `wordStagger`로 교체
- 배경 이미지 있을 때 `AmbientParticles` opacity를 0.04로 낮출 것
- 마지막 슬라이드(클로징)에서도 동일 패턴 사용 가능 — 부제만 CTA로 교체
