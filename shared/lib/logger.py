"""로깅 설정 모듈."""

from __future__ import annotations

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler

_console = Console(stderr=True)


def setup_logger(
    name: str = "video-automation",
    level: int = logging.INFO,
    *,
    rich_output: bool = True,
) -> logging.Logger:
    """애플리케이션 로거를 설정하여 반환.

    Args:
        name: 로거 이름.
        level: 로그 레벨.
        rich_output: Rich 포맷팅 사용 여부.

    Returns:
        설정된 Logger 인스턴스.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    if rich_output:
        handler = RichHandler(
            console=_console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    logger.addHandler(handler)
    return logger


def get_logger(name: str = "video-automation") -> logging.Logger:
    """기존 로거를 가져온다. 없으면 기본 설정으로 생성."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
