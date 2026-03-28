"""subprocess 래퍼 — Windows cp949 인코딩 문제 방지.

모든 subprocess 호출에 encoding='utf-8', errors='replace'를 강제합니다.
프로젝트 내에서 subprocess.run / subprocess.Popen 대신 이 모듈을 사용하세요.

    from shared.lib.subprocess import run, Popen
"""

from __future__ import annotations

import subprocess
from subprocess import (  # noqa: F401 — re-export for convenience
    PIPE,
    CalledProcessError,
    CompletedProcess,
    TimeoutExpired,
)
from typing import Any

_ENCODING_DEFAULTS: dict[str, Any] = {
    "encoding": "utf-8",
    "errors": "replace",
}


def run(*args: Any, **kwargs: Any) -> CompletedProcess[str]:
    """subprocess.run 래퍼 (encoding='utf-8' 강제).

    text=True가 설정되지 않았으면 자동으로 추가합니다.
    encoding/errors가 이미 지정됐으면 덮어쓰지 않습니다.
    """
    kwargs.setdefault("text", True)
    for key, value in _ENCODING_DEFAULTS.items():
        kwargs.setdefault(key, value)
    return subprocess.run(*args, **kwargs)


class Popen(subprocess.Popen):  # type: ignore[type-arg]
    """subprocess.Popen 래퍼 (encoding='utf-8' 강제)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("text", True)
        for key, value in _ENCODING_DEFAULTS.items():
            kwargs.setdefault(key, value)
        super().__init__(*args, **kwargs)
