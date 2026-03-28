# Config 프로필 시스템

> 소스: `app/config.py`, `shared/config/schema.py`

## 프로필 로딩 흐름

```
CONFIG_PROFILE 환경변수 (기본: "base")
  → config/config.{profile}.yaml 로드
    → _apply_env_overrides() (환경변수 오버라이드)
      → apply_pipeline_overrides() (pipeline.* → 세부 config 동기화)
        → _validate_config() (경고 출력)
          → 싱글턴 캐싱
```

## 핵심 함수

### `get_config(config_path=None) -> AppConfig`
- 싱글턴 패턴 (최초 호출 시 로드, 이후 캐시 반환)
- `config_path` 지정 시 해당 YAML 직접 로드
- `reload_config()` 으로 싱글턴 초기화 가능

### `_load_profile_config(profile) -> AppConfig`
- `config/config.{profile}.yaml` 로드
- 프로필 파일 없으면 "base"로 fallback

## 프로필 종류

| 프로필 | 파일 | 용도 |
|--------|------|------|
| `base` | `config.base.yaml` | 기본 (로컬 GPU) |
| `api` | `config.api.yaml` | GPU 없는 API-Only |
| `test` | `config.test.yaml` | 테스트용 |
| `prod` | `config.prod.yaml` | 프로덕션 |
| `elevenlabs` | `config.elevenlabs.yaml` | ElevenLabs TTS |

## Pydantic 스키마 (AppConfig)

`shared/config/schema.py`의 주요 서브 Config:

| Config | 핵심 필드 |
|--------|-----------|
| `TTSConfig` | `force_backend`, `model`, `speaker`, `language`, `CudaConfig`, `ElevenLabsConfig` |
| `SlidesConfig` | `backend`, `width`, `height`, `context_stride`, `RemotionSlidesConfig` |
| `BrollConfig` | `force_backend`, `Flux2KleinConfig`, `FluxKontextConfig`, `NanoBananaConfig`, `ImageSearchConfig` |
| `AvatarConfig` | `enabled`, `image_path`, `size`, `margin_y`, `ditto_project_path` |
| `SubtitlesConfig` | `font_size`, `max_chars_per_line`, `position`, `margin_v` |
| `PipelineConfig` | `tts`, `slides`, `broll`, `avatar` (마스터 컨트롤 패널) |
| `ShortsConfig` | `max_shorts`, `min_duration`, `max_duration`, `accent_color` |
| `CarouselConfig` | `max_cards`, `width`, `height`, `model` |

## 주의사항

- **기본 프로필은 `base`** -- `config.yaml`이 아닌 `config.base.yaml`을 로드함
- **`config.yaml`은 레거시** -- 파이프라인에서 사용되지 않음
- Config 변경 시 반드시 **활성 프로필 파일**을 수정할 것
