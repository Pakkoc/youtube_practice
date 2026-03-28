# Batch Dispatch (에이전트 배치 디스패치)

## Batch Sizing

| 슬라이드 수 | 배치 수 | 전략 |
|------------|--------|------|
| 1-6 | 1 (순차) | 직접 작성, 에이전트 불필요 |
| 7-12 | 2 | 2개 균등 분배 |
| 13-18 | 3 | 3개 균등 분배 |
| 19+ | 4 | 4개 균등 분배 |

## Agent Dispatch

각 배치마다 Task agent (subagent_type=`general-purpose`)를 launch.

### 에이전트에 전달할 정보

1. **Full slide table** — 전체 테이블 (이 에이전트 담당 표시)
2. **Assigned slide numbers** — 명시적 목록
3. **Art Direction summary** — content type, visual anchor, motifs, color strategy, visual progression plan
4. **디자인 철학 핵심** — 상보성, 점진적 공개, 비례=중요도, 여백, Anti-Polish, Elevation Push
5. **Reference files to read** (에이전트가 직접 읽을 경로):
   - TSX용: `remotion/docs/tsx-contract.md`, `remotion/docs/design-philosophy.md`, `remotion/docs/slide-patterns.md`, `remotion/docs/slide-icons.md`, `remotion/docs/slide-examples.md`, `.claude/skills/remotion-visual-standards/SKILL.md` + 필요한 layout sub-file
   - Manim용: `prompts/manim_scene_generation.txt`, `remotion/docs/design-philosophy.md`, `.claude/skills/manim-slides/chapter-animation-patterns.md`, `.claude/skills/manim-slides/chapter-design-system.md`
   - Shorts 추가: `remotion/docs/slide-layouts-extras.md` (Shorts-Safe 필수)
   - Agent rules: `remotion/docs/agent-rules.md`
6. **Output paths** — `projects/$PROJECT/slides/NNN.tsx` or `NNN.py`
7. **Animation Memory** (해당 시):
   - 파일: `projects/$PROJECT/animation-memory.json`
   - 담당 SAVE 슬라이드: [번호 + entry_id]
   - 담당 RECALL 슬라이드: [번호 + entry_id + recall_type]

### Shorts 에이전트 추가 정보

- Shorts Tempo (rapid-fire/standard/breathing)
- "찰나의 순간" 애니메이션 철학:
  - 기본 spring: SNAPPY (GENTLE 아님)
  - 입장 0.4s 이내, 퇴장 대부분 hard cut
  - Camera 축소: maxZoom 1.015, drift 3px
  - ShortsSlideWrapper에 SceneFade 없음 — fade 최소화
- Reference: `remotion/docs/tsx-contract.md` (Shorts Contract 섹션)

### CC Shorts 에이전트 추가 정보

- Content format (translator/flow/situation)
- CC 참조: `cc-content/docs/cc-shorts-patterns.md`
- Rendering-critical 금지 목록:
  - backdropFilter 절대 금지
  - COLORS.CODE_BORDER, COLORS.PRE_BG 등 미정의 상수 금지
  - 허용 COLORS: BG, TEXT, ACCENT, ACCENT_BRIGHT, MUTED, TEAL, CODE_BG
  - 터미널 배경: "#141618", 테두리: "rgba(255,255,255,0.08)"

## Animation Memory 배치 규칙

1. 메인 세션이 `animation-memory.json` 생성 (recall_links 포함, entries 비움)
2. SAVE-RECALL 쌍 → 가능하면 같은 배치에 배정
3. 크로스 배치 불가피 시 → SAVE 배치를 먼저 완료 후 RECALL 배치 실행
4. Fallback: RECALL 에이전트가 entry 못 찾으면 recall_links의 transformation 참고

## Parallelism

Launch all batch agents in a SINGLE message using multiple Task tool calls — this enables true parallelism.

## Post-Agent Merge

After ALL agents complete:
1. Count total .tsx + .py files — must match total slide count
2. Fix any missing slides immediately
3. Spot-check 2-3 slides for visual consistency with art direction
