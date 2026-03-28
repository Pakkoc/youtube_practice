# Carousel Patterns — Quiet Luxury Theme

> This file is read by Claude Code during `/generate-carousel` Step 4 when theme is **quiet-luxury**.
> For dark theme (default) patterns, see `carousel-patterns.md`.
> All patterns share the same canvas (1080x1350) and component structure — only colors, spacing, and decorations differ.

---

## Quiet Luxury Theme

> White-based "조용한 럭셔리" 테마. Apple minimal + quiet luxury 톤.
> 기존 다크 테마와 **동일한 캔버스/컴포넌트 구조** — 색상·여백·장식만 교체.

---

### QL Color Palette

Import from `../design/theme`:

```tsx
import { QUIET_LUXURY, QL_SHADOW, FONT } from "../design/theme";
```

| Token | Hex | Role |
|-------|-----|------|
| `QUIET_LUXURY.BG` | `#FFFFFF` | 카드 배경 (순백) |
| `QUIET_LUXURY.TEXT` | `#1A1A1A` | 본문 텍스트 |
| `QUIET_LUXURY.TEXT_SECONDARY` | `#555555` | 보조 텍스트, 설명문 |
| `QUIET_LUXURY.ACCENT` | `#2C2C2C` | 기본 악센트 (거의 블랙) |
| `QUIET_LUXURY.ACCENT_WARM` | `#8B7355` | 따뜻한 포인트 (taupe) |
| `QUIET_LUXURY.ACCENT_COOL` | `#6B7B8D` | 차가운 포인트 (slate blue) |
| `QUIET_LUXURY.MUTED` | `#999999` | 캡션, 비활성 |
| `QUIET_LUXURY.BORDER` | `#E5E5E5` | 얇은 구분선, PageDots 비활성 |
| `QUIET_LUXURY.SURFACE` | `#F7F7F5` | 오프화이트 카드 표면 |
| `QUIET_LUXURY.SURFACE_WARM` | `#F5F0EB` | 크림 톤 표면 (따뜻한 카드) |
| `QUIET_LUXURY.CODE_BG` | `#F2F2F2` | 코드/수치 배경 |

**다크 → QL 색상 대체표:**

