# Icon Grid — 카테고리/그리드 슬라이드

## 언제 사용

카테고리 나열, 서비스 종류, 기능 목록, 영역별 분류. 4-6개 아이템.
각 항목이 대등한 위계일 때 적합. 순서가 중요한 단계 설명에는 부적합.

## 핵심 기법

- `layeredReveal` — 3단 점진적 공개 (제목 → 그리드 진입 → 레이블/설명)
- `float` — 아이콘 둥둥 뜨는 효과 (진입 완료 후 지속)
- `shimmer` — 카드 컨테이너 오버레이 sheen (position:absolute 오버레이 div 사용)
- `pickSpring("energetic")` — BOUNCY 2배 역동적 순환
- `scaleIn` — 아이콘/배지 전용 팝업 등장
- `fadeSlideOut` — 부드러운 퇴장
- `getAnimationZone` + `staggerDelays` — 하드코딩 프레임 없는 타이밍

## TSX

```tsx
import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  spring, interpolate,
} from "remotion";
import { COLORS, FONT, LAYOUT, GLOW, STYLE } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import { CameraPan } from "../design/CameraPan";
import { layeredReveal, scaleIn, fadeSlideIn } from "../motifs/entries";
import { fadeSlideOut } from "../motifs/exits";
import { float, shimmer } from "../motifs/emphasis";
import { glassCardOpacity } from "../motifs/decorations";
import {
  getAnimationZone, zoneDelay, staggerDelays, getExitStart, exitStaggerDelays,
} from "../motifs/timing";
import { pickSpring, SPRING_GENTLE, SPRING_SNAPPY } from "../motifs/springConfigs";
import type { FreeformProps } from "./types";

// --- 데이터 ---
const ITEMS = [
  {
    label: "자연어 처리",
    desc: "텍스트 이해·생성 핵심 기술",
    color: "#7C7FD9",
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    ),
  },
  {
    label: "컴퓨터 비전",
    desc: "이미지·영상 인식·분석",
    color: "#3CB4B4",
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <circle cx={11} cy={11} r={8} />
        <line x1={21} y1={21} x2={16.65} y2={16.65} />
        <line x1={11} y1={8} x2={11} y2={14} />
        <line x1={8} y1={11} x2={14} y2={11} />
      </svg>
    ),
  },
  {
    label: "생성 모델",
    desc: "이미지·음성·텍스트 생성",
    color: "#9B9EFF",
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    ),
  },
  {
    label: "강화학습",
    desc: "보상 기반 의사결정 학습",
    color: "#F472B6",
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    label: "멀티모달",
    desc: "텍스트+이미지+음성 통합",
    color: "#34D399",
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <rect x={2} y={3} width={20} height={14} rx={2} ry={2} />
        <line x1={8} y1={21} x2={16} y2={21} />
        <line x1={12} y1={17} x2={12} y2={21} />
      </svg>
    ),
  },
  {
    label: "AI 에이전트",
    desc: "자율 목표 달성 자동화",
    color: "#FB923C",
    icon: (
      <svg width={36} height={36} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <circle cx={12} cy={12} r={10} />
        <line x1={12} y1={8} x2={12} y2={12} />
        <line x1={12} y1={16} x2={12.01} y2={16} />
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

  // --- 타이밍 ---
  const zone = getAnimationZone(durationInFrames, { fps });
  const exitStart = getExitStart(durationInFrames, { fps });

  // Layer 0: 제목
  const titleAnim = layeredReveal(frame, fps, 0, { config: SPRING_GENTLE });
  const titleExit = fadeSlideOut(frame, fps, exitStart, durationInFrames);

  // Layer 1: 그리드 카드 (아이콘 scaleIn + 카드 container)
  const itemDelays = staggerDelays(ITEMS.length, zone, { offset: zoneDelay(0.25, zone) });
  const itemExitDelays = exitStaggerDelays(ITEMS.length, exitStart, durationInFrames);

  // Layer 2: 레이블·설명 (카드 진입 후 약간 뒤에 등장)
  const labelDelay = zoneDelay(0.6, zone);

  // 카드 컨테이너 전체 glassOpacity
  const glassOpacity = glassCardOpacity(frame, fps, 1.2);

  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />

      <CameraPan entranceFrames={zone} direction="right" distance={6}>
        <AbsoluteFill style={{
          padding: `${LAYOUT.padding.top}px ${LAYOUT.padding.right}px ${LAYOUT.padding.bottom}px ${LAYOUT.padding.left}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}>

          {/* 제목 — Layer 0 */}
          <div style={{
            marginBottom: 52,
            opacity: titleAnim.opacity * titleExit.opacity,
            transform: `${titleAnim.transform} ${titleExit.transform}`,
            textAlign: "center",
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
              AI 핵심 기술 6가지
            </h2>
            <p style={{
              margin: "16px 0 0",
              fontSize: 34,
              fontWeight: 500,
              fontFamily: FONT.family,
              color: COLORS.MUTED,
              lineHeight: 1.4,
            }}>
              현대 인공지능을 이루는 주요 영역
            </p>
          </div>

          {/* 그리드 — Layer 1 + Layer 2 */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 210px)",
            gridTemplateRows: "repeat(2, auto)",
            gap: "20px 24px",
            maxWidth: 700,
            justifyContent: "center",
          }}>
            {ITEMS.map((item, i) => {
              // 카드 진입 (Layer 1) — pickSpring("energetic") 순환
              const cardConfig = pickSpring(i, "energetic");
              const cardAnim = fadeSlideIn(frame, fps, itemDelays[i], cardConfig);
              const cardExit = fadeSlideOut(frame, fps, itemExitDelays[i], durationInFrames);

              // 아이콘 scaleIn (Layer 1 동시)
              const iconAnim = scaleIn(frame, fps, itemDelays[i], pickSpring(i, "energetic"));

              // 레이블 등장 (Layer 2 — 조금 늦게)
              const lblAnim = layeredReveal(frame, fps, 2, {
                itemIndex: i,
                config: SPRING_SNAPPY,
                baseDelay: labelDelay,
              });

              // float — 진입 완료 후 bobbing
              const floatY = float(frame, fps, zone, 5, 0.3 + i * 0.04);

              // shimmer — 오버레이 div에 적용
              const shimmerStyle = shimmer(frame, fps, zone, 200, 0.4 + i * 0.06);

              return (
                <div
                  key={i}
                  style={{
                    position: "relative",
                    width: 210,
                    borderRadius: 20,
                    border: `1px solid rgba(${hexToRgb(item.color)}, 0.18)`,
                    background: `rgba(${hexToRgb(item.color)}, 0.06)`,
                    padding: "24px 16px 20px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 12,
                    opacity: cardAnim.opacity * cardExit.opacity * glassOpacity,
                    transform: `${cardAnim.transform} ${cardExit.transform}`,
                    overflow: "hidden",
                  }}
                >
                  {/* shimmer 오버레이 */}
                  <div style={{
                    position: "absolute",
                    inset: 0,
                    pointerEvents: "none",
                    borderRadius: 20,
                    opacity: 0.55,
                    ...shimmerStyle,
                  }} />

                  {/* 아이콘 컨테이너 — scaleIn */}
                  <div style={{
                    width: 72,
                    height: 72,
                    borderRadius: 18,
                    border: `1px solid rgba(${hexToRgb(item.color)}, 0.22)`,
                    background: `rgba(${hexToRgb(item.color)}, 0.1)`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: item.color,
                    opacity: iconAnim.opacity,
                    transform: `${iconAnim.transform} translateY(${floatY}px)`,
                    flexShrink: 0,
                  }}>
                    {item.icon}
                  </div>

                  {/* 레이블 + 설명 — Layer 2 */}
                  <div style={{
                    opacity: lblAnim.opacity,
                    transform: lblAnim.transform,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 6,
                    textAlign: "center",
                  }}>
                    <span style={{
                      ...STYLE.cardLabel,
                      fontFamily: FONT.family,
                      color: COLORS.TEXT,
                      fontSize: 28,
                      fontWeight: 700,
                    }}>
                      {item.label}
                    </span>
                    <span style={{
                      ...STYLE.cardDesc,
                      fontFamily: FONT.family,
                      color: COLORS.MUTED,
                      fontSize: 24,
                      lineHeight: 1.4,
                      wordBreak: "keep-all",
                    }}>
                      {item.desc}
                    </span>
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

- 아이템 4개이면 `gridTemplateColumns: "repeat(2, 210px)"` 2x2 그리드로 변경
- 배경 이미지 있을 때 카드 border opacity를 0.12로 낮출 것
- 강조 아이템 1개만 있을 때: 해당 카드 border color를 `COLORS.ACCENT_BRIGHT`로 고정하고 나머지는 기본 색 유지
- `float` amplitude를 `i % 2 === 0 ? 5 : -5`로 교대하면 파도 효과
