"""자막 엔티티 모델."""

from __future__ import annotations

from pydantic import BaseModel


class WordTimestamp(BaseModel):
    """Whisper word-level timestamp."""

    word: str
    start: float  # seconds
    end: float  # seconds


class SubtitleSegment(BaseModel):
    """단일 자막 세그먼트."""

    index: int
    start: float  # 시작 시간(초)
    end: float  # 종료 시간(초)
    text: str


class SubtitleTrack(BaseModel):
    """자막 트랙 전체."""

    segments: list[SubtitleSegment] = []

    def to_srt(self) -> str:
        """SRT 형식 문자열로 변환."""
        lines: list[str] = []
        for seg in self.segments:
            lines.append(str(seg.index))
            start = _format_srt_time(seg.start)
            end = _format_srt_time(seg.end)
            lines.append(f"{start} --> {end}")
            lines.append(seg.text)
            lines.append("")
        return "\n".join(lines)


def _format_srt_time(seconds: float) -> str:
    """초를 SRT 타임스탬프로 변환 (HH:MM:SS,mmm)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
