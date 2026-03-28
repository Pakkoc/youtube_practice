# Data Bar Chart — 데이터 비교 바 차트

## 언제 사용

수치 비교, 퍼센트 순위, 성능 차이, 점유율 등 데이터 시각화.
4-6개 항목 비교에 최적. 항목이 7개 이상이면 상위 5개로 압축.

## 핵심 기법

- `drawBar` — scaleX 0→1 바 성장 애니메이션 (수평 바 전용)
- `countUpProgress` — 퍼센트 숫자 카운트업
- `staggerDelays` — 순차 등장 (상단→하단)
- `fadeSlideIn` + `SPRING_SNAPPY` — 제목 빠른 배치
- `scaleOut` — 제목 퇴장 / `fadeSlideOut` — 바 항목 퇴장
- `getAnimationZone` + `zoneDelay` — 타이밍 (하드코딩 프레임 없음)

## TSX

```tsx
import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate,
} from "remotion";
import { COLORS, FONT, LAYOUT, GLOW } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import { fadeSlideIn } from "../motifs/entries";
import { scaleOut, fadeSlideOut } from "../motifs/exits";
import { drawBar, glassCardOpacity } from "../motifs/decorations";
import { countUpProgress } from "../motifs/emphasis";
import {
  getAnimationZone, zoneDelay, staggerDelays, getExitStart, exitStaggerDelays,
} from "../motifs/timing";
import { SPRING_SNAPPY, SPRING_GENTLE } from "../motifs/springConfigs";
import type { FreeformProps } from "./types";

// 데이터 정의 — 실제 슬라이드 작성 시 대본에서 추출
const BARS = [
  { label: "생성형 AI 도입률", value: 87, color: COLORS.ACCENT },
  { label: "업무 자동화 비율", value: 73, color: COLORS.TEAL },
  { label: "비용 절감 효과", value: 61, color: COLORS.ACCENT },
  { label: "인력 재배치 필요", value: 44, color: COLORS.TEAL },
] as const;

const BAR_MAX_WIDTH = 820; // px — 바 최대 길이 (1920 캔버스에서 70% 이내)

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // --- 타이밍 ---
  const zone = getAnimationZone(durationInFrames, { fps });
  const exitStart = getExitStart(durationInFrames, { fps });

  // 제목
  const titleDelay = zoneDelay(0.0, zone);
  const titleAnim = fadeSlideIn(frame, fps, titleDelay, SPRING_SNAPPY);
  const titleExit = scaleOut(frame, fps, exitStart, durationInFrames);

  // 바 항목들: staggerDelays로 순차 등장
  const barDelays = staggerDelays(BARS.length, zone, { offset: zoneDelay(0.18, zone) });
  const barExitDelays = exitStaggerDelays(BARS.length, exitStart, durationInFrames);

  // 카운트업: 각 바가 완전히 등장한 후 숫자 카운트 (delay와 동기화)
  const countProgress = countUpProgress(frame, fps, 1.2);

  // 전체 카드 배경 불투명도
  const cardOpacity = glassCardOpacity(frame, fps, 0.4);

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

        {/* 제목 */}
        <div style={{
          opacity: titleAnim.opacity * titleExit.opacity,
          transform: `${titleAnim.transform} ${titleExit.transform}`,
          marginBottom: 52,
          textAlign: "center",
        }}>
          <h2 style={{
            fontSize: 52,
            fontWeight: 800,
            fontFamily: FONT.family,
            letterSpacing: "-0.03em",
            color: COLORS.TEXT,
            margin: 0,
            lineHeight: 1.1,
          }}>
            AI 전환 지표 현황
          </h2>
          <div style={{
            marginTop: 12,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 8,
          }}>
            {/* 구분선 */}
            <div style={{
              width: 40, height: 3, borderRadius: 2,
              background: COLORS.ACCENT,
              boxShadow: GLOW.bar,
            }} />
            <span style={{
              fontSize: 28,
              fontWeight: 500,
              fontFamily: FONT.family,
              color: COLORS.MUTED,
            }}>
              2025년 국내 기업 조사 기준
            </span>
            <div style={{
              width: 40, height: 3, borderRadius: 2,
              background: COLORS.TEAL,
            }} />
          </div>
        </div>

        {/* 바 차트 컨테이너 */}
        <div style={{
          width: 1100,
          display: "flex",
          flexDirection: "column",
          gap: 28,
          padding: "40px 48px",
          borderRadius: 24,
          border: "1px solid rgba(124,127,217,0.12)",
          background: `rgba(12,13,16,${cardOpacity * 0.6})`,
        }}>
          {BARS.map((bar, i) => {
            const barDelay = barDelays[i];
            const entryAnim = fadeSlideIn(frame, fps, barDelay, SPRING_SNAPPY);
            const barGrowth = drawBar(frame, fps, barDelay);
            const exitFrame = barExitDelays[i];
            const exitAnim = fadeSlideOut(frame, fps, exitFrame, durationInFrames);

            // 카운트업 숫자 (바 등장 이후 시작)
            const animatedValue = Math.round(bar.value * countProgress);

            return (
              <div
                key={i}
                style={{
                  opacity: entryAnim.opacity * exitAnim.opacity,
                  transform: `${entryAnim.transform} ${exitAnim.transform}`,
                  display: "flex",
                  flexDirection: "column",
                  gap: 10,
                }}
              >
                {/* 레이블 행 */}
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}>
                  <span style={{
                    fontSize: 32,
                    fontWeight: 600,
                    fontFamily: FONT.family,
                    color: COLORS.TEXT,
                    wordBreak: "keep-all",
                  }}>
                    {bar.label}
                  </span>
                  <span style={{
                    fontSize: 32,
                    fontWeight: 800,
                    fontFamily: FONT.family,
                    color: bar.color,
                    minWidth: 72,
                    textAlign: "right",
                    textShadow: bar.color === COLORS.ACCENT ? GLOW.text : "0 0 12px rgba(60,180,180,0.5)",
                    fontVariantNumeric: "tabular-nums",
                  }}>
                    {animatedValue}%
                  </span>
                </div>

                {/* 바 트랙 */}
                <div style={{
                  width: "100%",
                  height: 14,
                  borderRadius: 7,
                  background: "rgba(237,237,239,0.07)",
                  overflow: "hidden",
                  position: "relative",
                }}>
                  {/* 채워진 바 — scaleX 애니메이션 */}
                  <div style={{
                    position: "absolute",
                    top: 0, left: 0,
                    height: "100%",
                    width: `${bar.value}%`,
                    borderRadius: 7,
                    background: bar.color === COLORS.ACCENT
                      ? `linear-gradient(90deg, ${COLORS.ACCENT}, ${COLORS.ACCENT_BRIGHT})`
                      : `linear-gradient(90deg, ${COLORS.TEAL}, rgba(60,180,180,0.6))`,
                    boxShadow: bar.color === COLORS.ACCENT ? GLOW.bar : "0 0 10px rgba(60,180,180,0.5)",
                    transformOrigin: "left center",
                    transform: `scaleX(${barGrowth})`,
                  }} />
                </div>
              </div>
            );
          })}
        </div>

        {/* 하단 출처 레이블 */}
        <div style={{
          marginTop: 32,
          opacity: titleAnim.opacity * titleExit.opacity,
        }}>
          <span style={{
            fontSize: 26,
            fontWeight: 400,
            fontFamily: FONT.family,
            color: COLORS.MUTED,
          }}>
            출처: 한국 AI 전환 현황 보고서 2025
          </span>
        </div>

      </AbsoluteFill>

      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />
      <SceneFade />
    </AbsoluteFill>
  );
};
```

## 변형 팁

- 항목이 3개 이하: `gap`을 40으로 늘리고 바 높이를 20px로 키울 것
- 값이 아닌 절대 수치(억 원 등)라면 `countUpProgress`에 `parseAnimatedNumber` + `formatAnimatedNumber` 조합 사용
- 수직 바 차트로 전환 시: `drawBar`는 `scaleY`(하→상)로 사용, `transformOrigin: "center bottom"`
- 배경 이미지가 있으면 카드 `background` 투명도를 0.08 → 0.15로 높여 가독성 확보
