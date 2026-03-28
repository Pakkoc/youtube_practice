import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { useFonts } from "../design/fonts";
import { HookTitle } from "./HookTitle";
import { StyledSubtitle } from "./StyledSubtitle";
import { SHORTS_LAYOUT, type ShortsCompositionProps } from "./types";

export const ShortsComposition: React.FC<ShortsCompositionProps> = ({
  hookTitle,
  hookTitleLine2 = "",
  subDetail = "",
  videoSrc,
  words,
  accentColor = "#A2FFEB",
  backgroundColor = "#0f0f0f",
  hookFontSize = 200,
  subtitleFontSize = 48,
}) => {
  useFonts();

  const videoUrl = videoSrc ? staticFile(videoSrc) : "";

  return (
    <AbsoluteFill style={{ backgroundColor }}>
      {/* Video in middle zone — cover crops 16:9 sides for zoom effect */}
      {videoUrl && (
        <OffthreadVideo
          src={videoUrl}
          style={{
            position: "absolute",
            top: SHORTS_LAYOUT.videoY,
            left: 0,
            width: SHORTS_LAYOUT.videoWidth,
            height: SHORTS_LAYOUT.videoHeight,
            objectFit: "cover",
          }}
        />
      )}

      {/* Soft gradient at video top edge (dark zone → video) */}
      <div
        style={{
          position: "absolute",
          top: SHORTS_LAYOUT.videoY,
          left: 0,
          right: 0,
          height: 80,
          background:
            "linear-gradient(to bottom, rgba(15,15,15,0.7) 0%, transparent 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Soft gradient at video bottom edge (video → dark zone) */}
      <div
        style={{
          position: "absolute",
          top: SHORTS_LAYOUT.videoY + SHORTS_LAYOUT.videoHeight - 80,
          left: 0,
          right: 0,
          height: 80,
          background:
            "linear-gradient(to top, rgba(15,15,15,0.7) 0%, transparent 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Hook Title — centered in top dark zone, 3-layer */}
      <HookTitle
        line1={hookTitle}
        line2={hookTitleLine2}
        subDetail={subDetail}
        fontSize={hookFontSize}
        accentColor={accentColor}
      />

      {/* Subtitle — overlaid on video lower area */}
      <StyledSubtitle
        words={words}
        accentColor={accentColor}
        fontSize={subtitleFontSize}
      />
    </AbsoluteFill>
  );
};
