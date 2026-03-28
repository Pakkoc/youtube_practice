# 프로젝트 분석 대시보드 -- Implementation Plan

## 1. 구현 순서

총 5단계, 각 단계마다 검증 체크포인트가 있다.

### Phase 1: 기반 인프라 (shared + entities)

**목표**: SQLite 연결 + 스키마 생성 + 도메인 모델

**작업**:
1. `shared/constants.py`에 `ANALYTICS_DB_PATH` 상수 추가
2. `shared/lib/database.py` 신규 생성
   - `get_db_connection()`, `ensure_schema()`, 마이그레이션 시스템
3. `entities/analytics/__init__.py` + `model.py` 신규 생성
   - `PipelineRun`, `PipelineStep`, `PipelineResult` 모델
4. `.gitignore`에 `data/analytics.db` 추가

**검증**:
```bash
pytest tests/shared/test_database.py -v
# DB 파일 생성, 테이블 존재, 마이그레이션 적용 확인
```

**예상 작업량**: 신규 3파일, 수정 2파일

---

### Phase 2: 기록 기능 (features/track_analytics)

**목표**: 파이프라인에서 호출할 write API 완성

**작업**:
1. `features/track_analytics/__init__.py` -- public exports
2. `features/track_analytics/api.py` -- `record_run_start()`, `record_step()`, `record_run_end()`, `PipelineTracker`, `track_pipeline()`
3. `features/track_analytics/model.py` -- 조회 결과 모델 (AnalyticsSummary, RunHistoryRow, StepRanking)

**검증**:
```bash
pytest tests/features/test_track_analytics.py -v
# record_run_start -> run_id 반환
# record_step -> pipeline_steps에 행 삽입
# record_run_end -> status 업데이트 + pipeline_results 삽입
# track_pipeline context manager: 정상 종료 시 success, 예외 시 failed
# PipelineTracker.step(): 소요 시간 자동 기록
# 에러 안전: DB 연결 실패 시 None 반환, 예외 미발생
```

**예상 작업량**: 신규 3파일

---

### Phase 3: 조회 기능 + CLI

**목표**: CLI로 통계 조회 가능

**작업**:
1. `features/track_analytics/lib.py` -- `get_project_summary()`, `get_run_history()`, `compare_projects()`, `get_slow_steps()`
2. `app/cli.py` -- `analytics` 커맨드 그룹 + 4개 서브커맨드
3. Rich Table/Panel 포맷팅

**검증**:
```bash
# 조회 함수 단위 테스트
pytest tests/features/test_track_analytics.py::test_get_project_summary -v

# CLI 통합 테스트 (테스트 DB로)
uv run video-automation analytics summary
uv run video-automation analytics history --project 001 --limit 5
uv run video-automation analytics slow-steps --top 5
```

**예상 작업량**: 신규 1파일, 수정 1파일

---

### Phase 4: 파이프라인 통합

**목표**: 4개 파이프라인에 analytics 기록 코드 추가

**작업** (순서대로, 하나씩 검증):
1. `pipelines/script_to_video/lib.py` -- `track_pipeline` + `tracker.step()` 삽입
2. `pipelines/script_to_shorts/lib.py` -- 동일 패턴
3. `pipelines/script_to_carousel/lib.py` -- 동일 패턴 (단순)
4. `pipelines/video_to_shorts/lib.py` -- 동일 패턴

**검증 (각 파이프라인마다)**:
```bash
# 1. ruff lint
ruff check pipelines/script_to_video/lib.py

# 2. import-linter
lint-imports

# 3. 단위 테스트 (mock pipeline으로 기록 확인)
pytest tests/pipelines/test_script_to_video_analytics.py -v

# 4. 실제 파이프라인 실행 후 analytics 확인
uv run video-automation pipeline script-to-video --input test_script.txt --project test-analytics
uv run video-automation analytics history --project test-analytics
```

**예상 작업량**: 수정 4파일

---

### Phase 5: 품질 검증 + 정리

