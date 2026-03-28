import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { COLORS, FONT, GLOW } from "../design/theme";
import { useFonts } from "../design/fonts";
import type { FreeformCardProps } from "./types";
import { CAROUSEL_LAYOUT } from "./types";
import { PageDots } from "./CoverCard";

export const FreeformCard: React.FC<FreeformCardProps> = ({
  cardIndex,
  totalCards,
  colors,
  backgroundImage,
}) => {
  useFonts();

  const adopters = [
    { name: "OpenAI", opacity: "CC" },
    { name: "Microsoft", opacity: "CC" },
    { name: "Cursor", opacity: "CC" },
    { name: "Gemini CLI", opacity: "CC" },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: colors.background }}>
      {backgroundImage && (
        <AbsoluteFill style={{ overflow: "hidden" }}>
          <Img
            src={staticFile(backgroundImage)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              opacity: 0.15,
              filter: "saturate(0.6)",
            }}
          />
        </AbsoluteFill>
      )}
      {backgroundImage && (
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.5) 50%, transparent 100%)",
          }}
        />
      )}

      {/* Radial glow */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 60% 45% at 50% 50%, ${colors.accent}25 0%, transparent 70%)`,
        }}
      />

      {/* CTA content — centered */}
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "80px 72px",
          textAlign: "center" as const,
        }}
      >
        {/* Star icon */}
        <svg
          width="56"
          height="56"
          viewBox="0 0 24 24"
          fill="none"
          stroke={colors.accent}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ marginBottom: 32 }}
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>

        {/* Main title */}
        <div
          style={{
            fontSize: 44,
            fontWeight: 800,
            fontFamily: FONT.family,
            color: colors.text,
            lineHeight: 1.3,
            letterSpacing: "-0.02em",
            marginBottom: 16,
            whiteSpace: "pre-line",
          }}
        >
          {"Skills =\n포터블한 전문성"}
        </div>

        {/* Subtitle */}
        <div
          style={{
            fontSize: 22,
            fontWeight: 500,
            fontFamily: FONT.family,
            color: `${colors.text}88`,
            lineHeight: 1.5,
            marginBottom: 36,
            wordBreak: "keep-all" as const,
          }}
        >
          {"한 번 만들면 어디서든 사용\n오픈 스탠다드로 확산 중"}
        </div>

        {/* Adopters row */}
        <div
          style={{
            display: "flex",
            gap: 12,
            marginBottom: 40,
            flexWrap: "wrap" as const,
            justifyContent: "center",
          }}
        >
          {adopters.map((a, i) => (
            <div
              key={i}
              style={{
                padding: "8px 20px",
                background: "rgba(255,255,255,0.04)",
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.10)",
                fontSize: 17,
                fontWeight: 600,
                fontFamily: FONT.family,
                color: `${colors.text}${a.opacity}`,
              }}
            >
              {a.name}
            </div>
          ))}
        </div>

        {/* Accent divider */}
        <div
          style={{
            width: 80,
            height: 3,
            background: `linear-gradient(90deg, ${colors.accent}, ${COLORS.ACCENT_BRIGHT})`,
            borderRadius: 2,
            marginBottom: 32,
            boxShadow: GLOW.bar,
          }}
        />

        {/* Digital asset message */}
        <div
          style={{
            fontSize: 24,
            fontWeight: 600,
            fontFamily: FONT.family,
            color: colors.accent,
            lineHeight: 1.5,
            marginBottom: 44,
            wordBreak: "keep-all" as const,
          }}
        >
          {"커스텀 Skill = 복리로 쌓이는 디지털 자산"}
        </div>

        {/* CTA button */}
        <div
          style={{
            padding: "16px 48px",
            background: colors.accent,
            borderRadius: 50,
            fontSize: 22,
            fontWeight: 700,
            fontFamily: FONT.family,
            color: "#FFFFFF",
            boxShadow: `0 0 24px ${colors.accent}50`,
            marginBottom: 20,
          }}
        >
          Follow @ai.sam_hottman
        </div>

        {/* Secondary CTA */}
        <div
          style={{
            display: "flex",
            gap: 24,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke={COLORS.TEAL}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
            <span
              style={{
                fontSize: 18,
                fontWeight: 600,
                fontFamily: FONT.family,
                color: `${colors.text}77`,
              }}
            >
              저장 + 공유
            </span>
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke={colors.accent}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
              <polyline points="17 6 23 6 23 12" />
            </svg>
            <span
              style={{
                fontSize: 18,
                fontWeight: 600,
                fontFamily: FONT.family,
                color: `${colors.text}77`,
              }}
            >
              Hype 누르기
            </span>
          </div>
        </div>
      </AbsoluteFill>

      <PageDots
        current={cardIndex}
        total={totalCards}
        accent={colors.accent}
        muted={`${colors.text}33`}
      />
    </AbsoluteFill>
  );
};
