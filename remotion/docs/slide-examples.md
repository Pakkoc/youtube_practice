# Slide Examples

> 10개 complete TSX 예제. Content type에 맞는 2-3개만 선택적으로 읽을 것.
> 모든 예제는 tsx-contract.md 규칙 100% 준수, 한국어 텍스트 사용.
> 각 예제는 서로 다른 entry motif + spring preset 사용.

---

## Content Type → Example 라우팅

| Content Type | Example File | 주요 기법 | Spring |
|-------------|-------------|-----------|--------|
| 도입/히어로 | [hero-intro.md](slide-examples/hero-intro.md) | charSplit, CameraTilt, AmbientParticles | GENTLE |
| 데이터/차트 | [data-bar-chart.md](slide-examples/data-bar-chart.md) | drawBar, countUpProgress, staggerDelays | SNAPPY |
| 비교/대비 | [comparison-split.md](slide-examples/comparison-split.md) | insetReveal, colorShift, scaleOut | STIFF |
| 타임라인/과정 | [timeline-process.md](slide-examples/timeline-process.md) | cascadeUp, drawLine, svgStrokeDraw | varied |
| 인용/텍스트 | [text-quote.md](slide-examples/text-quote.md) | wordStagger, glassCardOpacity, shimmer | GENTLE |
| 플로우 다이어그램 | [diagram-flow.md](slide-examples/diagram-flow.md) | circleReveal, scaleIn, orbit | varied |
| 숫자/통계 | [statistic-number.md](slide-examples/statistic-number.md) | blurReveal, countUpProgress, pulse | BOUNCY |
| 감성/서사 | [emotional-narrative.md](slide-examples/emotional-narrative.md) | blurReveal+blurOut, CameraMotion, GradientShift | GENTLE |
| 카테고리/그리드 | [icon-grid.md](slide-examples/icon-grid.md) | layeredReveal, float, shimmer | energetic |
| 튜토리얼/단계 | [step-tutorial.md](slide-examples/step-tutorial.md) | cascadeUp, diagonalWipe, CameraPan, penStroke | SNAPPY |

## Decision Flowchart

```
문단 분석:

인트로/오프닝/히어로?              → hero-intro
숫자/퍼센트/통계 강조?             → statistic-number
바 차트/순위/비교 수치?            → data-bar-chart
A vs B 비교/대비?                  → comparison-split
시간순/단계/과정?                  → timeline-process
인용문/핵심 메시지?                → text-quote
아키텍처/데이터 흐름?             → diagram-flow
감성/스토리/극적 전환?            → emotional-narrative
카테고리 나열/아이콘 그리드?      → icon-grid
튜토리얼/설정 방법/단계별 가이드? → step-tutorial
```

> **조합**: 2개 이상 예제의 기법을 조합할 수 있음. 예: statistic-number의 countUp + data-bar-chart의 drawBar.
