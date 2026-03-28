import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { FONT } from "../design/theme";
import { SHORTS_LAYOUT, type ShortsWordTimestamp } from "./types";

interface StyledSubtitleProps {
  words: ShortsWordTimestamp[];
  accentColor?: string;
  fontSize?: number;
}

/** Maximum number of words per chunk */
const CHUNK_SIZE = 3;

interface Chunk {
  words: ShortsWordTimestamp[];
  startFrame: number;
  endFrame: number;
}

function buildChunks(words: ShortsWordTimestamp[]): Chunk[] {
  if (words.length === 0) return [];

  const chunks: Chunk[] = [];
  for (let i = 0; i < words.length; i += CHUNK_SIZE) {
    const slice = words.slice(i, i + CHUNK_SIZE);
    chunks.push({
      words: slice,
      startFrame: slice[0].startFrame,
      endFrame: slice[slice.length - 1].endFrame,
    });
  }
  return chunks;
}

export const StyledSubtitle: React.FC<StyledSubtitleProps> = ({
  words,
  accentColor = "#FFD700",
  fontSize = 48,
}) => {
  const frame = useCurrentFrame();

  const chunks = React.useMemo(() => buildChunks(words), [words]);

  // Find the current chunk
  const currentChunk = chunks.find(
    (c) => frame >= c.startFrame && frame <= c.endFrame,
  );

  if (!currentChunk) return null;

  return (
    <div
      style={{
        position: "absolute",
        top: SHORTS_LAYOUT.subtitleY,
        left: SHORTS_LAYOUT.safeZone.left,
        right: SHORTS_LAYOUT.safeZone.right,
        display: "flex",
        flexWrap: "nowrap",
        justifyContent: "center",
        alignItems: "center",
        gap: "14px",
      }}
    >
      {currentChunk.words.map((w, i) => {
        const isActive = frame >= w.startFrame && frame <= w.endFrame;

        // Ensure strictly monotonically increasing inputRange
        // (startFrame === endFrame can happen with very short words)
        const sf = w.startFrame;
        const ef = Math.max(w.endFrame, sf + 1);
        const scale = interpolate(
          frame,
          [sf - 2, sf, ef, ef + 2],
          [1, 1.1, 1.1, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );

        return (
          <span
            key={i}
            style={{
              fontFamily: FONT.family,
              fontSize,
              fontWeight: 700,
              color: isActive ? accentColor : "#FFFFFF",
              transform: `scale(${scale})`,
              textShadow:
                "0 2px 8px rgba(0,0,0,0.9), 0 0 4px rgba(0,0,0,0.6)",
              letterSpacing: "0.04em",
              display: "inline-block",
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
};
