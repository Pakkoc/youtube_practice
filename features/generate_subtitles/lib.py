"""자막 생성 (문단 + 오디오 → SRT)."""

from __future__ import annotations

import re
from pathlib import Path

from entities.audio.model import AudioClip
from entities.script.model import Paragraph
from shared.lib.logger import get_logger

from .model import SubtitleEntry, SubtitleResult

logger = get_logger()


def generate_subtitles(
    paragraphs: list[Paragraph],
    audio_clips: list[AudioClip],
    output_path: Path,
    *,
    max_chars_per_line: int = 25,
    min_chars_per_line: int = 5,
    display_texts: list[str] | None = None,
) -> SubtitleResult:
    """문단과 오디오 클립에서 SRT 자막 파일을 생성.

    각 문단을 짧은 구(phrase) 단위로 분리하고, 오디오 길이를 글자 수에
    비례하여 각 구에 할당합니다.

    Args:
        paragraphs: 문단 목록 (텍스트 포함).
        audio_clips: 오디오 클립 목록 (duration 포함).
        output_path: 출력 SRT 파일 경로.
        max_chars_per_line: 한 줄 최대 글자 수 (기본 20).
        min_chars_per_line: 최소 글자 수, 이하면 병합 (기본 5).
        display_texts: 자막 표시용 정규화된 텍스트 목록. None이면 paragraph.text 사용.

    Returns:
        자막 생성 결과.
    """
    if len(paragraphs) != len(audio_clips):
        raise ValueError(f"문단({len(paragraphs)})과 오디오({len(audio_clips)}) 개수가 다릅니다.")

    if display_texts and len(display_texts) != len(paragraphs):
        logger.warning(
            "display_texts(%d) != paragraphs(%d) — 원본 텍스트 사용",
            len(display_texts),
            len(paragraphs),
        )
        display_texts = None

    entries: list[SubtitleEntry] = []
    current_time = 0.0
    subtitle_index = 1

    for i, (paragraph, clip) in enumerate(zip(paragraphs, audio_clips)):
        # display_texts가 있으면 자막 표시용 텍스트 사용
        subtitle_text = display_texts[i] if display_texts else paragraph.text

        # 문단을 짧은 구 단위로 분리
        phrases = _split_into_phrases(
            subtitle_text,
            max_chars=max_chars_per_line,
            min_chars=min_chars_per_line,
        )

        if not phrases:
            phrases = [subtitle_text]

        # 각 구에 시간 배분 (글자 수 비례)
        total_chars = sum(len(s) for s in phrases)

        for phrase in phrases:
            # 글자 수에 비례하여 duration 계산
            if total_chars > 0:
                ratio = len(phrase) / total_chars
            else:
                ratio = 1.0 / max(len(phrases), 1)

            phrase_duration = clip.duration * ratio
            start_time = current_time
            end_time = current_time + phrase_duration

            entry = SubtitleEntry(
                index=subtitle_index,
                start_time=start_time,
                end_time=end_time,
                text=phrase.strip(),
            )
            entries.append(entry)

            current_time = end_time
            subtitle_index += 1

    # 부동소수점 누적 오차 보정: 마지막 엔트리의 end_time을 전체 duration에 맞춤
    total_audio_duration = sum(clip.duration for clip in audio_clips)
    if entries and abs(current_time - total_audio_duration) > 0.01:
        drift = total_audio_duration - current_time
        logger.debug(
            "자막 duration 보정: %.3f초 drift (%.3f -> %.3f)",
            drift, current_time, total_audio_duration,
        )
        entries[-1] = entries[-1].model_copy(update={"end_time": total_audio_duration})
        current_time = total_audio_duration

    # 자막 간 gap/overlap 검증
    for i in range(1, len(entries)):
        prev_end = entries[i - 1].end_time
        curr_start = entries[i].start_time
        if abs(prev_end - curr_start) > 0.05:
            logger.warning(
                "자막 gap/overlap: #%d end=%.3f, #%d start=%.3f (차이=%.3f초)",
                entries[i - 1].index, prev_end, entries[i].index, curr_start,
                curr_start - prev_end,
            )

    # SRT 파일 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)
    srt_content = _entries_to_srt(entries)
    output_path.write_text(srt_content, encoding="utf-8")

    logger.info("SRT 자막 생성: %s (%d개 항목)", output_path.name, len(entries))

    return SubtitleResult(
        entries=entries,
        srt_path=output_path,
        total_duration=current_time,
    )


