# Remotion Skills 아키텍처 가이드

> Claude Code의 `/slash-commands`(Skills)가 어떻게 TSX 슬라이드와 카루셀 카드를 생성하는지 설명합니다.

---

## 1. 전체 구조: 두 가지 모드

```mermaid
flowchart TB
    subgraph Traditional["기존 방식: Template 모드"]
        A1[script.txt] --> B1["GPT-5-mini API"]
        B1 --> C1["JSON props\n(template + data)"]
        C1 --> D1["11개 고정 템플릿\n(BulletList, BigNumber...)"]
        D1 --> E1[MP4 슬라이드]
    end

    subgraph Modern["현재 방식: Remotion-AI 모드 (Skills)"]
        A2[script.txt] --> B2["Claude Code\n(/generate-slides)"]
        B2 --> C2["커스텀 TSX 코드\n(SVG, 차트, 다이어그램)"]
        C2 --> D2["Freeform 컴포넌트\n(제약 없는 자유 레이아웃)"]
        D2 --> E2[MP4 슬라이드]
    end

    style Traditional fill:#1a1a2e,stroke:#555,color:#999
    style Modern fill:#0d1b2a,stroke:#7C7FD9,color:#fff
```

**핵심 차이**: Template 모드는 AI가 "어떤 템플릿을 쓸지" JSON으로 결정하고, Remotion-AI 모드는 Claude Code가 **TSX 코드 자체를 작성**합니다.

---

## 2. Skills(슬래시 커맨드) 목록

```mermaid
flowchart LR
    subgraph Skills[".claude/commands/"]
        S1["/generate-video\n(E2E 전체)"]
        S2["/generate-slides\n(TSX 슬라이드)"]
        S3["/generate-carousel\n(카드뉴스 TSX)"]
        S4["/generate-shorts\n(바이럴 쇼츠)"]
        S5["/review-carousel\n(시각 검수)"]
    end

    S1 -->|"내부적으로 호출"| S2
    S1 -->|"+ TTS + 렌더링 + 자막"| Pipeline

    S2 --> TSX["slides/001.tsx ~ NNN.tsx"]
    S3 --> CARD["carousel/card_001.tsx ~ NNN.tsx"]

    TSX --> MP4[MP4 영상]
    CARD --> PNG[PNG 이미지]
```

