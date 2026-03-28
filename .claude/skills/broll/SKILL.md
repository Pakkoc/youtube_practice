---
name: broll
description: "Reference manual for B-roll image generation — paragraph-based 1:1:1 mapping, source decision (generate vs search), and 4 image backends (FLUX.2 Klein, Flux Kontext, NanoBanana, SerperDev). Load when working with features/analyze_broll/ or features/fetch_broll/."
user-invocable: false
---

# B-roll Manual

## Activation Conditions
- **Keywords**: broll, b-roll, 비롤, 이미지 생성, flux, kontext, nanobanana, 배경 이미지
- **Intent Patterns**: "B-roll 수정", "이미지 백엔드 변경", "B-roll 재생성"
- **Working Files**: `features/analyze_broll/`, `features/fetch_broll/`
- **Content Patterns**: `generate_paragraph_broll_plan`, `fetch_broll_image`, `BrollPlan`, `BrollItem`

## Chapters
1. [아키텍처](chapter-architecture.md) -- 1:1:1 매핑, 컨텍스트 윈도우, 소스 결정
2. [백엔드](chapter-backends.md) -- 4개 이미지 생성 백엔드, 프롬프트 템플릿
3. [프롬프트 생성 워크플로](chapter-prompt-workflow.md) -- Claude Code가 직접 수행하는 scene grouping + source decision + prompt enhancement
