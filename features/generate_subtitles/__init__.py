"""자막 생성 feature."""

from .lib import generate_subtitles
from .model import SubtitleEntry, SubtitleResult

__all__ = ["generate_subtitles", "SubtitleEntry", "SubtitleResult"]
