# Text Quote — 인용/핵심 메시지 슬라이드

## 언제 사용

핵심 인용문, 중요 메시지, 명언, 결론적 문장 강조.
감성/스토리 성격의 슬라이드에서 단 하나의 문장을 시청자 마음에 새길 때.

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
import { wordStagger, fadeSlideIn } from "../motifs/entries";
import { blurOut } from "../motifs/exits";
import { glassCardOpacity, shimmer } from "../motifs/decorations";
import { shimmer as shimmerFx } from "../motifs/emphasis";
import { SPRING_GENTLE } from "../motifs/springConfigs";
import { getAnimationZone, zoneDelay, getExitStart } from "../motifs/timing";

export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const zone = getAnimationZone(durationInFrames, { fps });
  const exitStart = getExitStart(durationInFrames, { fps });

  // --- 인용문 단어 스태거 ---
  const quote = "실패는 성공의 어머니가 아니라, 다음 시도의 설계도다.";
  const words = quote.split(" ");

  // --- 출처 라인 등장 (인용문 이후) ---
  const attributionDelay = zoneDelay(0.65, zone);
  const attributionAnim = fadeSlideIn(frame, fps, attributionDelay, SPRING_GENTLE);

  // --- 글래스 카드 등장 ---
  const cardOpacity = glassCardOpacity(frame, fps, 0.5);

  // --- 시머 효과 (글래스 카드 위 빛줄기) ---
  const shimmerStyle = shimmerFx(frame, fps, zone, 220, 1.4, "rgba(255,255,255,0.06)");

  // --- 따옴표 아이콘 등장 ---
  const quoteMarkDelay = zoneDelay(0.0, zone);
  const quoteMarkAnim = fadeSlideIn(frame, fps, quoteMarkDelay, SPRING_GENTLE);

  // --- blurOut 퇴장 ---
  const exit = blurOut(frame, fps, exitStart, durationInFrames);

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

        {/* 글래스 카드 컨테이너 */}
        <div style={{
          position: "relative",
          maxWidth: 1300,
          width: "100%",
          background: `rgba(124, 127, 217, 0.06)`,
          border: "1px solid rgba(124, 127, 217, 0.18)",
          borderRadius: 28,
          padding: "72px 88px 64px 88px",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          opacity: cardOpacity,
        }}>

          {/* 시머 오버레이 */}
          <div style={{
            position: "absolute",
            inset: 0,
            borderRadius: 28,
            pointerEvents: "none",
            ...shimmerStyle,
          }} />

          {/* 따옴표 SVG 아이콘 */}
          <div style={{
            ...quoteMarkAnim,
            opacity: quoteMarkAnim.opacity * exit.opacity,
            transform: `${quoteMarkAnim.transform ?? ""} ${exit.transform}`,
            filter: exit.filter,
            marginBottom: 36,
          }}>
            <svg
              width="64"
              height="48"
              viewBox="0 0 64 48"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M0 48V28.8C0 20.16 1.8 13.08 5.4 7.56C9 2.04 14.52 0 22.08 0L24 3.6
                   C18.72 5.04 15 7.92 12.84 12.24C10.68 16.44 9.6 21.24 9.6 26.64H19.2V48H0Z
                   M36 48V28.8C36 20.16 37.8 13.08 41.4 7.56C45 2.04 50.52 0 58.08 0L60 3.6
                   C54.72 5.04 51 7.92 48.84 12.24C46.68 16.44 45.6 21.24 45.6 26.64H55.2V48H36Z"
                fill={COLORS.ACCENT}
                opacity={0.7}
              />
            </svg>
          </div>

          {/* 인용문 — 단어별 스태거 등장 */}
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0 12px",
            marginBottom: 48,
          }}>
            {words.map((word, i) => {
              const anim = wordStagger(frame, fps, i, words.length, zone, 0, SPRING_GENTLE);
              return (
                <span
                  key={i}
                  style={{
                    display: "inline-block",
                    fontFamily: FONT.family,
                    fontSize: 52,
                    fontWeight: 700,
                    lineHeight: 1.35,
                    color: COLORS.TEXT,
                    letterSpacing: "-0.02em",
                    wordBreak: "keep-all",
                    opacity: anim.opacity * exit.opacity,
                    transform: `${anim.transform ?? ""} ${exit.transform}`,
                    filter: `${anim.filter ?? ""} ${exit.filter}`,
                  }}
                >
                  {word}
                </span>
              );
            })}
          </div>

          {/* 구분선 */}
          <div style={{
            width: 60,
            height: 2,
            background: `rgba(124, 127, 217, 0.45)`,
            borderRadius: 2,
            marginBottom: 28,
            opacity: attributionAnim.opacity * exit.opacity,
          }} />

          {/* 출처/화자 */}
          <div style={{
            ...attributionAnim,
            opacity: attributionAnim.opacity * exit.opacity,
            transform: `${attributionAnim.transform ?? ""} ${exit.transform}`,
            filter: exit.filter,
            fontFamily: FONT.family,
            fontSize: 34,
            fontWeight: 500,
            color: COLORS.MUTED,
            letterSpacing: "0.02em",
          }}>
            — 에디슨의 노트, 1878
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

- `wordStagger` — 단어별 blur+slide-up reveal. `quote.split(" ")`로 분할 후 `i`, `words.length`, `zone`, `SPRING_GENTLE` 전달. 시청자 시선이 읽기 순서를 자연스럽게 따라감.
- `glassCardOpacity` — 카드 등장 페이드. `opacity` 반환값을 컨테이너 div에 직접 적용. `backdropFilter` 금지 — 대신 `rgba(0.06)` + `border 0.18` 조합.
- `shimmer` (emphasis) — `{ background, backgroundSize, backgroundPosition }` 반환. 반드시 `position: absolute, inset: 0, pointerEvents: "none"` 오버레이 div에 스프레드. 카드의 배경색과 분리해야 덮어쓰기 방지됨.
- `SPRING_GENTLE` — 감성/무게감 있는 슬라이드에 적합. 커튼이 열리듯 천천히 등장.
- `blurOut` — `{ opacity, transform: "scale(N)", filter: "blur(Npx)" }` 반환. 입장 anim과 opacity/transform/filter를 각각 곱/연결. cinematic 퇴장.
- `zoneDelay(0.65, zone)` — 출처 라인은 인용문이 거의 다 나온 뒤(65% 지점)에 등장.
- `getAnimationZone` + `zoneDelay` — 하드코딩된 프레임 딜레이 없이 슬라이드 길이에 비례한 타이밍 보장.
