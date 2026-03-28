# Step Tutorial — 튜토리얼/단계 슬라이드

## 언제 사용

단계별 설명, 설정 방법, 가이드, 튜토리얼, How-to.
순서가 있는 3-4단계 프로세스에 최적. 나열형 목록과 달리 단계 번호와 연결선이 흐름을 강조.

## 핵심 기법

- `diagonalWipe` — 콘텐츠 영역 대각선 스윕 진입 (에디토리얼 전환)
- `cascadeUp` — 단계 아이템 순차 등장 (아래에서 위로 솟구침)
- `scaleIn` — 번호 배지 팝업 등장 (아이콘/배지 전용)
- `penStroke` — 현재 단계 제목 아래 손그림 밑줄 강조
- `drawLine` — 단계 사이 연결선 그리기
- `CameraPan direction="right"` — 앞으로 나아가는 진행 서사
- `SPRING_SNAPPY` — 효율적 튜토리얼 느낌
- `slideOutLeft` — "다음 단계로 이동" 방향성 퇴장
- `getAnimationZone` + `staggerDelays` — 하드코딩 프레임 없는 타이밍

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
import { CameraPan } from "../design/CameraPan";
import { diagonalWipe, cascadeUp, scaleIn, fadeSlideIn } from "../motifs/entries";
import { slideOutLeft } from "../motifs/exits";
import { penStroke } from "../motifs/emphasis";
import { drawLine } from "../motifs/decorations";
import {
  getAnimationZone, zoneDelay, staggerDelays, getExitStart, exitStaggerDelays,
} from "../motifs/timing";
import { SPRING_SNAPPY, SPRING_GENTLE } from "../motifs/springConfigs";
import type { FreeformProps } from "./types";

// --- 데이터 ---
const STEPS = [
  {
    num: "01",
    title: "프롬프트 작성",
    desc: "원하는 결과를 명확하고 구체적으로 기술. 맥락·형식·제약 조건을 함께 명시.",
    color: "#7C7FD9",
    icon: (
      <svg width={28} height={28} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
    ),
  },
  {
    num: "02",
    title: "결과 검토",
    desc: "AI 출력물의 정확성·일관성 확인. 필요 시 프롬프트를 수정하여 재실행.",
    color: "#3CB4B4",
    icon: (
      <svg width={28} height={28} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
        <circle cx={12} cy={12} r={3} />
      </svg>
    ),
  },
  {
    num: "03",
    title: "자동 배포",
    desc: "검증된 결과물을 파이프라인에 연결. CI/CD로 반복 작업 완전 자동화.",
    color: "#34D399",
    icon: (
      <svg width={28} height={28} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <polyline points="16 3 21 3 21 8" />
        <line x1={4} y1={20} x2={21} y2={3} />
        <polyline points="21 16 21 21 16 21" />
        <line x1={15} y1={15} x2={21} y2={21} />
      </svg>
    ),
  },
];

