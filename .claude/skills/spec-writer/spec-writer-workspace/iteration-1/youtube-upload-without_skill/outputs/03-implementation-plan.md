# YouTube 업로드 기능 -- 구현 계획

## 1. 구현 순서 (의존성 기반)

하위 레이어부터 상위 레이어 순서로 구현한다.
각 단계에서 검증 가능한 체크포인트를 설정한다.

```
Phase 1: 기반 (shared + entities)
  -> Phase 2: 핵심 로직 (features)
    -> Phase 3: CLI 통합 (app)
      -> Phase 4: 파이프라인 통합 (pipelines)
        -> Phase 5: 테스트 + 문서
```


## 2. Phase 1: 기반 레이어 (shared + entities)

### 2.1 OAuth 인증 설정

**파일**: `config/credentials/` 디렉토리 확인 + `.gitignore` 확인

- [ ] `config/credentials/` 디렉토리가 이미 존재함을 확인
- [ ] `.gitignore`에 `config/credentials/*.json` 패턴 추가 (없는 경우)
- [ ] `.env.example`에 YouTube 관련 설정 안내 주석 추가 (OAuth는 파일 기반이므로 환경변수 불필요)

### 2.2 `shared/config/schema.py` 수정

- [ ] `YoutubeUploadConfig` 모델 추가
  - `credentials_dir: str = "config/credentials"`
  - `default_privacy: str = "private"`
  - `default_category: str = "28"`
  - `chunk_size_mb: int = 5`
  - `metadata_model: str = "gpt-5.4-mini"`
- [ ] `YoutubeConfig`에 `upload: YoutubeUploadConfig` 필드 추가

**검증**: `pytest tests/shared/` 통과 확인

### 2.3 `shared/api/youtube.py` 신규 작성

- [ ] `get_youtube_service()` -- OAuth 인증 + 서비스 객체 생성
  - `google-auth-oauthlib`의 `InstalledAppFlow` 사용
  - `token.json` 캐싱 + 자동 갱신
- [ ] `upload_video_resumable()` -- Resumable Upload
  - `googleapiclient.http.MediaFileUpload` 사용
  - `chunksize` 파라미터로 청크 크기 지정
  - `next_chunk()` 루프로 진행률 콜백 호출
  - 재시도 로직: `HttpError` 5xx -> 지수 백오프 (최대 3회)
- [ ] `set_thumbnail()` -- 썸네일 업로드
  - `service.thumbnails().set()` 호출
- [ ] `update_video_status()` -- 공개 상태 변경
  - `service.videos().update()` 호출
  - `publishAt` 파라미터로 예약 공개 지원
- [ ] `YouTubeUploadError` 예외 클래스 정의

**검증**: `client_secrets.json` 없이 import만 되는지 확인 (런타임 에러는 OK)

### 2.4 `entities/video/model.py` 수정

- [ ] `VideoMetadata`에 `privacy_status: str = "private"` 필드 추가

**검증**: 기존 테스트 깨지지 않는지 확인


## 3. Phase 2: Feature 슬라이스 (features/upload_youtube/)

### 3.1 디렉토리 구조 생성

```
features/upload_youtube/
  __init__.py
  model.py
  api.py
  lib.py
```

### 3.2 `model.py`

- [ ] `UploadRequest` -- 업로드 요청 모델
- [ ] `UploadResult` -- 업로드 결과 모델
- [ ] `MetadataGenerationResult` -- GPT 생성 메타데이터

### 3.3 `lib.py`

- [ ] `generate_metadata()` -- GPT-5.4-mini로 메타데이터 자동 생성
  - `shared/api/claude.py::ask()` 호출
  - 시스템 프롬프트에 YouTube SEO 지침 포함
  - JSON 파싱 + 검증 (제목 100자, 설명 5000자, 태그 총 500자)
  - 실패 시 기본값 fallback (프로젝트명 기반)
- [ ] `validate_thumbnail()` -- 썸네일 검증/리사이즈
  - Pillow로 크기 확인 + JPEG/PNG 확인
  - 2MB 초과 시 품질 조절하여 리사이즈
  - 해상도 1280x720 아닌 경우 리사이즈
- [ ] `find_thumbnail()` -- 프로젝트 내 썸네일 자동 탐색
  - 탐색 순서: `output/thumbnail.{png,jpg}` -> `slides/001.png`
- [ ] `save_upload_result()` -- 결과 JSON 저장
  - 경로: `projects/{name}/output/youtube_upload.json`
- [ ] `load_upload_result()` -- 결과 JSON 로드

### 3.4 `api.py`

- [ ] `authenticate()` -- YouTube API 인증 (shared 위임)
- [ ] `upload()` -- 전체 업로드 워크플로우 오케스트레이션
  1. 인증
  2. 메타데이터 구성 (snippet + status)
  3. Resumable Upload 실행
  4. 썸네일 설정 (있는 경우)
  5. 결과 반환
- [ ] `publish()` -- 공개 전환
  1. 인증
  2. `update_video_status()` 호출
  3. 결과 확인

### 3.5 `__init__.py`

```python
from .api import authenticate as authenticate
from .api import publish as publish
from .api import upload as upload
from .lib import generate_metadata as generate_metadata
from .model import UploadRequest as UploadRequest
from .model import UploadResult as UploadResult
```

**검증**: `ruff check features/upload_youtube/` + `lint-imports` 통과


## 4. Phase 3: CLI 통합 (app/cli.py)

### 4.1 `youtube` 커맨드 그룹 추가

