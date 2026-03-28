/**
 * Light-streak shimmer effect sweeping left-to-right.
 * Returns CSS background properties for a moving gradient highlight overlay.
 * Apply via spread: <div style={{ ...shimmer(...) }} />
 */

/**
 * Returns background style properties for a sweeping shimmer.
 * @param frame - Current frame
 * @param fps - Frames per second
 * @param startAfterFrames - Frames to wait before starting
 * @param width - Shimmer band width in % (default 40)
 * @param speed - Sweep speed in Hz (default 0.3 = one pass per ~3.3s)
 * @param color - Shimmer highlight color (default subtle white)
 */
export function shimmer(
  frame: number,
  fps: number,
  startAfterFrames: number = 15,
  width: number = 40,
  speed: number = 0.3,
  color: string = "rgba(255,255,255,0.06)",
): { background: string; backgroundSize: string; backgroundPosition: string } {
  if (frame < startAfterFrames) {
    return {
      background: "none",
      backgroundSize: "200% 100%",
      backgroundPosition: "-100% 0",
    };
  }

  const elapsed = frame - startAfterFrames;
  const cycle = (elapsed / fps) * speed;
  // Position sweeps from -100% to 200% in a continuous loop
  const pos = ((cycle % 1) * 300 - 100);

  return {
    background: `linear-gradient(90deg, transparent ${pos}%, ${color} ${pos + width / 2}%, transparent ${pos + width}%)`,
    backgroundSize: "100% 100%",
    backgroundPosition: "0 0",
  };
}
