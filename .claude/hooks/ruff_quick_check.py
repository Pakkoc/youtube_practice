"""PostToolUse hook: .py 파일 편집 후 ruff 즉시 검사 (핵심 규칙만).

py_compile(문법)과 별개로, 논리 오류를 조기 포착한다.
- E: pycodestyle errors (미사용 import 등)
- F: pyflakes (미정의 변수, 미사용 변수, return 누락 등)
- W: warnings

exit 0 = 통과, exit 2 = 블로킹.
"""

import json
import subprocess
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, UnicodeDecodeError):
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path or not file_path.endswith(".py"):
        sys.exit(0)

    # Normalize path separators for consistent matching
    normalized = file_path.replace("\\", "/")

    # Manim slide files use `from manim import *` — skip ruff for these
    if "/projects/" in normalized and "/slides/" in normalized:
        sys.exit(0)

    # uv run을 통해 프로젝트 venv의 ruff 사용 (CosyVoice venv 회피)
    try:
        subprocess.run(["uv", "--version"], capture_output=True, timeout=5)
        ruff_cmd = ["uv", "run", "ruff"]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        ruff_cmd = ["ruff"]

    try:
        result = subprocess.run(
            [*ruff_cmd, "check", "--select", "E,F,W", file_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if result.returncode != 0:
            output = (result.stdout or "") + (result.stderr or "")
            # 핵심 오류만 출력 (최대 5줄)
            lines = [line for line in output.strip().splitlines() if line.strip()]
            truncated = "\n".join(lines[:5])
            if len(lines) > 5:
                truncated += f"\n... and {len(lines) - 5} more"
            print(f"[ruff] {truncated}", file=sys.stderr)
            sys.exit(2)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # ruff 미설치 또는 타임아웃 시 통과
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
