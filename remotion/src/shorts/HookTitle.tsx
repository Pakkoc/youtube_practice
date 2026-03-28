import React, { useMemo } from "react";
import { FONT } from "../design/theme";
import { SHORTS_BRANDING, SHORTS_LAYOUT } from "./types";

interface HookTitleProps {
  line1: string;
  line2?: string;
  subDetail?: string;
  fontSize?: number;
  accentColor?: string;
}

/** Safe width = 1080 - 40*2 padding */
const SAFE_WIDTH = 1000;

/**
 * Height budget for main hook text inside 480px Hook Zone.
 * 480 - paddingBottom(8) - category(45+16) - subDetail(80) - breathing(40) ≈ 291px
 */
const MAIN_HEIGHT_BUDGET = 291;

const LINE_HEIGHT = 0.95;

/** Estimate total rendered width of text at a given fontSize. */
function estimateTextWidth(text: string, fontSize: number): number {
  let width = 0;
  for (const ch of text) {
    const code = ch.codePointAt(0) ?? 0;
    // CJK Unified, Hangul Syllables, Hangul Jamo, CJK symbols
    if (
      (code >= 0x3000 && code <= 0x9fff) ||
      (code >= 0xac00 && code <= 0xd7af) ||
      (code >= 0xf900 && code <= 0xfaff)
    ) {
      width += fontSize * 0.92; // Korean/CJK — roughly square
    } else if (ch === " ") {
      width += fontSize * 0.25;
    } else {
      width += fontSize * 0.55; // Latin, digits, symbols
    }
  }
  return width;
}

/**
 * Auto-scale font size to guarantee SINGLE LINE rendering.
 *
 * Shrinks from baseFontSize until estimated text width fits within SAFE_WIDTH.
 * Also caps at MAIN_HEIGHT_BUDGET for extreme cases.
 * Floor: 56px (below this the title is unreadable).
 */
const scaleFontSize = (text: string, baseFontSize: number): number => {
  let size = baseFontSize;
  const minSize = 56;

  while (size > minSize) {
    const textWidth = estimateTextWidth(text, size);
    // Force single line: text must fit within safe width
    if (textWidth <= SAFE_WIDTH && size * LINE_HEIGHT <= MAIN_HEIGHT_BUDGET) {
      return Math.round(size);
    }
    size *= 0.9; // shrink 10%
  }

  return Math.round(minSize);
};

/**
 * Auto-scale subDetail font size (handwriting font).
 * Base: 80px, Floor: 40px. Only width constraint (no height budget).
 */
const scaleSubDetailFontSize = (text: string): number => {
  let size = 80;
  const minSize = 40;

  while (size > minSize) {
    if (estimateTextWidth(text, size) <= SAFE_WIDTH) {
      return Math.round(size);
    }
    size *= 0.9;
  }

  return Math.round(minSize);
};

/**
 * 3-layer Hook Title for Shorts — CENTER-ALIGNED, STATIC (no animation).
 *
 * ┌──────────────────────────────────────┐ 0px
 * │  [Claude Code 왕기초]  샘호트만:시선  │ ← pill(left) + channel(right)
 * │       프로젝트 초기화 명령어           │ ← Main Hook (200px base, w900, neon)
 * │      /init · 바로 써먹기             │ ← Sub Detail (80px, center)
 * └──────────────────────────────────────┘ 480px
 */
export const HookTitle: React.FC<HookTitleProps> = ({
  line1,
  line2 = "",
  subDetail = "",
  fontSize = 200,
  accentColor = "#A2FFEB",
}) => {
  // Combine line1 + line2 into single display line (no split)
  const mainTitle = line2 ? `${line1} ${line2}` : line1;
  const mainFontSize = useMemo(() => scaleFontSize(mainTitle, fontSize), [mainTitle, fontSize]);
  const subDetailFontSize = useMemo(
    () => (subDetail ? scaleSubDetailFontSize(subDetail) : 80),
    [subDetail],
  );

  // Multi-layer neon glow — intensified "발광" effect
  const neonGlow = useMemo(
    () =>
      [
        `0 0 12px ${accentColor}DD`,
        `0 0 28px ${accentColor}66`,
        `0 0 56px ${accentColor}33`,
        `0 0 80px ${accentColor}1A`,
        `0 2px 10px rgba(0,0,0,0.95)`,
      ].join(", "),
    [accentColor],
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: SHORTS_LAYOUT.hookZoneHeight,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-end",
        paddingLeft: 40,
        paddingRight: 40,
        paddingBottom: 8,
        gap: 0,
        overflow: "hidden",
      }}
    >
      {/* Layer 0: Series name — small, left-aligned, own row */}
      <div
        style={{
          width: "100%",
          fontFamily: "'NanumGaramYeonkkot', cursive",
          fontSize: 24,
          fontWeight: 400,
          color: "rgba(255, 255, 255, 0.45)",
          letterSpacing: "0.04em",
          textShadow: "0 1px 3px rgba(0,0,0,0.4)",
          textAlign: "left",
          marginBottom: 4,
        }}
      >
        {SHORTS_BRANDING.seriesName}
      </div>

      {/* Layer 1: Channel name — right-aligned */}
      <div
        style={{
          width: "100%",
          fontFamily: "'NanumGaramYeonkkot', cursive",
          fontSize: 38,
          fontWeight: 400,
          color: "rgba(255, 255, 255, 0.45)",
          letterSpacing: "0.04em",
          textShadow: "0 1px 3px rgba(0,0,0,0.4)",
          textAlign: "right",
          marginBottom: 16,
        }}
      >
        {SHORTS_BRANDING.channelName}
      </div>

      {/* Layer 2: Main Hook Title — 화면을 뚫고 나오는 크기 */}
      <div
        style={{
          width: "100%",
          fontFamily: FONT.family,
          fontSize: mainFontSize,
          fontWeight: 900,
          color: accentColor,
          textShadow: neonGlow,
          lineHeight: 0.95,
          textAlign: "center",
          letterSpacing: "-0.03em",
          whiteSpace: "nowrap",
        }}
      >
        {mainTitle}
      </div>

      {/* Layer 3: Sub Detail — 메인 바로 아래, 괄호 스타일 (동적 폰트 스케일링) */}
      {subDetail && (
        <div
          style={{
            width: "100%",
            fontFamily: "'NanumGaramYeonkkot', cursive",
            fontSize: subDetailFontSize,
            fontWeight: 400,
            color: "rgba(255, 255, 255, 0.8)",
            textShadow: "0 1px 6px rgba(0,0,0,0.6)",
            textAlign: "center",
            marginTop: 0,
          }}
        >
          {subDetail}
        </div>
      )}
    </div>
  );
};
