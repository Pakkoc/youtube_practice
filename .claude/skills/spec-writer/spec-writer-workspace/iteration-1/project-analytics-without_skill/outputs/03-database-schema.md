# 프로젝트 분석 대시보드 -- Database Schema

## 1. DB 파일 위치

```python
# shared/constants.py 에 추가
ANALYTICS_DB_PATH = PROJECT_ROOT / "data" / "analytics.db"
```

- `projects/` 디렉토리와 분리하여 `data/` 디렉토리에 배치
- `.gitignore`에 `data/analytics.db` 추가 (로컬 데이터)
- 디렉토리 자동 생성: `ANALYTICS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)`

## 2. 테이블 설계

### 2.1 pipeline_runs (파이프라인 실행)

```sql
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name    TEXT    NOT NULL,
    pipeline_type   TEXT    NOT NULL,          -- script_to_video | script_to_shorts | ...
    config_profile  TEXT    NOT NULL DEFAULT 'base',
    started_at      TEXT    NOT NULL,          -- ISO 8601 UTC
    finished_at     TEXT,                      -- NULL = 실행 중
    duration_seconds REAL,                     -- finished_at - started_at (초)
    status          TEXT    NOT NULL DEFAULT 'running', -- running | success | failed | aborted
    error_message   TEXT,                      -- 실패 시 에러 메시지

    -- 인덱스용 컬럼
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_runs_project ON pipeline_runs(project_name);
CREATE INDEX IF NOT EXISTS idx_runs_status  ON pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_started ON pipeline_runs(started_at);
```

### 2.2 pipeline_steps (단계별 기록)

```sql
CREATE TABLE IF NOT EXISTS pipeline_steps (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    step_name       TEXT    NOT NULL,          -- split_paragraphs | tts_generation | ...
    step_order      INTEGER NOT NULL,          -- 실행 순서
    started_at      TEXT    NOT NULL,
    finished_at     TEXT,
    duration_seconds REAL,
    status          TEXT    NOT NULL DEFAULT 'running', -- running | success | failed | skipped
    metadata_json   TEXT                       -- 단계별 부가 정보 (JSON)
);

CREATE INDEX IF NOT EXISTS idx_steps_run ON pipeline_steps(run_id);
```

### 2.3 pipeline_results (결과 메트릭)

```sql
CREATE TABLE IF NOT EXISTS pipeline_results (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                 INTEGER NOT NULL UNIQUE REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    slide_count            INTEGER DEFAULT 0,
    paragraph_count        INTEGER DEFAULT 0,
    scene_count            INTEGER DEFAULT 0,
    tts_total_duration     REAL    DEFAULT 0.0,   -- 초
    broll_count            INTEGER DEFAULT 0,
    broll_search_count     INTEGER DEFAULT 0,     -- 검색으로 가져온 수
    broll_generated_count  INTEGER DEFAULT 0,     -- AI 생성된 수
    final_video_duration   REAL    DEFAULT 0.0,   -- 초
    final_video_size_bytes INTEGER DEFAULT 0,
    output_format          TEXT    DEFAULT '16:9'  -- 16:9 | 9:16 | 4:5
);

CREATE INDEX IF NOT EXISTS idx_results_run ON pipeline_results(run_id);
```

## 3. 스키마 버전 관리

간단한 버전 테이블로 마이그레이션을 관리한다.

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
```

### 마이그레이션 전략

```python
# shared/lib/database.py

MIGRATIONS = {
    1: [
        "CREATE TABLE IF NOT EXISTS pipeline_runs (...);",
        "CREATE TABLE IF NOT EXISTS pipeline_steps (...);",
        "CREATE TABLE IF NOT EXISTS pipeline_results (...);",
        "CREATE INDEX IF NOT EXISTS idx_runs_project ...;",
        # ... 모든 초기 DDL
    ],
    # 향후 스키마 변경 시:
    # 2: ["ALTER TABLE pipeline_results ADD COLUMN gpu_vram_peak_mb REAL;"],
}

def _get_current_version(conn: sqlite3.Connection) -> int:
    """현재 스키마 버전 조회. 테이블이 없으면 0."""
    ...

def _apply_migrations(conn: sqlite3.Connection) -> None:
    """미적용 마이그레이션을 순차 실행."""
    current = _get_current_version(conn)
    for version in sorted(MIGRATIONS.keys()):
        if version > current:
            for stmt in MIGRATIONS[version]:
                conn.execute(stmt)
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
    conn.commit()
```

## 4. 쿼리 예시

### 4.1 프로젝트 요약 (analytics summary)

```sql
SELECT
    r.project_name,
    COUNT(*)                                    AS total_runs,
    SUM(CASE WHEN r.status = 'success' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN r.status = 'failed' THEN 1 ELSE 0 END)  AS failed_count,
    AVG(r.duration_seconds)                     AS avg_duration,
    AVG(res.slide_count)                        AS avg_slides,
    AVG(res.tts_total_duration)                 AS avg_tts_duration,
    AVG(res.broll_count)                        AS avg_broll,
    MAX(r.started_at)                           AS last_run_at
FROM pipeline_runs r
LEFT JOIN pipeline_results res ON r.id = res.run_id
WHERE r.project_name = ?
GROUP BY r.project_name;
```

### 4.2 실행 이력 (analytics history)

```sql
SELECT
    r.id,
    r.started_at,
    r.status,
    r.duration_seconds,
    res.slide_count,
    res.tts_total_duration,
    res.broll_count,
    res.final_video_duration
FROM pipeline_runs r
LEFT JOIN pipeline_results res ON r.id = res.run_id
WHERE r.project_name = ?
ORDER BY r.started_at DESC
LIMIT ?;
```

### 4.3 느린 단계 분석 (analytics slow-steps)

```sql
SELECT
    s.step_name,
    AVG(s.duration_seconds)  AS avg_duration,
    MAX(s.duration_seconds)  AS max_duration,
    COUNT(*)                 AS occurrence_count
FROM pipeline_steps s
JOIN pipeline_runs r ON s.run_id = r.id
WHERE (? IS NULL OR r.project_name = ?)
  AND s.status = 'success'
GROUP BY s.step_name
ORDER BY avg_duration DESC
LIMIT ?;
```

## 5. 데이터 보존 정책

- 기본적으로 모든 기록을 영구 보존 (SQLite 파일 크기가 미미)
- 향후 필요 시 `analytics cleanup --older-than 90d` 커맨드 추가 가능
- `.gitignore`에 DB 파일 추가하여 Git 트래킹 제외
