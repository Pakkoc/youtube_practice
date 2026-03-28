"""PostToolUse hook: Write/Edit 후 수정된 파일 경로를 로그에 기록.

Stop 이벤트의 quality_check.py가 이 로그를 읽어 ruff/mypy를 실행한다.
exit 0 = 항상 통과 (비차단).
"""

import json
import os
import sys
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_PATH = os.path.join(LOG_DIR, "modifications.log")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, UnicodeDecodeError):
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Normalize to POSIX path
    file_path = file_path.replace("\\", "/")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tool_name = data.get("tool_name", "unknown")

    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}\t{tool_name}\t{file_path}\n")
    except OSError:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
