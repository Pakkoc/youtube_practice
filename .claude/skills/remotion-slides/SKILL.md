---
name: remotion-slides
description: "Reference manual for Remotion slide generation — Freeform TSX 작성법, 11개 레이아웃 패턴 참고, props 자동 주입, 병렬 렌더링. Load when working with features/generate_slides/, remotion/src/slides/, or debugging slide rendering."
user-invocable: false
---

# Remotion Slides Manual

## Activation Conditions
- **Keywords**: remotion, slide, 슬라이드, freeform, TSX, 레이아웃, 패턴
- **Intent Patterns**: "슬라이드 수정", "TSX 작성", "Remotion 렌더링", "레이아웃 변경"
- **Working Files**: `features/generate_slides/`, `remotion/src/slides/`, `remotion/src/design/`
- **Content Patterns**: `RemotionSlideBackend`, `FreeformSlotPool`, `generate_remotion_slide_props`

## 핵심 원칙

모든 슬라이드는 **Freeform TSX**로 생성합니다. Claude Code가 대본 맥락을 이해하고 직접 TSX를 작성합니다.
수학/알고리즘 시각화에는 Manim CE 모드 선택 가능.

## Relationship to Other Docs

| 문서 | 역할 | 읽을 타이밍 |
|------|------|------------|
| `/generate-slides` command | 실행 워크플로 (아트 디렉션 → 계획 → TSX 작성 → 검증 → 렌더링) | 슬라이드 생성 실행 시 |
| `/generate-video` command | E2E 워크플로 (대본 → 슬라이드 → 파이프라인) | 영상 전체 생성 시 |
| `remotion-visual-standards` skill | 시각 품질 기준 (WCAG 대비, 카드 스타일, spring, 한국어 타이포) | TSX 작성/리뷰 시 |
| `manim-slides` skill | Manim CE 패턴 라이브러리 (5 패턴, 디자인 시스템, 안티패턴) | Manim 슬라이드 작성 시 |
| `remotion/docs/tsx-contract.md` | TSX 작성 규약 (보일러플레이트, 사이징, 센터링, 임포트) | TSX 코드 작성 시 |
| `remotion/docs/slide-patterns.md` | 레이아웃 패턴 인덱스 + 모션 패턴 | TSX 구조 설계 시 |
| `remotion/docs/design-philosophy.md` | 인포그래픽 8원칙 (상보성, 점진적 공개, 데이터-잉크 등) | 아트 디렉션 시 |

## Chapters

### 1. [레이아웃 패턴 레퍼런스](chapter-template-mode.md)
과거 11개 템플릿 기반 레이아웃 패턴 (참고 자료). 시각 강화 컴포넌트.
**읽을 때**: Freeform TSX 작성 시 구조적 참고, 어떤 레이아웃 패턴이 있는지 확인할 때.

### 2. [Freeform TSX 슬라이드 생성](chapter-freeform-mode.md)
2단계 워크플로 (TSX 생성 → 파이프라인), TSX 작성 규칙 (필수/권장/금지), 레이아웃 선택 가이드, FreeformSlotPool 4-slot 병렬 렌더링.
**읽을 때**: TSX 코드를 직접 작성하거나 에이전트에 TSX 작성을 위임할 때.

### 3. [Remotion 프로젝트 구조](chapter-remotion-project.md)
디렉토리 구조 (`remotion/src/slides/`, `design/`, `motifs/`, `shorts/`, `carousel/`), CLI 명령어, Python 렌더링 호출, 디자인 시스템 (theme.ts, animations.ts, fonts.ts).
**읽을 때**: Remotion 프로젝트 구조를 파악하거나 빌드/렌더링 문제 디버깅 시.

## 2가지 슬라이드 모드

| 모드 | 선택 기준 | 핵심 파일 |
|------|----------|----------|
| **Freeform TSX** | 공간 배치가 정보 전달의 핵심 (아이콘 그리드, UI 목업, 다단 레이아웃) | `projects/*/slides/*.tsx` |
| **Manim CE** | 애니메이션이 정보 전달의 핵심 (수식, 그래프, 알고리즘 단계) | `projects/*/slides/*.py` |

Mode 선택 기준: "객체가 나타나고 변환되는 것이 정보 전달이면 → Manim. 공간 배치가 정보면 → TSX."
