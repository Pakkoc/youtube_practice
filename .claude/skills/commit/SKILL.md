---
name: commit
description: "Commit & Push - lint/test 검증 후 conventional commit 형식으로 커밋하고 선택적으로 푸시"
user-invocable: true
---

# Commit & Push

커밋 전 검증 → 커밋 → 푸시 워크플로우.

## Steps

1. `ruff check . && ruff format --check .` 로 lint 검사. 실패 시 자동 수정 후 재검사.
2. `pytest --tb=short -q` 로 테스트 실행. 실패 시 커밋하지 말고 원인 보고.
3. `git status`로 변경사항 확인. staged/unstaged 구분하여 보여주기.
4. `git diff --staged`와 `git diff`로 변경 내용 분석.
5. `git log --oneline -5`로 최근 커밋 스타일 확인.
6. conventional commit 형식으로 커밋 메시지 작성 (feat:, fix:, chore:, docs:, refactor:).
7. 관련 파일만 선택적으로 stage (`.env`, credentials 파일 제외).
8. 커밋 생성 후 `git log --oneline -3`으로 확인.
9. push 여부는 사용자에게 확인 후 진행.
