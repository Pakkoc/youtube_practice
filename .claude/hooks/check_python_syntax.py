"""PostToolUse hook: Python 파일 편집 후 문법 검사.

stdin으로 hook input JSON을 받아서 .py 파일이면 py_compile로 검사.
exit 0 = 통과, exit 2 = 블로킹 (Claude에게 오류 표시).
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
    file_path = file_path.replace("\\", "/")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", file_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if result.returncode != 0:
            print(f"Syntax error in {file_path}:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(2)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # Fail open — don't block on tool errors
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
