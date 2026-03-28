---
name: testing
description: "Reference manual for testing patterns and quality tools — pytest structure, API mocking, Pydantic validation, ruff, mypy, and import-linter FSD enforcement. Load when writing tests or running quality checks."
user-invocable: false
---

# Testing Manual

## Activation Conditions
- **Keywords**: test, pytest, mock, fixture, 테스트, 검증, ruff, mypy, lint
- **Intent Patterns**: "테스트 작성", "테스트 실행", "린트 검사", "타입 체크"
- **Working Files**: `tests/`, `pyproject.toml`
- **Content Patterns**: `pytest`, `@patch`, `tmp_path`, `monkeypatch`

## Chapters
1. [테스트 패턴](chapter-test-patterns.md) -- pytest 구조, 모킹, 픽스처
2. [품질 도구](chapter-quality-tools.md) -- ruff, mypy, import-linter
