# 품질 도구

## ruff (Lint + Format)

```bash
# 린트 검사
ruff check .

# 자동 수정
ruff check . --fix

# 포맷 검사
ruff format --check .

# 포맷 적용
ruff format .

# 한번에
ruff check . && ruff format .
```

규칙은 `pyproject.toml`의 `[tool.ruff]` 섹션에서 설정.

## mypy (Type Check)

```bash
# 핵심 디렉토리만 타입 체크
mypy app shared entities

# 특정 파일
mypy app/config.py

# missing imports 무시
mypy --ignore-missing-imports app/
```

타입 체크 대상: `app/`, `shared/`, `entities/`, `features/`, `pipelines/`

## import-linter (FSD 아키텍처 검증)

```bash
lint-imports
```

FSD 계층 규칙 검증:
- `app` → `pipelines`, `features`, `entities`, `shared` (가능)
- `pipelines` → `features`, `entities`, `shared` (가능)
- `features` → `entities`, `shared` (가능)
- `entities` → `shared` (가능)
- `shared` → 자신만 (다른 계층 import 불가)

**역방향 import 금지**: `shared` → `features` (X), `entities` → `pipelines` (X)

계약은 `pyproject.toml`의 `[tool.importlinter]` 섹션에 정의.
