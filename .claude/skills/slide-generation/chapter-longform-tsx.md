# Longform TSX Slides (16:9, 1920x1080)

## Step 1: Read Project Data

```
projects/$PROJECT/paragraphs/*.txt   -- 대본 문단 (001.txt ~ NNN.txt)
projects/$PROJECT/audio/*.wav        -- TTS 오디오 (duration 참고용)
projects/$PROJECT/broll/generated/   -- B-roll 배경 이미지 (있으면 참조)
prompts/channel_identity.txt         -- 채널 페르소나 규칙 (필수)
```

1. Read `prompts/channel_identity.txt` — **채널 호스트 = 샘호트만 (@ai.sam_hottman). "Sam Altman", "샘 올트만" 등으로 절대 바꾸지 않는다.** 대본 텍스트를 TSX에 옮길 때 고유명사를 "교정"하지 마라.
2. Read ALL paragraph files
3. Count total paragraphs (= total slides)
4. Check existing .tsx/.py/.mp4 in slides/ (skip those)

## Step 2: Slide Table

각 문단을 읽을 때, 나레이션이 무엇을 하는지 생각하라 — 설명? 비유? 전환? 비교?
그 답이 화면에 무엇이 나올지를 결정한다. 나레이션과 같은 계층의 정보를 반복하지 마라
(→ Art Direction § 상보성, 앵무새 규칙).

| # | Content Summary | Mode | Layout / Visual Plan | Key Visual Element | Entry+Exit | Intensity | Memory |

### Mode Selection (Manim-First)

Manim (animation IS information): math formulas, coordinate graphs, algorithm visualization, step-by-step transforms, data comparison.

TSX Freeform (spatial layout IS information): 3+ groups simultaneously, UI mockups, SVG icon grids, text-dense with icons.

Decision rule: "움직이는 것 자체가 정보 → Manim. 공간 배치 자체가 정보 → TSX."

Pacing rule: No more than 5 consecutive slides with same Mode.

### Entry+Exit Options

자유롭게 조합하라. 다양성이 핵심:
- wordStagger+blurOut, circleReveal+clipCircleOut, insetReveal+fadeSlideOut
- diagonalWipe+slideOutLeft, fadeSlideIn+scaleOut, charSplit+blurOut
- 또는 다른 조합 — 모티프 라이브러리에서 자유 선택

Chain Recall exit 규칙: SAVE→RECALL 체인에서 persistent 요소 끊김 방지를 위해 exit = `cut`.
상세: [chapter-animation-memory.md](chapter-animation-memory.md) § Seamless Handoff.

> 모션 레퍼런스: `remotion/docs/slide-patterns-motion.md`
> 고급 시각 어휘: `remotion/docs/slide-snippets-advanced.md`

### Layout Options (22+)

**기본**: title-hero, bullet-list, big-number, quote-glass, split-compare, step-indicator, icon-grid, minimal-text, bar-chart, timeline, doc-mockup

**순서/인과**: numbered-cards, vertical-descent, staircase-progress, annotated-hub, step-flow, diagram-flow

**구조/관계**: cycle-flow, branch-flow, funnel, radial-hub

수평 화살표 계열(diagram-flow, step-flow)은 영상 전체 2회 이하를 권장한다 — 대안으로 numbered-cards, vertical-descent, staircase-progress, annotated-hub 등 다양한 패턴 활용.

### Memory Column (선택적 — chapter-animation-memory.md)
- `SAVE:id` — 핵심 비주얼을 animation-memory.json에 기록
- `RECALL:id:type` — 이전 비주얼을 회상하여 변형 (expand/transform/compare/echo/simplify)
- `-` — 메모리 상호작용 없음

Slide Table에 SAVE/RECALL이 있으면 → `projects/$PROJECT/animation-memory.json` 생성.

### Narrative Pacing (9개 핵심)

