# track-project-analytics 인수 기준

## 시나리오

### [REQ-01] 파이프라인 완료 시 메트릭 자동 기록

**Scenario 1: script-to-video 파이프라인 정상 완료**
- **Given** `analytics.db`가 존재하고 `pipeline_runs` 테이블이 비어 있음
- **When** `run_script_to_video(project=Project(name="test-001"), ...)` 가 정상 완료됨
- **Then** `pipeline_runs` 테이블에 1개 레코드가 삽입되며, `project_name="test-001"`, `pipeline_type="script-to-video"`, `slide_count > 0`, `tts_total_duration > 0`, `render_duration > 0`, `created_at`이 ISO 8601 형식임

**Scenario 2: script-to-shorts 파이프라인 정상 완료**
- **Given** `analytics.db`가 존재함
- **When** `run_script_to_shorts(project=Project(name="cc-001"), ...)` 가 정상 완료됨
- **Then** `pipeline_runs`에 `pipeline_type="script-to-shorts"`, `config_profile="shorts"` 레코드가 삽입됨

**Scenario 3: script-to-carousel 파이프라인 정상 완료**
- **Given** `analytics.db`가 존재함
- **When** `run_script_to_carousel(project=Project(name="carousel-001"), ...)` 가 정상 완료됨
- **Then** `pipeline_runs`에 `pipeline_type="script-to-carousel"` 레코드가 삽입되며, `final_video_duration`은 `NULL`임 (카루셀은 영상이 아님)

**Scenario 4: 동일 프로젝트 다중 실행**
- **Given** `project_name="test-001"`에 대한 기존 레코드 2개 존재
- **When** 동일 프로젝트로 파이프라인을 한 번 더 실행함
- **Then** 총 3개 레코드가 존재하며, 각각 고유한 `id`와 `created_at` 값을 가짐

---

### [REQ-02] `analytics show --project` 프로젝트별 이력 조회

**Scenario 1: 프로젝트 이력 조회 성공**
- **Given** `project_name="test-001"`에 대한 레코드 3개가 DB에 존재
- **When** `uv run video-automation analytics show --project test-001` 실행
- **Then** `rich` 테이블에 3개 행이 출력되며, 각 행에 Pipeline, Slides, TTS, B-rolls, Render, Date 칼럼이 포함됨

**Scenario 2: 존재하지 않는 프로젝트 조회**
- **Given** `project_name="nonexistent"`에 대한 레코드가 DB에 없음
- **When** `uv run video-automation analytics show --project nonexistent` 실행
- **Then** "해당 프로젝트의 실행 이력이 없습니다." 메시지가 출력됨

---

### [REQ-03] `analytics summary` 전체 요약 통계

**Scenario 1: 복수 프로젝트 요약**
- **Given** 3개 프로젝트(test-001, test-002, cc-001)에 대한 총 8개 레코드 존재
- **When** `uv run video-automation analytics summary` 실행
- **Then** Total Projects=3, Total Runs=8, Avg Render Time/Total TTS Duration/Avg Slides/Avg B-rolls 값이 정확히 계산되어 출력됨

**Scenario 2: DB가 비어있을 때**
- **Given** `pipeline_runs` 테이블이 비어 있음
- **When** `uv run video-automation analytics summary` 실행
- **Then** "기록된 파이프라인 실행 이력이 없습니다." 메시지가 출력됨

---

### [REQ-04] `--last n` 옵션으로 최근 레코드 제한

**Scenario 1: 최근 2개만 조회**
- **Given** `project_name="test-001"`에 대한 레코드 5개 존재
- **When** `uv run video-automation analytics show --project test-001 --last 2` 실행
- **Then** 가장 최근 2개 레코드만 출력되며, `created_at` 내림차순으로 정렬됨

---

### [REQ-05] DB 파일 경로

**Scenario 1: DB 파일 위치 확인**
- **Given** 시스템이 최초 실행됨
- **When** `record_run()`이 호출됨
- **Then** `{PROJECT_ROOT}/data/analytics.db` 파일이 생성됨

