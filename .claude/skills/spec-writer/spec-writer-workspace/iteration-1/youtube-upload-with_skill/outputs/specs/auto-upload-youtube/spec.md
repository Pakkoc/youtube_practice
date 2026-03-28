# auto-upload-youtube -- YouTube 자동 업로드

## 배경

현재 시스템은 영상 생성(script-to-video, script-to-shorts)까지 자동화되어 있으나,
완성된 영상을 YouTube에 업로드하는 과정은 수동이다. 영상 생성 후 제목/설명/태그/썸네일을
자동으로 설정하여 YouTube에 비공개(private)로 업로드하고, 사용자가 확인 후 공개 전환할 수
있는 기능이 필요하다. 이를 통해 end-to-end 자동화의 마지막 구간을 완성한다.

## 요구사항 (EARS 형식)

### 핵심 요구사항

- **[REQ-01]** 시스템은 완성된 영상 파일(`final_video.mp4` 또는 shorts)을 YouTube Data API v3를 통해 YouTube에 업로드해야 한다.
- **[REQ-02]** WHEN 업로드 요청이 발생하면, THEN 시스템은 `VideoMetadata`(제목, 설명, 태그, 카테고리, 썸네일)를 자동 생성하여 업로드 요청에 포함해야 한다.
- **[REQ-03]** 시스템은 업로드 시 기본 공개 상태를 `private`(비공개)로 설정해야 한다.
- **[REQ-04]** WHEN 사용자가 공개 전환을 요청하면, THEN 시스템은 해당 영상의 공개 상태를 `public` 또는 `unlisted`로 변경해야 한다.
- **[REQ-05]** WHEN 업로드가 완료되면, THEN 시스템은 업로드 결과(video_id, URL, 상태)를 `upload_result.json`에 저장해야 한다.
- **[REQ-06]** 시스템은 OAuth2 인증 토큰을 안전하게 관리해야 한다. 토큰은 `credentials/youtube_token.json`에 저장하고, 만료 시 자동 갱신(refresh)해야 한다.
- **[REQ-07]** WHEN 썸네일 파일이 프로젝트 디렉토리에 존재하면(`thumbnail.png` 또는 `thumbnail.jpg`), THEN 시스템은 해당 파일을 YouTube 썸네일로 설정해야 한다.
- **[REQ-08]** WHEN 메타데이터(제목/설명/태그)가 프로젝트에 사전 정의되어 있지 않으면, THEN 시스템은 `script.txt`와 영상 정보를 기반으로 GPT-5를 사용하여 자동 생성해야 한다.

### 금지사항

- **[REQ-N01]** 시스템은 사용자의 명시적 요청 없이 영상을 `public`으로 업로드하면 안 된다.
- **[REQ-N02]** 시스템은 OAuth2 client_secret을 코드에 하드코딩하면 안 된다. 반드시 환경변수(`YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`) 또는 `credentials/client_secret.json` 파일을 사용해야 한다.
- **[REQ-N03]** 시스템은 업로드 실패 시 사용자에게 알리지 않고 조용히 실패하면 안 된다.

### 선택사항

- **[REQ-O01]** 가능하다면, 업로드 후 영상 목록을 조회하여 최근 업로드된 영상의 상태를 확인할 수 있어야 한다.
- **[REQ-O02]** 가능하다면, 예약 공개(scheduled publish) 기능을 지원해야 한다 (`publishAt` 파라미터).
- **[REQ-O03]** 가능하다면, 업로드 진행률을 Rich progress bar로 표시해야 한다.

## 제약 조건

- YouTube Data API v3 quota: 일일 10,000 유닛. 영상 업로드 1건 = 1,600 유닛. 일일 최대 약 6건 업로드 가능.
- 영상 파일 크기: YouTube 최대 256GB, 길이 12시간. 본 프로젝트에서는 현실적으로 1GB 이하.
- OAuth2 첫 인증 시 브라우저 기반 인증 플로우 필요 (headless 환경 불가).
- 썸네일 업로드는 YouTube Partner Program 또는 인증된 채널에서만 가능할 수 있음.
- `google-api-python-client`, `google-auth-oauthlib` 패키지 의존성 추가 필요.
- Windows 11 환경: 파일 경로에 한글 포함 가능, `encoding='utf-8'` 필수.

## FSD 레이어 매핑

| 레이어 | 슬라이스 | 변경 유형 |
|--------|----------|-----------|
| shared/api/ | `youtube.py` | 신규 생성 -- YouTube API 클라이언트 (인증, 업로드, 상태 변경) |
| entities/video/ | `model.py` | 수정 -- `UploadResult` 모델 추가 |
| features/ | `upload_youtube/` | 신규 생성 -- 업로드 오케스트레이션 (메타데이터 생성, 업로드 실행, 결과 저장) |
| features/ | `generate_metadata/` | 신규 생성 -- GPT-5 기반 제목/설명/태그 자동 생성 |
| app/ | `cli.py` | 수정 -- `youtube upload`, `youtube publish` CLI 커맨드 추가 |
| shared/config/ | `schema.py` | 수정 -- `YoutubeConfig`에 OAuth/업로드 관련 필드 추가 |

## 의존성

- 내부: `entities.video.model.Video`, `entities.video.model.VideoMetadata`, `entities.project.model.Project`, `shared.api.claude.ask()` (메타데이터 생성용)
- 외부:
  - `google-api-python-client` >= 2.0 (YouTube Data API v3 클라이언트)
  - `google-auth-oauthlib` >= 1.0 (OAuth2 인증 플로우)
  - `google-auth` >= 2.0 (토큰 갱신)
