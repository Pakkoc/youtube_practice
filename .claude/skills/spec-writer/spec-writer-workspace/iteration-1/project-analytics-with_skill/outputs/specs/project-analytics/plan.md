# track-project-analytics 구현 계획

## 기술 스택

- **DB**: `sqlite3` (Python 표준 라이브러리)
- **ORM**: 없음 -- 직접 SQL 사용 (단일 테이블, 복잡도 낮음)
- **모델**: `pydantic.BaseModel` (기존 패턴과 동일)
- **CLI**: `click` 커맨드 그룹
- **출력**: `rich.table.Table`, `rich.panel.Panel`
- **시간 측정**: `time.perf_counter()` (파이프라인 래퍼)

## 파일 구조 계획

### 신규 생성

- `shared/db/__init__.py` -- public export (`get_connection`, `ensure_schema`)
- `shared/db/connection.py` -- SQLite 커넥션 팩토리, 스키마 자동 생성
- `entities/analytics/__init__.py` -- public export
- `entities/analytics/model.py` -- `AnalyticsRecord`, `AnalyticsSummary` Pydantic 모델
- `features/track_analytics/__init__.py` -- public export (`record_run`, `query_project`, `get_summary`)
- `features/track_analytics/lib.py` -- 기록/조회/통계 구현 로직
- `features/track_analytics/model.py` -- feature 전용 DTO (필요 시)
- `data/` -- DB 파일 디렉토리 (`.gitignore`에 추가)

### 수정

- `app/cli.py` -- `analytics` 커맨드 그룹 추가 (`show`, `summary`)
- `pipelines/script_to_video/__init__.py` -- `run_script_to_video()` 완료 후 `record_run()` 호출
- `pipelines/script_to_shorts/__init__.py` -- `run_script_to_shorts()` 완료 후 `record_run()` 호출
- `pipelines/script_to_carousel/__init__.py` -- `run_script_to_carousel()` 완료 후 `record_run()` 호출
- `pipelines/video_to_shorts/__init__.py` -- `run_video_to_shorts()` 완료 후 `record_run()` 호출
- `.gitignore` -- `data/analytics.db` 추가

## 작업 분해

| # | TODO | 위험도 | 요구사항 |
|---|------|--------|----------|
| 1 | `shared/db/connection.py` -- SQLite 커넥션 팩토리 + 스키마 DDL 작성 | LOW | REQ-05, REQ-06 |
| 2 | `entities/analytics/model.py` -- `AnalyticsRecord`, `AnalyticsSummary` Pydantic 모델 정의 | LOW | REQ-01 |
| 3 | `features/track_analytics/lib.py` -- `record_run()` 함수 (INSERT) | LOW | REQ-01 |
| 4 | `features/track_analytics/lib.py` -- `query_project()` 함수 (SELECT, 필터, 정렬) | LOW | REQ-02, REQ-04 |
| 5 | `features/track_analytics/lib.py` -- `get_summary()` 함수 (집계 쿼리) | LOW | REQ-03 |
| 6 | `app/cli.py` -- `analytics show` 커맨드 (rich 테이블 출력) | LOW | REQ-02, REQ-04 |
| 7 | `app/cli.py` -- `analytics summary` 커맨드 (요약 통계 출력) | LOW | REQ-03 |
| 8 | 각 파이프라인에 `record_run()` 호출 삽입 + try/except 래핑 | MEDIUM | REQ-01, REQ-N01 |
| 9 | 파이프라인 실행 시간 측정 래퍼 (`time.perf_counter()`) 추가 | LOW | REQ-01 |
| 10 | `.gitignore` 업데이트 + `data/` 디렉토리 생성 로직 | LOW | REQ-05 |
| 11 | 단위 테스트 -- `features/track_analytics` (in-memory SQLite) | LOW | 품질 |
| 12 | (선택) `analytics export --format csv` 커맨드 | LOW | REQ-O01 |
| 13 | (선택) `analytics delete --project` 커맨드 | LOW | REQ-O03 |

## 상세 설계

### 1. SQLite 스키마 (`shared/db/connection.py`)

```sql
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name     TEXT    NOT NULL,
    pipeline_type    TEXT    NOT NULL,
    config_profile   TEXT    NOT NULL DEFAULT 'base',
    slide_count      INTEGER NOT NULL DEFAULT 0,
    tts_total_duration  REAL NOT NULL DEFAULT 0.0,
    broll_count      INTEGER NOT NULL DEFAULT 0,
    render_duration  REAL    NOT NULL DEFAULT 0.0,
    final_video_duration REAL DEFAULT NULL,
    created_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_project_name ON pipeline_runs(project_name);
CREATE INDEX IF NOT EXISTS idx_created_at ON pipeline_runs(created_at DESC);
```

### 2. 커넥션 팩토리 패턴

