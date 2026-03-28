# Art Direction (공통 아트 디렉션)

슬라이드 계획 전, 프로젝트 전체의 시각 전략을 먼저 수립한다.
이 챕터는 Longform / Shorts / CC Shorts 공통 + 포맷별 확장을 포함.

---

## Design Philosophy (핵심 원칙)

> "AI가 만든 티"를 없애는 핵심은 전문가의 디자인 판단을 규칙으로 번역하는 것이다.
> Full reference: `remotion/docs/design-philosophy.md`

### 상보성 (Complementary, Not Redundant)
화면은 나레이션의 자막이 아니다. 나레이터가 말로 설명하기 어려운 것을 **대신 보여주는 것**이다.
- 나레이션이 "왜" → 화면은 "무엇/얼마나"
- 나레이션이 감정·비유 → 화면은 비유가 가리키는 **실체** (데이터, 구조, 예시)

### 점진적 공개 (Progressive Disclosure)
정보를 한 번에 보여주지 않고 **단계별로 드러내라**.
- 제목(0s) → 비주얼(+0.3s) → 상세(+0.6s) — 최소 3단계 시차
- 모든 요소가 동시에 fadeIn = "AI 슬라이드"의 가장 흔한 특징
- `getAnimationZone()` + `staggerDelays()` 사용, 하드코딩 프레임 금지

### 비례 = 중요도 (Proportion Rule)
가장 큰 시각 공간 = 가장 중요한 정보. 한 슬라이드에 강조점은 **1개**.

### 데이터-잉크 비율 (Data-Ink Ratio)
모든 시각 요소는 정보를 전달해야 한다. 장식적 SVG, 의미 없는 글로우 → 제거.

### 여백 = 임팩트 (Whitespace)
빈 공간은 의도적 도구. 화면의 **30%+**는 비워둘 것. 넘치면 다음 슬라이드로.

### 색상 의미론 (Color Semantics)
ACCENT(보라)=핵심 | TEAL(청록)=긍정/해결 | ACCENT_BRIGHT=데이터 | MUTED=보조.
한 슬라이드에서 강조 색상은 **최대 2개**.

### 의도적 불완전함 (Anti-Polish)
과도하게 매끄러운 모션은 "AI/광고" 느낌을 준다.
- 모든 요소가 완벽한 대칭·정렬일 필요 없음 — **약간의 비대칭이 편집감**을 줌
- spring config를 다양하게: BOUNCY(역동), GENTLE(차분), STIFF(정보 전달), SNAPPY(기본)
- 같은 spring으로 모든 요소를 움직이면 기계적으로 보임
- 인접 슬라이드에서 다른 spring, 슬라이드 내에서도 최소 2종

### 앵무새 규칙 (Parrot Rule)
- **금지**: 나레이션의 비유/수사("함정", "무기", "숨겨진")를 대형 텍스트로 표시
- **허용**: 사실적 키워드(개념명, 단계명, 도구명)는 라벨/노드에 OK
- **필수**: 모든 아이콘/노드/카드에 한글 라벨
- **과잉 경고**: 텍스트를 빼고 아이콘만 남기면 정보 전달 불가. "나레이션과 다른 계층의 정보를 보여줘라"

---

## Longform 전용 확장

### Content Type Classification

대본 전체를 읽고 콘텐츠 유형을 분류:

| Type | Indicators | Visual Strategy |
|------|-----------|----------------|
| **Tutorial/Guide** | 단계별 설명, "방법", "설정" | step-indicator, cycle-flow, diagram-flow, 프로그레스 |
| **Comparison/Analysis** | "vs", 비교, 장단점 | bar-chart, split-compare, branch-flow, 데이터 시각화 |
| **Persuasion/Opinion** | 주장, 근거, 결론 | quote-glass, big-number, 감정적 강조 |
| **Storytelling/Narrative** | 시간순, 사건, 변화 | timeline, title-hero, 극적 전환 |
| **Technical/Explanation** | 개념, 구조, 원리 | cycle-flow, branch-flow, diagram-flow, doc-mockup |

### Recurring Motifs (2-3개)

프로젝트 응집력을 위해 반복할 시각 모티프 2-3개 선정:
- Section badges (numbered: 01, 02, 03...)
- Specific icon style (e.g., code brackets for tech, people for social)
- Recurring color emphasis (TEAL for positive, ACCENT for key concepts)
- Glass cards for quoted/emphasized content
- Bar charts / progress bars for quantitative slides

### Visual Anchor

영상마다 **하나의 고유 시각 요소**가 여러 슬라이드에 반복 등장하여 응집력을 만든다:

| 주제 유형 | 추천 비주얼 앵커 |
|-----------|----------------|
| **Tech/AI** | code bracket 모티프, terminal frame accent, node diagram 스타일 |
| **Business/수익** | metric card 테두리, trend line accent, dashboard grid |
| **Education/Guide** | step indicator + progress dots, numbered section badge |
| **비교/분석** | VS divider 스타일, split-screen 구도 반복 |
| **Creative/Story** | chapter badge, timeline connector, 극적 여백 |

이 앵커는 30%+ 슬라이드에 미묘한 반복 요소로 등장.

### Visual Progression (시각적 흐름 변화)

