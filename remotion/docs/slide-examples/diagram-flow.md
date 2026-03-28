# Diagram Flow — 플로우 다이어그램 슬라이드

## 언제 사용

아키텍처, 데이터 흐름, 파이프라인, 시스템 구조 설명.
순서가 있는 3단계 프로세스를 좌→우 흐름으로 시각화할 때.

## TSX

```tsx
import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  spring, interpolate, Easing,
} from "remotion";
import { COLORS, FONT, LAYOUT, GLOW } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import type { FreeformProps } from "./types";
import { circleReveal, scaleIn, fadeSlideIn } from "../motifs/entries";
import { clipCircleOut } from "../motifs/exits";
import { svgStrokeDraw } from "../motifs/decorations";
import { orbit } from "../motifs/emphasis";
import { pickSpring, SPRING_GENTLE, SPRING_SNAPPY } from "../motifs/springConfigs";
import { getAnimationZone, staggerDelays, zoneDelay, getExitStart } from "../motifs/timing";

// ── 노드 데이터 ─────────────────────────────────────────────────
const NODES = [
  {
    label: "데이터 수집",
    subLabel: "원시 입력 처리",
    icon: (
      // Feather: database
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <ellipse cx="12" cy="5" rx="9" ry="3" />
        <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
        <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
      </svg>
    ),
    accent: COLORS.TEAL,
  },
  {
    label: "AI 분석",
    subLabel: "패턴 학습 및 추론",
    icon: (
      // Feather: cpu
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="4" y="4" width="16" height="16" rx="2" ry="2" />
        <rect x="9" y="9" width="6" height="6" />
        <line x1="9" y1="1" x2="9" y2="4" />
        <line x1="15" y1="1" x2="15" y2="4" />
        <line x1="9" y1="20" x2="9" y2="23" />
        <line x1="15" y1="20" x2="15" y2="23" />
        <line x1="20" y1="9" x2="23" y2="9" />
        <line x1="20" y1="14" x2="23" y2="14" />
        <line x1="1" y1="9" x2="4" y2="9" />
        <line x1="1" y1="14" x2="4" y2="14" />
      </svg>
    ),
    accent: COLORS.ACCENT,
  },
  {
    label: "결과 출력",
    subLabel: "인사이트 자동 전달",
    icon: (
      // Feather: send
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="22" y1="2" x2="11" y2="13" />
        <polygon points="22 2 15 22 11 13 2 9 22 2" />
      </svg>
    ),
    accent: COLORS.ACCENT_BRIGHT,
  },
];

// ── 레이아웃 상수 ────────────────────────────────────────────────
const CANVAS_W = 1920;
const CY = 480;              // 수직 시각 중심
const NODE_W = 260;
const NODE_H = 180;
const GAP = 390;             // 노드 간격 (수평 분포 70-80% 활용)
const TOTAL_W = NODE_W * NODES.length + GAP * (NODES.length - 1);
const START_X = (CANVAS_W - TOTAL_W) / 2;

// 화살표 SVG 경로 계산 (노드 우측 끝 → 다음 노드 좌측 끝)
const ARROW_Y = CY;
const ARROW_PATH_LENGTH = 200; // 추정 경로 길이 (svgStrokeDraw용)

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const zone = getAnimationZone(durationInFrames, { fps });
  const exitStart = getExitStart(durationInFrames, { fps });

  // 노드별 등장 딜레이 (staggerDelays)
  const nodeDelays = staggerDelays(NODES.length, zone, { offset: 0, settleFrames: 24 });

  // 화살표: 노드 1 등장 이후에 그려짐
  const arrow0Delay = zoneDelay(0.28, zone);
  const arrow1Delay = zoneDelay(0.58, zone);

  // 제목 등장
  const titleDelay = 0;
  const titleAnim = fadeSlideIn(frame, fps, titleDelay, SPRING_GENTLE);

  // 다이어그램 컨테이너 — circleReveal (spotlight entrance)
  const containerDelay = zoneDelay(0.05, zone);
  const containerClip = circleReveal(frame, fps, containerDelay, SPRING_GENTLE);

  // orbit 장식 — 중앙 노드(index 1) 주변
  const orbitPos = orbit(frame, fps, zone, 130, 0.22);

  // 퇴장 — clipCircleOut (circleReveal 쌍)
  const containerExit = clipCircleOut(frame, fps, exitStart, durationInFrames);
  const titleExit = { opacity: frame >= exitStart
    ? interpolate(frame, [exitStart, durationInFrames], [1, 0], { extrapolateRight: "clamp" })
    : 1 };

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

        {/* 슬라이드 제목 */}
        <div style={{
          ...titleAnim,
          opacity: titleAnim.opacity * titleExit.opacity,
          fontFamily: FONT.family,
          fontSize: 38,
          fontWeight: 700,
          color: COLORS.MUTED,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          marginBottom: 56,
          alignSelf: "center",
        }}>
          AI 파이프라인 구조
        </div>

        {/* 다이어그램 영역 — circleReveal */}
        <div style={{
          position: "relative",
          width: TOTAL_W + 80,
          height: NODE_H + 60,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          clipPath: frame >= exitStart
            ? containerExit.clipPath
            : containerClip.clipPath,
          opacity: containerClip.opacity,
        }}>

          {/* ── 화살표 SVG ─────────────────────────────────────── */}
          <svg
            style={{ position: "absolute", inset: 0, overflow: "visible", pointerEvents: "none" }}
            width={TOTAL_W + 80}
            height={NODE_H + 60}
          >
            {[0, 1].map((arrowIdx) => {
              const x1 = 40 + arrowIdx * (NODE_W + GAP) + NODE_W;
              const x2 = x1 + GAP;
              const y = (NODE_H + 60) / 2;
              const arrowDelay = arrowIdx === 0 ? arrow0Delay : arrow1Delay;
              const dashOffset = svgStrokeDraw(frame, fps, ARROW_PATH_LENGTH, arrowDelay);
              const mx = (x1 + x2) / 2;
              const sz = 14;

              // 화살촉 x 위치 (path가 다 그려졌을 때만 표시)
              const arrowProgress = interpolate(
                frame,
                [arrowDelay, arrowDelay + 20],
                [0, 1],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
              );

              return (
                <g key={arrowIdx}>
                  {/* 연결선 */}
                  <line
                    x1={x1}
                    y1={y}
                    x2={x2}
                    y2={y}
                    stroke={COLORS.ACCENT}
                    strokeWidth={3}
                    strokeDasharray={ARROW_PATH_LENGTH}
                    strokeDashoffset={dashOffset}
                    strokeLinecap="round"
                    opacity={0.7}
                  />
                  {/* 화살촉 */}
                  <polygon
                    points={`${x2},${y} ${x2 - sz},${y - sz / 2} ${x2 - sz},${y + sz / 2}`}
                    fill={COLORS.ACCENT}
                    opacity={arrowProgress * 0.85}
                  />
                </g>
              );
            })}
          </svg>

          {/* ── 노드 ────────────────────────────────────────────── */}
          {NODES.map((node, i) => {
            const nodeDelay = nodeDelays[i];
            const cfg = pickSpring(i, "varied");

            // 노드 컨테이너 — fadeSlideIn
            const nodeAnim = fadeSlideIn(frame, fps, nodeDelay, cfg);

            // 아이콘 — scaleIn (아이콘 전용)
            const iconDelay = nodeDelays[i] + 8;
            const iconAnim = scaleIn(frame, fps, iconDelay, pickSpring(i, "energetic"));

            const nodeX = 40 + i * (NODE_W + GAP);
            const isCenter = i === 1;

            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: nodeX,
                  top: (NODE_H + 60) / 2 - NODE_H / 2,
                  width: NODE_W,
                  height: NODE_H,
                  ...nodeAnim,
                }}
              >
                {/* orbit 장식 (중앙 노드만) */}
                {isCenter && (
                  <div style={{
                    position: "absolute",
                    left: NODE_W / 2 + orbitPos.x - 6,
                    top: NODE_H / 2 + orbitPos.y - 6,
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    backgroundColor: COLORS.ACCENT,
                    opacity: 0.35,
                    pointerEvents: "none",
                  }} />
                )}

                {/* 노드 카드 */}
                <div style={{
                  width: "100%",
                  height: "100%",
                  background: `rgba(${isCenter ? "124, 127, 217, 0.10" : "60, 180, 180, 0.07"})`,
                  border: `1px solid ${node.accent}44`,
                  borderRadius: 20,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 14,
                  boxShadow: isCenter
                    ? `0 0 40px ${COLORS.ACCENT}22, 0 0 0 1px ${COLORS.ACCENT}33`
                    : "none",
                }}>

                  {/* 아이콘 */}
                  <div style={{
                    ...iconAnim,
                    color: node.accent,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}>
                    {node.icon}
                  </div>

                  {/* 라벨 */}
                  <div style={{
                    fontFamily: FONT.family,
                    fontSize: 34,
                    fontWeight: 700,
                    color: COLORS.TEXT,
                    letterSpacing: "-0.01em",
                    textAlign: "center",
                    wordBreak: "keep-all",
                  }}>
                    {node.label}
                  </div>

                  {/* 서브 라벨 */}
                  <div style={{
                    fontFamily: FONT.family,
                    fontSize: 26,
                    fontWeight: 400,
                    color: COLORS.MUTED,
                    textAlign: "center",
                    wordBreak: "keep-all",
                    lineHeight: 1.3,
                  }}>
                    {node.subLabel}
                  </div>
                </div>
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
```

