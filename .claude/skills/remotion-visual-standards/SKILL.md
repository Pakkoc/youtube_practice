---
name: remotion-visual-standards
description: "Visual quality guidelines for Remotion slides — background treatment, text contrast, layout variety, card styling, spring animations, Korean typography, and Shorts safe zones. Load when generating or reviewing Remotion TSX slides."
user-invocable: false
---

# Remotion Visual Quality Standards

## Activation Conditions
- **Keywords**: remotion, visual, quality, 비주얼, 품질, contrast, layout, 레이아웃, background, blur
- **Intent Patterns**: "슬라이드 품질 체크", "비주얼 가이드", "레이아웃 반복", "텍스트 가독성"
- **Working Files**: `remotion/src/slides/`, `remotion/src/design/`, `projects/*/slides/*.tsx`
- **Content Patterns**: `backgroundImage`, `filter: blur`, `mix-blend-mode`, `fontFamily`

---

## Pre-coding Protocol
- 비주얼 변경 전 레이아웃 해석을 사용자와 확인. px, hex color, opacity 명시 검증.
- 템플릿/테마 → 각 variant가 시각적으로 구분 가능한지 확인.

---

## 1. Background Image Treatment

### Rules
- **Blur**: minimum `filter: blur(8px)` on all B-roll background images
- **`mix-blend-mode` 사용 금지** — 테마/브라우저마다 렌더링 불일치, Remotion 서버 렌더에서 깨짐
- **Gradient overlay 필수** — 배경 이미지 위에 반드시 반투명 그라디언트 오버레이 적용

### Reference Implementation (`AnimatedBackground.tsx`)
```tsx
// B-roll image: opacity 0.1, saturate 0.7, progressive zoom
<Img src={backgroundImage} style={{
  opacity: 0.1,
  filter: 'saturate(0.7)',
  transform: `scale(${zoom})`,  // 1.02 → 1.08
}} />
```

### Freeform TSX에서 배경 사용 시
```tsx
// GOOD: gradient overlay + blur
<div style={{
  backgroundImage: `url(${bgUrl})`,
  filter: 'blur(12px)',
  opacity: 0.15,
}} />
<div style={{
  background: 'linear-gradient(180deg, rgba(11,12,14,0.9) 0%, rgba(11,12,14,0.7) 100%)',
  position: 'absolute', inset: 0,
}} />

// BAD: mix-blend-mode
<div style={{ mixBlendMode: 'overlay' }} />  // NEVER
```

---

## 2. Text Contrast (WCAG AA: 4.5:1 minimum)

### Dark Tech Theme (default)
| Element | Color | On Background | Ratio |
|---------|-------|---------------|-------|
| Primary text | `#EDEDEF` | `#0B0C0E` | 18.2:1 |
| Accent text | `#7C7FD9` | `#0B0C0E` | 5.8:1 |
| Muted text | `#9394A1` | `#0B0C0E` | 6.5:1 |
| Accent bright | `#9B9EFF` | `#0B0C0E` | 8.1:1 |
| Teal | `#3CB4B4` | `#0B0C0E` | 8.5:1 |

### Quiet Luxury Theme
| Element | Color | On Background | Ratio |
|---------|-------|---------------|-------|
| Primary text | `#1A1A1A` | `#FFFFFF` | 16.8:1 |
| Secondary text | `#555555` | `#FFFFFF` | 7.5:1 |
| Muted text | `#999999` | `#FFFFFF` | 2.8:1 (label only) |
| Accent warm | `#8B7355` | `#FFFFFF` | 4.0:1 (large text) |

### Rules
- Body text (`fontSize < 24px`): contrast ratio **4.5:1** 이상
- Large text (`fontSize >= 24px`, `fontWeight >= 700`): contrast ratio **3:1** 이상
- Muted 색상(`#999999`)은 **보조 라벨에만** 사용, 본문 텍스트 금지
- 배경 이미지 위 텍스트: `textShadow` 또는 카드 컨테이너로 가독성 확보

---

## 3. Layout Variety (반복 금지)

### Rule
연속 슬라이드에서 **동일한 레이아웃/구성을 반복하지 않는다**.

### Checklist
- [ ] 연속 슬라이드가 같은 flex direction, 같은 카드 배치를 사용하지 않도록
- [ ] 시각적 리듬: 정보 밀도 높은 슬라이드 → 심플한 슬라이드 교대
- [ ] 동일 레이아웃 패턴이 전체 슬라이드의 30% 이하

