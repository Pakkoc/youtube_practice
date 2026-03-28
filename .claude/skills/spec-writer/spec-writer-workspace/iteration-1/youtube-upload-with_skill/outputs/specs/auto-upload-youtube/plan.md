# auto-upload-youtube 구현 계획

## 기술 스택

- **YouTube Data API v3**: `google-api-python-client` -- 영상 업로드, 메타데이터 설정, 공개 상태 변경
- **OAuth2 인증**: `google-auth-oauthlib` -- 브라우저 기반 최초 인증, `google-auth` -- 토큰 자동 갱신
- **Resumable Upload**: `MediaFileUpload` (chunksize 기반) -- 대용량 파일 안정적 업로드 + 진행률 추적
- **메타데이터 자동 생성**: `shared.api.claude.ask()` (GPT-5) -- script.txt 기반 제목/설명/태그 생성
- **CLI**: Click -- `youtube upload`, `youtube publish`, `youtube status` 서브커맨드
- **설정**: Pydantic `YoutubeUploadConfig` -- credentials 경로, 기본 카테고리, 기본 언어

## 파일 구조 계획

### 신규 생성

- `shared/api/youtube.py` -- YouTube API 클라이언트 (인증, 서비스 객체 생성, 업로드, 상태 변경)
- `features/upload_youtube/__init__.py` -- public export
- `features/upload_youtube/api.py` -- `upload_video()`, `publish_video()`, `get_upload_status()` 공개 함수
- `features/upload_youtube/lib.py` -- 내부 헬퍼 (결과 파일 저장/로드, 썸네일 탐색, 메타데이터 조합)
- `features/upload_youtube/model.py` -- `UploadRequest`, `UploadResult` Pydantic 모델
- `features/generate_metadata/__init__.py` -- public export
- `features/generate_metadata/api.py` -- `generate_video_metadata()` 공개 함수
- `features/generate_metadata/lib.py` -- GPT-5 프롬프트 구성, 응답 파싱
- `credentials/.gitignore` -- OAuth 토큰/시크릿 파일 git 제외

### 수정

- `shared/config/schema.py` -- `YoutubeConfig`에 `YoutubeUploadConfig` 필드 추가 (credentials_dir, default_language, auto_generate_metadata 등)
- `entities/video/model.py` -- `UploadStatus` enum, `UploadResult` 모델 추가 (또는 features에서 관리)
- `app/cli.py` -- `youtube` 커맨드 그룹 + `upload`, `publish`, `status` 서브커맨드 추가
- `pyproject.toml` -- `google-api-python-client`, `google-auth-oauthlib` 의존성 추가

## 작업 분해

| # | TODO | 위험도 | 요구사항 |
|---|------|--------|----------|
| 1 | `pyproject.toml`에 Google API 패키지 의존성 추가 + `uv sync` | LOW | REQ-01 |
| 2 | `credentials/` 디렉토리 구조 + `.gitignore` 설정 | LOW | REQ-N02 |
| 3 | `shared/api/youtube.py` -- OAuth2 인증 플로우 구현 (첫 인증: 브라우저 플로우, 이후: 토큰 갱신) | HIGH | REQ-06 |
| 4 | `shared/api/youtube.py` -- Resumable Upload 구현 (`videos().insert()` + `MediaFileUpload`) | HIGH | REQ-01, REQ-03 |
| 5 | `shared/api/youtube.py` -- 썸네일 업로드 (`thumbnails().set()`) | MEDIUM | REQ-07 |
| 6 | `shared/api/youtube.py` -- 공개 상태 변경 (`videos().update()` + `status.privacyStatus`) | MEDIUM | REQ-04 |
| 7 | `features/upload_youtube/model.py` -- `UploadRequest`, `UploadResult` 모델 정의 | LOW | REQ-05 |
| 8 | `features/generate_metadata/lib.py` -- GPT-5 프롬프트로 제목/설명/태그 자동 생성 | MEDIUM | REQ-08 |
| 9 | `features/generate_metadata/api.py` -- `generate_video_metadata()` 공개 API | LOW | REQ-08 |
| 10 | `features/upload_youtube/lib.py` -- 썸네일 탐색, 결과 파일 저장/로드 헬퍼 | LOW | REQ-05, REQ-07 |
| 11 | `features/upload_youtube/api.py` -- `upload_video()` 오케스트레이션 (메타데이터 생성 -> 업로드 -> 썸네일 -> 결과 저장) | MEDIUM | REQ-01~REQ-08 |
| 12 | `features/upload_youtube/api.py` -- `publish_video()` 공개 전환 | LOW | REQ-04 |
| 13 | `shared/config/schema.py` -- `YoutubeUploadConfig` 추가, `YoutubeConfig` 필드 확장 | LOW | REQ-06 |
| 14 | `app/cli.py` -- `youtube upload`, `youtube publish`, `youtube status` CLI 커맨드 | MEDIUM | REQ-01~REQ-05 |
| 15 | `tests/features/test_upload_youtube.py` -- 단위 테스트 (mock API) | MEDIUM | 전체 |
| 16 | `tests/shared/test_youtube_api.py` -- YouTube API 클라이언트 단위 테스트 (mock) | MEDIUM | REQ-01, REQ-06 |