---

### [REQ-06] DB 자동 마이그레이션

**Scenario 1: DB 파일 미존재 시 자동 생성**
- **Given** `data/analytics.db` 파일이 존재하지 않음
- **When** `get_connection()`이 호출됨
- **Then** `data/` 디렉토리와 `analytics.db` 파일이 생성되고, `pipeline_runs` 테이블과 인덱스가 존재함

**Scenario 2: DB 파일은 있으나 테이블 미존재**
- **Given** `analytics.db` 파일은 있지만 `pipeline_runs` 테이블이 없음
- **When** `get_connection()`이 호출됨
- **Then** `pipeline_runs` 테이블이 `CREATE TABLE IF NOT EXISTS`로 자동 생성됨

---

### [REQ-N01] 분석 기록 실패 시 파이프라인 중단 금지

**Scenario 1: DB 쓰기 실패 시 파이프라인 정상 완료**
- **Given** `analytics.db` 파일에 쓰기 권한이 없음 (또는 디스크 꽉 참)
- **When** 파이프라인 실행이 완료되고 `record_run()`이 호출됨
- **Then** 경고 로그 `"analytics 기록 실패"`가 출력되지만, 파이프라인은 정상적으로 `Video` 객체를 반환함

**Scenario 2: DB 커넥션 실패**
- **Given** `analytics.db` 경로가 잘못되거나 파일 시스템 오류 발생
- **When** `record_run()`이 호출됨
- **Then** `Exception`이 `try/except`로 잡히고 `logger.warning()`으로 기록됨. 상위 파이프라인에 예외가 전파되지 않음

---

### [REQ-N03] 성능 영향 없음

**Scenario 1: 기록 소요 시간 확인**
- **Given** 파이프라인이 정상 실행 중
- **When** `record_run()`이 호출됨
- **Then** INSERT 쿼리 실행 시간이 100ms 미만임

## 엣지 케이스

- [ ] `project_name`에 특수문자 포함 (예: `my-video (copy)`, `test/001`) -- SQL injection 방지 (parameterized query 사용)
- [ ] `tts_total_duration`이 0인 경우 (TTS 미사용 파이프라인, 예: carousel)
- [ ] `broll_count`가 0인 경우 (`--no-broll` 옵션 사용 시)
- [ ] `final_video_duration`이 `None`인 경우 (carousel 등 영상 미생성 파이프라인)
- [ ] DB 파일이 다른 프로세스에 의해 잠겨 있는 경우 (Windows 파일 잠금)
- [ ] `--last 0` 또는 음수 값 입력 시 -- Click 유효성 검사로 차단 (`type=click.IntRange(min=1)`)
- [ ] 매우 큰 DB (10,000+ 레코드) 조회 성능 -- 인덱스(`idx_project_name`, `idx_created_at`)로 커버
- [ ] `render_duration`이 음수인 경우 -- 코드 레벨에서 `max(0.0, elapsed)` 방어

## 품질 게이트

- [ ] `ruff check .` 통과
- [ ] `ruff format --check .` 통과
- [ ] `mypy shared/db entities/analytics features/track_analytics` 타입 체크 통과
- [ ] `lint-imports` FSD 규칙 통과
- [ ] `pytest tests/features/test_track_analytics.py` 통과
- [ ] `pytest tests/shared/test_db_connection.py` 통과
- [ ] 신규 코드 테스트: in-memory SQLite(`:memory:`)를 사용한 단위 테스트 커버리지 확보
- [ ] 기존 테스트 회귀 없음: `pytest` 전체 스위트 통과

## 성능 기준

- `record_run()` 단일 INSERT: 100ms 미만
- `query_project()` 1,000 레코드 조회: 500ms 미만
- `get_summary()` 10,000 레코드 집계: 1,000ms 미만
- DB 파일 크기: 10,000 레코드 기준 5MB 미만
