# Shorts TSX Slides (9:16, 1080x1920)

Each paragraph/scene gets one .tsx file rendered to .mp4 at 1080x1920.

## Key Differences from Longform (16:9)

| 항목 | Longform (16:9) | Shorts (9:16) |
|------|----------------|---------------|
| 해상도 | 1920x1080 | 1080x1920 |
| TSX 콘텐츠 영역 | 1920x1080 전체 | 1080x1280 (상단 360px 훅존, 하단 280px 데드존) |
| 출력 위치 | projects/$PROJECT/slides/ | projects/$PROJECT/shorts_slides/slides/ |
| 래퍼 | 없음 | ShortsSlideWrapper (훅 타이틀 + 콘텐츠 + 워드 자막) |
| 훅 타이틀 | 없음 | 한 줄 훅 타이틀 (상단 360px) |
| 슬롯 파일 | FreeformSlot1-4.tsx | ShortsContentSlot1-4.tsx |
| SceneFade | 있음 | 없음 |
| 기본 Spring | GENTLE | SNAPPY |

## Step 1: Read Project Data

```
projects/$PROJECT/paragraphs/*.txt
projects/$PROJECT/audio/*.wav
prompts/channel_identity.txt         -- 채널 페르소나 규칙 (필수)
```

1. Read `prompts/channel_identity.txt` — **채널 호스트 = 샘호트만 (@ai.sam_hottman). "Sam Altman", "샘 올트만" 등으로 절대 바꾸지 않는다.** 대본 텍스트를 TSX에 옮길 때 고유명사를 "교정"하지 마라.
2. Read ALL paragraph files
2. Count total paragraphs (= total slides)
3. Check existing in shorts_slides/slides/ (skip those)

## Step 2: Slide + Hook Table

각 문단의 역할(훅? 설명? 비교? 마무리?)을 고려하여, 나레이션과 상보적인 시각 계획을 세운다.

| # | Content Summary | Layout | Key Visual | Entry+Exit | Spring | Intensity | Memory |

### Hook Title Rules (chapter-hook-titles.md 참조)
- docs/shorts/hook-patterns-70.md 읽고 패턴 응용
- line1에 메인 타이틀 전체 (1줄, whiteSpace: nowrap). line2는 빈 문자열
- 권장 10~13자, 최대 ~20자

### Entry+Exit (쇼츠 규칙)
- 입장: 0.4s 이내 완료 (12프레임 @30fps)
- 퇴장: cut (대부분), blurOut(fast) 또는 slideOutLeft (3초+ 드라마틱만)
- Chain Recall: 쇼츠의 기본 exit가 cut이므로 Seamless Handoff 자연 적용

> 고급 시각 어휘: `remotion/docs/slide-snippets-advanced.md`

### Layout Options (Shorts, 1080x1280)
세로 배치 우선. 2컬럼 maxWidth: 480. 텍스트: 제목 ≤56px, 본문 ≤36px. 하단 200px 자막 영역 비움.
title-hero, icon-stack, big-number, quote-glass, split-vertical, step-flow-vertical, bar-chart, diagram-flow, minimal-text, doc-mockup

### Memory Column (선택적, 최대 1-2회)
- `SAVE:id` | `RECALL:id:type` | `-`
- 상세: [chapter-animation-memory.md](chapter-animation-memory.md)

### Narrative Pacing (9개 핵심)

1. **Visual intensity curve**: 시작(high) → 중간(medium) → 끝(high)
2. **No 3+ consecutive same layout**
3. **Global frequency cap**: max 3 times
4. **Adjacent slides differ 2+ dimensions**
5. **Spring variety**: SNAPPY 기본, 훅→STIFF, 데이터→BOUNCY, 마무리→GENTLE
6. **Entry variety**: fadeSlideIn max 40%, wordStagger/charSplit/clipReveal 활용
7. **Exit**: cut-first (3초 미만은 exit 없음)
8. **Visual rhythm 2:1**
9. **가속된 점진적 공개**: title(0s) → visual(0.15s) → detail(0.3s)

### Visual Richness Rule
Every slide MUST have at least one SVG or structured visual.

### Anti-Patterns
Longform shared: quote-glass wall, naked minimal-text, bare bullet list, number island, empty title-hero, narration parrot, metaphor literalization, gradient-clip text
Shorts-only: fade soup, uniform timing, micro-slide overload (max 3 visuals for 2s slides)

### Animation Philosophy: "찰나의 순간"
1. STIFF/SNAPPY first. GENTLE은 마무리만
2. 입장: 0.4s 이내
3. 퇴장: cut 또는 0.3s
4. 카메라: 마이크로 움직임 (maxZoom 1.015, drift 3px)
5. fade 단축/제거

### Content Fidelity Rules
Same as longform: no hallucination, exact mapping, attribution check, simplify when uncertain, no empty slots.

## Step 3: Write TSX + Hook Titles JSON

### Reference Files (Shorts ALWAYS)
```
remotion/docs/tsx-contract.md (§ Common + § Shorts Contract)
remotion/docs/design-philosophy.md
remotion/docs/slide-patterns.md + slide-patterns-motion.md
remotion/docs/slide-icons.md
remotion/docs/slide-layouts.md + slide-layouts-extras.md (Shorts-Safe 필수)
.claude/skills/remotion-visual-standards/SKILL.md (§ 7 Shorts/Reels)
```

### TSX Contract (핵심 요약)
- Export: `export const Freeform`, Props: `FreeformProps`
- NO AnimatedBackground / ProgressBar / SceneFade (Wrapper가 처리)
- Content zone 1080x1280, bottom 200px reserved, backgroundColor "transparent"
- Font limits: 제목 ≤56px, 본문 ≤36px, 2-column maxWidth 480

### Hook Titles JSON
Write to projects/$PROJECT/shorts_slides/slides/hook_titles.json:
```json
[{"index": 1, "line1": "...", "line2": "", "subDetail": "..."}, ...]
```

### Animation Memory Update (해당 시)
SAVE 슬라이드 작성 후 key element 좌표를 `animation-memory.json`에 기록.

### Quality Checklist (15개)

#### 레이아웃 (3개)
- [ ] No 3+ consecutive same layout
- [ ] No layout > 3 times total
- [ ] Every slide has SVG/visual

#### 애니메이션 (5개)
- [ ] Motion variety (fadeSlideIn ≤ 40%)
- [ ] Exit: cut-first 원칙
- [ ] Entry 3종+ used
- [ ] Spring 3종+ used
- [ ] Adjacent slides different spring

#### 콘텐츠 (4개)
- [ ] Content fidelity (지어낸 이름/수치 없음)
- [ ] 음소거 test 통과
- [ ] 한글 라벨 필수
- [ ] Hook title line1 10~20자, line2 빈 문자열

#### 기술 (3개)
- [ ] Visual rhythm 2:1
- [ ] Entry 0.4s 이내
- [ ] inputRange strictly increasing
