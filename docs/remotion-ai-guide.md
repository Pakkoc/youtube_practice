# Remotion-AI 애니메이션 백엔드 완전 가이드

> 이 문서는 Remotion-AI 슬라이드 시스템의 아키텍처, 파일 구조, 실행 흐름을 설명하는 강의용 레퍼런스입니다.

---

## 목차

1. [시스템 개요](#1-시스템-개요)
2. [2가지 슬라이드 모드](#2-2가지-슬라이드-모드)
3. [파일 맵 — 전체 경로 가이드](#3-파일-맵--전체-경로-가이드)
4. [디자인 시스템](#4-디자인-시스템)
5. [모션 라이브러리 (Motifs)](#5-모션-라이브러리-motifs)
6. [Freeform TSX 모드 상세](#6-freeform-tsx-모드-상세)
7. [Manim CE 모드 상세](#7-manim-ce-모드-상세)
8. [렌더링 파이프라인](#8-렌더링-파이프라인)
9. [스킬 시스템 — Claude Code 지침서 구조](#9-스킬-시스템--claude-code-지침서-구조)
10. [실행 명령어 레퍼런스](#10-실행-명령어-레퍼런스)
11. [디자인 철학 7원칙](#11-디자인-철학-7원칙)
12. [트러블슈팅](#12-트러블슈팅)

---

## 1. 시스템 개요

### 한 줄 요약

**대본 텍스트(script.txt) → 문단별 모션 그래픽 슬라이드(MP4) → 영상 합성**

### 아키텍처 다이어그램

```
script.txt (대본)
     │
     ▼
┌─────────────────────────────────────┐
│  문단 분리 (1 문단 = 1 슬라이드)      │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  Claude Code (/generate-slides 스킬)                            │
│  문단별로 2가지 모드 중 하나로 슬라이드 생성                         │
│                                                              │
│  ┌──────────────────┐  ┌──────────────┐                     │
│  │  Freeform TSX    │  │  Manim CE    │                     │
│  │  (기본 모드)      │  │  (수학 전용)  │                     │
│  └──────┬───────────┘  └──────┬───────┘                     │
└─────────┼─────────────────────┼─────────────────────────────┘
          │                     │
          ▼                     ▼
   .tsx 파일 작성          .py 파일 작성
   (Claude Code)          (Claude Code)
          │                 │                 │
          ▼                 ▼                 ▼
   ┌──────────────────────────────────────────────────┐
   │            Remotion CLI / Manim CLI               │
   │         → 슬라이드별 .mp4 비디오 렌더링             │
   └──────────────────────────────────────────────────┘
          │
          ▼
   FFmpeg 합성 → video_raw.mp4 → 자막/아바타 → final_video.mp4
```

### 핵심 개념

| 개념 | 설명 |
|------|------|
| **1 문단 = 1 슬라이드** | 대본의 빈 줄로 구분된 각 문단이 하나의 슬라이드가 됨 |
| **TTS 연동** | 슬라이드 길이(duration)는 해당 문단의 TTS 오디오 길이와 동일 |
| **B-roll 배경** | 생성된 B-roll 이미지가 슬라이드 배경(20% opacity)으로 자동 주입 |
| **쇼츠 안전** | 모든 콘텐츠는 중앙 정렬 — 9:16 크롭 시에도 잘리지 않도록 설계 |

---

## 2. 2가지 슬라이드 모드

```
┌────────────────────────────────────────────────────────────────────┐
│                    어떤 모드를 사용하는가?                            │
│                                                                    │
│  ┌──────────────────┐    ┌─────────────┐                          │
│  │  Freeform TSX    │    │  Manim CE   │                          │
│  │  (기본 모드)      │    │             │                          │
│  ├──────────────────┤    ├─────────────┤                          │
│  │ Claude Code가    │    │ Claude Code │                          │
│  │ TSX 코드를       │    │ 가 Python   │                          │
│  │ 직접 작성        │    │ 코드를 작성  │                          │
│  ├──────────────────┤    ├─────────────┤                          │
│  │ 텍스트, 불릿     │    │ 수학 수식   │                          │
│  │ 숫자/통계        │    │ 좌표 그래프  │                          │
│  │ 비교/인용        │    │ 알고리즘    │                          │
│  │ SVG/차트         │    │             │                          │
│  │ UI 목업          │    │             │                          │
│  │ 인포그래픽       │    │             │                          │
│  └──────────────────┘    └─────────────┘                          │
│                                                                    │
│  Claude Code (/generate-slides 스킬)가 freeform / manim 중 선택             │
└────────────────────────────────────────────────────────────────────┘
```

### 모드별 적합한 콘텐츠

| 콘텐츠 유형 | 추천 모드 | 이유 |
|------------|----------|------|
| 일반 텍스트, 불릿 포인트 | Freeform TSX | motifs 라이브러리로 풍부한 애니메이션 |
| 숫자/통계 강조 | Freeform TSX | countUp motif 사용 |
| 좌우 비교 | Freeform TSX | 커스텀 레이아웃 자유도 높음 |
| SVG 아이콘 인포그래픽 | Freeform TSX | 커스텀 SVG 배치 필요 |
| UI 목업, 채팅 인터페이스 | Freeform TSX | 비표준 레이아웃 |
| 복잡한 다이어그램 | Freeform TSX | 노드+연결선 배치 |
| LaTeX 수학 수식 | Manim CE | MathTex 전용 |
| 좌표 그래프, 함수 플롯 | Manim CE | Axes + plot 필요 |
| 알고리즘 단계별 시각화 | Manim CE | Transform 애니메이션 |

---

## 3. 파일 맵 — 전체 경로 가이드

프로젝트 루트: `C:\Users\hoyoung\Desktop\Youtube-Automation\`

### 3.1 Claude Code 스킬 & 지침서

Claude Code가 작업할 때 자동으로 읽는 지침서 파일들입니다.

```
.claude/
├── commands/
│   └── generate-slides.md          ← 메인 스킬 (/generate-slides 실행 시 로드)
│                                      6단계 워크플로, 디자인 철학, TSX/Manim 계약서
│                                      737줄 — 시스템의 "교과서"
│
├── skills/
│   ├── remotion-slides/            ← Remotion 레퍼런스 매뉴얼 (자동 트리거)
│   │   ├── SKILL.md                   인덱스 (2개 챕터로 분기)
│   │   ├── chapter-freeform-mode.md   Freeform 모드 상세
│   │   └── chapter-remotion-project.md  Remotion 프로젝트 구조
│   │
│   └── manim-slides/               ← Manim CE 레퍼런스 매뉴얼 (자동 트리거)
│       ├── SKILL.md                   인덱스 (3개 챕터로 분기)
│       ├── chapter-design-system.md   디자인 시스템 (색상, 폰트, 글래스카드)
│       ├── chapter-animation-patterns.md  애니메이션 패턴 (stagger, transform)
│       └── chapter-practical-guide.md     실전 가이드 (정렬, 안티패턴)
│
└── agents/
    └── code-reviewer/              ← 코드 리뷰 에이전트 (pre-commit용)
```

**스킬 로딩 원리**: Claude Code는 사용자 요청의 키워드("슬라이드", "remotion", "manim")를 감지하면 해당 `SKILL.md` 인덱스를 읽고, 필요한 챕터만 선택적으로 로드합니다. 이 "인덱스 + 서브파일" 패턴이 토큰 효율의 핵심입니다.

### 3.2 패턴 레퍼런스 (TSX 코드 작성 시 참조)

```
remotion/docs/
├── slide-patterns.md               ← 인덱스 + Common 패턴 + VOX Motion + Shared Helper
│                                      (항상 읽음)
│
├── slide-icons.md                  ← SVG 아이콘 라이브러리 (28개, 복붙용)
│                                      (항상 읽음)
│
├── slide-layouts.md                ← 레이아웃 인덱스 — 4개 서브파일로 라우팅
│                                      (항상 읽음, Decision Flowchart 포함)
│
├── slide-layouts-diagrams.md       ← Circle Flow, Bar Chart, Timeline, Step Indicator
│                                      (수치/순서/시간흐름 대본일 때)
│
├── slide-layouts-mockups.md        ← Document Frame, Chat UI, Service Panel, Compare
│                                      (앱 화면/UI 묘사 대본일 때)
│
├── slide-layouts-metaphors.md      ← People Row, Balance Scale, Arrow Flow, Icon Grid
│                                      (추상 개념/비율/장단점 대본일 때)
│
└── slide-layouts-extras.md         ← Progress Bar, SVG Stroke Draw, Shorts-Safe 변형
                                       (보조 UI/쇼츠 대응 필요 시)
```

**읽기 전략**: `slide-patterns.md`(인덱스)와 `slide-icons.md`는 항상 로드. `slide-layouts.md`의 Decision Flowchart를 보고 필요한 서브파일 1~2개만 선택적 로드.

### 3.3 LLM 프롬프트 파일

```
prompts/
├── manim_scene_generation.txt      ← Manim CE 프롬프트
│                                      (디자인 시스템 + 정렬 규칙 + 예제)
│
└── channel_identity.txt            ← 채널 페르소나 (샘호트만 정체성)
                                       (모든 슬라이드 생성 시 참조)
```

### 3.4 Python 백엔드 코드

```
features/generate_slides/
├── __init__.py                     ← 공개 API exports
├── lib.py                          ← 핵심 로직 (문단→슬라이드 오케스트레이션)
│                                      generate_remotion_props_for_paragraphs()
│                                      generate_remotion_props_for_scenes()
│                                      render_remotion_slides()
│
├── remotion_backend.py             ← Remotion CLI 렌더링 엔진
│                                      RemotionSlideBackend.render()
│                                      FreeformSlotPool (4슬롯 병렬 렌더링)
│                                      validate_tsx() (tsc --noEmit 검증)
│
├── manim_backend.py                ← Manim CLI 렌더링 엔진
│                                      ManimSlideBackend.render()
│                                      2-pass duration control
│
└── model.py                        ← SlideGenerationResult 모델
```

### 3.5 Remotion 프론트엔드 (TSX)

```
remotion/
├── package.json                    ← Remotion v4.0.417
├── tsconfig.json
├── remotion.config.ts
│
├── src/
│   ├── Root.tsx                    ← Composition 등록 (Freeform 슬롯)
│   │
│   ├── slides/                     ← 슬라이드 컴포넌트
│   │   ├── types.ts                   Props 타입 정의 (FreeformProps 등)
│   │   │
│   │   │  # ── Freeform 슬롯 (병렬 렌더링용) ──
│   │   ├── Freeform.tsx               메인 슬롯 (검증용)
│   │   ├── FreeformSlot1.tsx          병렬 슬롯 1
│   │   ├── FreeformSlot2.tsx          병렬 슬롯 2
│   │   ├── FreeformSlot3.tsx          병렬 슬롯 3
│   │   └── FreeformSlot4.tsx          병렬 슬롯 4
│   │   │
│   │   │  # ── Shorts 전용 슬롯 ──
│   │   ├── ShortsContentSlot1~4.tsx   쇼츠 9:16 레이아웃
│   │
│   ├── design/                     ← 디자인 시스템
│   │   ├── theme.ts                   COLORS, FONT, LAYOUT, GLOW, STYLE 토큰
│   │   ├── animations.ts             AnimationStyle 6종 정의
│   │   ├── fonts.ts                   useFonts() 훅 (Pretendard 로드)
│   │   ├── AnimatedBackground.tsx     배경 컴포넌트 (B-roll 블러 처리)
│   │   ├── SceneFade.tsx              장면 전환 페이드
│   │   └── ProgressBar.tsx            하단 프로그레스 바
│   │
│   ├── motifs/                     ← 모션 라이브러리
│   │   ├── index.ts                   전체 re-export
│   │   ├── timing.ts                  getAnimationZone, staggerDelays, zoneDelay
│   │   ├── springConfigs.ts           4종 스프링 설정 + pickSpring
│   │   │
│   │   ├── entries/                ← 진입 애니메이션 (→ { opacity, transform })
│   │   │   ├── index.ts
│   │   │   ├── fadeSlideIn.ts         기본 페이드+슬라이드
│   │   │   ├── fadeIn.ts              단순 페이드
│   │   │   ├── cascadeUp.ts           리스트 순차 진입
│   │   │   ├── layeredReveal.ts       3레이어 점진적 공개 (VOX 스타일)
│   │   │   ├── scaleIn.ts             스케일 진입 (아이콘/배지 전용)
│   │   │   ├── bounceIn.ts            바운스 진입 (아이콘 전용)
│   │   │   ├── zoomPop.ts             줌 팝 (아이콘 전용)
│   │   │   ├── slideFromLeft.ts       좌측 슬라이드
│   │   │   ├── slideFromRight.ts      우측 슬라이드
│   │   │   └── slideFromBottom.ts     하단 슬라이드
│   │   │
│   │   ├── emphasis/               ← 강조 효과 (→ 숫자값)
│   │   │   ├── index.ts
│   │   │   ├── highlighter.ts         형광펜 효과 (0→1 scaleX)
│   │   │   ├── shiftingGradient.ts    그라디언트 오프셋 (0→360)
│   │   │   ├── countUp.ts             숫자 카운트업 (parse + format)
│   │   │   ├── pulse.ts               펄스 (0→0.45)
│   │   │   ├── typewriter.ts          타이프라이터 (글자 수 반환)
│   │   │   ├── breathe.ts             호흡 스케일 (~1.0)
│   │   │   ├── stutterStep.ts         VOX 12fps 스터터 효과
│   │   │   ├── penStroke.ts           손글씨 형광펜 (wobble 포함)
│   │   │   └── jitter.ts              미세 떨림 (결정론적)
│   │   │
│   │   ├── decorations/            ← 장식 효과 (→ 숫자값)
│   │   │   ├── index.ts
│   │   │   ├── glassCard.ts           글라스카드 불투명도 (0→1)
│   │   │   ├── drawBar.ts             바 그리기 (0→1 scaleY)
│   │   │   ├── drawLine.ts            선 그리기 (0→1 scaleX)
│   │   │   ├── radialGlow.ts          방사형 글로우
│   │   │   ├── svgStrokeDraw.ts       SVG 스트로크 드로잉
│   │   │   └── ringScale.ts           링 스케일 (0→1)
│   │   │
│   │   └── transitions/            ← 전환 효과
│   │       ├── index.ts
│   │       └── sceneFade.ts           장면 페이드 (0→1)
│   │
│   └── shorts/                     ← 쇼츠 전용 컴포넌트
│       ├── ShortsComposition.tsx
│       ├── HookTitle.tsx
│       ├── StyledSubtitle.tsx
│       └── types.ts
│
├── public/                         ← 정적 에셋 (B-roll 임시 복사 위치)
└── docs/                           ← 패턴 레퍼런스 문서 (위 3.2 참조)
```

### 3.6 실행 스크립트

```
scripts/
├── regenerate_slides.py             ← Remotion TSX + Manim → MP4 렌더링
│                                      FreeformSlotPool 4슬롯 병렬
│                                      --validate, --force, --parallel 옵션
│
├── regenerate_broll.py             ← B-roll 이미지만 재생성
├── recompose_video.py              ← 기존 슬라이드+오디오로 영상 재합성
└── continue_pipeline.py            ← Step 3부터 파이프라인 재실행
```

### 3.7 Config 파일

```
config/
├── config.base.yaml                ← 기본 프로필 (pipeline.slides.backend 여기서 변경)
├── config.api.yaml                 ← API-Only 모드
├── config.test.yaml                ← 테스트용
└── config.prod.yaml                ← 프로덕션

# 슬라이드 백엔드 설정 (config.base.yaml 내)
pipeline:
  slides:
    backend: remotion               # Freeform TSX + Manim
```

### 3.8 프로젝트 출력 구조

```
projects/my-video/
├── script.txt                      ← 입력 대본 (빈 줄로 문단 구분)
├── paragraphs/
│   ├── 001.txt                     ← 분리된 문단 파일
│   ├── 002.txt
│   └── ...
├── slides/
│   ├── 001.tsx                     ← Freeform 모드: TSX 소스
│   ├── 001.mp4                     ← 렌더링된 슬라이드 비디오
│   ├── 002.tsx
│   ├── 002.mp4
│   ├── 003.py                      ← Manim 모드: Python 소스
│   ├── 003.mp4
│   └── ...
├── audio/
│   ├── 001.wav                     ← TTS 오디오 (슬라이드 duration 결정)
│   └── ...
├── broll/
│   └── generated/
│       ├── broll_001.png           ← 슬라이드 배경으로 자동 주입 (20% opacity)
│       └── ...
└── output/
    ├── video_raw.mp4               ← 슬라이드 합성 결과
    └── final_video.mp4             ← 최종 출력 (자막+아바타 포함)
```

---

## 4. 디자인 시스템

> 경로: `remotion/src/design/theme.ts`

### 4.1 색상 (COLORS)

```
COLORS.BG            = "#0B0C0E"    ← 배경 (거의 검정)
COLORS.TEXT           = "#EDEDEF"    ← 본문 텍스트 (거의 흰색)
COLORS.ACCENT         = "#7C7FD9"   ← 핵심 강조 (보라)
COLORS.ACCENT_BRIGHT  = "#9B9EFF"   ← 데이터/수치 (밝은 보라)
COLORS.MUTED          = "#9394A1"   ← 보조 정보 (회색)
COLORS.TEAL           = "#3CB4B4"   ← 긍정/성과 (청록)
COLORS.CODE_BG        = "#1C1E21"   ← 코드 배경
```

**색상 의미론 규칙**:
- ACCENT(보라) = 핵심 개념, 주제 키워드
- TEAL(청록) = 긍정적 결과, 해결책
- ACCENT_BRIGHT(밝은 보라) = 데이터, 수치
- MUTED(회색) = 보조 정보, 라벨
- 한 슬라이드에 강조 색상은 **최대 2개**

### 4.2 폰트 (FONT)

```
FONT.family    = "'Pretendard', -apple-system, ..."
FONT.title     = { size: 76, weight: 800, letterSpacing: "-0.04em", lineHeight: 1.1 }
FONT.bullet    = { size: 36, weight: 500, lineHeight: 1.25 }
FONT.subtitle  = { size: 28, weight: 500, lineHeight: 1.4 }
FONT.bigNumber = { size: 120, weight: 800, lineHeight: 1.0 }
FONT.context   = { size: 32, weight: 500, lineHeight: 1.4 }
```

### 4.3 레이아웃 (LAYOUT)

```
LAYOUT.padding           = { top: 100, right: 120, bottom: 100, left: 120 }
LAYOUT.subtitleReserved  = 360       ← 하단 자막 예약 영역 (px)
LAYOUT.card.minWidth     = 160       ← 아이콘+라벨 카드 최소폭
LAYOUT.card.descMinWidth = 200       ← description 포함 카드 최소폭
```

### 4.4 글로우 (GLOW)

```
GLOW.text            = "0 0 20px rgba(124,127,217,0.5), ..."   ← 텍스트 글로우
GLOW.bar             = "0 0 12px rgba(124,127,217,0.6)"        ← 바 글로우
GLOW.highlightBg     = "rgba(124,127,217,0.15)"                ← 하이라이트 배경
GLOW.highlightBorder = "rgba(124,127,217,0.3)"                 ← 하이라이트 테두리
```

### 4.5 스타일 프리셋 (STYLE)

```
STYLE.cardLabel  = { fontSize:24, fontWeight:600, whiteSpace:"nowrap", textAlign:"center" }
STYLE.cardDesc   = { fontSize:18, fontWeight:400, wordBreak:"keep-all", textAlign:"center" }
STYLE.cardBody   = { fontSize:22, fontWeight:500, wordBreak:"keep-all" }
```

### 4.6 애니메이션 스타일 (AnimationStyle)

> 경로: `remotion/src/design/animations.ts`

6종 — Freeform TSX에서 motifs 라이브러리와 함께 사용:

| 스타일 | 효과 | 적합한 분위기 |
|--------|------|-------------|
| `default` | 기본 페이드+슬라이드 | 일반적인 정보 전달 |
| `cascadeUp` | 아래→위 순차 진입 | 리스트, 단계별 설명 |
| `fadeAll` | 전체 동시 페이드 | 차분한 강조 |
| `slideRight` | 좌→우 슬라이드 | 비교, 흐름 |
| `bounceIn` | 바운스 진입 | 역동적, 재미있는 |
| `zoomPop` | 확대 팝 | 임팩트, 숫자 강조 |

---

## 5. 모션 라이브러리 (Motifs)

> 경로: `remotion/src/motifs/`

슬라이드 애니메이션의 핵심 빌딩 블록입니다. 모든 모션은 이 라이브러리의 함수 조합으로 만듭니다.

### 5.1 진입 애니메이션 (entries/)

모두 `{ opacity: number; transform: string }`을 반환합니다.

```tsx
import { fadeSlideIn, cascadeUp, layeredReveal,
         scaleIn, bounceIn, zoomPop,
         slideFromLeft, slideFromRight, slideFromBottom,
         fadeIn } from "../motifs/entries";
```

| 함수 | 용도 | 주의사항 |
|------|------|---------|
| `fadeSlideIn(frame, fps, delay, config?)` | 범용 페이드+슬라이드 | 텍스트에 안전 |
| `cascadeUp(frame, fps, itemIndex, baseDelay?, stagger?, config?)` | 리스트 순차 진입 | 텍스트에 안전 |
| `layeredReveal(frame, fps, layer, opts?)` | VOX 3레이어 공개 | 읽기 시간 확보 |
| `scaleIn(frame, fps, delay)` | 스케일 진입 | **아이콘/배지 전용**, 텍스트 금지 |
| `bounceIn(frame, fps, delay)` | 바운스 진입 | **아이콘 전용**, 텍스트 금지 |
| `zoomPop(frame, fps, delay)` | 줌 팝 | **아이콘 전용**, 텍스트 금지 |

**핵심 규칙**: `scaleIn`, `bounceIn`, `zoomPop`은 scale(0.5→1.0) 과정에서 텍스트 줄바꿈이 변경(reflow)되므로 **텍스트 컨테이너에 절대 사용 금지**. 텍스트에는 `fadeSlideIn` 또는 `cascadeUp`만 사용.

### 5.2 강조 효과 (emphasis/)

숫자값을 반환합니다.

```tsx
import { highlighter, shiftingGradientOffset, countUpProgress,
         parseAnimatedNumber, formatAnimatedNumber,
         pulse, typewriterCount, breathe,
         stutterStep, penStroke, jitter } from "../motifs/emphasis";
```

| 함수 | 반환값 | 용도 |
|------|--------|------|
| `highlighter(frame, fps, delay?)` | 0→1 | 형광펜 밑줄 scaleX |
| `countUpProgress(frame, fps, durSec?)` | 0→1 | 숫자 카운트업 |
| `parseAnimatedNumber("73%")` | `{prefix, value, suffix, ...}` | 숫자 문자열 파싱 |
| `formatAnimatedNumber(parsed, progress)` | `"73%"` | 파싱된 숫자 포맷 |
| `stutterStep(progress, steps?)` | stepped 0→1 | VOX 12fps 느낌 |
| `penStroke(frame, fps, delay?)` | `{progress, wobble}` | 손글씨 형광펜 |
| `jitter(frame, seed, amplitude?)` | px offset | 미세 떨림 (결정론적) |

### 5.3 장식 효과 (decorations/)

```tsx
import { glassCardOpacity, drawBar, drawLine, radialGlow,
         svgStrokeDraw, ringScale } from "../motifs/decorations";
```

| 함수 | 반환값 | 용도 |
|------|--------|------|
| `glassCardOpacity(frame, fps, durSec?)` | 0→1 | 글라스카드 등장 |
| `drawBar(frame, fps, delay?)` | 0→1 scaleY | 바 차트 그리기 |
| `drawLine(frame, fps, delay?)` | 0→1 scaleX | 선 그리기 |
| `svgStrokeDraw(frame, fps, totalLength, delay?)` | strokeDashoffset | SVG 경로 드로잉 |

### 5.4 스프링 설정 (springConfigs.ts)

```tsx
import { SPRING_GENTLE, SPRING_SNAPPY, SPRING_BOUNCY, SPRING_STIFF,
         STAGGER_DELAY, pickSpring } from "../motifs/springConfigs";
```

| 설정 | 값 | 분위기 |
|------|-----|--------|
| `SPRING_GENTLE` | `{ damping: 15, mass: 0.8 }` | 차분, 감정적 |
| `SPRING_SNAPPY` | `{ damping: 20, mass: 0.6 }` | 정보 전달 (기본) |
| `SPRING_BOUNCY` | `{ damping: 8, mass: 0.6 }` | 역동, 재미 |
| `SPRING_STIFF` | `{ damping: 25, mass: 0.5 }` | 빠르고 정확 |
| `STAGGER_DELAY` | `6` frames | 리스트 아이템 간격 |

`pickSpring(index)`: 인접 아이템이 자동으로 다른 스프링을 받도록 순환.

### 5.5 Duration-Proportional Timing (timing.ts)

> **하드코딩된 프레임 딜레이 금지** — 모든 타이밍은 슬라이드 duration에 비례해야 합니다.

```tsx
import { getAnimationZone, staggerDelays, zoneDelay } from "../motifs/timing";

const zone = getAnimationZone(durationInFrames);
// 짧은 슬라이드(≤5s): zone = 100% of duration
// 긴 슬라이드(≥10s): zone = 50% of duration

// 단일 요소: 전체 zone의 30% 지점에서 등장
const delay = zoneDelay(0.3, zone);

// N개 아이템: zone 내에서 균등 분배
const delays = staggerDelays(items.length, zone, { offset: Math.round(zone * 0.2) });
```

---

## 6. Freeform TSX 모드 상세

> Skill: `.claude/commands/generate-slides.md`
> Pattern: `remotion/docs/slide-patterns.md` + 서브파일들
> 렌더링: `remotion/src/slides/Freeform.tsx` (+ FreeformSlot1~4.tsx)

### 6.1 워크플로 (2단계)

```bash
# Step 1: Claude Code가 TSX 파일 작성 (~10분)
/generate-slides 003

# Step 2: TSX → MP4 렌더링
uv run python scripts/regenerate_slides.py 003
```

### 6.2 TSX Component Contract (필수 구조)

모든 Freeform TSX 파일은 이 구조를 **반드시** 따라야 합니다:

```tsx
// 1. 필수 import
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, Easing } from "remotion";
import { COLORS, FONT, LAYOUT, GLOW, STYLE } from "../design/theme";
import { AnimatedBackground } from "../design/AnimatedBackground";
import { SceneFade } from "../design/SceneFade";
import { ProgressBar } from "../design/ProgressBar";
import { useFonts } from "../design/fonts";
import type { FreeformProps } from "./types";
// + 필요한 motifs import

// 2. 필수 export 이름
export const Freeform: React.FC<FreeformProps> = ({
  slideIndex, totalSlides, backgroundImage,
}) => {
  // 3. 필수 훅 호출
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 4. 필수 컴포넌트 구조
  return (
    <AbsoluteFill>
      <AnimatedBackground backgroundImage={backgroundImage} />  {/* 항상 첫 번째 */}
      <AbsoluteFill style={{ padding: "100px 120px", ... }}>
        {/* 콘텐츠 */}
      </AbsoluteFill>
      <ProgressBar slideIndex={slideIndex} totalSlides={totalSlides} />  {/* 항상 마지막 2개 */}
      <SceneFade />
    </AbsoluteFill>
  );
};
```

### 6.3 절대 규칙 19개

| # | 규칙 | 이유 |
|---|------|------|
| 1 | `export const Freeform` 이름 고정 | 파이프라인이 Freeform.tsx를 덮어쓰기 |
| 2 | `FreeformProps` 타입 사용 | `./types`에서 import |
| 3 | `useFonts()` 호출 | Pretendard 폰트 로드 |
| 4 | `AnimatedBackground` 첫 번째 자식 | B-roll 배경 표시 |
| 5 | `ProgressBar` + `SceneFade` 마지막 | UI 일관성 |
| 6 | CSS transition/animation 금지 | Remotion은 프레임 기반 렌더링 |
| 7 | `Math.random()` 금지 | 비결정론적 (프레임마다 다른 값) |
| 8 | Tailwind 금지 | 인라인 스타일만 |
| 9 | 한국어 개조식 | 명사/체언 종결 |
| 10 | 모든 콘텐츠 중앙 정렬 | 쇼츠 크롭 안전 |
| 11 | 하단 360px 비움 | 자막 예약 영역 |
| 12 | CSS 속성 중복 금지 | TypeScript strict mode |
| 13 | 다열 레이아웃 `maxWidth: 700` | 쇼츠 크롭 안전 |
| 14 | 차트 중앙 정렬 | `alignItems: "center"` |
| 15 | SVG는 라이브러리에서 복사 | `slide-icons.md` 참조 |
| 16 | 연속 연결선은 absolute 단일선 | 불연속 방지 |
| 17 | 빈 시각 슬롯 금지 | `icon: null` 금지 |
| 18 | 텍스트에 scale 계열 금지 | text reflow 방지 |
| 19 | `backdropFilter: "blur()"` 금지 | 배경 콘텐츠가 안 보임 |

### 6.4 FreeformSlotPool (병렬 렌더링)

> 경로: `features/generate_slides/remotion_backend.py`

```
┌─────────────────────────────────────────┐
│         FreeformSlotPool (4슬롯)          │
│                                          │
│   FreeformSlot1.tsx ──→ Composition "FreeformSlot1"   ← 동시 렌더링
│   FreeformSlot2.tsx ──→ Composition "FreeformSlot2"   ← 동시 렌더링
│   FreeformSlot3.tsx ──→ Composition "FreeformSlot3"   ← 동시 렌더링
│   FreeformSlot4.tsx ──→ Composition "FreeformSlot4"   ← 동시 렌더링
│                                          │
│   동작 원리:                               │
│   1. 슬롯 acquire() → 사용 가능한 슬롯 번호  │
│   2. write_slot(id, tsx) → 슬롯 파일 덮어쓰기│
│   3. Remotion CLI 렌더링                    │
│   4. release(id) → 슬롯 반환                │
│   5. restore_all() → 원본 복원              │
└─────────────────────────────────────────┘
```

4개의 독립 슬롯 파일을 사용하므로, 4개 슬라이드를 동시에 렌더링할 수 있습니다.

---

## 7. Manim CE 모드 상세

> Python 백엔드: `features/generate_slides/manim_backend.py`
> Prompt: `prompts/manim_scene_generation.txt`
> Skill: `.claude/skills/manim-slides/`

### 7.1 Scene Contract (필수 구조)

```python
from manim import *

class ManimSlide(Scene):
    def construct(self):
        self.camera.background_color = "#0B0C0E"

        # 색상 팔레트 (Remotion 디자인 시스템과 동일)
        TEXT = ManimColor("#EDEDEF")
        ACCENT = ManimColor("#7C7FD9")
        ACCENT_B = ManimColor("#9B9EFF")
        TEAL = ManimColor("#3CB4B4")
        MUTED = ManimColor("#9394A1")

        # ... 씬 콘텐츠 ...

        self.wait(0.01)  # DURATION_PLACEHOLDER
```

### 7.2 2-Pass Duration Control

```
Pass 1: DURATION_PLACEHOLDER = 0.01로 렌더링
    → 총 애니메이션 시간 측정 (예: 8.3초)

남은 시간 = 목표 duration - 애니메이션 시간
    → 예: 15.0초 - 8.3초 = 6.7초

Pass 2: DURATION_PLACEHOLDER = 6.7로 교체 후 최종 렌더링
    → 정확히 목표 duration에 맞는 MP4 출력
```

### 7.3 Auto-Injected Frame

Manim 백엔드가 자동 주입하는 요소:
- 그라디언트 배경
- 어두운 콘텐츠 카드 (13.4 x 7.28)
- 프로그레스 바

**따라서 `.py` 코드에서 배경/카드/프로그레스를 직접 만들면 안 됩니다.**

### 7.4 Alignment 검증 (3가지 안티패턴)

> 경로: `features/generate_slides/manim_backend.py` → `check_manim_alignment()`

| 안티패턴 | 왜 문제인가 | 올바른 대안 |
|---------|-----------|-----------|
| `SurroundingRectangle` in loop | 텍스트마다 폭이 달라짐 | 고정폭 `RoundedRectangle(width=ROW_W)` |
| Multiple `arrange(RIGHT)` | 행 너비가 가변적 | `move_to(bg.get_left() + RIGHT * offset)` |
| `move_to(card.get_center())` without top anchor | 세로 중앙으로 떠버림 | `next_to(underline, DOWN, buff=0.55)` |

검증 실패 시 피드백을 포함하여 LLM이 최대 3회 재시도합니다.

---

## 8. 렌더링 파이프라인

### 8.1 파이프라인 내 위치

```
pipelines/script_to_video/lib.py — 7단계 중 2~3단계

Step 2: 병렬 처리
   ┌─ TTS 생성 (ElevenLabs/local) ───────┐  ThreadPoolExecutor
   └─ B-roll 이미지 생성 ───────────────┘
   │  B-roll → 슬라이드 배경(20% opacity)으로 주입
   │  Freeform TSX: /generate-slides 스킬로 별도 생성

Step 3: 슬라이드 렌더링
   ├─ Freeform: FreeformSlotPool (4슬롯 병렬)
   └─ Manim: ManimSlideBackend.render() (2-pass, 순차)
```

### 8.2 파일 재사용 로직

파이프라인은 기존 파일을 감지하고 자동 재사용합니다:

| 파일 | 재사용 조건 | 재생성 방법 |
|------|-----------|-----------|
| `slides/NNN.mp4` | 파일 존재 + duration ±0.5초 매칭 → 렌더링 스킵 | MP4 파일 삭제 |
| `slides/NNN.tsx` | TSX 존재 → mode="freeform" 자동 감지 | TSX 파일 삭제 |
| `slides/NNN.py` | .py 존재 → mode="manim" 자동 감지 | .py 파일 삭제 |

**주의**: TSX를 수정했는데 영상에 반영이 안 되면, `.mp4`를 삭제해야 합니다. Stale MP4가 duration 매칭으로 재사용되기 때문입니다.

### 8.3 Remotion CLI 호출 구조

> 경로: `features/generate_slides/remotion_backend.py` → `RemotionSlideBackend.render()`

```
Python                          Remotion
  │                               │
  ├── props를 임시 JSON 파일로 저장   │
  │   (tempfile, UTF-8)           │
  │                               │
  ├── B-roll 이미지를              │
  │   remotion/public/에 복사      │
  │                               │
  ├── npx remotion render         │
  │   {template_name}             │
  │   {output_path}               │
  │   --props={json_path}    ───→ │ calculateMetadata()
  │   --fps=30                    │ durationInFrames 읽기
  │   --width=1920                │ 컴포넌트 렌더링
  │   --height=1080               │ → MP4 출력
  │   --frames=0-{N}              │
  │   --codec=h264                │
  │                               │
  ├── 임시 JSON 파일 삭제           │
  └── B-roll 임시 파일 삭제         │
```

---

## 9. 스킬 시스템 — Claude Code 지침서 구조

### 9.1 스킬이란?

Claude Code가 특정 작업을 수행할 때 자동으로 읽는 **지침서 파일**입니다. 두 가지 종류가 있습니다:

| 종류 | 경로 | 트리거 방식 | 예시 |
|------|------|-----------|------|
| **Command (사용자 호출)** | `.claude/commands/*.md` | 사용자가 `/command-name` 입력 | `/generate-slides 003` |
| **Skill (자동 트리거)** | `.claude/skills/*/SKILL.md` | 키워드/파일 패턴 자동 감지 | remotion 파일 수정 시 |

### 9.2 `/generate-slides` 스킬 — 6단계 워크플로

> 경로: `.claude/commands/generate-slides.md` (737줄)

이것이 Remotion-AI 시스템의 **메인 교과서**입니다.

```
Step 1: Read Project Data
   └── paragraphs/*.txt, audio/*.wav, broll/generated/ 읽기

Step 2: Art Direction (전체 영상의 비주얼 전략 수립)
   ├── 2a. Content Type Classification (Tutorial/Comparison/Persuasion/Story/Technical)
   ├── 2b. Recurring Motifs (2~3개 반복 모티프 선정)
   ├── 2c. Visual Anchor (영상 고유 시각 앵커 1개)
   ├── 2d. Subject-Relevant Design Language
   └── 2e. Output (내부 노트 작성)

Step 3: Plan All Slides (슬라이드 테이블 작성)
   ├── 3a. Slide Table (번호, 요약, 모드, 레이아웃, 비주얼, 강도)
   ├── 3b. Layout Options (13가지 레이아웃)
   ├── 3c. Narrative Pacing Rules (9개 규칙)
   ├── 3d. Visual Richness Rule (SVG/차트 필수)
   ├── 3e. Template Differentiation Rule
   ├── 3f. Anti-Patterns (5개 금지 패턴)
   ├── 3g. Quality Self-Review (14개 체크리스트) ← 필수
   └── 3h. Content Fidelity Rules (5개 충실도 규칙)

Step 4: Write Slide Files (병렬 Agent로 TSX/Manim 작성)
   ├── 4a. Batch Sizing (슬라이드 수에 따라 1~4 배치)
   ├── 4b. Agent Dispatch (병렬 Task agent 실행)
   └── 4c. Post-Agent Verification (파일 수 확인, tsc 검증)

Step 5: Validate
   ├── TSX: tsc --noEmit + remotion still (frame 0 PNG)
   └── Manim: AST parse + 구조 검증 + 보안 검증

Step 5.5: Cleanup Conflicting Files
   └── .json, .mp4 삭제 (stale 파일 재사용 방지)

Step 6: Render to MP4
   └── uv run python scripts/regenerate_slides.py $PROJECT
```

### 9.3 인덱스 + 서브파일 패턴

문서가 300줄을 초과하면 주제별 서브파일로 분할하는 원칙입니다.

```
예시: slide-layouts.md (86줄, 인덱스)
  ├── slide-layouts-diagrams.md      (차트/타임라인 — 수치 대본일 때만 읽음)
  ├── slide-layouts-mockups.md       (UI 목업 — 앱 화면 대본일 때만 읽음)
  ├── slide-layouts-metaphors.md     (시각 은유 — 추상 개념 대본일 때만 읽음)
  └── slide-layouts-extras.md        (보조/쇼츠 — 필요 시만 읽음)
```

**인덱스에 포함해야 할 것**:
- 서브파일 목록 + **"언제 이 문서를 읽어야 하는지"** 상세 설명
- Decision Flowchart (대본 내용 → 서브파일 매칭)
- 대본 예시

이 패턴으로 Claude Code는 전체 문서를 다 읽지 않고, 필요한 서브파일만 선택적으로 로드합니다.

---

## 10. 실행 명령어 레퍼런스

### 10.1 Freeform TSX 워크플로 (가장 일반적)

```bash
# 1. TSX 파일 생성 (Claude Code 스킬)
/generate-slides 003

# 2. 검증 (frame 0 렌더링으로 런타임 에러 감지)
uv run python scripts/regenerate_slides.py 003 --validate

# 3. MP4 렌더링 (4슬롯 병렬)
uv run python scripts/regenerate_slides.py 003

# 4. 특정 슬라이드만 재렌더링
uv run python scripts/regenerate_slides.py 003 013 020 --force

# 5. 전체 파이프라인 (영상 합성까지)
uv run video-automation pipeline script-to-video \
  --input projects/003/script.txt --project 003 --no-broll
```

### 10.2 검증 명령

```bash
# TSX 타입 체크
cp projects/003/slides/001.tsx remotion/src/slides/Freeform.tsx
cd remotion && npx tsc --noEmit

# TSX 런타임 검증 (frame 0 PNG)
uv run python scripts/regenerate_slides.py 003 --validate

# Manim 구문 검증
python -c "import ast; ast.parse(open('projects/003/slides/001.py', encoding='utf-8').read())"

# Manim 구조 검증
grep -q "class ManimSlide(Scene)" projects/003/slides/001.py
grep -q "DURATION_PLACEHOLDER" projects/003/slides/001.py
```

### 10.3 Stale 파일 정리

```bash
# TSX/Manim 소스가 있는 슬라이드의 MP4 삭제 (재렌더링 강제)
cd projects/003/slides
for f in *.tsx *.py; do
  base="${f%.*}"
  rm -f "${base}.mp4"
done
```

---

## 11. 디자인 철학 7원칙

> 출처: `.claude/commands/generate-slides.md` → Design Philosophy

이 원칙들은 VOX 스타일 모션 인포그래픽, Tufte의 정보 디자인, Gestalt 시각 인지 이론에서 도출되었습니다. "AI가 만든 티"를 없애는 핵심입니다.

### 11.1 상보성 (Complementary, Not Redundant)

슬라이드는 나레이션의 **자막이 아니라 시각적 보충 자료**입니다.
- 나레이션이 "왜"를 설명 → 슬라이드는 "무엇/얼마나"를 시각화
- 나레이션에서 이미 말하는 문장을 슬라이드에 다시 쓰지 않음

### 11.2 점진적 공개 (Progressive Disclosure)

정보를 한 번에 보여주지 말고 **단계별로 드러냅니다**.
- 제목(0s) → 아이콘/다이어그램(0.3s) → 상세 텍스트(0.6s)
- `layeredReveal(frame, fps, layer)` 사용
- **안티패턴**: 모든 요소가 동시에 fadeIn

### 11.3 비례 = 중요도 (Hitchcock's Proportion Rule)

화면에서 가장 큰 시각적 공간을 차지하는 요소가 가장 중요한 정보여야 합니다.
- 한 슬라이드에 강조점은 **1개만**
- 주요 요소가 화면의 50% 이상 차지

### 11.4 데이터-잉크 비율 (Tufte's Data-Ink Ratio)

슬라이드의 **모든 시각 요소는 정보를 전달**해야 합니다.
- 장식적 SVG, 의미 없는 글로우 → 제거
- SVG 아이콘은 내용과 직접 관련된 것만

### 11.5 근접 = 관계 (Gestalt Proximity)

**가까이 있는 요소는 관련 있는 것**으로 인식됩니다.
- 관련 요소 간격 8-16px, 무관한 그룹 간격 40-60px
- 시각적 그룹이 의미적 그룹과 일치

### 11.6 여백 = 임팩트 (Whitespace as Intentional Tool)

빈 공간은 의도적 도구입니다.
- 화면의 **30% 이상** 의도적으로 비움
- 정보를 더 넣고 싶으면 **다음 슬라이드에 배치**

### 11.7 색상 의미론 (Color Semantics)

색상을 일관되게 사용하면 시청자가 무의식적으로 의미를 파악합니다.
- ACCENT(보라) = 핵심 개념
- TEAL(청록) = 긍정/성과
- ACCENT_BRIGHT(밝은 보라) = 데이터/수치
- 한 슬라이드에서 강조 색상은 **최대 2개**

---

## 12. 트러블슈팅

### Q: TSX를 수정했는데 영상에 반영이 안 됩니다

stale `.mp4` 파일이 duration 매칭으로 재사용되고 있습니다.

```bash
# 해당 슬라이드의 .mp4 삭제
rm projects/003/slides/005.mp4

# 또는 전체 정리
cd projects/003/slides
for f in *.tsx *.py; do base="${f%.*}"; rm -f "${base}.mp4"; done
```

### Q: `tsc --noEmit` 에러

- **중복 CSS 속성**: TypeScript strict mode에서는 같은 style 객체에 같은 key 2번 불가
- **잘못된 import**: `../motifs/entries`의 export 목록에 없는 함수를 import
- **경로 오류**: `remotion/src/slides/` 기준으로 상대 경로 확인

### Q: Remotion 렌더링 시 빈 화면

- `useFonts()` 호출 누락
- `AnimatedBackground` 누락
- `backdropFilter: "blur()"` 사용 → 배경이 흐려져 안 보임

### Q: Manim 렌더링 실패

- `class ManimSlide(Scene):` 이름이 틀림
- `DURATION_PLACEHOLDER` 주석 누락 → 2-pass duration control 불가
- `os`, `subprocess` import → 보안 검증 실패

### Q: 슬라이드 렌더링 스크립트

```bash
uv run python scripts/regenerate_slides.py <project>  # Remotion TSX + Manim → MP4
```

Marp 백엔드는 제거되어 Remotion이 유일한 슬라이드 백엔드입니다.

---

## 부록: 강의 추천 커리큘럼

### Module 1: 개념 이해 (Why)
- 왜 2개 모드가 필요한가 (Freeform TSX + Manim CE)
- 디자인 철학 7원칙 (Section 11)
- **읽을 파일**: 이 문서의 Section 1~2

### Module 2: 디자인 시스템 (What)
- COLORS, FONT, LAYOUT, GLOW, STYLE 토큰
- AnimationStyle 6종
- **읽을 파일**: `remotion/src/design/theme.ts`, Section 4

### Module 3: 모션 라이브러리 (핵심)
- entries / emphasis / decorations / springConfigs
- Duration-Proportional Timing
- **읽을 파일**: Section 5, `remotion/src/motifs/` 전체
- **실습**: 간단한 TSX 슬라이드 직접 작성

### Module 4: Freeform TSX 모드 (심화)
- TSX Component Contract 19개 규칙
- 패턴 레퍼런스 활용법 (인덱스 → 서브파일 선택)
- FreeformSlotPool 병렬 렌더링
- **읽을 파일**: Section 6, `remotion/docs/slide-patterns.md`
- **실습**: `/generate-slides` 스킬로 프로젝트 생성

### Module 5: Manim CE 모드 (전문)
- Scene Contract, 2-pass duration control
- Alignment 검증 3가지 안티패턴
- **읽을 파일**: Section 7, `prompts/manim_scene_generation.txt`

### Module 6: 스킬 시스템 아키텍처 (설계)
- 인덱스 + 서브파일 패턴
- Command vs Skill 차이
- Agent Dispatch 병렬화
- **읽을 파일**: Section 9, `.claude/commands/generate-slides.md`

### Module 7: 전체 통합 (종합)
- 파이프라인 내 위치 (7단계 중 2~3)
- 파일 재사용 로직
- 트러블슈팅
- **읽을 파일**: Section 8, 12