### Layout Variation Strategies
```
슬라이드 1: title-hero (도입)
슬라이드 2: step-flow (단계)
슬라이드 3: big-number (핵심 수치)
슬라이드 4: split-compare (비교)
슬라이드 5: quote-glass (핵심 메시지)
```

### Visual Progression

영상 전체에서 시각적 단조로움을 피하기 위해, 색상/borderRadius/glow를 영상 흐름에 따라 변화시킨다.
정해진 공식 없음 — 대본의 서사 흐름에 맞게 자유롭게 전환.

변화의 도구들:
- **Color temperature**: cool(보라) → warm(코랄) → cool 복귀
- **borderRadius**: 둥근(20px+) → 날카로운(4-8px) → 부드러운 복귀
- **Glow**: full glow → clean shadow only → subtle glow 복귀

> 아트 디렉션 단계에서 "Visual Progression" 계획을 세울 때 이 palette를 참고.

---

## 4. Card & Container Styling

### Default Card Values (Dark Tech)
```tsx
const CARD_STYLE = {
  borderRadius: 20,                    // px
  padding: '32px 40px',
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(255,255,255,0.08)',
  boxShadow: '0 8px 40px rgba(0,0,0,0.6), 0 2px 8px rgba(0,0,0,0.3)',
};
```

### Default Card Values (Quiet Luxury)
```tsx
const CARD_STYLE_QL = {
  borderRadius: 16,                    // px
  padding: '32px 40px',
  background: '#F7F7F5',
  border: '1px solid #E5E5E5',
  boxShadow: '0 2px 20px rgba(0,0,0,0.06)',
};
```

### Glass Card (Dark Tech 전용)
```tsx
const GLASS_CARD = {
  borderRadius: 20,
  padding: '32px 40px',
  background: 'rgba(255,255,255,0.03)',
  backdropFilter: 'blur(12px)',
  border: '1px solid rgba(255,255,255,0.06)',
};
```

### Card Style Palette (선택적 — 시각 변화용)

영상 흐름에 따라 카드 스타일을 변화시키고 싶을 때 활용할 수 있는 palette.
필수가 아닌 선택 옵션 — 자유롭게 조합하거나 변형하라.

**Warm Card** — 따뜻한 느낌, glow 없음:
```tsx
const CARD_WARM = {
  borderRadius: 12, padding: '32px 40px',
  background: 'rgba(232,145,109,0.06)',
  border: '1px solid rgba(232,145,109,0.12)',
  boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
};
// accent: "#E8916D"
```

**Contrast Card** — 날카로운 느낌, 두꺼운 보더:
```tsx
const CARD_CONTRAST = {
  borderRadius: 6, padding: '28px 36px',
  background: 'rgba(155,158,255,0.04)',
  border: '2px solid rgba(155,158,255,0.25)',
  boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
};
// accent: "#9B9EFF"
```

**Soft Card** — 차분한 느낌, 미묘한 glow:
```tsx
const CARD_SOFT = {
  borderRadius: 24, padding: '36px 44px',
  background: 'rgba(255,255,255,0.03)',
  border: '1px solid rgba(255,255,255,0.06)',
  boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
};
// accent: "#9394A1", textShadow: "0 0 12px rgba(124,127,217,0.2)"
```

### Rules
- `borderRadius` 기본 20px — 영상 흐름에 따라 자유롭게 변화 가능 (6~28px)
- 카드 내부 `padding` 최소 `24px` (텍스트가 테두리에 붙지 않도록)
- 카드 간 간격 최소 `20px`
- Elevated card는 `boxShadow` 필수

---

## 5. Animation (Spring-Based Motion)

### Spring Presets
```tsx
// Remotion spring() 사용 — CSS transition/keyframe 금지 (렌더링 시 동작 안함)
SPRING_GENTLE  = { damping: 15, mass: 0.8 }  // 제목, 대형 요소
SPRING_SNAPPY  = { damping: 20, mass: 0.6 }  // 불릿, 소형 요소
SPRING_BOUNCY  = { damping: 8,  mass: 0.6 }  // 강조, 드라마틱 진입
SPRING_STIFF   = { damping: 25, mass: 0.5 }  // 빠른 결정적 동작
```

### Stagger Delay
- 기본 아이템 간 딜레이: **6 frames** (200ms @ 30fps)
- 최소 gap: 3 frames (~100ms)
- 최대 gap: 60 frames (~2s)
- 마지막 아이템 후 settle: 20 frames (~667ms)

