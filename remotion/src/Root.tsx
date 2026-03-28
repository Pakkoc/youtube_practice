import React from "react";
import { Composition } from "remotion";
import { Freeform } from "./slides/Freeform";
import { Freeform as FreeformSlot1 } from "./slides/FreeformSlot1";
import { Freeform as FreeformSlot2 } from "./slides/FreeformSlot2";
import { Freeform as FreeformSlot3 } from "./slides/FreeformSlot3";
import { Freeform as FreeformSlot4 } from "./slides/FreeformSlot4";
import {
  DEFAULT_SLIDE_FRAMES,
  type FreeformProps,
} from "./slides/types";
import { ShortsComposition } from "./shorts/ShortsComposition";
import { ShortsSlideWrapper } from "./shorts/ShortsSlideWrapper";
import type {
  ShortsCompositionProps,
  ShortsSlideCompositionProps,
} from "./shorts/types";
import { Freeform as ShortsContentSlot1 } from "./slides/ShortsContentSlot1";
import { Freeform as ShortsContentSlot2 } from "./slides/ShortsContentSlot2";
import { Freeform as ShortsContentSlot3 } from "./slides/ShortsContentSlot3";
import { Freeform as ShortsContentSlot4 } from "./slides/ShortsContentSlot4";
import { FreeformCard } from "./carousel/FreeformCard";
import type { FreeformCardProps } from "./carousel/types";

/**
 * Dynamic duration from props.
 * Python injects durationInFrames into the props JSON,
 * so Remotion allocates exactly the right number of frames.
 * Falls back to DEFAULT_SLIDE_FRAMES (150 = 5s) for Remotion Studio preview.
 */
function slideDuration<T extends { durationInFrames?: number }>({
  props,
}: {
  props: T;
}) {
  return {
    durationInFrames: props.durationInFrames ?? DEFAULT_SLIDE_FRAMES,
  };
}

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Freeform slide — LLM-generated TSX, overwritten per render */}
      <Composition
        id="Freeform"
        component={Freeform}
        durationInFrames={DEFAULT_SLIDE_FRAMES}
        fps={30}
        width={1920}
        height={1080}
        calculateMetadata={slideDuration<FreeformProps>}
        defaultProps={{
          template: "Freeform" as const,
        }}
      />

      {/* Freeform parallel rendering slots (FreeformSlot1-4) */}
      <Composition
        id="FreeformSlot1"
        component={FreeformSlot1}
        durationInFrames={DEFAULT_SLIDE_FRAMES}
        fps={30}
        width={1920}
        height={1080}
        calculateMetadata={slideDuration<FreeformProps>}
        defaultProps={{
          template: "Freeform" as const,
        }}
      />
      <Composition
        id="FreeformSlot2"
        component={FreeformSlot2}
        durationInFrames={DEFAULT_SLIDE_FRAMES}
        fps={30}
        width={1920}
        height={1080}
        calculateMetadata={slideDuration<FreeformProps>}
        defaultProps={{
          template: "Freeform" as const,
        }}
      />
      <Composition
        id="FreeformSlot3"
        component={FreeformSlot3}
        durationInFrames={DEFAULT_SLIDE_FRAMES}
        fps={30}
        width={1920}
        height={1080}
        calculateMetadata={slideDuration<FreeformProps>}
        defaultProps={{
          template: "Freeform" as const,
        }}
      />
      <Composition
        id="FreeformSlot4"
        component={FreeformSlot4}
        durationInFrames={DEFAULT_SLIDE_FRAMES}
        fps={30}
        width={1920}
        height={1080}
        calculateMetadata={slideDuration<FreeformProps>}
        defaultProps={{
          template: "Freeform" as const,
        }}
      />

      {/* Shorts/Reels composition — 1080x1920 vertical */}
      <Composition
        id="ShortsComposition"
        component={ShortsComposition}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={slideDuration<ShortsCompositionProps>}
        defaultProps={{
          hookTitle: "Preview",
          subDetail: "",
          videoSrc: "",
          words: [],
        }}
      />

      {/* ShortsSlideSlot{1-4} — script-to-shorts TSX slide compositions (1080x1920) */}
      <Composition
        id="ShortsSlideSlot1"
        component={(props: ShortsSlideCompositionProps) => (
          <ShortsSlideWrapper {...props} ContentComponent={ShortsContentSlot1} />
        )}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={slideDuration<ShortsSlideCompositionProps>}
        defaultProps={{
          hookTitle: "Preview",
          words: [],
        }}
      />
      <Composition
        id="ShortsSlideSlot2"
        component={(props: ShortsSlideCompositionProps) => (
          <ShortsSlideWrapper {...props} ContentComponent={ShortsContentSlot2} />
        )}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={slideDuration<ShortsSlideCompositionProps>}
        defaultProps={{
          hookTitle: "Preview",
          words: [],
        }}
      />
      <Composition
        id="ShortsSlideSlot3"
        component={(props: ShortsSlideCompositionProps) => (
          <ShortsSlideWrapper {...props} ContentComponent={ShortsContentSlot3} />
        )}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={slideDuration<ShortsSlideCompositionProps>}
        defaultProps={{
          hookTitle: "Preview",
          words: [],
        }}
      />
      <Composition
        id="ShortsSlideSlot4"
        component={(props: ShortsSlideCompositionProps) => (
          <ShortsSlideWrapper {...props} ContentComponent={ShortsContentSlot4} />
        )}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={slideDuration<ShortsSlideCompositionProps>}
        defaultProps={{
          hookTitle: "Preview",
          words: [],
        }}
      />

      {/* Freeform carousel card — LLM-generated TSX, overwritten per render */}
      <Composition
        id="FreeformCard"
        component={FreeformCard}
        durationInFrames={1}
        fps={30}
        width={1080}
        height={1350}
        defaultProps={{
          cardIndex: 0,
          totalCards: 1,
          colors: {
            background: "#0B0C0E",
            accent: "#7C7FD9",
            text: "#EDEDEF",
          },
        } satisfies FreeformCardProps}
      />

    </>
  );
};
