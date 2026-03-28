# 프로젝트 분석 대시보드 -- Module Specifications

## 1. shared/lib/database.py -- SQLite 연결 관리

### 책임
- SQLite 연결 생성/관리 (thread-safe)
- 스키마 마이그레이션 자동 실행
- 연결 풀링 없이 단순 연결 패턴 (SQLite 특성상 충분)

### Public API

```python
def get_db_connection() -> sqlite3.Connection:
    """SQLite 연결을 반환. 첫 호출 시 스키마 마이그레이션 자동 실행.

    Returns:
        sqlite3.Connection (WAL 모드, foreign_keys ON).
    """

def ensure_schema() -> None:
    """스키마가 최신인지 확인하고, 미적용 마이그레이션을 실행."""
```

### 설계 결정

- **WAL 모드**: 읽기/쓰기 동시 접근 허용 (파이프라인 실행 중 CLI 조회 가능)
- **`check_same_thread=False`**: ThreadPoolExecutor에서 사용하므로 필요
- 연결은 호출자가 관리 (context manager 패턴 권장)
- 마이그레이션은 dict 기반 버전 관리 (Alembic 등 외부 도구 불필요)

### 연결 설정

```python
conn = sqlite3.connect(str(ANALYTICS_DB_PATH), check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA foreign_keys=ON")
conn.row_factory = sqlite3.Row  # dict-like 접근
```

---

## 2. entities/analytics/model.py -- 분석 데이터 모델

### 책임
- 분석 데이터의 도메인 모델 정의 (Pydantic BaseModel)
- DB 행 <-> Python 객체 변환의 기준

### 모델 정의

```python
from datetime import datetime
from pydantic import BaseModel, Field


class PipelineRun(BaseModel):
    """파이프라인 실행 기록."""
    id: int | None = None
    project_name: str
    pipeline_type: str                           # script_to_video | script_to_shorts | ...
    config_profile: str = "base"
    started_at: datetime
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    status: str = "running"                      # running | success | failed | aborted
    error_message: str | None = None


class PipelineStep(BaseModel):
    """파이프라인 단계별 기록."""
    id: int | None = None
    run_id: int
    step_name: str
    step_order: int
    started_at: datetime
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    status: str = "running"                      # running | success | failed | skipped
    metadata_json: str | None = None             # JSON 문자열


class PipelineResult(BaseModel):
    """파이프라인 실행 결과 메트릭."""
    id: int | None = None
    run_id: int
    slide_count: int = 0
    paragraph_count: int = 0
    scene_count: int = 0
    tts_total_duration: float = 0.0
    broll_count: int = 0
    broll_search_count: int = 0
    broll_generated_count: int = 0
    final_video_duration: float = 0.0
    final_video_size_bytes: int = 0
    output_format: str = "16:9"
```

---

## 3. features/track_analytics/api.py -- 데이터 기록

### 책임
- 파이프라인 실행 시작/종료/단계 완료 기록
- 모든 write 함수는 에러를 삼키고 None 반환 (파이프라인 방해 금지)

### Public API

```python
def record_run_start(
    project_name: str,
    pipeline_type: str,
    config_profile: str = "base",
) -> int | None:
    """파이프라인 실행 시작 기록. run_id를 반환."""

def record_step(
    run_id: int | None,
    step_name: str,
    step_order: int,
    duration_seconds: float,
    status: str = "success",
    metadata: dict | None = None,
) -> None:
    """단계 완료 기록. run_id가 None이면 무시."""

def record_run_end(
    run_id: int | None,
    status: str,
    result: PipelineResult | None = None,
    error_message: str | None = None,
) -> None:
    """파이프라인 실행 종료 기록."""
```

### PipelineTracker 클래스

```python
class PipelineTracker:
    """파이프라인 실행 중 메트릭을 수집하는 헬퍼.

    context manager 내부에서 사용되며, step 기록과
    최종 result 메트릭을 축적한다.
    """

    def __init__(self, run_id: int | None):
        self.run_id = run_id
        self._step_order = 0
        self.result = PipelineResult(run_id=run_id or 0)

    def step(self, step_name: str) -> _StepTimer:
        """단계 타이머를 시작하는 context manager.

        사용 예:
            with tracker.step("tts_generation"):
                audio_clips = generate_tts(...)
        """

    def set_result(self, **kwargs) -> None:
        """결과 메트릭 필드를 업데이트.

        사용 예:
            tracker.set_result(slide_count=22, broll_count=18)
        """
```

