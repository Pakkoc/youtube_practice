# YouTube 업로드 기능 -- 파일 변경 요약

## 신규 파일 (7개)

| 파일 | 레이어 | 역할 |
|------|--------|------|
| `shared/api/youtube.py` | shared | YouTube Data API v3 클라이언트 (OAuth, Upload, Status) |
| `features/upload_youtube/__init__.py` | features | Public API export |
| `features/upload_youtube/model.py` | features | UploadRequest, UploadResult, MetadataGenerationResult |
| `features/upload_youtube/api.py` | features | 업로드/공개전환 오케스트레이션 |
| `features/upload_youtube/lib.py` | features | 메타데이터 생성, 썸네일 검증, 결과 저장 |
| `tests/features/test_upload_youtube.py` | tests | Feature 유닛 테스트 |
| `tests/shared/test_youtube_api.py` | tests | API 클라이언트 mock 테스트 |


## 수정 파일 (6개)

| 파일 | 변경 내용 |
|------|----------|
| `shared/config/schema.py` | `YoutubeUploadConfig` 추가, `YoutubeConfig`에 `upload` 필드 추가, `PipelineUploadControl` 추가, `PipelineConfig`에 `upload` 필드 추가 |
| `entities/video/model.py` | `VideoMetadata`에 `privacy_status` 필드 추가 |
| `entities/project/model.py` | `youtube_upload_path` 프로퍼티 추가 |
| `app/cli.py` | `youtube` 커맨드 그룹 추가 (upload, publish, generate-metadata, status) |
| `pipelines/script_to_video/lib.py` | `auto_upload` 파라미터 추가, 업로드 스텝 추가 |
| `config/config.base.yaml` | `youtube.upload` 섹션 추가, `pipeline.upload` 섹션 추가 |


## 설정/환경 파일 변경 (3개)

| 파일 | 변경 내용 |
|------|----------|
| `.env.example` | YouTube OAuth 안내 주석 추가 |
| `.gitignore` | `config/credentials/*.json` 패턴 추가 확인 |
| `config/config.api.yaml` | `youtube.upload` 섹션 추가 (base.yaml과 동일) |


## 의존성 변경

없음. `google-api-python-client`와 `google-auth-oauthlib`는 `pyproject.toml`에 이미 포함되어 있다.

```toml
# pyproject.toml (기존, 변경 불필요)
"google-api-python-client>=2.160.0",
"google-auth-oauthlib>=1.2.0",
```


## FSD Import 방향 검증

```
app/cli.py
  -> features.upload_youtube     [app -> features]     OK
  -> entities.project.model      [app -> entities]     OK

features/upload_youtube/api.py
  -> shared.api.youtube          [features -> shared]  OK

features/upload_youtube/lib.py
  -> shared.api.claude           [features -> shared]  OK
  -> entities.project.model      [features -> entities] OK
  -> entities.video.model        [features -> entities] OK

pipelines/script_to_video/lib.py
  -> features.upload_youtube     [pipelines -> features] OK

shared/api/youtube.py
  -> (외부 패키지만)             [shared: 하위 없음]   OK
```

역방향 import 없음. `lint-imports` 통과 예상.


## 변경 영향 범위

### 영향 없는 영역
- TTS 파이프라인
- 슬라이드 생성
- B-roll 생성
- 자막 생성/합성
- 쇼츠 파이프라인
- 카루셀 파이프라인

### 영향 있는 영역
- `script-to-video` 파이프라인: `--auto-upload` 플래그 추가 (기존 동작 변경 없음)
- `YoutubeConfig`: `upload` 필드 추가 (Pydantic default이므로 기존 YAML과 호환)
- `PipelineConfig`: `upload` 필드 추가 (동일)
- `VideoMetadata`: `privacy_status` 필드 추가 (기본값 있으므로 호환)

### 하위 호환성
모든 신규 필드에 기본값이 있으므로, 기존 config YAML 파일이나 코드에서
새 필드를 명시하지 않아도 정상 동작한다.