1. **Visual intensity curve**: 도입(high) → 본론(medium) → 클라이맥스(high) → 마무리(low)
2. **No 3+ consecutive same layout**
3. **Global frequency cap**: max 3 times per layout type
4. **Adjacent slides differ 2+ dimensions** (layout, color, density, direction 중)
5. **Spring variety**: 인접 슬라이드에서 같은 spring 사용하지 않기
6. **Visual rhythm 2:1**: dense 2장 → breathing 1장 교대
7. **Progressive disclosure**: title(0s) → visual(+0.3s) → detail(+0.6s) — 최소 3단계
8. **Motion variety**: entry, exit, camera, ambient를 다양하게 (fadeSlideIn 일변도 금지)
9. **Arrow-flow limit**: 수평 화살표 패턴 영상 전체 최대 2회

### Visual Richness Rule

Every slide MUST contain at least one SVG or structured visual.
NOT sufficient alone: glass card with only text, single badge, gradient text only.

### Anti-Patterns (9개)

1. **quote-glass wall** — 연속 인용 유리 카드
2. **naked minimal-text** — 시각 요소 없는 미니멀 텍스트
3. **bare bullet list** — 아이콘/시각 없는 불릿 리스트
4. **number island** — 맥락 없는 숫자만 덩그러니
5. **empty title-hero** — 제목만 있고 비주얼 없음
6. **narration parrot** — 나레이션을 그대로 텍스트로 반복
7. **metaphor literalization** — 비유를 글자 그대로 시각화 ("함정" → 구덩이 그림)
8. **gradient-clip text** — `WebkitBackgroundClip: "text"` (Remotion 렌더링 시 깨짐)
9. **arrow-flow wall** — 수평 박스+화살표가 영상에서 2회 초과

### Content Fidelity Rules

1. **No hallucination** — 대본에 없는 사실/수치 추가 금지
2. **Exact mapping** — 대본 내용과 슬라이드 1:1 대응
3. **Attribution check** — 인용/출처가 대본에 있으면 슬라이드에도 표시
4. **When in doubt, simplify** — 불확실하면 단순하게
5. **No empty visual slots** — 모든 시각 슬롯에 실제 콘텐츠 배치

## Step 3: Write Slide Files

### Reference Files

**필수 (항상 읽기):**
```
remotion/docs/tsx-contract.md                          -- § Slides Contract
remotion/docs/slide-patterns.md                        -- 핵심 규칙 + anti-patterns
remotion/docs/slide-layouts.md                         -- 인덱스 → 필요한 sub-file만
```

**선택적 (슬라이드 내용에 따라):**
```
remotion/docs/slide-patterns-motion.md                 -- 고급 애니메이션
remotion/docs/slide-icons.md                           -- SVG 아이콘
remotion/docs/slide-examples/[패턴명].md               -- 특정 패턴 풀 예시
remotion/docs/typography-patterns.md                   -- 텍스트 중심
remotion/docs/design-philosophy.md                     -- 디자인 원칙 상세
.claude/skills/remotion-visual-standards/SKILL.md      -- 시각 품질 + 카드 스타일 palette
```

**Manim (mode=manim일 때만):**
```
.claude/skills/manim-slides/chapter-animation-patterns.md
.claude/skills/manim-slides/chapter-design-system.md
```

### TSX Component Contract

> Full reference: remotion/docs/tsx-contract.md

- Export: `export const Freeform`, Props: `FreeformProps`
- AnimatedBackground first child, ProgressBar + SceneFade last
- No CSS transitions, no backdropFilter, no Math.random()
- Multi-column maxWidth: 700, subtitle reserve 360px, center everything
- Korean: 개조식 (명사형 종결), wordBreak: 'keep-all'

Write each slide as `projects/$PROJECT/slides/NNN.tsx` (TSX) or `NNN.py` (Manim).

### Animation Memory Update (해당 시)
SAVE 슬라이드 작성 후 key element 좌표를 `animation-memory.json`에 기록.
상세: [chapter-animation-memory.md](chapter-animation-memory.md).

## Step 4: Render to MP4

```bash
uv run python scripts/regenerate_slides.py $PROJECT
# Custom parallel: --parallel 2
# Specific slides: $PROJECT 013 020
# Force: --force
```

NEVER run `npx remotion render` directly. NEVER use full pipeline just for slides.
