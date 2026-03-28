"""쇼츠 슬라이드 렌더링 모델."""

from __future__ import annotations

from pydantic import BaseModel


class ShortsSlideWordTimestamp(BaseModel):
    """Remotion 쇼츠 슬라이드용 단어 타임스탬프 (프레임 단위)."""

    word: str
    startFrame: int
    endFrame: int


class ShortsSlideProps(BaseModel):
    """Remotion ShortsSlideWrapper에 전달할 props."""

    durationInFrames: int
    hookTitle: str
    hookTitleLine2: str = ""
    subDetail: str = ""
    words: list[ShortsSlideWordTimestamp]
    accentColor: str = "#A2FFEB"
    backgroundColor: str = "#0f0f0f"
    hookFontSize: int = 200
    subtitleFontSize: int = 48
    slideIndex: int = 0
    totalSlides: int = 1


class HookTitleEntry(BaseModel):
    """훅 타이틀 엔트리."""

    index: int
    line1: str
    line2: str = ""
    subDetail: str = ""