- [ ] `@cli.group() def youtube()` -- YouTube 커맨드 그룹
- [ ] `youtube upload` -- 영상 업로드
  - `--project` (필수): 프로젝트 이름
  - `--video` (선택): 영상 경로 (미지정 시 `output/final_video.mp4`)
  - `--generate-metadata/--no-generate-metadata` (기본 True)
  - `--title` (선택): 수동 제목 지정
  - `--thumbnail` (선택): 수동 썸네일 경로
- [ ] `youtube publish` -- 공개 전환
  - `--project` (필수)
  - `--schedule` (선택): ISO 8601 예약 시각
- [ ] `youtube generate-metadata` -- 메타데이터만 생성
  - `--project` (필수)
  - 생성 결과를 Rich Panel로 출력
- [ ] `youtube status` -- 업로드 상태 확인
  - `--project` (필수)
  - `youtube_upload.json`에서 정보 로드

### 4.2 Upload 커맨드 실행 흐름

```
1. Project 로드 + 영상 파일 확인
2. 썸네일 탐색 (find_thumbnail)
3. 메타데이터 생성 (generate_metadata 또는 수동 지정)
4. Rich Panel로 미리보기 출력 (제목, 설명, 태그)
5. 사용자 확인 프롬프트 (--yes 옵션으로 skip 가능)
6. upload() 호출 (Rich progress bar)
7. 결과 출력 + youtube_upload.json 저장
```

**검증**: `python -m app.cli youtube --help` 출력 확인


## 5. Phase 4: 파이프라인 통합

### 5.1 `pipelines/script_to_video/lib.py` 수정

- [ ] `run_script_to_video()` 함수에 `auto_upload: bool = False` 파라미터 추가
- [ ] `auto_upload=True`일 때 최종 단계 후 업로드 스텝 추가
  - 메타데이터 자동 생성
  - 비공개 업로드
  - 결과 저장

### 5.2 `app/cli.py` -- `pipeline script-to-video` 수정

- [ ] `--auto-upload` 플래그 추가
- [ ] 플래그 활성화 시 `run_script_to_video(auto_upload=True)` 호출

### 5.3 `shared/config/schema.py` -- PipelineConfig 확장

- [ ] `PipelineUploadControl` 모델 추가
  ```python
  class PipelineUploadControl(BaseModel):
      auto_upload: bool = False  # 파이프라인 완료 후 자동 업로드
  ```
- [ ] `PipelineConfig`에 `upload: PipelineUploadControl` 필드 추가

**검증**: 기존 `script-to-video` 파이프라인이 `--auto-upload` 없이 동일하게 동작


## 6. Phase 5: 테스트 + 문서

### 6.1 테스트 파일

```
tests/
  features/
    test_upload_youtube.py    -- lib.py 유닛 테스트
  shared/
    test_youtube_api.py       -- shared/api/youtube.py mock 테스트
```

### 6.2 테스트 항목

- [ ] `generate_metadata()` -- GPT 응답 파싱 정상 동작
- [ ] `generate_metadata()` -- GPT 응답 실패 시 fallback
- [ ] `validate_thumbnail()` -- 정상 이미지 통과
- [ ] `validate_thumbnail()` -- 2MB 초과 이미지 리사이즈
- [ ] `validate_thumbnail()` -- 잘못된 포맷 거부
- [ ] `find_thumbnail()` -- 탐색 순서 검증
- [ ] `save_upload_result()` / `load_upload_result()` -- JSON 직렬화/역직렬화
- [ ] OAuth 인증 mock -- `client_secrets.json` 없을 때 명확한 에러
- [ ] Resumable Upload mock -- 진행률 콜백 호출 검증
- [ ] CLI `youtube upload --help` 출력 검증

### 6.3 통합 테스트 (수동)

- [ ] 실제 `client_secrets.json`으로 OAuth 인증 성공
- [ ] 짧은 테스트 영상 비공개 업로드 성공
- [ ] 썸네일 설정 성공
- [ ] 비공개 -> 공개 전환 성공
- [ ] YouTube Studio에서 메타데이터 확인

### 6.4 config 파일 업데이트

- [ ] `config/config.base.yaml` -- youtube.upload 섹션 추가
- [ ] `config/config.api.yaml` -- 동일 (API 프로필도 업로드 가능)
- [ ] `.env.example` -- YouTube OAuth 안내 주석


## 7. 예상 작업량

| Phase | 예상 시간 | 파일 수 |
|-------|----------|---------|
| Phase 1: 기반 | 1-2시간 | 3 수정 + 1 신규 |
| Phase 2: Feature | 2-3시간 | 4 신규 |
| Phase 3: CLI | 1-2시간 | 1 수정 |
| Phase 4: 파이프라인 | 1시간 | 2 수정 |
| Phase 5: 테스트 | 2시간 | 2 신규 |
| **합계** | **7-10시간** | **7 신규 + 6 수정** |


## 8. 리스크 및 대응

| 리스크 | 영향 | 대응 |
|--------|------|------|
| YouTube API 할당량 초과 | 업로드 실패 | 할당량 확인 API 호출 추가, 에러 메시지에 남은 할당량 표시 |
| OAuth 토큰 만료 후 갱신 실패 | 인증 실패 | refresh token이 없으면 재인증 안내 메시지 |
| 대용량 영상 (>2GB) 업로드 타임아웃 | 업로드 중단 | Resumable Upload의 자동 재개 기능 활용 |
| GPT 메타데이터 생성 품질 불안정 | 부적절한 제목/태그 | JSON schema 강제 + 후처리 검증 + fallback |
| `client_secrets.json` 미설정 | 기능 자체 사용 불가 | 명확한 에러 메시지 + 설정 가이드 출력 |
