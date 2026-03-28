---
name: verify
description: "Verify Implementation - 구현 완료 후 self-review, lint, test, FSD import 검증 수행"
user-invocable: true
---

# Verify Implementation

구현 완료 후 self-review + 자동 검증을 수행하여 버그를 조기 포착한다.

## Steps

### 1. 변경 파일 식별
- `git diff --name-only` 와 `git diff --cached --name-only`로 변경된 파일 목록 수집.
- 변경 파일이 없으면 "검증할 변경사항 없음" 보고 후 종료.

### 2. Self-review (변경 파일 전체 재읽기)
변경된 모든 파일을 다시 읽고 아래 체크리스트 확인:
- [ ] **return 값**: 함수가 의도한 값을 반환하는지 (None 반환 누락, 조건 분기 빠짐)
- [ ] **type 안전성**: Pydantic 모델 필드 타입 일치, TypeScript props 인터페이스 준수
- [ ] **하드코딩**: config로 빠져야 할 값이 코드에 직접 박혀있지 않은지
- [ ] **미구현 stub**: `pass`, `TODO`, `...`, `NotImplementedError` 잔존 여부
- [ ] **import 정합성**: 사용하지 않는 import, 순환 참조, FSD 위반 (상위→하위만 허용)
- [ ] **API 모델**: OpenAI GPT-5 family만 사용하는지 (claude 모델 혼입 금지)
- [ ] **encoding**: 파일 I/O에 `encoding='utf-8'` 명시 여부 (Windows cp949 방지)

### 3. Lint & Type Check
```bash
# Python
ruff check . --select E,F,W
ruff format --check .

# TypeScript (remotion/ 내 변경이 있을 때만)
cd remotion && npx tsc --noEmit
```
- 오류 발견 시 자동 수정 후 재실행. 수정 내용 보고.

### 4. FSD Import 규칙
```bash
lint-imports
```
- multi-file 변경 시 필수 실행. 위반 시 import 경로 수정.

### 5. Test 실행
```bash
# 변경 관련 테스트 우선 실행
pytest tests/ -x --tb=short -q

# API 코드 변경 시 추가
pytest tests/shared/test_ask_api.py -v
```
- 실패 시 원인 분석 + 수정 + 재실행. 모든 테스트 통과할 때까지 반복.

### 6. 결과 보고
아래 형식으로 보고:

```
## Verification Report
- **변경 파일**: N개
- **Self-review**: [PASS/이슈 N건 수정]
- **Lint**: [PASS/이슈 N건 수정]
- **FSD Import**: [PASS/위반 N건 수정]
- **Tests**: [PASS (N passed) / FAIL (원인)]
- **최종 상태**: VERIFIED / BLOCKED (사유)
```
