# 파이프라인 오버라이드

> 소스: `app/config.py` → `apply_pipeline_overrides()`

## 오버라이드 우선순위 (높은 것이 이김)

```
1. config.{profile}.yaml의 세부 값 (기본)
2. pipeline.* 섹션 값 (덮어씀)
3. 환경변수 오버라이드 (최우선)
```

## `pipeline.*` → 세부 config 매핑

| pipeline 설정 | 덮어쓰는 대상 | 매핑 규칙 |
|---------------|---------------|-----------|
| `pipeline.slides.backend: "api"` | `slides.backend` | `"api"` → `"marp"` |
| `pipeline.slides.backend: "remotion"` | `slides.backend` | `"remotion"` → `"remotion"` |
| `pipeline.slides.backend: "remotion-ai"` | `slides.backend` | `"remotion-ai"` → `"remotion"` |
| `pipeline.broll.enabled` | `broll` 관련 | 전체 B-roll on/off |
| `pipeline.broll.image_gen_backend: "nanobanana"` | `broll.force_backend` | `"nanobanana"` 설정 |
| `pipeline.broll.image_gen_backend: "local"` | `broll.force_backend` | 기존 값 유지 |
| `pipeline.avatar.enabled` | `avatar.enabled` | 직접 동기화 |
| `pipeline.tts.backend` | TTS 백엔드 | `"elevenlabs"` / `"local"` |

## 환경변수 오버라이드

`_apply_env_overrides()` 에서 처리:

| 환경변수 | 대상 | 예시 |
|----------|------|------|
| `ENABLE_AVATAR` | `pipeline.avatar.enabled` | `ENABLE_AVATAR=false` |
| `ENABLE_BROLL` | `pipeline.broll.enabled` | `ENABLE_BROLL=false` |
| `IMAGE_GEN_BACKEND` | `pipeline.broll.image_gen_backend` | `IMAGE_GEN_BACKEND=nanobanana` |
| `SLIDES_BACKEND` | `pipeline.slides.backend` | `SLIDES_BACKEND=remotion` |
| `CONFIG_PROFILE` | 프로필 자체 변경 | `CONFIG_PROFILE=api` |

## 함정 주의

### slides 백엔드 변경
```yaml
# WRONG - pipeline이 덮어써서 무시됨
slides:
  backend: "remotion"

# CORRECT - pipeline 섹션에서 변경해야 함
pipeline:
  slides:
    backend: "remotion"
```

### B-roll 백엔드와 force_backend
```yaml
# "nanobanana"이면 force_backend를 덮어씀
pipeline:
  broll:
    image_gen_backend: "nanobanana"  # → force_backend: "nanobanana"

# "local"이면 기존 force_backend 유지 (flux2_klein, flux_kontext 등)
pipeline:
  broll:
    image_gen_backend: "local"  # → force_backend 변경 없음
```

### Remotion-AI 모드
- `pipeline.slides.backend: "remotion-ai"` → 실제로는 `slides.backend: "remotion"`으로 매핑
- `/generate-slides` 스킬로 TSX 생성 후 파이프라인 실행하는 2단계 워크플로
