# Agent Rules for Slide Generation

> 에이전트 프롬프트에 포함할 규칙. `/generate-slides` Step 4b에서 참조.

## Core Rules

- Follow the slide table EXACTLY. Do NOT re-plan, substitute layouts, or change visual elements
- Read each paragraph file (`projects/$PROJECT/paragraphs/NNN.txt`) for the actual text content
- **TSX slides**: Write `.tsx` files to `projects/$PROJECT/slides/NNN.tsx`
- **Manim slides**: Write `.py` files to `projects/$PROJECT/slides/NNN.py`. Read `prompts/manim_scene_generation.txt` for full reference. Verify structure (ManimSlide class, construct method, DURATION_PLACEHOLDER) and security (no os/subprocess/eval/exec imports)
- Every TSX slide must contain at least one SVG or structured visual (see Visual Richness Rule)
- No cross-file imports between slide files — each slide is self-contained

## Validation

- **TSX validation**: After writing, spot-check 3-4 representative files by copying to `remotion/src/slides/Freeform.tsx` and running `cd remotion && npx tsc --noEmit`. Do NOT run `--validate` (runtime errors are caught during MP4 render)
- **Manim validation**: Run `python -c "import ast; ast.parse(open('NNN.py', encoding='utf-8').read())"` for syntax check

## Content & Style

- **Content fidelity**: All text on slides must come directly from the paragraph file. NEVER invent names, quotes, numbers, or platform actions not present in the source text.
- **Shorts-safe widths** (TSX only): Multi-column layouts must use `maxWidth: 700` (not flex:1 or width:100%). All chart/grid containers must be center-aligned.
- **SVG icons** (TSX only): Copy from `slide-icons.md` Icon Library. If an icon isn't in the library, use feather icon conventions (viewBox 0-24, stroke-based). When using strokeDasharray for animation, the value MUST equal the actual SVG path perimeter.
- **No empty visual slots**: Every icon slot in diagrams/grids must be filled. Never use `icon: null` or leave a node/card visually empty.
- **Continuous connector lines** (TSX only): For timelines/flow diagrams, use a single `position: absolute` line instead of per-row individual lines. This prevents misalignment from varying dot sizes or row heights.
- **Text animation** (TSX only): `scaleIn`, `bounceIn`, `zoomPop`은 텍스트 컨테이너에 사용 금지. 텍스트에는 `fadeSlideIn` 또는 `cascadeUp`만 사용. scale 계열은 아이콘/배지/SVG 전용.

## Sizing & Centering (STRICT)

`tsx-contract.md` § Sizing & Centering Rules 참조. 핵심:
- 다이어그램 노드 최소 240x80px, font-size 32px+
- 수직 중심 `cY = 500` (420이나 430 금지)
- 수평 캔버스 70-80% 활용 (좌우 여백 150-250px)
- 화살표 strokeWidth 3px+, 화살촉 16px+
- cycle-flow: `hSpan ≥ 260`, `vSpan ≥ 140`
- 배지/태그 최소 120x48px, font-size 26px+

## Arrow & interpolate

**Arrow tip inputRange (STRICT)**: `svgStrokeDraw` + `interpolate`로 화살촉 opacity 계산 시 **inputRange는 반드시 오름차순**. `[len*0.15, 0]`은 런타임 크래시 → 반드시 `[0, len*0.15]`로 쓰고 outputRange를 뒤집을 것 (`[1, 0]`).

```tsx
// GOOD
const tipOp = interpolate(offset, [0, len * 0.15], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
// BAD — crashes
const tipOp = interpolate(offset, [len * 0.15, 0], [0, 1], ...);
```

## Centering Self-Check (TSX 완성 전 필수)

TSX 작성 완료 후, 아래 레이아웃을 사용했다면 반드시 값을 검증:
- **Vertical Descent**: `startY`가 `(1080 - totalH) / 2` 기반인가? (720 사용 = 즉시 수정). `dotX`가 660-740 범위인가?
- **Balance Scale**: `pivotY`가 420-460인가? 팬 하단과 annotation 사이 ≥ 60px 간격?
- **Hub-Satellite (가장 빈번한 위반 — 반드시 확인)**:
  - `hubY`는 **490-520** 범위 필수. 420-440은 타이틀 겹침 유발 → 금지.
  - 위성 중 angle이 180~360 범위이면 위로 올라감. **특히 angle=270은 최상단**으로 가므로 `hubY - orbitR ≥ 200` 필수.
  - 산술 검증: 모든 위성에 대해 `sy = hubY + sin(angle) * orbitR` 계산 후 `sy - nH/2 ≥ 180` (타이틀 클리어런스) 확인.
  - 위반 시 증상: 타이틀 텍스트와 위성 노드가 겹쳐 글자를 읽을 수 없음.

## Language

슬라이드에 표시되는 모든 텍스트는 한글로 작성. 영문 라벨("Status Unknown", "Verified" 등) 금지. 대본이 영어 용어를 포함하더라도 화면 표시용 텍스트는 한글 번역 사용.
