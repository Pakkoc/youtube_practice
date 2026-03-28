---
name: generate-carousel
description: "Remotion Freeform TSX Carousel Generator"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
argument-hint: "<project-name>"
---

# /generate-carousel -- Remotion Freeform TSX Carousel Generator

You are generating custom Remotion Freeform TSX carousel cards (card news) for an Instagram project.
Each card gets one `.tsx` file that will be rendered to a static `.png` by `remotion still`.

**Argument**: project name (e.g., `fastcampus-landing`)

---

## Channel Persona & Branding (필수)

**Before generating any card**, read these two files:

1. `prompts/channel_identity.txt` — 페르소나 규칙 (샘호트만 ≠ Sam Altman)
2. `config/config.base.yaml` → `carousel.branding` 섹션:
   - **brand_name**: 어트리뷰션에 사용
   - **brand_voice**: 모든 카드 텍스트의 톤 기준 (예: "친근하지만 전문적, 개조식, 핵심만")
   - **target_audience**: 콘텐츠 난이도/용어 수준 결정 기준
3. `config/config.base.yaml` → `carousel.background.enabled`:
   - **`true`**: AI 배경 이미지 ON → Step 3.5에서 NanoBanana로 생성, TSX에 반영
   - **`false`** (기본값): AI 배경 이미지 OFF → Step 3.5 스킵, 순수 TSX만

**적용 규칙:**
- CTA 카드의 핸들 → `brand_name` 값 사용 (하드코딩 금지)
- 카드 텍스트 톤 → `brand_voice`에 맞춰 작성
- 전문 용어 수준 → `target_audience`에 맞게 조절 (너무 쉽거나 어렵지 않게)

---

## Step 1: Read Project Data

```
projects/$PROJECT/carousel/copy_deck.md -- 카피 덱 (있으면 텍스트 소스로 우선 사용)
projects/$PROJECT/script.txt            -- 대본 원문 (copy_deck 없을 때 fallback)
projects/$PROJECT/carousel/             -- 카루셀 출력 디렉토리
projects/$PROJECT/carousel/card_*.tsx   -- 기존 TSX 파일 (있으면 참조)
projects/$PROJECT/carousel/card_*.png   -- 기존 PNG 파일 (있으면 재사용)
```

1. **`copy_deck.md` 존재 시** → 카드별 텍스트, 훅, 세컨드 전략, 감정 곡선, 테마 제안을 그대로 사용. Step 2-3 대부분 skip 가능 (copy_deck의 메타 정보 활용).
2. **`copy_deck.md` 없을 시** → 기존대로 `script.txt`에서 Art Direction + Card Plan 진행.
3. Check which `.tsx` or `.png` files already exist in `carousel/` (skip those)
4. Determine how many cards to create (typically 8-12, max 15)

---

## Step 2: Art Direction

> **`copy_deck.md` 있으면**: 테마 제안·카드 수·훅을 copy_deck에서 가져오고 아래는 skip.

### 2a. Content Type → Visual Strategy

| Type | Visual Strategy |
|------|----------------|
| Product/Service | icon-grid, numbered-list, bar-chart, CTA |
| Tutorial/How-to | numbered-list, split-top-bottom, diagram |
| Listicle | numbered-list, icon-grid, quote |
| Comparison | before-after, bar-chart, split-compare |
| Storytelling | quote, big-number, cover |

### 2b. Cover Hook + Theme

- 커버 제목 **10자 이내** 목표. 훅 공식: `remotion/docs/carousel-editorial-strategy.md` § 1
- Theme: `dark` (테크/AI) | `quiet-luxury` (브랜드/교육). 색상: `tsx-contract.md` § Theme System

### 2c. Output

```
Content type: [type] | Theme: [dark|quiet-luxury] | Cards: [N]
Cover hook: [제목] | Keyword: [떡밥 회수용]
```

---

## Step 3: Plan All Cards

### 3a. Card Table

`copy_deck.md`에 카드 테이블이 있으면 그대로 사용. 없으면 아래 형식으로 작성:

| # | Role | Layout | Emotion | Bridge → Next | Key Visual |
|---|------|--------|---------|---------------|------------|

공감→전환→증거→실천 흐름, 최소 2번 온도 변화. 상세: `carousel-editorial-strategy.md`

### 3b. Layout Options (23종)

**Base (A-I):** cover, icon-grid, numbered-list, split-top-bottom, quote, bar-chart, donut-chart, before-after, cta-ending

**Extended (J-W):** stat-dashboard, progress-tracker, ranking-list, code-snippet, terminal-output, feature-matrix, pros-cons, big-number, highlight-box, testimonial, timeline, split-image-text, accordion, chapter-divider

> 패턴 상세: `carousel-patterns-layouts.md` (A-I), `carousel-patterns-layouts-extended.md` (J-W)

### 3c. Pacing Rules

1. **Card 1 = Cover**, **Last card = CTA**
2. **같은 레이아웃 2연속 금지**
3. **최소 3가지 다른 레이아웃** 사용
4. Content density: ~2-4 key points per card (모바일 가독성)
5. Korean text: 개조식 (concise nominal phrases)
6. **Minimum density**: 카드당 3+ substantive items (제목 제외)
7. **같은 감정 온도 3장 연속 금지**
8. **인접 카드 Emotion Phase 동일 시 → Layout은 달라야 함**

### 3d. Visual Richness Rule

Every card MUST contain **at least one** of: SVG icon, chart, glass card, numbered badge, progress indicator.

### 3e. Quality Self-Review (MANDATORY)

