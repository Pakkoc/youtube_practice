"""공용 HTTP 유틸리티."""

from __future__ import annotations

from pathlib import Path

import requests

from shared.lib.file_io import ensure_dir
from shared.lib.logger import get_logger

logger = get_logger()


def download_file(url: str, dest: Path, *, timeout: int = 60) -> Path:
    """URL에서 파일을 다운로드하여 저장.

    Args:
        url: 다운로드 URL.
        dest: 저장할 파일 경로.
        timeout: 요청 타임아웃(초).

    Returns:
        저장된 파일 경로.
    """
    ensure_dir(dest.parent)
    response = requests.get(url, timeout=timeout, stream=True)
    response.raise_for_status()

    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.debug("Downloaded: %s → %s", url, dest)
    return dest
