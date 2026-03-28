"""쇼츠 렌더링 모델."""

from __future__ import annotations

from pydantic import BaseModel


class ShortsWordTimestamp(BaseModel):
    """Remotion 쇼츠용 단어 타임스탬프 (프레임 단위)."""

    word: str
    startFrame: int
    endFrame: int


class ShortsProps(BaseModel):
    """Remotion ShortsComposition에 전달할 props."""

    durationInFrames: int
    hookTitle: str
    hookTitleLine2: str = ""
    subDetail: str = ""
    videoSrc: str  # remotion/public/ 내 상대 경로
    words: list[ShortsWordTimestamp]
    accentColor: str = "#A2FFEB"
    backgroundColor: str = "#0f0f0f"
    hookFontSize: int = 200
    subtitleFontSize: int = 48
    videoCornerRadius: int = 0
