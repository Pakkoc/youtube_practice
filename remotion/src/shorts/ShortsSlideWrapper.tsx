/**
 * Wrapper that composites: HookTitle (top) + TSX slide content (middle) + StyledSubtitle.
 *
 * Used by ShortsSlideSlot{1-4} compositions for script-to-shorts pipeline.
 * ContentComponent is injected at registration time in Root.tsx.
 */
import React from "react";
import { AbsoluteFill } from "remotion";
import { useFonts } from "../design/fonts";
import type { FreeformProps } from "../slides/types";
import { HookTitle } from "./HookTitle";
import { StyledSubtitle } from "./StyledSubtitle";
import {
  SHORTS_CONTENT,
  SHORTS_LAYOUT,
  type ShortsSlideCompositionProps,
} from "./types";

interface ShortsSlideWrapperProps extends ShortsSlideCompositionProps {
  ContentComponent: React.FC<FreeformProps>;
}

export const ShortsSlideWrapper: React.FC<ShortsSlideWrapperProps> = ({
  hookTitle,
  hookTitleLine2 = "",
  subDetail = "",
  words,
  accentColor = "#A2FFEB",
  backgroundColor = "#0f0f0f",
  hookFontSize = 200,
  subtitleFontSize = 48,
  slideIndex,
  totalSlides,
  ContentComponent,
}) => {
  useFonts();

  return (
    <AbsoluteFill style={{ backgroundColor }}>
      {/* TSX slide content in middle zone */}
      <div
        style={{
          position: "absolute",
          top: SHORTS_CONTENT.top,
          left: 0,
          width: SHORTS_CONTENT.width,
          height: SHORTS_CONTENT.height,
          overflow: "hidden",
        }}
      >
        <ContentComponent
          template="Freeform"
          slideIndex={slideIndex}
          totalSlides={totalSlides}
        />
      </div>

      {/* Soft gradient at content top edge (dark zone → content) */}
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

      {/* Soft gradient at content bottom edge (content → dark zone) */}
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

      {/* Subtitle — overlaid on content lower area */}
      <StyledSubtitle
        words={words}
        accentColor={accentColor}
        fontSize={subtitleFontSize}
      />
    </AbsoluteFill>
  );
};
