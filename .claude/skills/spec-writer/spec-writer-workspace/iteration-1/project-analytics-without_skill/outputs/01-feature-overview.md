# 프로젝트 분석 대시보드 -- Feature Overview

## 1. 목적

프로젝트별 영상 생성 이력을 SQLite에 자동 기록하고, CLI 명령어로 통계를 조회할 수 있는 분석 대시보드 기능.

## 2. 해결하는 문제

현재 파이프라인은 영상 생성이 끝나면 결과물만 남기고 메트릭(슬라이드 수, TTS 소요 시간, B-roll 수, 렌더링 시간 등)을 어디에도 저장하지 않는다. 반복 생성 시 과거 이력 비교, 병목 분석, 프로젝트별 리소스 사용량 파악이 불가능하다.

## 3. 핵심 요구사항

| 항목 | 설명 |
|------|------|
| 데이터 수집 | 파이프라인 실행 시 자동으로 메트릭 기록 (슬라이드 수, TTS 총 시간, B-roll 수, 렌더링 소요 시간) |
| 저장소 | SQLite (단일 파일, 외부 DB 의존성 없음) |
| CLI 조회 | `video-automation analytics` 그룹 아래 여러 서브커맨드 |
| FSD 준수 | `shared` (DB 클라이언트) / `entities` (모델) / `features` (수집/조회) / `app` (CLI) 계층 분리 |

## 4. 수집 대상 메트릭

### 4.1 파이프라인 실행 레벨 (pipeline_run)

- `project_name`: 프로젝트 이름
- `pipeline_type`: 파이프라인 종류 (`script_to_video`, `script_to_shorts`, `script_to_carousel`, `video_to_shorts`)
- `config_profile`: 사용된 설정 프로필 (`base`, `api`, `shorts`, `asmr`)
- `started_at`: 실행 시작 시각 (UTC)
- `finished_at`: 실행 종료 시각 (UTC)
- `duration_seconds`: 전체 소요 시간 (초)
- `status`: 실행 결과 (`success`, `failed`, `aborted`)
- `error_message`: 실패 시 에러 메시지 (nullable)

### 4.2 단계별 메트릭 (pipeline_step)

- `run_id`: FK -> pipeline_run
- `step_name`: 단계 이름 (`split_paragraphs`, `tts_generation`, `broll_generation`, `slide_rendering`, `video_compositing`, `subtitle_burn`, `avatar_overlay`)
- `started_at` / `finished_at` / `duration_seconds`
- `status`: `success` / `failed` / `skipped`

### 4.3 결과 메트릭 (pipeline_result)

- `run_id`: FK -> pipeline_run
- `slide_count`: 생성된 슬라이드 수
- `tts_total_duration`: TTS 오디오 총 길이 (초)
- `broll_count`: 생성된 B-roll 이미지 수
- `broll_search_count`: 검색으로 가져온 B-roll 수
- `broll_generated_count`: AI 생성된 B-roll 수
- `paragraph_count`: 문단 수
- `scene_count`: 씬 수
- `final_video_duration`: 최종 영상 길이 (초)
- `final_video_size_bytes`: 최종 영상 파일 크기
- `output_format`: 출력 포맷 (`16:9`, `9:16`, `4:5`)

## 5. CLI 명령어 설계

```
video-automation analytics summary [--project NAME] [--last N]
video-automation analytics history [--project NAME] [--limit N]
video-automation analytics compare <project1> <project2>
video-automation analytics slow-steps [--project NAME] [--top N]
```

### 5.1 `analytics summary`

프로젝트별 또는 전체 요약 통계를 표시한다.

```
Project: 001
  Total runs: 5 (success: 4, failed: 1)
  Avg. duration: 12m 34s
  Avg. slides: 22  |  Avg. TTS: 5m 12s  |  Avg. B-roll: 18
  Last run: 2026-03-25 14:30 (success, 11m 22s)
```

### 5.2 `analytics history`

특정 프로젝트의 실행 이력을 시간순으로 표시한다.

```
# | Date                | Status  | Duration | Slides | TTS     | B-roll
1 | 2026-03-20 10:00    | success | 10m 34s  | 20     | 4m 55s  | 16
2 | 2026-03-22 15:30    | failed  | 3m 12s   | 0      | 0s      | 0
3 | 2026-03-25 14:30    | success | 11m 22s  | 22     | 5m 12s  | 18
```

### 5.3 `analytics compare`

두 프로젝트의 최근 성공 실행을 비교한다.

### 5.4 `analytics slow-steps`

가장 오래 걸리는 파이프라인 단계를 순위로 표시한다 (병목 분석용).

## 6. 비포함 사항 (Scope 밖)

- 웹 대시보드 UI (CLI만 제공)
- 실시간 모니터링 (사후 조회만)
- 외부 DB 지원 (SQLite 단일)
- 영상 품질 메트릭 (화질, 인코딩 비트레이트 등)
- YouTube 업로드 후 조회수/반응 추적