## 위험 분석

| 위험 | 영향 | 완화 전략 |
|------|------|-----------|
| **OAuth2 첫 인증 실패** -- 브라우저 플로우가 headless/WSL 환경에서 동작하지 않을 수 있음 | HIGH | `InstalledAppFlow`의 `run_local_server()` 사용. 실패 시 `run_console()` 폴백 제공. 인증 가이드 문서화. |
| **YouTube API quota 초과** -- 일일 10,000 유닛, 업로드 1건 = 1,600 유닛 | HIGH | 업로드 전 quota 잔여량 확인은 API로 불가 -> CLI에 일일 업로드 횟수 경고 표시. `upload_result.json`에 타임스탬프 기록하여 일일 업로드 수 추적. |
| **토큰 만료 및 갱신 실패** -- refresh token이 revoke되거나 만료됨 | MEDIUM | `google.auth.transport.requests.Request()`로 자동 갱신 시도. 실패 시 재인증 플로우 안내 메시지 출력. |
| **대용량 파일 업로드 중 네트워크 단절** -- 업로드가 중간에 끊김 | MEDIUM | `MediaFileUpload(resumable=True)`로 chunk 단위 업로드. 실패 시 `next_chunk()`로 이어서 업로드. 최대 3회 재시도. |
| **썸네일 업로드 권한 부족** -- YouTube Partner Program 미가입 채널 | LOW | 썸네일 업로드 실패 시 경고만 출력하고 영상 업로드 자체는 완료 처리. `UploadResult.thumbnail_set` 필드로 결과 기록. |
| **메타데이터 자동 생성 품질 저하** -- GPT-5가 부적절한 제목/태그 생성 | MEDIUM | 사전 정의된 `metadata.json`이 있으면 우선 사용. 자동 생성은 폴백. `upload_result.json`에 사용된 메타데이터 기록하여 사후 확인 가능. |
| **Google Cloud 프로젝트 OAuth consent screen 설정 누락** | HIGH | 첫 사용 시 필요한 GCP 설정 단계를 CLI `youtube setup` 커맨드 또는 에러 메시지에서 상세 안내. |

## 의존성 분석

### 기존 코드 영향 범위

- `shared/config/schema.py`: `YoutubeConfig` 클래스에 필드 추가 -- 기존 config 로딩에 영향 없음 (Pydantic default 값 제공)
- `entities/video/model.py`: `VideoMetadata` 클래스는 이미 존재. 그대로 활용하고 `UploadResult`만 추가.
- `app/cli.py`: `youtube` 커맨드 그룹 신규 추가 -- 기존 `pipeline`, `tts`, `subtitles` 그룹에 영향 없음.

### FSD import 규칙 준수 확인 포인트

- `features/upload_youtube/` -> `shared/api/youtube.py` (OK: features -> shared)
- `features/upload_youtube/` -> `entities/video/model.py` (OK: features -> entities)
- `features/generate_metadata/` -> `shared/api/claude.py` (OK: features -> shared)
- `features/upload_youtube/` -> `features/generate_metadata/` (주의: features 간 import는 허용되지만, 순환 의존 금지. `upload_youtube`가 `generate_metadata`를 단방향 참조.)
- `app/cli.py` -> `features/upload_youtube/` (OK: app -> features)
