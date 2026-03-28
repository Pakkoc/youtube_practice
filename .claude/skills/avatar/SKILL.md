---
name: avatar
description: "Reference manual for Ditto avatar integration — batch clip generation, WSL2 subprocess handling, circular overlay with FFmpeg geq filter. Load when working with features/generate_avatar/ or ditto-talkinghead/."
user-invocable: false
---

# Avatar Manual

## Activation Conditions
- **Keywords**: avatar, 아바타, ditto, lip sync, 립싱크, talking head
- **Intent Patterns**: "아바타 생성", "아바타 오버레이", "Ditto 설정"
- **Working Files**: `features/generate_avatar/`, `ditto-talkinghead/`
- **Content Patterns**: `generate_avatar_clips`, `overlay_avatar_circular`, `AvatarClip`

## Chapters
1. [Ditto 통합](chapter-ditto-integration.md) -- 배치 모드, WSL2 subprocess, 원형 오버레이
