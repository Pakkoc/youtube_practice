# Statistic Number — 숫자/통계 강조 슬라이드

## 언제 사용

큰 숫자 강조, 퍼센트 변화, 성과 지표, KPI, 놀라운 통계.
단일 핵심 수치가 슬라이드 전체 메시지인 경우에 적합.
여러 숫자를 나열하는 슬라이드에는 부적합 (히어로 1개 원칙).

## 핵심 기법

- `blurReveal` — blur→sharp 프리미엄 등장 (히어로 숫자 1개 전용)
- `countUpProgress` — 0→73 숫자 카운트업 (parseAnimatedNumber + formatAnimatedNumber)
- `pulse` — 글로우 링 강조 (숫자 주변 발광 효과)
- `SPRING_BOUNCY` — 놀라움·wow 인상 (큰 숫자에 최적)
- `fadeSlideIn` — 컨텍스트 텍스트 등장 (SPRING_GENTLE로 무게감 확보)
- `radialGlow` — 배경 방사형 글로우 (분위기 조성)
- `blurOut` — 시네마틱 블러 디졸브 퇴장 (blurReveal과 쌍)
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
import { CameraMotion } from "../design/CameraMotion";
import { blurReveal, fadeSlideIn } from "../motifs/entries";
import { blurOut } from "../motifs/exits";
import {
  countUpProgress, parseAnimatedNumber, formatAnimatedNumber,
  pulse,
} from "../motifs/emphasis";
import { radialGlow } from "../motifs/decorations";
import {
  getAnimationZone, zoneDelay, getExitStart,
} from "../motifs/timing";
import { SPRING_BOUNCY, SPRING_GENTLE } from "../motifs/springConfigs";
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

  // --- 숫자 파싱 ---
  const parsed = parseAnimatedNumber("73%");
  const countProgress = countUpProgress(frame, fps, 1.6);
  const displayNumber = parsed
    ? formatAnimatedNumber(parsed, countProgress)
    : "73%";

  // --- 히어로 숫자: blurReveal ---
  const numberDelay = zoneDelay(0.05, zone);
  const numberAnim = blurReveal(frame, fps, numberDelay, SPRING_BOUNCY);
  const numberExit = blurOut(frame, fps, exitStart, durationInFrames);

  // --- 글로우 링: pulse ---
  const glowValue = pulse(frame, fps);

  // --- 배경 방사형 글로우 ---
  const bgGlow = radialGlow(frame, fps, 1.5, 0.55);

  // --- 컨텍스트 레이블: fadeSlideIn ---
  const labelDelay = zoneDelay(0.35, zone);
  const labelAnim = fadeSlideIn(frame, fps, labelDelay, SPRING_GENTLE);
  const labelExit = blurOut(frame, fps, exitStart, durationInFrames);

  // --- 부연 설명: 더 늦게 등장 ---
  const descDelay = zoneDelay(0.55, zone);
  const descAnim = fadeSlideIn(frame, fps, descDelay, SPRING_GENTLE);
  const descExit = blurOut(frame, fps, exitStart, durationInFrames);

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />

      {/* 방사형 배경 글로우 */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <div style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 600,
          height: 600,
          borderRadius: "50%",
          background: `radial-gradient(ellipse, rgba(124,127,217,${bgGlow}) 0%, transparent 70%)`,
        }} />
      </AbsoluteFill>

      <CameraMotion entranceFrames={zone} maxZoom={1.022} driftX={3} driftY={2}>
        <AbsoluteFill style={{
          padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}>

          {/* 글로우 링 (pulse 강조) */}
          <div style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -54%)",
            width: 340,
            height: 340,
            borderRadius: "50%",
            border: `2px solid rgba(124,127,217,${0.15 + glowValue * 0.7})`,
            boxShadow: `0 0 ${24 + glowValue * 48}px rgba(124,127,217,${0.2 + glowValue * 0.5}), inset 0 0 ${16 + glowValue * 32}px rgba(124,127,217,${0.05 + glowValue * 0.15})`,
            pointerEvents: "none",
          }} />

          {/* 히어로 숫자 */}
          <div style={{
            ...numberAnim,
            opacity: numberAnim.opacity * numberExit.opacity,
            filter: [numberAnim.filter, numberExit.filter].filter(Boolean).join(" ") || undefined,
            transform: `${numberAnim.transform ?? ""} ${numberExit.transform ?? ""}`.trim() || undefined,
            marginBottom: 28,
          }}>
            <span style={{
              fontSize: FONT.bigNumber.size,
              fontWeight: FONT.bigNumber.weight,
              fontFamily: FONT.family,
              lineHeight: FONT.bigNumber.lineHeight,
              letterSpacing: "-0.04em",
              color: COLORS.TEXT,
              textShadow: GLOW.text,
              display: "block",
              textAlign: "center",
            }}>
              {displayNumber}
            </span>
          </div>

          {/* 컨텍스트 레이블 */}
          <div style={{
            opacity: labelAnim.opacity * labelExit.opacity,
            transform: `${labelAnim.transform ?? ""} ${labelExit.transform ?? ""}`.trim() || undefined,
            filter: labelExit.filter,
            marginBottom: 20,
          }}>
            <span style={{
              fontSize: 36,
              fontWeight: 600,
              fontFamily: FONT.family,
              color: COLORS.ACCENT_BRIGHT,
              letterSpacing: "-0.02em",
              textAlign: "center",
              display: "block",
            }}>
              자동화 가능한 업무 비율
            </span>
          </div>

          {/* 부연 설명 */}
          <div style={{
            opacity: descAnim.opacity * descExit.opacity,
            transform: `${descAnim.transform ?? ""} ${descExit.transform ?? ""}`.trim() || undefined,
            filter: descExit.filter,
            maxWidth: 720,
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
              맥킨지 글로벌 연구소 — 2024년 AI 업무 자동화 리포트
            </p>
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

- 숫자가 정수이면 `parseAnimatedNumber("73")` → suffix 없이 카운트업
- 단위가 "만 명", "억 원" 등 한글 suffix이면 `parseAnimatedNumber`보다 `interpolate(countProgress, [0,1], [0, 73])`로 직접 계산 후 `Math.floor()` + suffix 수동 concat이 더 안전
- 글로우 링이 너무 강하면 `pulse(frame, fps, 0.1, 0.25)` — base/amp 줄이기
- 배경 이미지 있을 때 `bgGlow` 목표 opacity를 `0.35`로 낮춰 이미지와 충돌 방지
- 비교 슬라이드 (이전 vs 이후): 숫자 2개 → `blurReveal` 1개 + `fadeSlideIn` 1개, 크기 차별화
