/**
 * Floating light particles for ambient background motion.
 *
 * Renders small, semi-transparent circles that drift upward slowly.
 * Creates a subtle "alive" feel without distracting from content.
 * Uses deterministic seed-based positioning (no Math.random).
 */
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

interface AmbientParticlesProps {
  /** Number of particles (default 6) */
  count?: number;
  /** Base opacity of particles (default 0.08) */
  opacity?: number;
  /** Particle color (default matches ACCENT with low alpha) */
  color?: string;
}

/** Deterministic pseudo-random from seed (0-1 range) */
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
}

interface ParticleData {
  x: number;       // 0-100 (%)
  startY: number;  // initial Y position (%)
  size: number;    // px
  speed: number;   // px per frame
  phase: number;   // horizontal wobble phase offset
}

function generateParticles(count: number): ParticleData[] {
  return Array.from({ length: count }, (_, i) => ({
    x: seededRandom(i * 7 + 1) * 90 + 5,
    startY: seededRandom(i * 13 + 3) * 60 + 30,
    size: seededRandom(i * 19 + 5) * 3 + 2,
    speed: seededRandom(i * 23 + 7) * 0.3 + 0.15,
    phase: seededRandom(i * 31 + 11) * Math.PI * 2,
  }));
}

export const AmbientParticles: React.FC<AmbientParticlesProps> = ({
  count = 6,
  opacity = 0.08,
  color = "rgba(124, 127, 217, 1)",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Fade in over first 1s, fade out over last 0.5s
  const fadeInEnd = Math.min(fps * 1.0, durationInFrames * 0.4);
  const fadeOutStart = Math.max(fadeInEnd + 1, durationInFrames - fps * 0.5);
  const globalOpacity = interpolate(
    frame,
    [0, fadeInEnd, fadeOutStart, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const particles = React.useMemo(() => generateParticles(count), [count]);

  return (
    <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>
      {particles.map((p, i) => {
        // Slow upward drift
        const yOffset = -p.speed * frame;
        // Gentle horizontal wobble (sine wave)
        const wobble = Math.sin((frame / fps) * 0.5 + p.phase) * 8;
        // Individual particle fade based on vertical position
        const currentY = p.startY + (yOffset * 100) / 1080;
        const particleOpacity = interpolate(
          currentY,
          [-10, 10, 80, 100],
          [0, 1, 1, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${p.x + wobble * 0.3}%`,
              top: `${p.startY}%`,
              transform: `translateY(${yOffset}px)`,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              backgroundColor: color,
              opacity: opacity * globalOpacity * particleOpacity,
              filter: `blur(${p.size * 0.3}px)`,
              willChange: "transform, opacity",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
