# 프로젝트 분석 대시보드 -- Architecture Design

## 1. FSD 계층 배치

기존 아키텍처 규칙 (`app -> pipelines -> features -> entities -> shared`)을 준수하여 각 모듈을 배치한다.

```
shared/
  lib/
    database.py          # SQLite 연결 관리, 마이그레이션 (범용 DB 유틸)

entities/
  analytics/
    __init__.py           # public exports
    model.py              # PipelineRun, PipelineStep, PipelineResult (Pydantic)

features/
  track_analytics/
    __init__.py           # public exports: record_run_start, record_run_end, ...
    model.py              # AnalyticsSummary, StepRanking 등 조회 결과 모델
    api.py                # DB write 함수 (기록)
    lib.py                # DB read 함수 (조회, 통계 집계)

app/
  cli.py                  # `analytics` 커맨드 그룹 추가
```

### 1.1 Import 방향 검증

```
app/cli.py
  -> features/track_analytics (조회 함수 호출)                    OK: app -> features
  -> entities/analytics/model (타입 힌트)                         OK: app -> entities

features/track_analytics/api.py
  -> entities/analytics/model (PipelineRun 모델)                  OK: features -> entities
  -> shared/lib/database (DB 연결)                                OK: features -> shared

features/track_analytics/lib.py
  -> entities/analytics/model                                     OK: features -> entities
  -> shared/lib/database                                          OK: features -> shared

pipelines/script_to_video/lib.py
  -> features/track_analytics (기록 함수 호출)                     OK: pipelines -> features

entities/analytics/model.py
  -> (pydantic만 사용, 내부 import 없음)                           OK

shared/lib/database.py
  -> (sqlite3 stdlib만 사용)                                      OK
```

import-linter 계약을 위반하지 않음.

### 1.2 신규 파일 목록

| 파일 경로 | 역할 | 계층 |
|-----------|------|------|
| `shared/lib/database.py` | SQLite 연결 관리, 스키마 마이그레이션 | shared |
| `entities/analytics/__init__.py` | public exports | entities |
| `entities/analytics/model.py` | 분석 데이터 Pydantic 모델 | entities |
| `features/track_analytics/__init__.py` | public exports | features |
| `features/track_analytics/model.py` | 조회 결과 모델 | features |
| `features/track_analytics/api.py` | 데이터 기록 (write) | features |
| `features/track_analytics/lib.py` | 데이터 조회 (read) | features |
| `tests/features/test_track_analytics.py` | 단위 테스트 | tests |

### 1.3 기존 파일 수정 목록

| 파일 경로 | 수정 내용 |
|-----------|-----------|
| `app/cli.py` | `analytics` 커맨드 그룹 + 서브커맨드 4개 추가 |
| `pipelines/script_to_video/lib.py` | `run_script_to_video()` 시작/종료 시 기록 호출 추가 |
| `pipelines/script_to_shorts/lib.py` | `run_script_to_shorts()` 시작/종료 시 기록 호출 추가 |
| `pipelines/script_to_carousel/lib.py` | `run_script_to_carousel()` 시작/종료 시 기록 호출 추가 |
| `pipelines/video_to_shorts/lib.py` | `run_video_to_shorts()` 시작/종료 시 기록 호출 추가 |
| `shared/constants.py` | `ANALYTICS_DB_PATH` 상수 추가 |

## 2. 데이터 흐름

### 2.1 기록 흐름 (파이프라인 실행 시)

```
pipeline/script_to_video/lib.py::run_script_to_video()
  |
  |-- [시작] features.track_analytics.record_run_start(project, pipeline_type, profile)
  |          -> INSERT INTO pipeline_runs (...) -> run_id 반환
  |
  |-- [각 단계 완료] features.track_analytics.record_step(run_id, step_name, duration, status)
  |                  -> INSERT INTO pipeline_steps (...)
  |
  |-- [완료] features.track_analytics.record_run_end(run_id, status, result_metrics)
  |          -> UPDATE pipeline_runs SET finished_at, status, ...
  |          -> INSERT INTO pipeline_results (...)
  |
  |-- [실패] features.track_analytics.record_run_end(run_id, "failed", error_message=str(e))
```

### 2.2 조회 흐름 (CLI 명령어)

```
app/cli.py::analytics_summary()
  |
  |-- features.track_analytics.get_project_summary(project_name)
  |   -> SELECT + GROUP BY 집계 쿼리
  |   -> AnalyticsSummary 모델 반환
  |
  |-- Rich Console로 테이블 렌더링
```

### 2.3 Context Manager 패턴

파이프라인 코드 침투를 최소화하기 위해 context manager를 제공한다.

```python
# features/track_analytics/api.py

@contextmanager
def track_pipeline(project_name: str, pipeline_type: str, config_profile: str):
    """파이프라인 실행을 자동 추적하는 context manager.

    정상 종료 시 success, 예외 발생 시 failed로 자동 기록.
    """
    run_id = record_run_start(project_name, pipeline_type, config_profile)
    try:
        tracker = PipelineTracker(run_id)
        yield tracker
        record_run_end(run_id, "success", tracker.result_metrics)
    except Exception as e:
        record_run_end(run_id, "failed", error_message=str(e))
        raise
```

파이프라인 코드에서의 사용:

```python
# pipelines/script_to_video/lib.py (수정 예시)

def run_script_to_video(project, config, *, include_broll=True):
    from features.track_analytics import track_pipeline

    with track_pipeline(project.name, "script_to_video", os.getenv("CONFIG_PROFILE", "base")) as tracker:
        # ... 기존 파이프라인 코드 ...

        # 각 단계 완료 후:
        tracker.record_step("tts_generation", duration=tts_duration)

        # 최종 결과:
        tracker.set_result(slide_count=len(slides), tts_total_duration=..., broll_count=...)

        return video
```

## 3. 에러 핸들링 전략

분석 기록은 **부가 기능**이므로 파이프라인 실행을 방해해서는 안 된다.

```python
# features/track_analytics/api.py

def record_run_start(project_name: str, ...) -> int | None:
    """기록 실패 시 None 반환, 예외를 삼킨다."""
    try:
        # INSERT ...
        return run_id
    except Exception as e:
        logger.warning("Analytics 기록 실패 (무시): %s", e)
        return None
```

- 모든 write 함수는 try/except로 감싸고, 실패해도 파이프라인은 계속 진행
- read 함수(CLI 조회)는 에러를 사용자에게 표시
