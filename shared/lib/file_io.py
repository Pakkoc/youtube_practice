"""파일 I/O 유틸리티."""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """디렉토리가 존재하지 않으면 생성한다.

    Args:
        path: 확보할 디렉토리 경로.

    Returns:
        생성된(또는 이미 존재하는) 디렉토리 경로.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """텍스트 파일을 읽어서 문자열로 반환."""
    return path.read_text(encoding=encoding)


def write_text(path: Path, content: str, encoding: str = "utf-8") -> Path:
    """텍스트 파일을 작성한다. 부모 디렉토리가 없으면 생성.

    Returns:
        작성된 파일 경로.
    """
    ensure_dir(path.parent)
    path.write_text(content, encoding=encoding)
    return path


def list_files(directory: Path, pattern: str = "*") -> list[Path]:
    """디렉토리 내 파일을 패턴으로 검색, 이름순 정렬하여 반환."""
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern))