### Duration-Proportional Entrance
| 슬라이드 길이 | 진입 비율 |
|---------------|-----------|
| ≤3초 | 50% |
| 3~5초 | 50%→65% (선형) |
| 5~10초 | 65%→50% (선형) |
| ≥10초 | 50% |

### Rules
- **CSS `transition`, `@keyframes`, `animation` 사용 금지** — Remotion 서버 렌더에서 동작 안함
- 모든 모션은 `spring()` + `interpolate()` 조합
- 진입 애니메이션: `opacity 0→1` + `translateY 30px→0` (기본)
- 퇴장 애니메이션: 슬라이드 duration의 15% (최대 0.8초)

---

## 6. Korean Typography

### Font Priority
```tsx
fontFamily: "'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, system-ui, sans-serif"
```

### Font Weights & Sizes (Design System)
| Element | Size | Weight | Letter Spacing | Line Height |
|---------|------|--------|----------------|-------------|
| Title | 76px | 800 | -0.04em | 1.1 |
| Subtitle | 28px | 500 | — | 1.4 |
| Bullet text | 36px | 500 | — | 1.25 |
| Big Number | 120px | 800 | — | 1.0 |
| Context | 32px | 500 | — | 1.4 |
| Card label | 24px | 600 | — | — |
| Card desc | 18px | 400 | — | 1.4 |
| Card body | 22px | 500 | — | 1.35 |

### Korean Text Rules
- `wordBreak: 'keep-all'` 필수 — 한국어 단어 중간 줄바꿈 방지
- `lineHeight` 최소 1.25 — 한글은 라틴 문자보다 높이가 큼
- `whiteSpace: 'pre-wrap'` 또는 `'normal'` 사용 (줄바꿈 보존)
- 긴 한국어 텍스트: `fontSize` 적응형 축소 (`FONT.title` 76px → 64px → 52px)

---

## 7. Shorts/Reels Layout (9:16)

### Canvas
- Resolution: **1080 x 1920** (9:16)
- Background: `#0F0F0F` (near-black)

### Safe Zones
```
┌──────────────────────┐
│   Hook Title Zone    │ y: 0~310px
│   (hookY = 310)      │
├──────────────────────┤
│                      │
│   Video Content      │ y: 460px, 1080x608
│   (16:9 contained)   │ videoY = 460
│                      │
├──────────────────────┤
│   Subtitle Zone      │ y: 1120px~
│   (subtitleY = 1120) │
│                      │
│   Bottom Safe Zone   │ margin-bottom: 120px (nav bar)
└──────────────────────┘

Left/Right safe margin: 48px
```

### Hook Title
- Font size: 80px (기본, 긴 텍스트 시 축소)
- Font weight: 800
- Max 2 lines
- Text shadow: heavy drop shadow for readability
- Spring entrance: `SPRING_GENTLE`

### Subtitle
- Font size: 48px
- Font weight: 700
- 3-word chunks
- Text shadow: `0 2px 8px rgba(0,0,0,0.9), 0 0 4px rgba(0,0,0,0.6)`
- Active word scale: `1.1x`

### Rules
- 16:9 원본 비율 유지 — 절대 crop/stretch 금지
- 검은 배경 위 샌드위치 레이아웃 (풀스크린 영상 아님)
- Hook title과 subtitle이 video content와 겹치지 않도록
- Bottom 120px은 모바일 네비게이션 바 영역 — 콘텐츠 배치 금지

---

## Quick Checklist (슬라이드 생성/리뷰 시)

- [ ] 배경 이미지: blur ≥ 8px, opacity ≤ 0.15, gradient overlay 적용
- [ ] `mix-blend-mode` 미사용
- [ ] 텍스트 contrast ratio ≥ 4.5:1 (본문), ≥ 3:1 (대형 텍스트)
- [ ] 연속 슬라이드 동일 레이아웃 반복 없음
- [ ] 카드: `padding ≥ 24px`, borderRadius 적절
- [ ] 애니메이션: `spring()` + `interpolate()` only (CSS transition 금지)
- [ ] 한국어: `wordBreak: 'keep-all'`, `fontFamily` Pretendard 우선
- [ ] Shorts: safe zone 준수, 16:9 비율 유지
- [ ] **레이어 겹침 없음**: centered AbsoluteFill 내 요소와 position:absolute 요소가 같은 수직 영역을 차지하지 않음 (타이틀+다이어그램 패턴 시 타이틀은 absolute 상단 고정)
