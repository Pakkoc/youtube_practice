# auto-upload-youtube 인수 기준

## 시나리오

### [REQ-01] YouTube 영상 업로드

**Scenario 1: 정상 업로드**
- **Given** `projects/my-video/output/final_video.mp4` 파일이 존재하고, OAuth2 인증 토큰이 유효한 상태
- **When** `uv run video-automation youtube upload --project my-video` 실행
- **Then** 영상이 YouTube에 비공개(private)로 업로드되고, `projects/my-video/output/upload_result.json`에 `video_id`, `url`, `status: "private"` 가 저장됨

**Scenario 2: 영상 파일 미존재**
- **Given** `projects/my-video/output/final_video.mp4` 파일이 존재하지 않는 상태
- **When** `uv run video-automation youtube upload --project my-video` 실행
- **Then** `FileNotFoundError` 메시지와 함께 "output 디렉토리에 final_video.mp4가 없습니다" 안내 후 종료

**Scenario 3: OAuth2 토큰 미설정**
- **Given** `credentials/youtube_token.json` 파일이 존재하지 않는 상태
- **When** `uv run video-automation youtube upload --project my-video` 실행
- **Then** "YouTube 인증이 필요합니다. `youtube auth`를 먼저 실행하세요" 메시지 출력 후 종료

### [REQ-02] 메타데이터 자동 생성

**Scenario 1: script.txt 기반 자동 생성**
- **Given** `projects/my-video/script.txt`가 존재하고, `projects/my-video/metadata.json`이 존재하지 않는 상태
- **When** 업로드 프로세스에서 메타데이터 생성 단계 실행
- **Then** GPT-5가 script.txt를 분석하여 `title`(60자 이내), `description`(5000자 이내), `tags`(최대 30개, 각 100자 이내)를 생성하고 `VideoMetadata` 객체를 반환

**Scenario 2: 사전 정의된 metadata.json 존재**
- **Given** `projects/my-video/metadata.json`이 `{"title": "...", "description": "...", "tags": [...]}`를 포함하는 상태
- **When** 업로드 프로세스에서 메타데이터 생성 단계 실행
- **Then** GPT-5 호출 없이 `metadata.json`의 값을 그대로 사용

### [REQ-03] 기본 비공개 업로드

**Scenario 1: 공개 상태 기본값**
- **Given** 업로드 요청에 `privacy_status` 지정이 없는 상태
- **When** 영상 업로드 API 호출
- **Then** YouTube `status.privacyStatus`가 `"private"`로 설정됨

### [REQ-04] 공개 전환

**Scenario 1: 비공개 -> 공개 전환**
- **Given** 영상이 비공개(private)로 업로드된 상태이고, `upload_result.json`에 `video_id`가 기록됨
- **When** `uv run video-automation youtube publish --project my-video --status public` 실행
- **Then** 해당 영상의 공개 상태가 `public`으로 변경되고, `upload_result.json`의 `status`가 `"public"`으로 업데이트됨

**Scenario 2: 존재하지 않는 video_id**
- **Given** `upload_result.json`이 없거나 `video_id`가 유효하지 않은 상태
- **When** `uv run video-automation youtube publish --project my-video --status public` 실행
- **Then** "업로드 기록을 찾을 수 없습니다. 먼저 업로드를 실행하세요" 에러 메시지 출력

**Scenario 3: 미리보기(unlisted) 전환**
- **Given** 영상이 비공개(private)로 업로드된 상태
- **When** `uv run video-automation youtube publish --project my-video --status unlisted` 실행
- **Then** 해당 영상의 공개 상태가 `unlisted`로 변경됨

### [REQ-05] 업로드 결과 저장

**Scenario 1: upload_result.json 형식**
- **Given** 업로드가 성공적으로 완료된 상태
- **When** 결과 저장 함수 호출
- **Then** `upload_result.json`에 아래 필드가 포함됨:
  ```json
  {
    "video_id": "abc123",
    "url": "https://youtu.be/abc123",
    "status": "private",
    "uploaded_at": "2026-03-26T12:00:00Z",
    "title": "...",
    "description": "...",
    "tags": ["..."],
    "thumbnail_set": true
  }
  ```

### [REQ-06] OAuth2 토큰 관리

**Scenario 1: 최초 인증**
- **Given** `credentials/client_secret.json`이 존재하고, `credentials/youtube_token.json`이 존재하지 않는 상태
- **When** `uv run video-automation youtube auth` 실행
- **Then** 브라우저가 열려 Google OAuth2 동의 화면이 표시되고, 사용자가 승인하면 `credentials/youtube_token.json`에 access_token + refresh_token이 저장됨

**Scenario 2: 토큰 자동 갱신**
- **Given** `credentials/youtube_token.json`의 access_token이 만료된 상태이나 refresh_token은 유효
- **When** YouTube API 호출 시도
- **Then** `google.auth.transport.requests.Request()`로 자동 갱신되고, 갱신된 토큰이 파일에 저장됨