def _split_into_phrases(
    text: str,
    *,
    max_chars: int = 20,
    min_chars: int = 5,
) -> list[str]:
    """텍스트를 짧은 구(phrase) 단위로 분리.

    1. 문장 종결 부호(.?!)로 문장 분리
    2. 긴 문장은 쉼표(,) 기준으로 재분할
    3. 그래도 길면 공백 기준으로 max_chars 근처에서 분할
    4. 너무 짧은 구(min_chars 미만)는 다음 구와 병합
    """
    # Step 1: 문장 분리
    pattern = r"(?<=[.?!])\s+"
    sentences = re.split(pattern, text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    # Step 2: 긴 문장 재분할
    phrases: list[str] = []
    for sentence in sentences:
        if len(sentence) <= max_chars:
            phrases.append(sentence)
        else:
            # 쉼표 기준 분할 시도
            sub_phrases = _split_by_comma(sentence, max_chars)
            for sub in sub_phrases:
                if len(sub) <= max_chars:
                    phrases.append(sub)
                else:
                    # 공백 기준으로 max_chars 근처에서 분할
                    phrases.extend(_split_by_space(sub, max_chars))

    # Step 3: 너무 짧은 구 병합
    phrases = _merge_short_phrases(phrases, min_chars)

    return phrases


def _split_by_comma(text: str, max_chars: int) -> list[str]:
    """쉼표 기준으로 분할. 분할 결과가 max_chars 이하가 되도록 인접 조각을 병합."""
    parts = [p.strip() for p in text.split(",") if p.strip()]

    if len(parts) <= 1:
        return [text]

    merged: list[str] = []
    current = parts[0]

    for part in parts[1:]:
        candidate = current + ", " + part
        if len(candidate) <= max_chars:
            current = candidate
        else:
            merged.append(current)
            current = part

    if current:
        merged.append(current)

    return merged


def _split_by_space(text: str, max_chars: int) -> list[str]:
    """공백 기준으로 max_chars 근처에서 분할."""
    words = text.split()
    if not words:
        return [text]

    result: list[str] = []
    current = words[0]

    for word in words[1:]:
        candidate = current + " " + word
        if len(candidate) <= max_chars:
            current = candidate
        else:
            result.append(current)
            current = word

    if current:
        result.append(current)

    return result


def _merge_short_phrases(phrases: list[str], min_chars: int) -> list[str]:
    """min_chars 미만인 구를 인접 구와 병합."""
    if not phrases:
        return phrases

    merged: list[str] = []

    for phrase in phrases:
        if merged and len(phrase) < min_chars:
            # 이전 구에 병합
            merged[-1] = merged[-1] + " " + phrase
        elif merged and len(merged[-1]) < min_chars:
            # 이전 구가 짧으면 현재 구를 이전에 병합
            merged[-1] = merged[-1] + " " + phrase
        else:
            merged.append(phrase)

    return merged


def _entries_to_srt(entries: list[SubtitleEntry]) -> str:
    """SubtitleEntry 목록을 SRT 형식 문자열로 변환."""
    lines: list[str] = []

    for entry in entries:
        lines.append(str(entry.index))
        lines.append(f"{_format_time(entry.start_time)} --> {_format_time(entry.end_time)}")
        lines.append(entry.text)
        lines.append("")  # 빈 줄로 구분

    return "\n".join(lines)


def _format_time(seconds: float) -> str:
    """초를 SRT 시간 형식(HH:MM:SS,mmm)으로 변환."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
