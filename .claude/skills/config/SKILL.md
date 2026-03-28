---
name: config
description: "Reference manual for the config profile system, Pydantic schema, pipeline overrides, and environment variable precedence. Load when modifying config files, debugging config loading, or changing pipeline backend settings."
user-invocable: false
---

# Config System Manual

## Activation Conditions
- **Keywords**: config, 설정, profile, yaml, override, 프로필, 환경변수
- **Intent Patterns**: "설정 변경", "config 수정", "프로필 전환", "환경변수 설정"
- **Working Files**: `app/config.py`, `shared/config/schema.py`, `config/config.*.yaml`
- **Content Patterns**: `get_config()`, `AppConfig`, `apply_pipeline_overrides`, `CONFIG_PROFILE`

## Chapters
1. [프로필 시스템](chapter-profile-system.md) -- 프로필 로딩, Pydantic 스키마, 싱글턴 패턴
2. [파이프라인 오버라이드](chapter-pipeline-overrides.md) -- 오버라이드 우선순위, 환경변수, 함정 주의