- [ ] Card 1=cover, last=CTA, 8-12장, 최소 3종 레이아웃
- [ ] 같은 레이아웃 2연속/3회 초과 없음, 감정 온도 3연속 없음
- [ ] 카드당 SVG/chart/visual 1+, substantive items 3+
- [ ] Bridge 연결, 떡밥 회수, 제목 ≤15자, 숫자/데이터 활용

카드당 items 1-2개 → **병합 > 이미지 추가 > 확대**. 꽉 찬 7장 > 허전한 10장.

---

## Step 3.5: AI 배경 이미지 생성 (background.enabled=true일 때만)

`carousel.background.enabled: false`(기본값) → **스킵**, Step 4로 직행.
`true` → `copy_deck.md`의 `image_prompt` 파싱 → NanoBanana 배경 생성.

```bash
uv run python scripts/generate_carousel_backgrounds.py $PROJECT
```

결과: `projects/$PROJECT/carousel/backgrounds/bg_NNN.png`. Step 4 TSX에 반영.
-> 전체 절차 + CLI 옵션 + TSX 통합: `remotion/docs/carousel-ai-backgrounds.md`

---

## Step 4: Write TSX Files

**필수 읽기 (항상):**
```
Read remotion/docs/tsx-contract.md                       -- § Common Rules + § Carousel Contract
Read remotion/docs/carousel-patterns.md                  -- 인덱스 + boilerplate + 규칙 + Layout Pattern Index
```

**선택적 읽기 (Step 3 Card Table의 Layout에 따라):**
```
Read remotion/docs/carousel-patterns-layouts.md           -- Layout A-I 사용 시 (거의 항상)
Read remotion/docs/carousel-patterns-layouts-extended.md  -- Layout J-W 사용 시에만
Read remotion/docs/carousel-patterns-fills.md             -- 배경 장식/AI 이미지 사용 시
Read remotion/docs/carousel-patterns-ql.md               -- Theme = quiet-luxury일 때만
Read remotion/docs/carousel-patterns-icons.md             -- SVG 아이콘 필요 시
Read .claude/skills/remotion-visual-standards/SKILL.md   -- WCAG 대비 검수 시 (참조)
```

**로딩 순서**: 인덱스(`carousel-patterns.md`)의 Layout Pattern Index를 보고, Card Table에 사용된 패턴 ID가 포함된 파일만 선택적으로 로드.

Write each card as `projects/$PROJECT/carousel/card_NNN.tsx` (001, 002, ...).

### AI 배경 이미지 카드의 TSX (background.enabled=true이고 해당 카드에 배경 이미지가 있을 때)

`projects/$PROJECT/carousel/backgrounds/bg_NNN.png`가 존재하는 카드는 TSX에 `backgroundImage` prop 핸들링을 포함해야 한다. 렌더링 파이프라인이 자동으로 `backgroundImage` prop을 주입하므로, TSX에서는 **받아서 렌더링**하면 된다.

패턴은 `carousel-patterns-fills.md` § J-AI 참조. 핵심:
1. `import { AbsoluteFill, Img, staticFile } from "remotion";`
2. props에서 `backgroundImage` 디스트럭처링
3. `backgroundImage && (...)` 조건부 렌더링 (이미지 + 다크 그라디언트)
4. 나머지 콘텐츠는 위에 쌓임

배경 이미지가 **없는** 카드는 기존과 동일하게 순수 TSX로 작성 — `backgroundImage` 관련 코드 불필요.

### Batch Sizing & Agent Dispatch

| Cards | Strategy |
|-------|----------|
| 1-6 | Write all cards yourself (sequential) |
| 7-12 | 2 parallel agent batches |
| 13+ | 3 parallel agent batches |

> Agent dispatch 상세: `remotion/docs/tsx-contract.md` § Agent Dispatch Rules

---

## Step 5: Validate + Cleanup

### 5a. Automated Rule Validation

```bash
uv run python scripts/validate_carousel.py $PROJECT
```

- **CRITICAL** → 즉시 수정 후 재실행
- **WARNING만** → 필요시 수정
- 모든 CRITICAL 해소 후 5b로

### 5b. TypeScript Validation

```bash
cp projects/$PROJECT/carousel/card_001.tsx remotion/src/carousel/FreeformCard.tsx
cd remotion && npx tsc --noEmit
```

Spot-check 3-4 representative files (first, middle, last, most complex).

### 5c. Delete Stale PNGs

```bash
cd projects/$PROJECT/carousel && for f in card_*.tsx; do rm -f "${f%.tsx}.png"; done
```

---

## Step 6: Render to PNG

```bash
uv run python scripts/regenerate_carousel.py $PROJECT           # All
uv run python scripts/regenerate_carousel.py $PROJECT 1 3 5     # Specific
uv run python scripts/regenerate_carousel.py $PROJECT --force    # Force re-render
```

**CRITICAL:**
- NEVER run `npx remotion still` directly — the Python script handles props, paths, restoration
- NEVER use the pipeline just to render — use `regenerate_carousel.py`
- NEVER use slide scripts (`regenerate_slides.py`) — those are for video slides

---

## Step 7: 시각 리뷰 (품질 게이트)

렌더링 완료 후 자동 검증 → 카드별 시각 검수 → 수정 루프.
-> 검수 프로세스 + 리포트 템플릿: `remotion/docs/carousel-visual-review.md`

1. `uv run python scripts/validate_carousel.py $PROJECT` → CRITICAL 먼저 해소
2. 각 PNG Read로 열어 6항목 검사 (이미지/가독성/레이아웃/일관성/전달력/서사)
3. FAIL 카드 수정 → `regenerate_carousel.py $PROJECT <nums> --force` → 재검수
4. 모든 PASS → 최종 승인

---

ARGUMENTS: $ARGUMENTS
