# Timeline Process — 타임라인/과정 슬라이드

## 언제 사용

시간 순서, 발전 과정, 로드맵, 연혁, 프로세스 흐름.

## TSX

```tsx
import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
} from "remotion";
import { COLORS, FONT, LAYOUT } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import type { FreeformProps } from "./types";
import { fadeSlideIn, cascadeUp } from "../motifs/entries";
import { slideOutLeft } from "../motifs/exits/slideOutLeft";
import { getAnimationZone, zoneDelay, staggerDelays, getExitStart, exitStaggerDelays } from "../motifs/timing";
import { pickSpring, SPRING_GENTLE } from "../motifs/springConfigs";
import { drawLine, svgStrokeDraw } from "../motifs/decorations";
import { CameraPan } from "../design/CameraPan";

const ITEMS = [
  { year: "2020", desc: "초기 알고리즘 연구 착수 및 데이터셋 구축" },
  { year: "2021", desc: "첫 번째 프로토타입 개발, 내부 파일럿 테스트" },
  { year: "2022", desc: "모델 정확도 87% 달성, 베타 서비스 출시" },
  { year: "2023", desc: "정식 서비스 런칭, 누적 사용자 100만 돌파" },
];

// SVG circle circumference for a r=10 circle
const CIRCLE_CIRCUMFERENCE = 2 * Math.PI * 10; // ≈ 62.8

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const zone = getAnimationZone(durationInFrames);
  const exitStart = getExitStart(durationInFrames);

  // ── 타이틀 ──────────────────────────────────────────────────
  const titleAnim = fadeSlideIn(frame, fps, zoneDelay(0, zone), SPRING_GENTLE);
  const titleExit = slideOutLeft(frame, fps, exitStart, durationInFrames);

  // ── 연결선 (위에서 아래로) ───────────────────────────────────
  const lineProgress = drawLine(frame, fps, zoneDelay(0.1, zone));

  // ── 타임라인 아이템 ──────────────────────────────────────────
  const itemDelays = staggerDelays(ITEMS.length, zone, { offset: zoneDelay(0.15, zone) });
  const itemExitDelays = exitStaggerDelays(ITEMS.length, exitStart, durationInFrames);

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />
      <CameraPan entranceFrames={zone} direction="up" distance={8}>
        <AbsoluteFill style={{
          padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}>

          {/* 타이틀 */}
          <div style={{
            marginBottom: 52,
            opacity: titleAnim.opacity * titleExit.opacity,
            transform: `${titleAnim.transform} ${titleExit.transform}`,
          }}>
            <h1 style={{
              color: COLORS.TEXT,
              fontSize: FONT.title.size - 10,
              fontWeight: FONT.title.weight,
              fontFamily: FONT.family,
              letterSpacing: FONT.title.letterSpacing,
              margin: 0,
              textAlign: "center",
            }}>
              성장의 여정
            </h1>
          </div>

          {/* 타임라인 레이아웃 */}
          <div style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            gap: 0,
            alignItems: "center",
            width: 860,
          }}>

            {/* 연속 연결선 (position: absolute) */}
            <div style={{
              position: "absolute",
              left: "50%",
              top: 20,
              bottom: 20,
              width: 2,
              marginLeft: -1,
              background: "rgba(147,148,161,0.2)",
              overflow: "hidden",
            }}>
              <div style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                background: `linear-gradient(180deg, ${COLORS.ACCENT} 0%, ${COLORS.TEAL} 100%)`,
                height: `${lineProgress * 100}%`,
              }} />
            </div>

            {/* 타임라인 아이템 */}
            {ITEMS.map((item, i) => {
              const isLeft = i % 2 === 0;
              const springConfig = pickSpring(i, "varied");
              const anim = cascadeUp(frame, fps, i, itemDelays[0], itemDelays[1] - itemDelays[0], springConfig);
              const itemExitAnim = slideOutLeft(frame, fps, itemExitDelays[i], durationInFrames);

              // SVG 원 stroke 애니메이션
              const strokeOffset = svgStrokeDraw(frame, fps, CIRCLE_CIRCUMFERENCE, itemDelays[i]);

              return (
                <div key={i} style={{
                  display: "flex",
                  flexDirection: "row",
                  alignItems: "center",
                  width: "100%",
                  marginBottom: i < ITEMS.length - 1 ? 36 : 0,
                  opacity: anim.opacity * itemExitAnim.opacity,
                  transform: `${anim.transform} ${itemExitAnim.transform}`,
                }}>

                  {/* 왼쪽 영역 */}
                  <div style={{
                    flex: 1,
                    display: "flex",
                    justifyContent: isLeft ? "flex-end" : "flex-start",
                    paddingRight: isLeft ? 36 : 0,
                    paddingLeft: isLeft ? 0 : 36,
                  }}>
                    {isLeft && (
                      <div style={{
                        background: "rgba(28,30,33,0.75)",
                        border: `1px solid rgba(124,127,217,0.22)`,
                        borderRadius: 16,
                        padding: "20px 28px",
                        maxWidth: 320,
                      }}>
                        <div style={{
                          color: COLORS.ACCENT,
                          fontSize: 28,
                          fontWeight: 700,
                          fontFamily: FONT.family,
                          marginBottom: 8,
                          letterSpacing: "0.04em",
                        }}>
                          {item.year}
                        </div>
                        <div style={{
                          color: COLORS.TEXT,
                          fontSize: 28,
                          fontWeight: 500,
                          fontFamily: FONT.family,
                          lineHeight: 1.4,
                          wordBreak: "keep-all",
                        }}>
                          {item.desc}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 중앙 노드 (SVG 원) */}
                  <div style={{
                    flexShrink: 0,
                    width: 40,
                    height: 40,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    zIndex: 1,
                  }}>
                    <svg width="40" height="40" viewBox="0 0 40 40">
                      {/* 배경 원 */}
                      <circle
                        cx="20" cy="20" r="10"
                        fill="rgba(11,12,14,0.9)"
                        stroke="rgba(147,148,161,0.25)"
                        strokeWidth="2"
                      />
                      {/* 애니메이션 stroke */}
                      <circle
                        cx="20" cy="20" r="10"
                        fill="none"
                        stroke={COLORS.ACCENT}
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeDasharray={CIRCLE_CIRCUMFERENCE}
                        strokeDashoffset={strokeOffset}
                        transform="rotate(-90 20 20)"
                      />
                      {/* 내부 점 */}
                      <circle cx="20" cy="20" r="4" fill={COLORS.ACCENT} />
                    </svg>
                  </div>

                  {/* 오른쪽 영역 */}
                  <div style={{
                    flex: 1,
                    display: "flex",
                    justifyContent: isLeft ? "flex-start" : "flex-end",
                    paddingLeft: isLeft ? 36 : 0,
                    paddingRight: isLeft ? 0 : 36,
                  }}>
                    {!isLeft && (
                      <div style={{
                        background: "rgba(28,30,33,0.75)",
                        border: `1px solid rgba(124,127,217,0.22)`,
                        borderRadius: 16,
                        padding: "20px 28px",
                        maxWidth: 320,
                      }}>
                        <div style={{
                          color: COLORS.ACCENT,
                          fontSize: 28,
                          fontWeight: 700,
                          fontFamily: FONT.family,
                          marginBottom: 8,
                          letterSpacing: "0.04em",
                        }}>
                          {item.year}
                        </div>
                        <div style={{
                          color: COLORS.TEXT,
                          fontSize: 28,
                          fontWeight: 500,
                          fontFamily: FONT.family,
                          lineHeight: 1.4,
                          wordBreak: "keep-all",
                        }}>
                          {item.desc}
                        </div>
                      </div>
                    )}
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
```

## 핵심 기법

- `cascadeUp` — 타임라인 아이템 순차 등장 (위에서 아래로 하나씩)
- `drawLine` — 중앙 연결선이 위에서 아래로 성장 (`height: lineProgress%`)
- `svgStrokeDraw` — 각 노드의 SVG 원 테두리가 순서대로 그려짐
- `pickSpring("varied")` — 아이템마다 GENTLE → SNAPPY → BOUNCY → STIFF 순환 (시각적 다양성)
- `slideOutLeft` — 왼쪽으로 슬라이드 퇴장 ("앞으로 나아가는" 방향감)
- `exitStaggerDelays` — 아이템 역순 퇴장 (마지막 항목이 먼저 사라짐)
- `CameraPan direction="up"` — 상승/성장 서사와 일치하는 위 방향 드리프트
- `getAnimationZone` + `zoneDelay` + `staggerDelays` — 하드코딩 프레임 없음
- 좌우 교대 배치 (짝수 인덱스 왼쪽, 홀수 인덱스 오른쪽) — 지그재그 타임라인
- 단일 `position: absolute` 연속 연결선 (Slides Contract Rule #10 준수)
