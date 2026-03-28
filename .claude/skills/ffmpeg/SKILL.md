---
name: ffmpeg
description: "Reference manual for FFmpeg wrapper functions — concat, trim, slideshow composition, duration queries, and Windows path gotchas. Load when working with shared/lib/ffmpeg.py or debugging video processing."
user-invocable: false
---

# FFmpeg Manual

## Activation Conditions
- **Keywords**: ffmpeg, 영상 합성, concat, trim, overlay, 인코딩, 코덱
- **Intent Patterns**: "FFmpeg 명령", "영상 합치기", "영상 자르기", "영상 변환"
- **Working Files**: `shared/lib/ffmpeg.py`
- **Content Patterns**: `compose_video_slideshow`, `concat_videos`, `trim_video`, `get_duration`

## Chapters
1. [FFmpeg 함수 목록](chapter-ffmpeg-operations.md) -- 모든 FFmpeg 래퍼 함수와 Windows 주의사항
