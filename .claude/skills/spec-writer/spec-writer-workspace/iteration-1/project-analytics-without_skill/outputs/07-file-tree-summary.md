# 프로젝트 분석 대시보드 -- File Tree Summary

## 전체 파일 변경 맵

```
Youtube-Automation/
|
|-- .gitignore                              [수정] data/analytics.db 추가
|
|-- shared/
|   |-- constants.py                        [수정] ANALYTICS_DB_PATH 상수 추가
|   |-- lib/
|       |-- database.py                     [신규] SQLite 연결 관리, 마이그레이션
|
|-- entities/
|   |-- analytics/
|       |-- __init__.py                     [신규] public exports
|       |-- model.py                        [신규] PipelineRun, PipelineStep, PipelineResult
|
|-- features/
|   |-- track_analytics/
|       |-- __init__.py                     [신규] public exports (track_pipeline, get_*)
|       |-- api.py                          [신규] record_run_start/end, PipelineTracker
|       |-- model.py                        [신규] AnalyticsSummary, RunHistoryRow, StepRanking
|       |-- lib.py                          [신규] get_project_summary, get_run_history, ...
|
|-- app/
|   |-- cli.py                              [수정] analytics 커맨드 그룹 + 4개 서브커맨드
|
|-- pipelines/
|   |-- script_to_video/
|   |   |-- lib.py                          [수정] track_pipeline + tracker.step 삽입
|   |-- script_to_shorts/
|   |   |-- lib.py                          [수정] track_pipeline + tracker.step 삽입
|   |-- script_to_carousel/
|   |   |-- lib.py                          [수정] track_pipeline + tracker.step 삽입
|   |-- video_to_shorts/
|       |-- lib.py                          [수정] track_pipeline + tracker.step 삽입
|
|-- tests/
|   |-- shared/
|   |   |-- test_database.py                [신규] DB 연결, 마이그레이션 테스트
|   |-- features/
|       |-- test_track_analytics.py         [신규] 기록/조회/에러 안전 테스트
|
|-- data/
    |-- analytics.db                        [런타임 생성] SQLite DB 파일 (gitignored)
```

## 파일 수 요약

| 구분 | 파일 수 |
|------|---------|
| 신규 파일 | 9 |
| 수정 파일 | 7 |
| 총 영향 파일 | 16 |

## 계층별 분류

| FSD 계층 | 신규 | 수정 | 설명 |
|----------|------|------|------|
| shared | 1 | 1 | database.py (신규), constants.py (수정) |
| entities | 2 | 0 | analytics 패키지 |
| features | 4 | 0 | track_analytics 패키지 |
| pipelines | 0 | 4 | 4개 파이프라인에 tracking 삽입 |
| app | 0 | 1 | cli.py에 analytics 커맨드 추가 |
| tests | 2 | 0 | DB + analytics 테스트 |
| config | 0 | 1 | .gitignore 수정 |