## 핵심 기법

- `circleReveal` — `{ clipPath, opacity }` 반환. 다이어그램 컨테이너 div에 `clipPath` + `opacity` 적용. spotlight가 확장되며 3개 노드 전체가 드러남.
- `scaleIn` — 아이콘/SVG 전용. 노드 카드 내 아이콘에만 적용 (텍스트 라벨에는 금지).
- `svgStrokeDraw` — `strokeDashoffset` 반환값. `strokeDasharray`와 같은 값으로 설정하고 `strokeDashoffset`에 대입. 선이 왼쪽→오른쪽으로 그려지는 효과.
- `orbit` — `{ x, y }` 픽셀 오프셋 반환. 중심 노드 위에 `position: absolute`로 작은 원 배치 후 `left: cx + o.x`, `top: cy + o.y`로 공전.
- `pickSpring("varied")` — 노드마다 GENTLE→SNAPPY→BOUNCY 순환. 다이어그램 시각적 다양성 확보.
- `clipCircleOut` — `circleReveal`의 퇴장 쌍. `frame >= exitStart`일 때 조건부로 `clipPath` 교체. iris-out 아이리스 닫힘 효과.
- `staggerDelays` — N개 노드를 `animZone` 안에 균등 분배. 하드코딩 프레임 없이 슬라이드 길이 변화에 자동 적응.
- 레이아웃: `cY = 480`, `NODE_W = 260, NODE_H = 180` (최소 200×70 준수), `GAP = 390` (3노드 수평 70-80% 활용), 화살촉 `sz = 14`.
