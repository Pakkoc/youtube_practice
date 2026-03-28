---
name: slide-generation
description: "Remotion Freeform TSX 슬라이드 생성 워크플로 — longform 16:9, shorts 9:16, CC shorts. Art direction, batch dispatch, TSX 작성, 검증까지 포함. /generate-video, /generate-shorts가 내부적으로 이 skill을 로드."
user-invocable: false
---

# Slide Generation Workflow

TSX 슬라이드 파일(.tsx)을 생성하는 워크플로 skill. 렌더링/TTS/파이프라인 실행은 포함하지 않음.
커맨드(`/generate-video`, `/generate-shorts`)가 이 skill의 chapter를 로드하여 실행.

## Decision Flowchart

| 조건 | 로드할 Chapter | 핵심 차이 |
|------|---------------|----------|
| 16:9 longform 영상 | [chapter-longform-tsx.md](chapter-longform-tsx.md) | SceneFade, AnimatedBackground, Manim 선택지, 1920x1080 |
| 9:16 shorts (일반, non-CC) | [chapter-shorts-tsx.md](chapter-shorts-tsx.md) | ShortsContentSlot, SNAPPY 기본, 1080x1280 콘텐츠 |
| 9:16 CC shorts (`cc-*` 프로젝트) | [chapter-cc-shorts.md](chapter-cc-shorts.md) | 1080x1080 정사각형 중앙, CC 패턴 3종, AnimatedBackground 금지 |

## 모든 포맷 공통 참조 (ALWAYS)

```
remotion/docs/tsx-contract.md              -- § Common Rules + § Slides/Shorts Contract + § Available Imports + § Design System
remotion/docs/slide-patterns.md            -- 모션 패턴, 공유 헬퍼
remotion/docs/slide-patterns-motion.md     -- Exit, Camera, Ambient, Spring Decision Guide
remotion/docs/slide-icons.md               -- SVG 아이콘 라이브러리
remotion/docs/slide-layouts.md             -- 레이아웃 인덱스: 4개 서브파일 라우팅
remotion/docs/slide-examples.md            -- 콘텐츠 타입별 few-shot TSX 예제
remotion/docs/slide-snippets-advanced.md   -- 고급 시각 어휘: 애니메이션, 도형, 구도, 데이터 시각화, 전환 스니펫
.claude/skills/remotion-visual-standards/SKILL.md -- WCAG 대비, spring presets, 카드 스타일, 한국어 타이포
```

추가 레이아웃 서브파일 (필요한 것만 선택적 로드):
```
remotion/docs/slide-layouts-diagrams.md    -- 차트, 타임라인, 스텝
remotion/docs/slide-layouts-mockups.md     -- 앱 UI, 채팅, 서비스 화면
remotion/docs/slide-layouts-metaphors.md   -- 피플 픽토그램, 저울, 화살표 흐름
remotion/docs/slide-layouts-extras.md      -- 프로그레스 바, SVG 드로우, 쇼츠 안전 변형
```

## Chapters

| # | Chapter | 용도 |
|---|---------|------|
| 1 | [Art Direction](chapter-art-direction.md) | 공통 아트 디렉션 프로세스 (콘텐츠 분석, 템포, 시각 전략) |
| 2 | [Longform TSX (16:9)](chapter-longform-tsx.md) | 1920x1080 슬라이드 워크플로 (Mode 선택, 레이아웃, 페이싱) |
| 3 | [Shorts TSX (9:16)](chapter-shorts-tsx.md) | 1080x1920 쇼츠 슬라이드 (템포 분류, ShortsContentSlot) |
| 4 | [CC Shorts](chapter-cc-shorts.md) | CC 전용 패턴 (번역기/구조도/상황카드, 정사각형 제약) |
| 5 | [Hook Titles](chapter-hook-titles.md) | 훅 타이틀 생성 규칙 (line1, subDetail, 70패턴) |
| 6 | [Batch Dispatch](chapter-batch-dispatch.md) | 에이전트 배치 사이징 + 병렬 디스패치 지침 |
| 7 | [TSX Validation](chapter-tsx-checklist.md) | TSX 검증 + stale 파일 정리 + 자가 검증 체크리스트 |
| 8 | [Animation Memory](chapter-animation-memory.md) | 시각 연속성 시스템 (SAVE/RECALL, 자동 감지, recall_type 5종) |

## 자연어 트리거

이 skill은 사용자가 다음과 같이 요청할 때 자동 로드:
- "슬라이드만 다시 만들어줘" → 포맷별 chapter 로드
- "TSX 수정해줘", "특정 슬라이드 수정" → 포맷별 chapter 로드
- "아트 디렉션 변경" → chapter-art-direction.md
- "훅 타이틀 수정" → chapter-hook-titles.md

**포맷 자동 감지**:
- 프로젝트에 `shorts_slides/` 디렉토리가 있으면 → shorts chapter
- 프로젝트명이 `cc-*` 패턴이면 → CC chapter
- 그 외 → longform chapter