**Scenario 3: client_secret.json 미존재**
- **Given** `credentials/client_secret.json` 파일이 존재하지 않는 상태
- **When** `uv run video-automation youtube auth` 실행
- **Then** "Google Cloud Console에서 OAuth 2.0 Client ID를 생성하고 client_secret.json을 credentials/ 디렉토리에 배치하세요" 안내 메시지 출력 후 종료

### [REQ-07] 썸네일 자동 설정

**Scenario 1: 썸네일 파일 존재**
- **Given** `projects/my-video/output/thumbnail.png` 파일이 존재하는 상태
- **When** 업로드 완료 후 썸네일 설정 단계 실행
- **Then** `thumbnails().set()`으로 해당 파일이 업로드되고, `upload_result.json`의 `thumbnail_set`이 `true`

**Scenario 2: 썸네일 파일 미존재**
- **Given** 프로젝트 디렉토리에 thumbnail 파일이 없는 상태
- **When** 업로드 완료 후 썸네일 설정 단계 실행
- **Then** 경고 메시지 "[yellow]썸네일 파일이 없습니다. YouTube 기본 썸네일을 사용합니다.[/yellow]" 출력하고, `thumbnail_set`이 `false`

**Scenario 3: 썸네일 업로드 권한 없음**
- **Given** 채널이 커스텀 썸네일 업로드 권한이 없는 상태
- **When** 썸네일 업로드 API 호출
- **Then** `HttpError 403` 캐치 후 경고 메시지 출력, 영상 업로드 자체는 성공 처리

### [REQ-08] GPT-5 기반 메타데이터 생성

**Scenario 1: 정상 생성**
- **Given** `script.txt`에 유효한 한국어 대본이 있는 상태
- **When** `generate_video_metadata(script_text, project_name)` 호출
- **Then** `VideoMetadata` 객체가 반환되며, `title`은 60자 이내 한국어, `tags`는 5~15개의 관련 키워드 포함

**Scenario 2: script.txt가 비어있음**
- **Given** `script.txt`가 빈 파일인 상태
- **When** `generate_video_metadata(script_text, project_name)` 호출
- **Then** `ValueError("script.txt가 비어 있어 메타데이터를 생성할 수 없습니다")` 발생

### [REQ-N01] 비공개 기본값 강제

**Scenario 1: CLI에서 public 직접 업로드 시도 차단**
- **Given** 사용자가 `--status public` 플래그로 업로드를 시도하는 상태
- **When** `uv run video-automation youtube upload --project my-video --status public` 실행
- **Then** "[yellow]안전을 위해 업로드는 항상 비공개로 진행됩니다. 공개 전환은 `youtube publish`를 사용하세요.[/yellow]" 메시지 출력 후 비공개로 업로드 진행

## 엣지 케이스

- [ ] 프로젝트에 `final_video.mp4`와 `final_shorts.mp4` 모두 존재하는 경우 -- `--type` 플래그로 선택 또는 사용자에게 질문
- [ ] 업로드 중 프로세스 강제 종료 (Ctrl+C) -- resumable upload 특성상 재실행 시 처음부터 다시 시작 (부분 업로드 정리 불필요)
- [ ] `metadata.json`에 일부 필드만 존재 (`title`만 있고 `description`이 없는 경우) -- 누락 필드만 GPT-5로 보완
- [ ] YouTube API rate limit 429 응답 -- exponential backoff (1초, 2초, 4초) 후 최대 3회 재시도
- [ ] 동일 프로젝트 재업로드 -- `upload_result.json`에 이전 기록이 있으면 "[yellow]이미 업로드된 영상이 있습니다 (video_id: xxx). 재업로드하시겠습니까?[/yellow]" 확인
- [ ] `tags` 합계가 500자 초과 -- YouTube 제한. 자동 생성 시 총 길이를 체크하여 초과 시 후순위 태그 제거
- [ ] `title`이 100자 초과 (YouTube 제한) -- 자동 생성 시 60자 제한, 수동 입력 시 검증 후 경고
- [ ] OAuth2 refresh_token이 revoke된 경우 -- `RefreshError` 캐치 후 "인증이 만료되었습니다. `youtube auth`를 다시 실행하세요" 안내

## 품질 게이트

- [ ] `ruff check .` 통과
- [ ] `ruff format --check .` 통과
- [ ] `mypy app shared entities features` 타입 체크 통과 (신규 파일 포함)
- [ ] `lint-imports` FSD 규칙 통과 -- 특히 `features/upload_youtube` -> `shared/api/youtube` 방향 확인
- [ ] `pytest tests/features/test_upload_youtube.py` 통과 (mock 기반 단위 테스트)
- [ ] `pytest tests/shared/test_youtube_api.py` 통과 (mock 기반 API 클라이언트 테스트)
- [ ] 신규 코드 테스트 커버리지: 핵심 경로(업로드, 인증, 메타데이터 생성) 80% 이상

## 성능 기준

- 메타데이터 자동 생성 (GPT-5 호출): 10초 이내
- 1GB 이하 영상 업로드: 네트워크 속도에 의존하되, chunk size 256KB~1MB로 설정하여 진행률 표시 가능
- OAuth2 토큰 갱신: 2초 이내
- 공개 상태 변경 API 호출: 3초 이내