### track_pipeline Context Manager

```python
@contextmanager
def track_pipeline(
    project_name: str,
    pipeline_type: str,
    config_profile: str = "base",
) -> Generator[PipelineTracker, None, None]:
    """파이프라인 실행을 자동 추적.

    with 블록 정상 종료 시 success, 예외 시 failed로 기록.
    analytics 기록 실패 자체는 파이프라인에 영향 없음.
    """
```

---

## 4. features/track_analytics/lib.py -- 데이터 조회

### 책임
- CLI에서 호출하는 통계 조회 함수
- SQLite 쿼리 실행 -> Pydantic 모델 변환

### Public API

```python
def get_project_summary(
    project_name: str | None = None,
) -> list[AnalyticsSummary]:
    """프로젝트별 요약 통계. project_name이 None이면 전체."""

def get_run_history(
    project_name: str | None = None,
    limit: int = 20,
) -> list[RunHistoryRow]:
    """실행 이력 조회 (최신순)."""

def compare_projects(
    project1: str,
    project2: str,
) -> tuple[AnalyticsSummary, AnalyticsSummary]:
    """두 프로젝트의 요약을 비교용으로 반환."""

def get_slow_steps(
    project_name: str | None = None,
    top_n: int = 10,
) -> list[StepRanking]:
    """평균 소요 시간 기준 느린 단계 순위."""
```

### 조회 결과 모델

```python
# features/track_analytics/model.py

class AnalyticsSummary(BaseModel):
    """프로젝트 요약 통계."""
    project_name: str
    total_runs: int
    success_count: int
    failed_count: int
    avg_duration_seconds: float
    avg_slide_count: float
    avg_tts_duration: float
    avg_broll_count: float
    last_run_at: str | None
    last_run_status: str | None


class RunHistoryRow(BaseModel):
    """실행 이력 한 행."""
    run_id: int
    started_at: str
    pipeline_type: str
    status: str
    duration_seconds: float | None
    slide_count: int
    tts_total_duration: float
    broll_count: int
    final_video_duration: float


class StepRanking(BaseModel):
    """느린 단계 순위 한 행."""
    step_name: str
    avg_duration_seconds: float
    max_duration_seconds: float
    occurrence_count: int
```

---

## 5. app/cli.py -- CLI 커맨드

### 추가할 커맨드 그룹

```python
@cli.group()
def analytics() -> None:
    """프로젝트 분석 대시보드."""
    pass


@analytics.command("summary")
@click.option("--project", "project_name", default=None, help="프로젝트 이름 (미지정 시 전체)")
def analytics_summary(project_name: str | None) -> None:
    """프로젝트별 요약 통계를 표시합니다."""


@analytics.command("history")
@click.option("--project", "project_name", default=None, help="프로젝트 이름")
@click.option("--limit", default=20, help="표시할 최대 행 수")
def analytics_history(project_name: str | None, limit: int) -> None:
    """파이프라인 실행 이력을 표시합니다."""


@analytics.command("compare")
@click.argument("project1")
@click.argument("project2")
def analytics_compare(project1: str, project2: str) -> None:
    """두 프로젝트의 통계를 비교합니다."""


@analytics.command("slow-steps")
@click.option("--project", "project_name", default=None, help="프로젝트 이름")
@click.option("--top", "top_n", default=10, help="상위 N개 단계")
def analytics_slow_steps(project_name: str | None, top_n: int) -> None:
    """가장 오래 걸리는 파이프라인 단계를 표시합니다."""
```

### 출력 포맷

- Rich `Table` 위젯으로 정렬된 테이블 렌더링
- `Panel` 위젯으로 요약 정보 표시
- 시간은 `Xm Ys` 형식으로 변환 (예: `12m 34s`)
- 파일 크기는 `X.X MB` 형식으로 변환
