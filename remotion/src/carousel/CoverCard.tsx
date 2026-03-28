/**
 * Shared carousel components — PageDots.
 * Kept in CoverCard.tsx for backward-compat with existing card_*.tsx imports.
 */
import React from "react";

/** Shared page dots component */
export const PageDots: React.FC<{
  current: number;
  total: number;
  accent: string;
  muted: string;
}> = ({ current, total, accent, muted }) => (
  <div
    style={{
      position: "absolute",
      bottom: 40,
      left: 0,
      right: 0,
      display: "flex",
      justifyContent: "center",
      gap: 8,
    }}
  >
    {Array.from({ length: total }).map((_, i) => (
      <div
        key={i}
        style={{
          width: i === current ? 24 : 8,
          height: 8,
          borderRadius: 4,
          backgroundColor: i === current ? accent : muted,
        }}
      />
    ))}
  </div>
);
