/**
 * Pretendard font loading via Remotion staticFile().
 *
 * Fonts are loaded from remotion/public/fonts/ directory.
 * The actual font files should be copied or symlinked from assets/fonts/.
 */
import React from "react";
import { staticFile, continueRender, delayRender } from "remotion";

const FONT_WEIGHTS = [
  { weight: 400, file: "Pretendard-Regular.otf" },
  { weight: 500, file: "Pretendard-Medium.otf" },
  { weight: 600, file: "Pretendard-SemiBold.otf" },
  { weight: 700, file: "Pretendard-Bold.otf" },
  { weight: 800, file: "Pretendard-ExtraBold.otf" },
  { weight: 900, file: "Pretendard-Black.otf" },
] as const;

/** 가람연꽃 (handwriting font for shorts sub-detail) */
const HANDWRITING_FONTS = [
  { family: "NanumGaramYeonkkot", file: "NanumGaramYeonkkot.ttf", weight: 400 },
] as const;

let fontPromise: Promise<void> | null = null;

/**
 * Load Pretendard + handwriting fonts. Safe to call multiple times (singleton promise).
 */
export async function loadFonts(): Promise<void> {
  if (fontPromise) return fontPromise;

  const pretendardLoads = FONT_WEIGHTS.map(({ weight, file }) => {
    const url = staticFile(`fonts/${file}`);
    const font = new FontFace("Pretendard", `url('${url}')`, {
      weight: String(weight),
      style: "normal",
    });
    return font.load().then((loaded) => {
      document.fonts.add(loaded);
    });
  });

  const handwritingLoads = HANDWRITING_FONTS.map(({ family, file, weight }) => {
    const url = staticFile(`fonts/${file}`);
    const font = new FontFace(family, `url('${url}')`, {
      weight: String(weight),
      style: "normal",
    });
    return font.load().then((loaded) => {
      document.fonts.add(loaded);
    });
  });

  fontPromise = Promise.all([...pretendardLoads, ...handwritingLoads]).then(() => {});

  return fontPromise;
}

/**
 * React hook to ensure fonts are loaded before rendering.
 * Use at the top of each slide component.
 */
export function useFonts(): void {
  const [handle] = React.useState(() => delayRender("Loading Pretendard fonts"));

  React.useEffect(() => {
    loadFonts().then(() => continueRender(handle));
  }, [handle]);
}
