"""문단을 문장 단위 씬으로 분할하는 핵심 로직."""

from __future__ import annotations

import re

from entities.scene.model import Scene
from entities.script.model import Paragraph

# 한국어 문장 종결 패턴: ~다. ~요. ~죠. ~까? ~야! 등
_SENTENCE_END_RE = re.compile(
    r"(?<=[다요죠까니자임음됨함습것들란면서며고도지만네세라려워])[.?!]"
    r"|(?<=[.?!])\s+"
)


def _split_into_sentences(text: str) -> list[str]:
    """텍스트를 한국어 문장 종결 패턴으로 분할.

    마침표, 물음표, 느낌표 뒤에서 분할하되,
    종결어미 패턴(다/요/죠 등) 뒤의 문장부호를 기준으로 함.
    """
    # 문장 종결 패턴 위치를 찾아 분할
    parts: list[str] = []
    last_end = 0

    for match in re.finditer(
        r"[다요죠까니자임음됨함습것들란면서며고도지만네세라려워][.?!]",
        text,
    ):
        end = match.end()
        sentence = text[last_end:end].strip()
        if sentence:
            parts.append(sentence)
        last_end = end

    # 마지막 잔여 텍스트
    remainder = text[last_end:].strip()
    if remainder:
        if parts:
            # 잔여가 짧으면 마지막 문장에 병합
            parts[-1] = parts[-1] + " " + remainder
        else:
            parts.append(remainder)

    return parts if parts else [text.strip()]


def _merge_short_sentences(
    sentences: list[str],
    merge_threshold: int = 30,
) -> list[str]:
    """짧은 문장을 인접 문장과 병합.

    merge_threshold 미만 글자수의 문장은 이전 문장과 병합.
    첫 문장이 짧으면 다음 문장과 병합.
    """
    if len(sentences) <= 1:
        return sentences

    merged: list[str] = []

    for sentence in sentences:
        if len(sentence) < merge_threshold and merged:
            # 짧은 문장 -> 이전 결과에 병합
            merged[-1] = merged[-1] + " " + sentence
        else:
            merged.append(sentence)

    # 첫 문장이 매우 짧으면 다음 문장과 병합 (앞에 병합할 대상이 없었으므로)
    _FORWARD_MERGE_LIMIT = 12
    if len(merged) > 1 and len(merged[0]) < _FORWARD_MERGE_LIMIT:
        merged[1] = merged[0] + " " + merged[1]
        merged.pop(0)

    return merged


def split_paragraphs_into_scenes(
    paragraphs: list[Paragraph],
    merge_threshold: int = 30,
) -> list[Scene]:
    """문단 목록을 문장 단위 씬으로 분할.

    Args:
        paragraphs: 문단 목록 (1-based index).
        merge_threshold: 이 글자수 미만 문장은 인접 문장과 병합.

    Returns:
        전체 씬 목록 (연속 인덱싱, 1-based).
    """
    scenes: list[Scene] = []
    scene_index = 1

    for paragraph in paragraphs:
        sentences = _split_into_sentences(paragraph.text)
        sentences = _merge_short_sentences(sentences, merge_threshold)

        for sentence in sentences:
            scenes.append(
                Scene(
                    index=scene_index,
                    paragraph_index=paragraph.index,
                    text=sentence,
                )
            )
            scene_index += 1

    return scenes
