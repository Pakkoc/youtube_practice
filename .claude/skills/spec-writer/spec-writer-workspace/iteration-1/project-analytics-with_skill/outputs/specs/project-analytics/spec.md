# track-project-analytics -- 프로젝트별 분석 대시보드

## 배경

현재 영상 자동화 시스템은 파이프라인 실행 후 결과물(영상, 오디오 등)만 남기고 **생성 과정의 메트릭을 추적하지 않는다**. 프로젝트별 슬라이드 수, TTS 총 시간, B-roll 수, 렌더링 소요 시간 등의 이력이 없어 다음과 같은 문제가 발생한다:

- 파이프라인 성능 병목 식별 불가 (어떤 단계가 오래 걸리는지)
- 프로젝트 간 비교 불가 (A 프로젝트 vs B 프로젝트 효율성)
- 리소스 사용량 예측 불가 (유사 프로젝트의 예상 소요 시간)

SQLite에 실행 이력을 저장하고 CLI로 조회할 수 있는 분석 대시보드가 필요하다.

## 요구사항 (EARS 형식)

### 핵심 요구사항

- **[REQ-01]** 시스템은 파이프라인 실행 완료 시 다음 메트릭을 SQLite DB에 자동 기록해야 한다:
  - `project_name`: 프로젝트 이름 (예: `my-video`, `cc-001`)
  - `pipeline_type`: 파이프라인 유형 (`script-to-video` | `script-to-shorts` | `script-to-carousel` | `video-to-shorts`)
  - `slide_count`: 생성된 슬라이드 수
  - `tts_total_duration`: TTS 오디오 총 길이 (초)
  - `broll_count`: 생성된 B-roll 이미지 수
  - `render_duration`: 전체 렌더링 소요 시간 (초)
  - `created_at`: 실행 시각 (ISO 8601)
  - `config_profile`: 사용된 설정 프로필 (`base` | `api` | `shorts` | `asmr`)
  - `final_video_duration`: 최종 출력 영상 길이 (초, 해당 시)

- **[REQ-02]** WHEN 사용자가 `uv run video-automation analytics show --project <name>` 명령을 실행하면, THEN 해당 프로젝트의 모든 실행 이력을 `rich` 테이블로 출력해야 한다.

- **[REQ-03]** WHEN 사용자가 `uv run video-automation analytics summary` 명령을 실행하면, THEN 전체 프로젝트의 요약 통계(프로젝트 수, 총 실행 횟수, 평균 렌더링 시간, 총 TTS 시간)를 출력해야 한다.

- **[REQ-04]** WHEN 사용자가 `uv run video-automation analytics show --project <name> --last <n>` 옵션을 사용하면, THEN 최근 n개 레코드만 출력해야 한다.

- **[REQ-05]** 시스템은 SQLite DB 파일을 `{PROJECT_ROOT}/data/analytics.db` 경로에 저장해야 한다.

- **[REQ-06]** WHEN DB 파일이 존재하지 않을 때 최초 접근하면, THEN 테이블 스키마를 자동 생성(migration)해야 한다.

### 금지사항

- **[REQ-N01]** 분석 기록 실패가 파이프라인 실행 자체를 중단시키면 안 된다. 기록 실패 시 경고 로그만 출력하고 파이프라인은 정상 완료해야 한다.
- **[REQ-N02]** SQLite 외의 외부 DB(PostgreSQL, Redis 등)를 사용하면 안 된다.
- **[REQ-N03]** 분석 데이터 수집이 파이프라인 성능에 유의미한 영향(100ms 이상)을 주면 안 된다.

### 선택사항

- **[REQ-O01]** 가능하다면, `analytics export --format csv` 명령으로 CSV 내보내기를 지원해야 한다.
- **[REQ-O02]** 가능하다면, `analytics show`에 `--sort <column>` 옵션으로 정렬 기준을 변경할 수 있어야 한다.
- **[REQ-O03]** 가능하다면, `analytics delete --project <name>` 명령으로 특정 프로젝트의 이력을 삭제할 수 있어야 한다.

## 제약 조건

- Python >= 3.13, `sqlite3`는 표준 라이브러리 사용 (추가 의존성 없음)
- CLI 프레임워크: `click` (기존 CLI와 동일)
- 출력 포맷: `rich.table.Table` (기존 `rich` 의존성 재사용)
- DB 접근은 thread-safe해야 함 (`sqlite3.connect(..., check_same_thread=False)` 또는 커넥션 풀 불필요 -- CLI 단일 스레드)
- Windows 11 환경에서 파일 경로는 `pathlib.Path` 사용, 인코딩은 UTF-8
- FSD import 규칙 준수: `app` -> `pipelines` -> `features` -> `entities` -> `shared`

## FSD 레이어 매핑

| 레이어 | 슬라이스 | 변경 유형 | 설명 |
|--------|----------|-----------|------|
| `shared/` | `db/` | 신규 생성 | SQLite 커넥션 관리, 마이그레이션 |
| `entities/` | `analytics/` | 신규 생성 | `AnalyticsRecord` Pydantic 모델 |
| `features/` | `track_analytics/` | 신규 생성 | 기록/조회/통계 로직 |
| `app/` | `cli.py` | 수정 | `analytics` 커맨드 그룹 추가 |
| `pipelines/` | 각 파이프라인 | 수정 | 파이프라인 완료 시 `record_analytics()` 호출 |

## 의존성

- **내부**:
  - `entities.project.model.Project` -- 프로젝트 이름, 경로 참조
  - `shared.constants.PROJECT_ROOT` -- DB 파일 경로 기준
  - `shared.lib.logger` -- 경고 로그 출력
  - `pipelines.script_to_video`, `pipelines.script_to_shorts`, `pipelines.script_to_carousel`, `pipelines.video_to_shorts` -- 메트릭 수집 포인트
- **외부**:
  - `sqlite3` (표준 라이브러리)
  - `click` (기존 의존성)
  - `rich` (기존 의존성)
