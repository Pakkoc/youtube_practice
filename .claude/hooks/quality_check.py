"""Stop hook: 세션 중 수정된 .py 파일에 ruff check + mypy 실행.

modifications.log를 읽어 수정된 .py 파일 목록을 추출하고,
ruff check와 mypy를 실행한다.

변경 사항:
- ruff: 수정된 파일만 검사 (전체 프로젝트 lint 금지)
- mypy: non-blocking (경고만 표시)
- 존재하지 않는 파일 자동 스킵
- encoding UTF-8 명시

exit 0 = 통과, exit 2 = 블로킹.
"""

import os
import subprocess
import sys

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_PATH = os.path.join(LOG_DIR, "modifications.log")

# mypy 검사 대상 디렉토리 (FSD 아키텍처 핵심 레이어)
MYPY_TARGET_PREFIXES = ("app", "shared", "entities", "features", "pipelines")


def _is_manim_slide(path: str) -> bool:
    """Manim 슬라이드 파일 여부 (projects/*/slides/*.py)."""
    normalized = path.replace("\\", "/")
    return "/projects/" in normalized and "/slides/" in normalized


def _read_modified_py_files() -> list[str]:
    """modifications.log에서 .py 파일 경로만 추출 (중복 제거)."""
    if not os.path.exists(LOG_PATH):
        return []

    seen: set[str] = set()
    files: list[str] = []
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) < 3:
                    continue
                file_path = parts[2]
                if not file_path.endswith(".py"):
                    continue
                # Normalize path
                normalized = file_path.replace("\\", "/")
                abs_path = os.path.abspath(normalized)
                if abs_path not in seen and os.path.exists(abs_path):
                    seen.add(abs_path)
                    # Skip Manim slide files
                    if not _is_manim_slide(abs_path):
                        files.append(abs_path)
    except (OSError, UnicodeDecodeError):
        pass
    return files


def _clear_log():
    """검사 완료 후 로그 클리어."""
    try:
        os.remove(LOG_PATH)
    except OSError:
        pass


def _find_tool(name: str) -> list[str]:
    """프로젝트 uv 환경에서 도구 실행 명령을 결정."""
    try:
        subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            timeout=5,
        )
        return ["uv", "run", name]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return [name]


def _run_ruff(files: list[str]) -> tuple[bool, str]:
    """ruff check on modified files only (not whole project)."""
    try:
        result = subprocess.run(
            [*_find_tool("ruff"), "check", *files],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if result.returncode != 0:
            return False, (result.stdout or "") + (result.stderr or "")
        return True, ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return True, ""


def _run_mypy(files: list[str]) -> tuple[bool, str]:
    """mypy 실행 (핵심 디렉토리 파일만, non-blocking)."""
    target_files = []
    for f in files:
        normalized = f.replace("\\", "/")
        for prefix in MYPY_TARGET_PREFIXES:
            if f"/{prefix}/" in normalized or normalized.startswith(f"{prefix}/"):
                target_files.append(f)
                break

    if not target_files:
        return True, ""

    project_root = os.getcwd()
    cmd = [*_find_tool("mypy"), "--ignore-missing-imports"]
    for f in target_files:
        rel = os.path.relpath(f, project_root).replace("\\", "/")
        mod = rel.removesuffix(".py").replace("/", ".")
        if mod.endswith(".__init__"):
            mod = mod.removesuffix(".__init__")
        cmd.extend(["-m", mod])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
        )
        if result.returncode != 0:
            return False, (result.stdout or "") + (result.stderr or "")
        return True, ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return True, ""


def main():
    files = _read_modified_py_files()
    if not files:
        _clear_log()
        sys.exit(0)

    has_errors = False

    ruff_ok, ruff_output = _run_ruff(files)
    if not ruff_ok:
        # Show errors but truncate for readability
        lines = ruff_output.strip().splitlines()
        truncated = "\n".join(lines[:15])
        if len(lines) > 15:
            truncated += f"\n... and {len(lines) - 15} more lines"
        print(f"[ruff] Lint errors in modified files:\n{truncated}", file=sys.stderr)
        has_errors = True

    # mypy: always non-blocking (warn only)
    mypy_ok, mypy_output = _run_mypy(files)
    if not mypy_ok:
        lines = mypy_output.strip().splitlines()
        truncated = "\n".join(lines[:10])
        if len(lines) > 10:
            truncated += f"\n... and {len(lines) - 10} more lines"
        print(f"[mypy] Type warnings (non-blocking):\n{truncated}", file=sys.stderr)

    _clear_log()

    if has_errors:
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