| Dark Theme | Quiet Luxury 대체 |
|-----------|-------------------|
| `COLORS.BG` (#0B0C0E) | `QUIET_LUXURY.BG` (#FFFFFF) |
| `COLORS.TEXT` (#EDEDEF) | `QUIET_LUXURY.TEXT` (#1A1A1A) |
| `COLORS.ACCENT` (#7C7FD9) | `QUIET_LUXURY.ACCENT_WARM` or `ACCENT_COOL` |
| `COLORS.ACCENT_BRIGHT` (#9B9EFF) | `QUIET_LUXURY.ACCENT` (#2C2C2C) |
| `COLORS.MUTED` (#9394A1) | `QUIET_LUXURY.MUTED` (#999999) |
| `COLORS.TEAL` (#3CB4B4) | `QUIET_LUXURY.ACCENT_COOL` (#6B7B8D) |
| `GLOW.text` | `QL_SHADOW.text` (none) |
| `GLOW.bar` | (사용하지 않음 — glow 금지) |
| `rgba(255,255,255,0.04)` | `QUIET_LUXURY.SURFACE` |
| `rgba(255,255,255,0.08)` border | `1px solid ${QUIET_LUXURY.BORDER}` |

---

### QL Typography

다크 테마와 동일한 `FONT` 상수를 사용하되, **weight 계층과 정렬**이 다름:

| Level | Weight | Letter-spacing | 용도 |
|-------|--------|---------------|------|
| Display | 800 | `-0.04em` | 커버 타이틀 |
| Heading | 600 | `-0.02em` | 섹션 제목 |
| Body | 400 | `0` | 본문, 설명 |
| Light | 300 | `0.02em` | 숫자, 라벨, 캡션 |

**핵심 규칙:**
- **좌측 정렬 기본** (`textAlign: "left"`). 커버와 CTA만 중앙 허용
- Weight 대비로 시각 계층 생성 (800 vs 300), 색상 대비는 최소화
- letter-spacing은 weight에 반비례: 무거울수록 tight, 가벼울수록 loose

---

### QL Spacing & Negative Space

전체 면적의 **50% 이상을 여백**으로 유지. 콘텐츠를 한 쪽에 몰고 나머지는 비워둔다.

| 요소 | 다크 테마 | Quiet Luxury |
|------|----------|-------------|
| Content wrapper top | 80px | 100px |
| Content wrapper left | 72px | 88px |
| Content wrapper right | 72px | 72px (비대칭) |
| Content wrapper bottom | 80px | 80px |
| Item gap | 24-32px | 32-40px |
| Section gap | 32px | 48px |

```tsx
// QL 콘텐츠 래퍼 — 좌측 편향, 넉넉한 상단 여백
<div style={{
  position: "absolute",
  top: 100, left: 88, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 40,
}}>
  {/* Content */}
</div>
```

---

### QL Card Variation Rules

매 카드마다 **최소 2가지**를 변경하여 시각적 단조로움 방지:

1. **히어로 위치**: 우측 하단 → 중앙 → 좌측 상단 (교대)
2. **컷 무드**: 스튜디오 → 디테일 → 에디토리얼 (순환)
3. **텍스트 스케일**: 표준 → 1.5배 확대 → 표준 (콘텐츠 양에 따라)
4. **표면 온도**: `SURFACE` (쿨) → `SURFACE_WARM` (웜) → `BG` (순백) (교대)
5. **악센트 톤**: `ACCENT_WARM` → `ACCENT_COOL` → `ACCENT` (교대)

**금지:** 동일 조합 2장 연속 반복

---

### QL Component Boilerplate

QL 카드도 동일한 `FreeformCard` export 구조를 따름. 색상과 장식만 교체:

```tsx
import React from "react";
import { AbsoluteFill } from "remotion";
import { QUIET_LUXURY, QL_SHADOW, FONT } from "../design/theme";
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

  return (
    <AbsoluteFill style={{ backgroundColor: QUIET_LUXURY.BG }}>
      {/* Background image (optional) — lower opacity for white bg */}
      {backgroundImage && (
        <AbsoluteFill>
          <img
            src={`/${backgroundImage}`}
            style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.08, filter: "saturate(0.3)" }}
          />
        </AbsoluteFill>
      )}

      {/* Content wrapper — QL spacing */}
      <div style={{
        position: "absolute",
        top: 100, left: 88, right: 72, bottom: 80,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: 40,
      }}>
        {/* === Card content here === */}
      </div>

      {/* PageDots — ALWAYS last child */}
      <PageDots
        current={cardIndex}
        total={totalCards}
        accent={QUIET_LUXURY.ACCENT}
        muted={QUIET_LUXURY.BORDER}
      />
    </AbsoluteFill>
  );
};
```

**다크 테마와의 차이:**
- `backgroundColor`: `colors.background` → `QUIET_LUXURY.BG`
- `backgroundImage opacity`: 0.2 → 0.08 (화이트 배경에서는 더 은은하게)
- `backgroundImage filter`: 없음 → `saturate(0.3)` (채도 낮춤)
- `PageDots muted`: `${colors.text}33` → `QUIET_LUXURY.BORDER`
- Content wrapper padding: 대칭 → 비대칭 (left: 88, right: 72)

---

### QL Background & Decoration Patterns

다크 테마의 glow/glass를 **헤어라인·워시·소재 텍스처**로 대체.

#### Hairline Rule (수평 구분선)

glow bar 대신 얇은 1px 라인. 섹션 구분이나 타이틀 아래에 사용.

```tsx
{/* Hairline rule — replaces glow bar */}
<div style={{
  width: 60,
  height: 1,
  background: QUIET_LUXURY.BORDER,
  marginTop: 20,
  marginBottom: 20,
}} />
```

#### Subtle Wash (배경 워시)

radial-gradient glow 대신 은은한 단색 워시. 표면 온도감 추가.

```tsx
{/* Warm wash — subtle cream layer behind content */}
<AbsoluteFill style={{
  background: `linear-gradient(180deg, ${QUIET_LUXURY.SURFACE_WARM}80 0%, transparent 60%)`,
}} />

{/* Cool wash — neutral gray-white gradient */}
<AbsoluteFill style={{
  background: `linear-gradient(160deg, ${QUIET_LUXURY.SURFACE} 0%, ${QUIET_LUXURY.BG} 50%)`,
}} />
```

#### Accent Dot (포인트 점)

floating shape 대신 작은 점 하나로 시선 유도.

```tsx
{/* Accent dot — small warm point */}
<div style={{
  position: "absolute",
  top: 100,
  left: 88,
  width: 8,
  height: 8,
  borderRadius: 4,
  background: QUIET_LUXURY.ACCENT_WARM,
}} />
```

#### Material Texture (소재 텍스처)

blur floating shape 대신 미묘한 질감. 카드 표면에 고급감 추가.

```tsx
{/* Marble-like texture strip — top edge */}
<div style={{
  position: "absolute",
  top: 0,
  left: 0,
  right: 0,
  height: 3,
  background: `linear-gradient(90deg, ${QUIET_LUXURY.BORDER}00, ${QUIET_LUXURY.BORDER}, ${QUIET_LUXURY.BORDER}00)`,
}} />
```

---

### QL Layout Patterns

#### QL-A. Cover Card — 비대칭 좌측 정렬

다크 커버(중앙 정렬 + radial glow)와 달리 **좌측에 텍스트, 우측에 네거티브 스페이스**.

```tsx
{/* Warm wash background */}
<AbsoluteFill style={{
  background: `linear-gradient(170deg, ${QUIET_LUXURY.SURFACE_WARM} 0%, ${QUIET_LUXURY.BG} 45%)`,
}} />

{/* Section label */}
<div style={{
  position: "absolute",
  top: 100,
  left: 88,
  fontSize: 14,
  fontWeight: 300,
  fontFamily: FONT.family,
  color: QUIET_LUXURY.MUTED,
  letterSpacing: "0.15em",
  textTransform: "uppercase" as const,
}}>
  AI AUTOMATION
</div>

{/* Accent dot */}
<div style={{
  position: "absolute",
  top: 106,
  left: 68,
  width: 6,
  height: 6,
  borderRadius: 3,
  background: QUIET_LUXURY.ACCENT_WARM,
}} />

{/* Content — left-aligned, vertically centered */}
<div style={{
  position: "absolute",
  top: 100, left: 88, right: 200, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 28,
}}>
  <div style={{
    fontSize: 52,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT,
    lineHeight: 1.15,
    letterSpacing: "-0.04em",
  }}>
    커버 타이틀
  </div>

  {/* Hairline */}
  <div style={{ width: 48, height: 1, background: QUIET_LUXURY.BORDER }} />

  <div style={{
    fontSize: 22,
    fontWeight: 400,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT_SECONDARY,
    lineHeight: 1.6,
  }}>
    서브타이틀 설명문
  </div>
</div>
```

#### QL-B. Icon Grid — Flat Surface Cards

다크 glass card 대신 **flat surface + thin border**. 아이콘 stroke를 얇게.

```tsx
const items = [
  { label: "빠른 속도", desc: "수동 대비 10배 빠른 처리" },
  { label: "안정성", desc: "99.9% 가동률 보장" },
  { label: "유연성", desc: "완전한 커스터마이징" },
  { label: "프리미엄", desc: "엔터프라이즈급 품질" },
];

{/* Content wrapper — QL spacing */}
<div style={{
  position: "absolute",
  top: 100, left: 88, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "flex-start",
}}>
  {/* Section title — left-aligned */}
  <div style={{
    fontSize: 32,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT,
    marginBottom: 40,
    letterSpacing: "-0.02em",
  }}>
    핵심 기능
  </div>

  {/* Grid — flat surface cards */}
  <div style={{
    display: "flex",
    flexWrap: "wrap" as const,
    gap: 20,
  }}>
    {items.map((item, i) => (
      <div key={i} style={{
        width: 430,
        padding: "36px 28px",
        background: QUIET_LUXURY.SURFACE,
        borderRadius: 12,
        border: `1px solid ${QUIET_LUXURY.BORDER}`,
        boxShadow: QL_SHADOW.card,
        display: "flex",
        flexDirection: "column",
        gap: 10,
      }}>
        {/* SVG icon — strokeWidth: 1 for QL */}
        <div style={{
          fontSize: 22,
          fontWeight: 600,
          fontFamily: FONT.family,
          color: QUIET_LUXURY.TEXT,
        }}>
          {item.label}
        </div>
        <div style={{
          fontSize: 17,
          fontWeight: 400,
          fontFamily: FONT.family,
          color: QUIET_LUXURY.TEXT_SECONDARY,
          lineHeight: 1.5,
        }}>
          {item.desc}
        </div>
      </div>
    ))}
  </div>
</div>
```

#### QL-C. Numbered List — Thin Weight Numbers

다크 테마의 accent badge 대신 **큰 thin-weight 숫자 + 넉넉한 행간**.

```tsx
const listItems = [
  { title: "첫 번째 항목", desc: "항목에 대한 간결한 설명" },
  { title: "두 번째 항목", desc: "항목에 대한 간결한 설명" },
  { title: "세 번째 항목", desc: "항목에 대한 간결한 설명" },
];

<div style={{
  position: "absolute",
  top: 100, left: 88, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 48,
}}>
  {/* Section title */}
  <div style={{
    fontSize: 32,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT,
    letterSpacing: "-0.02em",
  }}>
    실행 단계
  </div>

  {/* List items — generous spacing */}
  <div style={{ display: "flex", flexDirection: "column", gap: 36 }}>
    {listItems.map((item, i) => (
      <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 28 }}>
        {/* Thin weight number */}
        <div style={{
          fontSize: 36,
          fontWeight: 300,
          fontFamily: FONT.family,
          color: QUIET_LUXURY.ACCENT_WARM,
          letterSpacing: "0.02em",
          minWidth: 40,
          lineHeight: 1,
        }}>
          {String(i + 1).padStart(2, "0")}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{
            fontSize: 24,
            fontWeight: 600,
            fontFamily: FONT.family,
            color: QUIET_LUXURY.TEXT,
            lineHeight: 1.3,
          }}>
            {item.title}
          </div>
          <div style={{
            fontSize: 18,
            fontWeight: 400,
            fontFamily: FONT.family,
            color: QUIET_LUXURY.TEXT_SECONDARY,
            lineHeight: 1.5,
          }}>
            {item.desc}
          </div>
        </div>
      </div>
    ))}
  </div>
</div>
```

#### QL-D. Quote Card — Hairline Accent

glass card + glow 대신 **큰 인용문 + 헤어라인 바**.

```tsx
{/* Warm wash */}
<AbsoluteFill style={{
  background: `linear-gradient(180deg, ${QUIET_LUXURY.SURFACE_WARM}60 0%, transparent 50%)`,
}} />

{/* Content — centered */}
<div style={{
  position: "absolute",
  top: 100, left: 88, right: 88, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 32,
}}>
  {/* Large open quote — light weight */}
  <div style={{
    fontSize: 80,
    fontWeight: 300,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.BORDER,
    lineHeight: 0.8,
  }}>
    {"\u201C"}
  </div>

  {/* Quote text */}
  <div style={{
    fontSize: 36,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT,
    lineHeight: 1.5,
    letterSpacing: "-0.02em",
  }}>
    인용문 텍스트가 여기에 들어갑니다
  </div>

  {/* Hairline + attribution */}
  <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 8 }}>
    <div style={{ width: 40, height: 1, background: QUIET_LUXURY.ACCENT_WARM }} />
    <div style={{
      fontSize: 16,
      fontWeight: 400,
      fontFamily: FONT.family,
      color: QUIET_LUXURY.MUTED,
      letterSpacing: "0.04em",
    }}>
      출처 또는 화자
    </div>
  </div>
</div>
```

#### QL-E. Split Left/Right — Text 40% + Visual Hero 60%

NotebookLM 레퍼런스의 핵심 레이아웃. 좌측 텍스트 + 우측(또는 하단) 비주얼.

```tsx
{/* Left text block — 40% */}
<div style={{
  position: "absolute",
  top: 100, left: 88, bottom: 80,
  width: 380,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 24,
}}>
  {/* Label */}
  <div style={{
    fontSize: 13,
    fontWeight: 300,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.MUTED,
    letterSpacing: "0.15em",
    textTransform: "uppercase" as const,
  }}>
    FEATURE
  </div>

  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT,
    lineHeight: 1.2,
    letterSpacing: "-0.03em",
  }}>
    섹션 타이틀
  </div>

  <div style={{ width: 40, height: 1, background: QUIET_LUXURY.BORDER }} />

  <div style={{
    fontSize: 18,
    fontWeight: 400,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT_SECONDARY,
    lineHeight: 1.7,
  }}>
    본문 설명. 3줄 이내 권장.
  </div>
</div>

{/* Right visual hero — 60% */}
<div style={{
  position: "absolute",
  top: 160,
  right: 0,
  bottom: 160,
  width: 540,
  background: QUIET_LUXURY.SURFACE,
  borderRadius: "20px 0 0 20px",
  overflow: "hidden",
  boxShadow: QL_SHADOW.elevated,
}}>
  {/* Image, diagram, or large visual content */}
</div>
```

#### QL-F. CTA Ending — Outlined Button

다크 테마의 filled button + glow 대신 **outlined 버튼 + 미니멀 구성**.

```tsx
{/* Subtle top wash */}
<AbsoluteFill style={{
  background: `linear-gradient(180deg, ${QUIET_LUXURY.SURFACE} 0%, ${QUIET_LUXURY.BG} 40%)`,
}} />

{/* Content — centered */}
<AbsoluteFill style={{
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  padding: "100px 88px",
  textAlign: "center" as const,
}}>
  <div style={{
    fontSize: 40,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT,
    lineHeight: 1.3,
    letterSpacing: "-0.03em",
    marginBottom: 20,
  }}>
    CTA 타이틀
  </div>

  <div style={{
    fontSize: 20,
    fontWeight: 400,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT_SECONDARY,
    lineHeight: 1.5,
    marginBottom: 40,
  }}>
    행동을 유도하는 설명문
  </div>

  {/* Outlined button — no fill, no glow */}
  <div style={{
    padding: "14px 44px",
    border: `1.5px solid ${QUIET_LUXURY.ACCENT}`,
    borderRadius: 40,
    fontSize: 20,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.ACCENT,
  }}>
    팔로우 @handle
  </div>
</AbsoluteFill>
```

---

### QL Common Elements

#### Section Label

다크 테마의 glowing badge 대신 가벼운 대문자 라벨.

```tsx
<div style={{
  fontSize: 13,
  fontWeight: 300,
  fontFamily: FONT.family,
  color: QUIET_LUXURY.MUTED,
  letterSpacing: "0.15em",
  textTransform: "uppercase" as const,
}}>
  SECTION 01
</div>
```

#### Surface Card

glass card(반투명 + blur) 대신 flat surface.

```tsx
<div style={{
  padding: "32px 28px",
  background: QUIET_LUXURY.SURFACE,
  borderRadius: 12,
  border: `1px solid ${QUIET_LUXURY.BORDER}`,
  boxShadow: QL_SHADOW.card,
}}>
  {/* Content */}
</div>
```

#### Hairline Divider

accent gradient divider 대신 1px 실선.

```tsx
<div style={{
  width: 48,
  height: 1,
  background: QUIET_LUXURY.BORDER,
}} />
```

#### Accent Dot

badge/pill 대신 작은 원형 점.

```tsx
<div style={{
  width: 6,
  height: 6,
  borderRadius: 3,
  background: QUIET_LUXURY.ACCENT_WARM,
}} />
```

---

### QL SVG Icons

> QL 아이콘 예시와 규칙은 `carousel-patterns-icons.md`의 "Quiet Luxury Icons" 섹션을 참조하세요.
> 핵심: `strokeWidth: 1` + `QUIET_LUXURY.ACCENT_WARM` 또는 `ACCENT_COOL` 사용.

---

### QL Horizontal Bar Chart

다크 테마 bar chart의 QL 버전. glow 대신 flat bar + subtle shadow.

```tsx
const bars = [
  { label: "항목 A", value: 85, color: QUIET_LUXURY.ACCENT_WARM },
  { label: "항목 B", value: 62, color: QUIET_LUXURY.ACCENT_COOL },
  { label: "항목 C", value: 40, color: QUIET_LUXURY.ACCENT },
];

<div style={{
  position: "absolute",
  top: 100, left: 88, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 36,
}}>
  <div style={{
    fontSize: 32,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: QUIET_LUXURY.TEXT,
    letterSpacing: "-0.02em",
  }}>
    비교 차트
  </div>

  <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
    {bars.map((bar, i) => (
      <div key={i} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 18,
          fontFamily: FONT.family,
        }}>
          <span style={{ color: QUIET_LUXURY.TEXT, fontWeight: 400 }}>{bar.label}</span>
          <span style={{ color: bar.color, fontWeight: 600 }}>{bar.value}%</span>
        </div>
        <div style={{
          width: "100%",
          height: 8,
          background: QUIET_LUXURY.SURFACE,
          borderRadius: 4,
          overflow: "hidden",
        }}>
          <div style={{
            width: `${bar.value}%`,
            height: "100%",
            background: bar.color,
            borderRadius: 4,
          }} />
        </div>
      </div>
    ))}
  </div>
</div>
```

**다크 테마와의 차이:**
- Bar height: 24px → 8px (슬림)
- Bar background: `rgba(255,255,255,0.05)` → `QUIET_LUXURY.SURFACE`
- `boxShadow`: glow 제거
- Label weight: 600 → 400 (가볍게)

---

### QL Content Fill Strategies

| 콘텐츠 양 | QL 전략 |
|----------|---------|
| 소량 (< 3 항목) | 폰트 1.5배 확대, warm/cool wash 배경, accent dot |
| 중간 (3-5 항목) | 표준 폰트, hairline divider, surface card |
| 고밀도 (6+ 항목) | 표준 폰트, 장식 최소, 여백으로 가독성 확보 |

**QL에서 절대 사용하지 않을 것:**
- `glow`, `boxShadow: "0 0 Npx"` (glow 계열)
- `radial-gradient` with accent 색상
- `blur(40px)` floating shapes
- `backdrop-filter: blur()` (glass morphism)
- filled accent background buttons
- neon/bright 색상 조합

**QL에서 대신 사용할 것:**
- `QL_SHADOW.card` / `QL_SHADOW.elevated` (은은한 drop shadow)
- `linear-gradient` with `SURFACE`/`SURFACE_WARM` (워시)
- hairline rules (1px border)
- weight 대비 (800 vs 300)
- 네거티브 스페이스 (50%+ 여백)