**작업**:
1. 전체 lint: `ruff check . && ruff format .`
2. 타입 체크: `mypy shared/lib/database.py entities/analytics features/track_analytics`
3. import-linter: `lint-imports`
4. 전체 테스트: `pytest`
5. 실제 E2E 파이프라인 실행 -> analytics 확인

---

## 2. 테스트 전략

### 2.1 단위 테스트 (tests/features/test_track_analytics.py)

```python
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def analytics_db(tmp_path, monkeypatch):
    """임시 SQLite DB로 analytics 테스트."""
    db_path = tmp_path / "test_analytics.db"
    monkeypatch.setattr("shared.constants.ANALYTICS_DB_PATH", db_path)
    return db_path


class TestRecordRunStart:
    def test_returns_run_id(self, analytics_db): ...
    def test_stores_project_name(self, analytics_db): ...
    def test_stores_pipeline_type(self, analytics_db): ...
    def test_status_is_running(self, analytics_db): ...


class TestRecordRunEnd:
    def test_updates_status_to_success(self, analytics_db): ...
    def test_updates_status_to_failed(self, analytics_db): ...
    def test_stores_error_message(self, analytics_db): ...
    def test_calculates_duration(self, analytics_db): ...
    def test_inserts_result_metrics(self, analytics_db): ...


class TestRecordStep:
    def test_inserts_step(self, analytics_db): ...
    def test_ignores_none_run_id(self, analytics_db): ...


class TestTrackPipeline:
    def test_success_flow(self, analytics_db): ...
    def test_failure_flow(self, analytics_db): ...
    def test_step_timer(self, analytics_db): ...
    def test_set_result(self, analytics_db): ...


class TestErrorSafety:
    def test_record_start_on_db_error(self, analytics_db): ...
    def test_record_step_on_db_error(self, analytics_db): ...
    def test_record_end_on_db_error(self, analytics_db): ...


class TestQueries:
    def test_get_project_summary(self, analytics_db): ...
    def test_get_run_history(self, analytics_db): ...
    def test_get_slow_steps(self, analytics_db): ...
    def test_compare_projects(self, analytics_db): ...
```

### 2.2 통합 테스트

- 실제 파이프라인은 실행하지 않고, mock으로 `track_pipeline` 호출 패턴만 검증
- CLI 테스트: `CliRunner`로 `analytics summary` 등 출력 포맷 확인

---

## 3. 의존성

### 추가 필요 패키지: 없음

- `sqlite3`: Python stdlib
- `datetime`: Python stdlib
- `time`: Python stdlib
- `pydantic`: 이미 의존성에 포함
- `click`, `rich`: 이미 의존성에 포함

### pyproject.toml 수정: 불필요

---

## 4. 리스크 및 주의사항

| 리스크 | 대응 |
|--------|------|
| 파이프라인 코드 들여쓰기 1레벨 증가 | `with track_pipeline()` 블록이 본문 전체를 감싸므로 diff가 크지만, 로직 변경은 없음 |
| 병렬 실행 중 DB 동시 쓰기 | WAL 모드 + SQLite의 내장 잠금으로 충분. 동시성이 낮으므로 문제 없음 |
| analytics 코드 버그가 파이프라인 방해 | 모든 write 함수를 try/except로 감싸고, 실패 시 경고 로그만 출력 |
| DB 파일 커밋 방지 | `.gitignore`에 `data/` 디렉토리 추가 |
| Windows 경로 인코딩 | `sqlite3.connect(str(path))` -- Path 객체를 문자열로 변환하여 전달 |

---

## 5. 향후 확장 가능성 (v2+)

아래 항목은 v1에서 구현하지 않지만, 스키마 설계 시 고려하였다.

- `pipeline_steps.metadata_json`: 단계별 세부 메트릭 (GPU 사용량, API 호출 수 등)
- `analytics export --format csv`: 데이터 내보내기
- `analytics cleanup --older-than 90d`: 오래된 기록 정리
- 기존 프로젝트 백필: 완료된 프로젝트의 파일 시스템에서 메트릭 역추산
- 웹 대시보드: SQLite -> JSON API -> 프론트엔드 (필요 시)
