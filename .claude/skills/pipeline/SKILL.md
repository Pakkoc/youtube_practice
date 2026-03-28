---
name: pipeline
description: "Reference manual for the 4 video automation pipelines (script-to-video, video-to-shorts, script-to-carousel, add-subtitles). Covers 7-step flow, parallel processing, output chain, and file reuse logic. Load when working with pipelines/, discussing pipeline steps, or debugging video generation."
user-invocable: false
---

# Pipeline Manual

## Activation Conditions
- **Keywords**: pipeline, script-to-video, video-to-shorts, carousel, add-subtitles, 파이프라인, 영상 생성
- **Intent Patterns**: "영상 만들어줘", "파이프라인 실행", "쇼츠 만들어줘", "카루셀 생성"
- **Working Files**: `pipelines/*/lib.py`, `pipelines/*/cli.py`
- **Content Patterns**: `run_script_to_video`, `run_video_to_shorts`, `run_script_to_carousel`

## Chapters
1. [script-to-video 7단계](chapter-script-to-video.md) -- 메인 파이프라인 전체 흐름, 병렬 처리, 출력 체인
2. [기타 파이프라인](chapter-other-pipelines.md) -- video-to-shorts, script-to-carousel, add-subtitles
3. [파일 재사용 로직](chapter-file-reuse.md) -- 아티팩트 캐싱과 재사용 조건
4. [video-to-shorts 워크플로](chapter-video-to-shorts.md) -- 외부 영상 → 쇼츠 (Whisper + 바이럴 구간 선정 + 캡션)

## Utility Scripts
- `scripts/regenerate_slides.py <project>` — TSX/Manim → MP4
- `scripts/regenerate_broll.py <project>` — B-roll만 재생성
- `scripts/regenerate_carousel.py <project> [--force]`
- `scripts/continue_pipeline.py <project>` — Step 3부터 재실행
- `scripts/recompose_video.py <project>` — 중간 아티팩트로 재합성
