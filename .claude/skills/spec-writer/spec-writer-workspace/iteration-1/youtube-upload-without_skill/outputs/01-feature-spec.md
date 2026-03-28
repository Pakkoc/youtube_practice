# YouTube 자동 업로드 기능 명세서

## 1. 기능 개요

영상 생성 파이프라인 완료 후, 생성된 영상을 YouTube에 자동 업로드하는 기능.
제목, 설명, 태그, 썸네일을 자동 설정하고, 비공개(private)로 우선 업로드한 뒤
사용자가 확인 후 공개 전환할 수 있도록 한다.

### 1.1 해결하려는 문제

현재 파이프라인은 `final_video.mp4` 생성까지만 자동화되어 있다.
업로드, 메타데이터 설정, 썸네일 지정은 수동으로 YouTube Studio에서 수행해야 한다.
이 과정을 자동화하여 E2E 워크플로우를 완성한다.

### 1.2 핵심 요구사항

| # | 요구사항 | 우선순위 |
|---|---------|---------|
| R1 | 영상 파일을 YouTube Data API v3로 업로드 | P0 |
| R2 | 제목/설명/태그를 대본(script.txt) 기반으로 GPT-5로 자동 생성 | P0 |
| R3 | 썸네일 이미지를 자동 설정 (프로젝트 내 기존 썸네일 사용) | P0 |
| R4 | 초기 업로드 시 비공개(private) 상태로 설정 | P0 |
| R5 | CLI 명령으로 비공개 -> 공개 전환 지원 | P0 |
| R6 | OAuth 2.0 인증 (최초 1회 브라우저 인증, 이후 토큰 재사용) | P0 |
| R7 | 업로드 결과(video_id, URL)를 프로젝트 메타데이터로 저장 | P1 |
| R8 | 파이프라인 통합: `script-to-video` 완료 후 선택적 자동 업로드 | P1 |
| R9 | 업로드 진행률 표시 (resumable upload) | P2 |
| R10 | 예약 공개(scheduled publish) 지원 | P2 |

### 1.3 범위 밖 (Out of Scope)

- YouTube Analytics 조회
- 댓글 자동 관리
- 채널 설정 변경
- YouTube Shorts 전용 업로드 (향후 확장)
- 다중 채널 지원 (v1에서는 단일 채널)


## 2. 사용자 시나리오

### 시나리오 A: 독립 업로드 (수동)

```bash
# 1. 영상 업로드 (비공개)
uv run video-automation youtube upload \
  --project my-video \
  --video projects/my-video/output/final_video.mp4

# 2. 업로드 확인 후 공개 전환
uv run video-automation youtube publish --project my-video
```

### 시나리오 B: 파이프라인 통합 (자동)

```bash
# script-to-video 완료 후 자동 업로드 (비공개)
uv run video-automation pipeline script-to-video \
  --input script.txt \
  --project my-video \
  --auto-upload

# 확인 후 공개
uv run video-automation youtube publish --project my-video
```

### 시나리오 C: 메타데이터만 자동 생성 (업로드 없이)

```bash
# 제목/설명/태그만 생성하여 미리보기
uv run video-automation youtube generate-metadata --project my-video
```

### 시나리오 D: 예약 공개

```bash
# 특정 시간에 공개 예약
uv run video-automation youtube publish \
  --project my-video \
  --schedule "2026-03-28T18:00:00+09:00"
```


## 3. 기술 스택

| 구성 요소 | 기술 | 비고 |
|-----------|------|------|
| YouTube API | YouTube Data API v3 | `google-api-python-client` (이미 의존성에 포함) |
| OAuth 인증 | `google-auth-oauthlib` | 이미 의존성에 포함 |
| 메타데이터 생성 | GPT-5.4-mini (`shared/api/claude.py::ask()`) | 비용 효율적 |
| CLI | Click (`app/cli.py`) | 기존 패턴 |
| 설정 | Pydantic (`shared/config/schema.py`) | `YoutubeConfig` 이미 존재 |
| 진행률 표시 | Rich progress bar | 기존 의존성 |


## 4. YouTube Data API v3 제약사항

| 제약 | 값 | 대응 |
|------|-----|------|
| 일일 할당량 | 10,000 units | 업로드 1회 = 1,600 units, 일 ~6회 가능 |
| 영상 최대 크기 | 256 GB | 제약 없음 |
| 썸네일 최대 크기 | 2 MB | 업로드 전 리사이즈 검증 |
| resumable upload 청크 | 256 KB 배수, 최소 5 MB 권장 | 5 MB 청크 사용 |
| 제목 최대 길이 | 100자 | GPT 프롬프트에 명시 |
| 설명 최대 길이 | 5,000자 | GPT 프롬프트에 명시 |
| 태그 총 길이 | 500자 | GPT 프롬프트에 명시 |
| 비공개 -> 공개 전환 | `videos.update` (50 units) | 별도 CLI 명령 |
| 썸네일 설정 | `thumbnails.set` (50 units) | 업로드 직후 실행 |