// 활성 단계 인덱스 (하이라이트할 단계, 0-based)
const ACTIVE_STEP = 1;

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // --- 타이밍 ---
  const zone = getAnimationZone(durationInFrames, { fps });
  const exitStart = getExitStart(durationInFrames, { fps });

  // 제목 fadeSlideIn
  const titleAnim = fadeSlideIn(frame, fps, zoneDelay(0.0, zone), SPRING_GENTLE);
  const titleExit = slideOutLeft(frame, fps, exitStart, durationInFrames);

  // 콘텐츠 영역 diagonalWipe
  const wipeDelay = zoneDelay(0.1, zone);
  const wipeAnim = diagonalWipe(frame, fps, wipeDelay, SPRING_SNAPPY, "topLeft");

  // 단계 cascadeUp — staggerDelays로 고르게 분포
  const stepDelays = staggerDelays(STEPS.length, zone, { offset: zoneDelay(0.2, zone) });
  const stepExitDelays = exitStaggerDelays(STEPS.length, exitStart, durationInFrames);

  // 연결선 drawLine — 각 단계 사이 (STEPS.length - 1 개)
  const lineDelays = staggerDelays(STEPS.length - 1, zone, { offset: zoneDelay(0.3, zone) });

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />

      <CameraPan entranceFrames={zone} direction="right" distance={8}>
        <AbsoluteFill style={{
          padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}>

          {/* 제목 */}
          <div style={{
            marginBottom: 56,
            textAlign: "center",
            opacity: titleAnim.opacity * titleExit.opacity,
            transform: `${titleAnim.transform} ${titleExit.transform}`,
          }}>
            <h2 style={{
              margin: 0,
              fontSize: 56,
              fontWeight: 800,
              fontFamily: FONT.family,
              letterSpacing: "-0.03em",
              color: COLORS.TEXT,
              lineHeight: 1.1,
              textShadow: GLOW.text,
            }}>
              3단계 자동화 워크플로우
            </h2>
          </div>

          {/* 단계 목록 컨테이너 — diagonalWipe */}
          <div style={{
            ...wipeAnim,
            maxWidth: 700,
            width: "100%",
            display: "flex",
            flexDirection: "column",
            gap: 0,
            position: "relative",
          }}>

            {/* 연속 연결선 (position: absolute) */}
            {[0, 1].map((lineIdx) => {
              const lineProgress = drawLine(frame, fps, lineDelays[lineIdx]);
              return (
                <div
                  key={`line-${lineIdx}`}
                  style={{
                    position: "absolute",
                    left: 47,
                    // 배지 중심(52px) + 아이템 높이(128px) * lineIdx + 배지 반지름(26px)
                    top: 52 + 128 * lineIdx + 26,
                    width: 4,
                    height: 76,
                    borderRadius: 2,
                    background: `linear-gradient(180deg, ${STEPS[lineIdx].color}88, ${STEPS[lineIdx + 1].color}88)`,
                    transformOrigin: "top center",
                    transform: `scaleY(${lineProgress})`,
                    opacity: 0.6,
                  }}
                />
              );
            })}

            {STEPS.map((step, i) => {
              // 배지 scaleIn
              const badgeAnim = scaleIn(frame, fps, stepDelays[i], SPRING_SNAPPY);

              // 단계 카드 cascadeUp
              const cardAnim = cascadeUp(frame, fps, i, stepDelays[i], 0, SPRING_SNAPPY);
              const cardExit = slideOutLeft(frame, fps, stepExitDelays[i], durationInFrames);

              // 활성 단계: penStroke 밑줄
              const pen = i === ACTIVE_STEP
                ? penStroke(frame, fps, zoneDelay(0.65, zone), SPRING_SNAPPY)
                : { progress: 0, wobble: 0 };

              const isActive = i === ACTIVE_STEP;

              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "flex-start",
                    gap: 24,
                    height: 128,
                    opacity: cardAnim.opacity * cardExit.opacity,
                    transform: `${cardAnim.transform} ${cardExit.transform}`,
                    position: "relative",
                    zIndex: 1,
                  }}
                >
                  {/* 번호 배지 */}
                  <div style={{
                    width: 52,
                    height: 52,
                    borderRadius: "50%",
                    border: `2px solid ${isActive ? step.color : `${step.color}66`}`,
                    background: isActive
                      ? `rgba(${hexToRgb(step.color)}, 0.18)`
                      : `rgba(${hexToRgb(step.color)}, 0.07)`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    marginTop: 8,
                    opacity: badgeAnim.opacity,
                    transform: badgeAnim.transform,
                    boxShadow: isActive ? `0 0 16px rgba(${hexToRgb(step.color)}, 0.4)` : "none",
                  }}>
                    <span style={{
                      fontSize: 24,
                      fontWeight: 800,
                      fontFamily: FONT.family,
                      color: isActive ? step.color : COLORS.MUTED,
                      letterSpacing: "0.02em",
                    }}>
                      {step.num}
                    </span>
                  </div>

                  {/* 내용 영역 */}
                  <div style={{
                    flex: 1,
                    borderRadius: 18,
                    border: `1px solid ${isActive
                      ? `rgba(${hexToRgb(step.color)}, 0.28)`
                      : "rgba(237,237,239, 0.07)"}`,
                    background: isActive
                      ? `rgba(${hexToRgb(step.color)}, 0.07)`
                      : "rgba(237,237,239, 0.03)",
                    padding: "18px 24px 16px",
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                    gap: 20,
                  }}>
                    {/* 아이콘 */}
                    <div style={{
                      width: 52,
                      height: 52,
                      borderRadius: 14,
                      border: `1px solid rgba(${hexToRgb(step.color)}, 0.2)`,
                      background: `rgba(${hexToRgb(step.color)}, 0.1)`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: step.color,
                      flexShrink: 0,
                    }}>
                      {step.icon}
                    </div>

                    {/* 텍스트 */}
                    <div style={{ flex: 1 }}>
                      {/* 제목 + penStroke 밑줄 */}
                      <div style={{ position: "relative", display: "inline-block", marginBottom: 8 }}>
                        <span style={{
                          fontSize: 34,
                          fontWeight: 700,
                          fontFamily: FONT.family,
                          color: isActive ? COLORS.TEXT : COLORS.MUTED,
                          letterSpacing: "-0.02em",
                          lineHeight: 1.2,
                        }}>
                          {step.title}
                        </span>
                        {/* penStroke 밑줄 — 활성 단계만 */}
                        {isActive && (
                          <div style={{
                            position: "absolute",
                            bottom: -3,
                            left: pen.wobble,
                            width: `${pen.progress * 100}%`,
                            height: 3,
                            borderRadius: 2,
                            background: step.color,
                            boxShadow: `0 0 8px rgba(${hexToRgb(step.color)}, 0.6)`,
                          }} />
                        )}
                      </div>

                      <p style={{
                        margin: 0,
                        fontSize: 26,
                        fontWeight: 400,
                        fontFamily: FONT.family,
                        color: COLORS.MUTED,
                        lineHeight: 1.45,
                        wordBreak: "keep-all",
                      }}>
                        {step.desc}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

        </AbsoluteFill>
      </CameraPan>

      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};

// 헬퍼: hex → "r, g, b" (rgba() 내부에서 사용)
function hexToRgb(hex: string): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `${r}, ${g}, ${b}`;
}
```

## 변형 팁

- 4단계이면 `STEPS`에 항목 추가, `height: 128`을 `110`으로 줄이고 연결선 배열 `[0,1,2]`로 확장
- `ACTIVE_STEP`을 -1로 설정하면 모든 단계가 동일 강도로 표시 (완료 요약 슬라이드 용도)
- 배경 이미지 있을 때 카드 `background` opacity를 0.04로 낮출 것
- 마지막 슬라이드 퇴장을 `blurOut`으로 바꾸면 더 드라마틱한 전환 가능