```python
# shared/db/connection.py
from pathlib import Path
from shared.constants import PROJECT_ROOT
import sqlite3

DB_PATH = PROJECT_ROOT / "data" / "analytics.db"

def get_connection() -> sqlite3.Connection:
    """SQLite 커넥션 반환. 최초 호출 시 스키마 자동 생성."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # 동시 읽기 성능
    _ensure_schema(conn)
    return conn
```

### 3. Pydantic 모델 (`entities/analytics/model.py`)

```python
class AnalyticsRecord(BaseModel):
    """단일 파이프라인 실행 기록."""
    id: int | None = None
    project_name: str
    pipeline_type: str
    config_profile: str = "base"
    slide_count: int = 0
    tts_total_duration: float = 0.0
    broll_count: int = 0
    render_duration: float = 0.0
    final_video_duration: float | None = None
    created_at: str = ""  # ISO 8601

class AnalyticsSummary(BaseModel):
    """전체 프로젝트 요약 통계."""
    total_projects: int
    total_runs: int
    avg_render_duration: float
    total_tts_duration: float
    avg_slide_count: float
    avg_broll_count: float
```

### 4. 파이프라인 통합 패턴

```python
# pipelines/script_to_video/__init__.py 내 run_script_to_video() 끝부분
import time
from features.track_analytics import record_run

start = time.perf_counter()
# ... 기존 파이프라인 로직 ...
elapsed = time.perf_counter() - start

try:
    record_run(
        project_name=project.name,
        pipeline_type="script-to-video",
        config_profile=os.getenv("CONFIG_PROFILE", "base"),
        slide_count=len(slides),
        tts_total_duration=sum(a.duration for a in audio_clips),
        broll_count=len(broll_images),
        render_duration=elapsed,
        final_video_duration=video.duration,
    )
except Exception:
    logger.warning("analytics 기록 실패, 파이프라인은 정상 완료")
```

### 5. CLI 출력 형식

`analytics show --project my-video`:
```
 Pipeline Runs: my-video
 +---------+------------------+---------+-------+----------+--------+---------+---------------------+
 | Profile | Pipeline         | Slides  | TTS   | B-rolls  | Render | Output  | Date                |
 +---------+------------------+---------+-------+----------+--------+---------+---------------------+
 | base    | script-to-video  | 15      | 124.3s| 8        | 312.5s | 185.2s  | 2026-03-26T14:30:00 |
 | shorts  | script-to-shorts | 5       | 28.1s | 3        | 45.2s  | 42.0s   | 2026-03-25T10:15:00 |
 +---------+------------------+---------+-------+----------+--------+---------+---------------------+
```

`analytics summary`:
```
 Analytics Summary
 +---------------------+-------+
 | Total Projects      | 12    |
 | Total Runs          | 45    |
 | Avg Render Time     | 234.5s|
 | Total TTS Duration  | 1,842s|
 | Avg Slides/Run      | 11.3  |
 | Avg B-rolls/Run     | 5.7   |
 +---------------------+-------+
```

## 위험 분석

| 위험 | 영향 | 완화 전략 |
|------|------|-----------|
| 파이프라인 변수 접근: 슬라이드 수, B-roll 수 등의 변수가 파이프라인 함수 스코프에 따라 접근 어려울 수 있음 | MEDIUM | 각 파이프라인의 `lib.py`를 읽고 반환값/로컬 변수를 확인 후, 필요 시 반환 DTO에 메트릭 필드 추가 |
| DB 파일 잠금: Windows에서 SQLite WAL 모드의 파일 잠금 문제 | LOW | CLI는 단일 프로세스 -- 동시 접근 없음. WAL 모드로 읽기/쓰기 분리 |
| 기존 파이프라인 수정 범위: 4개 파이프라인 모두 수정 필요 | MEDIUM | try/except로 감싸서 기록 실패가 파이프라인에 영향 없게 함 (REQ-N01). 한 파이프라인씩 순차 적용 |
| `data/` 디렉토리 git 관리: DB 파일이 커밋되면 안 됨 | LOW | `.gitignore`에 `data/*.db` 추가 |

## 의존성 분석

- **기존 코드 영향 범위**:
  - `app/cli.py`: `analytics` 그룹 추가 (기존 그룹 `pipeline`, `tts`, `subtitles`와 동일 패턴)
  - 4개 파이프라인 `__init__.py`: 함수 끝에 `record_run()` 호출 추가 (기존 로직 변경 없음)
- **FSD import 규칙 준수 확인**:
  - `shared/db/` -> 외부 의존 없음 (stdlib `sqlite3`만 사용)
  - `entities/analytics/` -> `shared/` 참조 가능 (하위 레이어)
  - `features/track_analytics/` -> `entities/analytics/` + `shared/db/` 참조 가능
  - `app/cli.py` -> `features/track_analytics/` 참조 가능 (상위 -> 하위)
  - `pipelines/` -> `features/track_analytics/` 참조 가능 (상위 -> 하위)
  - 모든 import 방향이 FSD 규칙(`app` -> `pipelines` -> `features` -> `entities` -> `shared`)을 준수함