| Skill | 입력 | 출력 | 용도 |
|-------|------|------|------|
| `/generate-video` | script.txt | final_video.mp4 | E2E 영상 (TSX + TTS + 렌더링 + 자막) |
| `/generate-slides` | paragraphs/*.txt | slides/*.tsx | 영상용 TSX 슬라이드 |
| `/generate-carousel` | script.txt | carousel/card_*.tsx | 인스타 카드뉴스용 TSX |
| `/generate-shorts` | 영상 파일 | 쇼츠 클립 | 바이럴 구간 추출 |

---

## 3. `/generate-slides` 상세 흐름

가장 핵심인 TSX 슬라이드 생성 과정입니다.

```mermaid
flowchart TD
    START(["/generate-slides 003"]) --> READ

    subgraph Step1["Step 1: 데이터 읽기"]
        READ["paragraphs/*.txt 전체 읽기\n(문단 = 씬 = 슬라이드)"]
    end

    subgraph Step2["Step 2: Art Direction"]
        READ --> ANALYZE["대본 분석"]
        ANALYZE --> ART["Content type: Tutorial/Comparison/...\nVisual anchor: 반복 시각 요소\nColor strategy: ACCENT/TEAL 역할"]
    end

    subgraph Step3["Step 3: Slide Table 설계"]
        ART --> TABLE["| # | Content | Layout | Key Visual | Intensity |\n|1| 매출 1억 | big-number | 경고 아이콘 | high |\n|2| AI 프리랜서 | icon-grid | 3종 아이콘 | medium |\n|...| ... | ... | ... | ... |"]
        TABLE --> CHECK{"품질 검증\n- 같은 레이아웃 3회 초과?\n- 연속 3개 동일?\n- 모든 슬라이드에 SVG?"}
        CHECK -->|"Fail"| TABLE
        CHECK -->|"Pass"| DISPATCH
    end

    subgraph Step4["Step 4: 병렬 에이전트 TSX 작성"]
        DISPATCH["슬라이드 수에 따라 배치 분할"]
        DISPATCH --> AG1["Agent 1\nSlides 1-5"]
        DISPATCH --> AG2["Agent 2\nSlides 6-9"]
        AG1 --> TSX1["001.tsx ~ 005.tsx"]
        AG2 --> TSX2["006.tsx ~ 009.tsx"]
    end

    subgraph Step5["Step 5: 검증"]
        TSX1 --> VALIDATE["TypeScript 검증\ncp NNN.tsx → Freeform.tsx\nnpx tsc --noEmit"]
        TSX2 --> VALIDATE
    end

    VALIDATE --> DONE([slides/001.tsx ~ 009.tsx 완성])
```

---

## 4. 병렬 에이전트 디스패치

Claude Code가 여러 에이전트를 동시에 실행하여 TSX를 병렬 작성합니다.

```mermaid
flowchart LR
    MAIN["Claude Code\n(메인 에이전트)"]

    MAIN -->|"Slide Table\n+ Art Direction\n+ Pattern Library\n+ Component Contract"| AG1
    MAIN -->|"동일 컨텍스트\n+ 담당 슬라이드 번호"| AG2

    subgraph Parallel["동시 실행 (Task tool)"]
        AG1["Agent 1\n(general-purpose)\nSlides 1~5 담당"]
        AG2["Agent 2\n(general-purpose)\nSlides 6~9 담당"]
    end

    AG1 -->|"각 paragraph 읽고\nTSX 코드 작성"| F1["001.tsx\n002.tsx\n003.tsx\n004.tsx\n005.tsx"]
    AG2 -->|"각 paragraph 읽고\nTSX 코드 작성"| F2["006.tsx\n007.tsx\n008.tsx\n009.tsx"]
```

**배치 사이징 규칙:**

| 슬라이드 수 | 배치 수 | 이유 |
|------------|--------|------|
| 1~6 | 1 (순차) | 에이전트 오버헤드 > 이득 |
| 7~12 | 2 | 2개 에이전트 병렬 |
| 13~18 | 3 | 3개 에이전트 병렬 |
| 19+ | 4 | 최대 4개 병렬 |

**각 에이전트에게 전달되는 정보:**
1. 전체 Slide Table (자기 담당 표시)
2. Art Direction 요약
3. 디자인 철학 핵심 원칙
4. 해당 레이아웃의 패턴 코드 (`slide-patterns.md`에서 발췌)
5. TSX Component Contract (필수 구조)
6. 출력 경로

---

## 5. TSX Component Contract

모든 TSX 슬라이드가 반드시 따라야 하는 구조입니다.

```mermaid
flowchart TD
    subgraph TSX["Freeform.tsx 구조"]
        ROOT["<AbsoluteFill>"]
        ROOT --> BG["<AnimatedBackground />\n(항상 첫 번째)"]
        ROOT --> CONTENT["<AbsoluteFill style=padding>\n커스텀 콘텐츠\n(SVG, 차트, 다이어그램 등)"]
        ROOT --> PROGRESS["<ProgressBar />\n(항상 마지막)"]
        ROOT --> FADE["<SceneFade />\n(항상 마지막)"]
    end

    subgraph Imports["사용 가능한 도구들"]
        I1["entries: fadeSlideIn, cascadeUp,\nbounceIn, zoomPop ..."]
        I2["emphasis: highlighter,\ncountUpProgress, pulse ..."]
        I3["decorations: glassCardOpacity,\ndrawBar, svgStrokeDraw ..."]
        I4["springConfigs: SPRING_GENTLE,\nSPRING_BOUNCY, pickSpring ..."]
    end

    subgraph Rules["절대 규칙"]
        R1["export const Freeform"]
        R2["useFonts() 필수"]
        R3["CSS transition 금지\nspring/interpolate만"]
        R4["Math.random() 금지"]
        R5["하단 360px 비움\n(자막 영역)"]
    end
```

---

## 6. 패턴 라이브러리 체계

에이전트들이 참고하는 디자인 레퍼런스입니다.

```mermaid
flowchart TD
    subgraph Docs["remotion/docs/ (패턴 라이브러리)"]
        SP["slide-patterns.md\n모션 패턴 + 공유 헬퍼\n(~255줄)"]
        SI["slide-icons.md\nSVG 아이콘 28개\nstrokeDasharray 가이드"]
        SL["slide-layouts.md\n인덱스 → 4개 서브파일\n(diagrams/mockups/metaphors/extras)"]
        CP["carousel-patterns.md\n카루셀 전용 레이아웃 9종\n(~1047줄)"]
    end

    subgraph Slides["영상 슬라이드 (/generate-slides)"]
        SP --> AGENT_S["에이전트에게\n해당 레이아웃 패턴만 발췌 전달"]
        SI --> AGENT_S
        SL --> AGENT_S
    end

    subgraph Carousel["카루셀 카드 (/generate-carousel)"]
        CP --> AGENT_C["에이전트에게\n해당 카드 타입 패턴만 발췌 전달"]
    end
```

---

## 7. TSX → 최종 영상 렌더링

TSX 파일이 생성된 후, MP4로 변환되는 과정입니다.

```mermaid
flowchart TD
    subgraph Input["생성된 파일들"]
        TSX["slides/001.tsx ~ 009.tsx"]
        WAV["audio/001.wav ~ 009.wav"]
    end

    subgraph Render["Remotion 렌더링 (4슬롯 병렬)"]
        TSX -->|"복사"| SLOT1["FreeformSlot1.tsx"]
        TSX -->|"복사"| SLOT2["FreeformSlot2.tsx"]
        TSX -->|"복사"| SLOT3["FreeformSlot3.tsx"]
        TSX -->|"복사"| SLOT4["FreeformSlot4.tsx"]

        WAV -->|"duration 계산\n→ durationInFrames"| PROPS["props.json\n{durationInFrames, slideIndex,\ntotalSlides, backgroundImage}"]

        SLOT1 --> CLI["npx remotion render"]
        SLOT2 --> CLI
        SLOT3 --> CLI
        SLOT4 --> CLI
        PROPS --> CLI

        CLI --> MP4S["slides/001.mp4 ~ 009.mp4"]
    end

    subgraph Compose["영상 합성"]
        MP4S --> CONCAT["FFmpeg concat\n→ video_raw.mp4"]
        CONCAT --> SUB["자막 생성 + 합성\n→ final_video.mp4"]
    end
```

**4슬롯 병렬 렌더링**: 각 슬롯(`FreeformSlot1~4.tsx`)은 독립된 Remotion Composition ID를 가져서 동시에 4개 슬라이드를 렌더링할 수 있습니다.

---

## 8. 슬라이드 vs 카루셀 비교

```mermaid
flowchart LR
    subgraph Video["영상 슬라이드"]
        direction TB
        V1["export const Freeform"]
        V2["1920 x 1080"]
        V3["spring() 애니메이션"]
        V4["MP4 출력"]
        V5["AnimatedBackground\n+ ProgressBar + SceneFade"]
    end

    subgraph Carousel["카루셀 카드"]
        direction TB
        C1["export const FreeformCard"]
        C2["1080 x 1350"]
        C3["애니메이션 없음 (정적)"]
        C4["PNG 출력"]
        C5["PageDots만\n(배경/페이드 없음)"]
    end
```

| | 영상 슬라이드 | 카루셀 카드 |
|---|---|---|
| **Skill** | `/generate-slides` | `/generate-carousel` |
| **Export** | `Freeform` | `FreeformCard` |
| **해상도** | 1920x1080 (16:9) | 1080x1350 (4:5) |
| **애니메이션** | spring(), interpolate() | 없음 (정적 이미지) |
| **출력** | .mp4 | .png |
| **렌더러** | `npx remotion render` | `npx remotion still` |
| **필수 래퍼** | AnimatedBackground + ProgressBar + SceneFade | PageDots만 |

---

## 9. E2E 흐름 (`/generate-video`)

전체 영상 생성을 하나의 커맨드로 실행합니다.

```mermaid
flowchart TD
    START(["/generate-video 003"]) --> S1

    subgraph S1["Step 1: 전처리"]
        SC["script.txt\n(날것의 대본)"]
        SC -->|"빈 줄 기준"| PARA["문단 분리\n(4개)"]
        PARA -->|"마침표 단위 분할\n30자 미만 병합"| SCENE["씬 분할\n(9개)"]
        SCENE -->|"paragraphs/ 덮어씀"| FINAL["paragraphs/001.txt ~ 009.txt"]
    end

    subgraph S2["Step 2: TTS"]
        FINAL -->|"ElevenLabs API"| AUDIO["audio/001.wav ~ 009.wav"]
    end

    subgraph S3["Step 3: TSX 생성 (/generate-slides)"]
        FINAL --> ART["Art Direction"]
        ART --> TABLE["Slide Table"]
        TABLE --> AGENTS["병렬 에이전트 TSX 작성"]
        AGENTS --> TSX["slides/001.tsx ~ 009.tsx"]
    end

    subgraph S4["Step 4: 파이프라인"]
        AUDIO --> PIPELINE
        TSX --> PIPELINE["script-to-video 파이프라인"]
        PIPELINE --> |"Remotion 렌더링\n+ FFmpeg 합성\n+ 자막 생성/합성"| VIDEO["output/final_video.mp4"]
    end

    style S3 stroke:#7C7FD9,stroke-width:2px
```

**Step 3이 핵심** — Claude Code가 직접 TSX 코드를 작성하므로 SVG 다이어그램, 커스텀 차트, UI 목업 등 **제약 없는 시각 표현**이 가능합니다. 기존 Template 모드의 11개 고정 레이아웃 제한을 완전히 벗어납니다.

---

## 10. 디자인 철학 요약

```mermaid
mindmap
  root((Remotion-AI\n디자인 철학))
    상보성
      나레이션 = "왜"
      슬라이드 = "무엇/얼마나"
      자막 복사 금지
    점진적 공개
      제목 → 0.3s → 아이콘 → 0.5s → 상세
      cascadeUp / stagger delay
      동시 fadeIn = AI 느낌
    비례 = 중요도
      강조점 1개만
      주요 요소 > 50% 화면
      보조 요소 = 작고 흐리게
    여백 = 임팩트
      30% 이상 의도적 비움
      정보 과밀 → 다음 슬라이드로
    Spring 다양성
      BOUNCY = 역동
      GENTLE = 차분
      SNAPPY = 정보 전달
      STIFF = 구조적
```