영상 전체가 시각적으로 단조롭지 않게 하라. 같은 accent color, borderRadius, glow가 처음부터 끝까지 동일하면 시청자는 "다 비슷해 보인다"고 느낀다.

변화를 만드는 방법은 자유롭다:
- 색상 온도 전환 (cool 보라 → warm 코랄 → cool 복귀)
- borderRadius 변화 (둥근 카드 → 날카로운 카드 → 부드러운 복귀)
- glow/shadow 전환 (빛나는 → 절제된 → 미묘한 복귀)
- 레이아웃 밀도 변화 (넓은 여백 → 밀도 높은 다이어그램 → 여백 복귀)

대본의 서사 흐름과 감정 변화에 맞게 시각 스타일을 자연스럽게 전환하는 것이 목표. 정해진 공식 없음.

> Card style palette: `.claude/skills/remotion-visual-standards/SKILL.md` § 4

### Elevation Push (창의적 격상)

모든 슬라이드에 자문하라: **"이 내용을 단순 카드+텍스트로 표현할 수 있는가?"**
YES라면, **한 단계 더 풍부한 방식**으로 표현하라.

- 단순 텍스트 → SVG 아이콘 + 구조화된 레이아웃
- 단순 아이콘 → 애니메이션 다이어그램 또는 UI 목업
- 단순 비교 → 시각적 대비가 명확한 split-compare
- 단순 숫자 → 카운트업 + 맥락 바차트

Freeform TSX의 힘은 무한한 시각 표현력이다. 그 자유를 활용하라.

#### Visual Vocabulary Expansion

시각적 단조로움을 피하기 위해, `remotion/docs/slide-snippets-advanced.md`의 스니펫에서 영감을 얻어라.
스니펫 라이브러리에서 자유롭게 기법을 조합하되, 사용 시기에 대한 규칙은 없다 — 내용이 결정한다.

### Animation Memory Candidates (선택적)

대본에서 시각적 연속성 기회를 탐색. 하나도 없으면 "해당 없음"으로 넘어간다:
1. 동일 개념이 3+ 슬라이드 간격으로 재등장?
2. 명시적 콜백 표현("앞서 살펴본", "다시 돌아가서")?
3. 점진적 구축 패턴(단계 1→2→3)?
4. 대비 쌍(문제→해결)?
5. 반복 엔티티(고유명사 3회+)?

기회 발견 시 → [chapter-animation-memory.md](chapter-animation-memory.md).

### Subject-Relevant Design Language

주제가 디자인을 결정한다. 모든 영상에 동일한 dark-glow를 적용하면 "AI 느낌".

- **AI/Tech** → monospace accent, terminal frame, circuit 연결선
- **Business/수익** → 대시보드 레이아웃, KPI 카드, 트렌드 라인
- **비교/분석** → 분할 구도, 색상 대비, 바 차트
- **Tutorial** → step badge, checklist UI, progress indicator
- **스토리/변화** → 타임라인, 전환점 마커, 드라마틱 여백

### Output (Internal Note)

```
Content type: [type]
Visual anchor: [recurring element]
Subject design language: [visual vocabulary]
Recurring motifs: [motif1], [motif2]
Color emphasis: [TEAL vs ACCENT usage]
Animation memory candidates: [list, or "해당 없음"]
Visual progression: [자유 형식 — 영상 흐름에 따른 시각 변화 계획]
```

---

## Shorts 전용 확장

### Shorts Tempo Classification

| Tempo | 슬라이드 수 | 기본 Spring | 특징 |
|-------|-----------|-----------|------|
| **Rapid-fire** | 15+ | STIFF→SNAPPY | 빠른 정보 전달 |
| **Standard** | 10-14 | SNAPPY 기본 | 균형잡힌 페이스 |
| **Breathing** | 6-9 | SNAPPY→GENTLE | 여유 |

### Content Type Classification (Shorts)

| Type | Indicators | Visual Strategy |
|------|-----------|----------------|
| **Tutorial** | 단계별 설명 | step-flow-vertical, doc-mockup |
| **Comparison** | "vs", 비교 | bar-chart, split-vertical |
| **Persuasion** | 주장, 근거 | quote-glass, big-number |
| **Technical** | 개념, 구조 | diagram-flow, icon-stack |

### Recurring Motifs (Shorts)

1080x1280 기준으로 2-3개 선정.

### Output (Internal Note)

```
Content type: [type]
Tempo: [rapid-fire/standard/breathing]
Visual anchor: [element]
Recurring motifs: [motif1], [motif2]
Animation memory candidates: [list or "해당 없음"]
Visual progression: [자유 형식]
```

---

## CC Shorts 전용 확장

### CC Art Direction

- **Content Format**: translator / flow / situation (대본 구조에서 자동 감지)
- **Recurring Motifs**: 포맷별 2-3개 (e.g., translator → 번역 카드, flow → 노드 연결선)
- **Accent Color**: `#A2FFEB` (mint) 또는 `#3CB4B4` (teal)
- **Visual Anchor**: 에피소드 전체 시각 요소 (e.g., 커맨드 배지, 터미널 프레임)

---

## Channel Persona

슬라이드 생성 전, 반드시 `prompts/channel_identity.txt`를 읽을 것.
핵심 규칙: 채널 호스트는 **샘호트만** (@ai.sam_hottman). Sam Altman (OpenAI CEO)과 절대 혼동 금지.
