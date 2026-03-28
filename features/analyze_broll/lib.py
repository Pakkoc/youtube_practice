"""B-roll 구간 분석 핵심 로직."""

from __future__ import annotations

import json
from pathlib import Path

from entities.audio.model import AudioClip
from entities.script.model import Paragraph
from shared.lib.logger import get_logger

from .api import group_paragraphs_into_scenes
from .model import BrollItem, BrollPlan, SceneGroup

logger = get_logger()


def load_broll_prompts(
    prompts_path: Path,
    audio_clips: list[AudioClip],
) -> tuple[BrollPlan, list[SceneGroup]]:
    """사전 생성된 prompts.json에서 BrollPlan + SceneGroup을 로드.

    Skill이 생성한 prompts.json을 읽고, audio_clips로 timing을 주입합니다.
    prompts.json에는 timing 정보가 없으므로 (TTS 이전에 생성되기 때문),
    audio_clips의 cumulative duration으로 start_time을 계산합니다.

    Args:
        prompts_path: prompts.json 파일 경로.
        audio_clips: TTS 생성 후 오디오 클립 리스트 (timing 계산용).

    Returns:
        (BrollPlan, list[SceneGroup]) 튜플.

    Raises:
        FileNotFoundError: prompts.json이 없을 때.
        ValueError: JSON 스키마가 유효하지 않을 때.
    """
    raw = json.loads(prompts_path.read_text(encoding="utf-8"))

    # 버전 검증
    version = raw.get("version", 0)
    if version != 1:
        raise ValueError(f"prompts.json version {version} is not supported (expected 1)")

    items_raw = raw.get("items", [])
    if not items_raw:
        raise ValueError("prompts.json has no items")

    # paragraph_index 순서로 정렬
    items_raw.sort(key=lambda x: x["paragraph_index"])

    # audio_clips로 timing 계산 (generate_paragraph_broll_plan과 동일 로직)
    # paragraph_index -> AudioClip 매핑
    clip_map: dict[int, AudioClip] = {c.index: c for c in audio_clips}

    cumulative_time = 0.0
    broll_items: list[BrollItem] = []

    for item_data in items_raw:
        para_idx = item_data["paragraph_index"]
        clip = clip_map.get(para_idx)
        clip_duration = clip.duration if clip else 0.0

        # B-roll을 음성 중간 타이밍에 배치
        start_time = cumulative_time + clip_duration / 2 - 1.5

        hours = int(start_time // 3600)
        minutes = int((start_time % 3600) // 60)
        seconds = start_time % 60
        start_time_str = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

        broll_items.append(
            BrollItem(
                start_time=start_time_str,
                duration=item_data.get("duration", 3),
                keyword=item_data["keyword"],
                source=item_data.get("source", "generate"),
                reason=item_data.get("reason", ""),
                context_chunk=item_data.get("context_chunk", ""),
                paragraph_index=para_idx,
                scene_group_id=item_data.get("scene_group_id"),
            )
        )

        cumulative_time += clip_duration

    plan = BrollPlan(broll_items=broll_items)

    # SceneGroup 로드
    scene_groups: list[SceneGroup] = []
    for sg_data in raw.get("scene_groups", []):
        scene_groups.append(
            SceneGroup(
                group_id=sg_data["group_id"],
                paragraph_indices=sg_data["paragraph_indices"],
                representative_index=sg_data["representative_index"],
                reason=sg_data.get("reason", ""),
            )
        )

    logger.info(
        "prompts.json 로드 완료: %d개 항목, %d개 씬 그룹",
        len(broll_items),
        len(scene_groups),
    )
    return plan, scene_groups


def generate_paragraph_broll_plan(
    paragraphs: list[Paragraph],
    audio_clips: list[AudioClip],
    character_description: str = "",
    *,
    enable_image_search: bool = True,
    source_decision_model: str = "gpt-5-nano",
    image_gen_backend: str | None = None,
) -> BrollPlan:
    """문단 기반 B-roll 계획을 생성 (1:1:1 매핑).

    문단 1개 = 슬라이드 1개 = 음성 1개 = B-roll 이미지 1개.
    컨텍스트는 ±1 문단으로 통일 (dual-context 없음).

    Args:
        paragraphs: 대본 문단 리스트.
        audio_clips: 각 문단에 대응하는 오디오 클립 리스트.
        character_description: 캐릭터 설명 (FLUX.2 프롬프트용).
        enable_image_search: 이미지 검색 기능 활성화 (기본 True).
        source_decision_model: source 판단에 사용할 모델.
        image_gen_backend: 이미지 생성 백엔드 (프롬프트 템플릿 선택에 사용).

    Returns:
        BrollPlan.
    """
    from .api import decide_broll_sources, enhance_broll_prompts

    items: list[BrollItem] = []

    # audio_clips의 duration 누적합으로 각 문단의 시작 시간 계산
    cumulative_time = 0.0

    for idx, paragraph in enumerate(paragraphs):
        # 해당 문단의 오디오 클립 찾기
        clip = next((c for c in audio_clips if c.index == paragraph.index), None)
        clip_duration = clip.duration if clip else 0.0

        # B-roll을 각 음성의 **중간 타이밍**에 배치
        # 음성이 [cumulative_time, cumulative_time + clip_duration]일 때
        # 3초 B-roll이 정확히 음성 중간점에 걸쳐지도록
        start_time = cumulative_time + clip_duration / 2 - 1.5

        # 시간 포맷 변환
        hours = int(start_time // 3600)
        minutes = int((start_time % 3600) // 60)
        seconds = start_time % 60
        start_time_str = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

        # ±1 문단 컨텍스트 생성
        context = _get_paragraph_context(paragraphs, idx, stride=1)

        # 간단한 키워드 (나중에 enhance로 강화됨)
        keyword = f"scene {idx + 1}: {paragraph.text[:50]}"

        items.append(
            BrollItem(
                start_time=start_time_str,
                duration=3,
                keyword=keyword,
                source="generate",
                reason=f"paragraph {idx + 1}",
                context_chunk=context,
                paragraph_index=paragraph.index,
            )
        )

        cumulative_time += clip_duration

    plan = BrollPlan(broll_items=items)
    logger.info(
        "문단 기반 B-roll 계획: %d개 (1:1:1 매핑)",
        len(items),
    )

    # 1. 이미지 검색 활성화 시 source 판단 (generate vs search)
    if enable_image_search:
        plan = decide_broll_sources(plan, model=source_decision_model)

    # 2. generate로 분류된 항목만 프롬프트 강화
    if character_description:
        generate_items = [item for item in plan.broll_items if item.source == "generate"]
        if generate_items:
            generate_plan = BrollPlan(broll_items=generate_items)
            enhanced_plan = enhance_broll_prompts(
                generate_plan, character_description, backend=image_gen_backend
            )

            enhanced_map = {item.start_time: item.keyword for item in enhanced_plan.broll_items}

            updated_items = []
            for item in plan.broll_items:
                if item.source == "generate" and item.start_time in enhanced_map:
                    updated_items.append(
                        item.model_copy(update={"keyword": enhanced_map[item.start_time]})
                    )
                else:
                    updated_items.append(item)

            plan = BrollPlan(broll_items=updated_items)

    # B-roll 통계
    search_count = sum(1 for item in plan.broll_items if item.source == "search")
    generate_count = len(plan.broll_items) - search_count
    if enable_image_search:
        logger.info("  - 검색: %d개, 생성: %d개", search_count, generate_count)

    return plan


def apply_scene_grouping(
    plan: BrollPlan,
    paragraphs: list[Paragraph],
    *,
    model: str = "gpt-5-mini",
) -> tuple[BrollPlan, list[SceneGroup]]:
    """BrollPlan에 씬 그룹핑을 적용.

    연속 문단을 시각적 장면으로 그룹핑하여 각 BrollItem에 scene_group_id를 설정합니다.
    같은 그룹의 문단은 대표 이미지 1개를 공유합니다.

    Args:
        plan: 기존 BrollPlan (generate_paragraph_broll_plan 결과).
        paragraphs: 대본 문단 리스트.
        model: 씬 그룹핑에 사용할 LLM 모델.

    Returns:
        (업데이트된 BrollPlan, SceneGroup 리스트) 튜플.
    """
    raw_groups = group_paragraphs_into_scenes(paragraphs, model=model)

    scene_groups = [
        SceneGroup(
            group_id=g["group_id"],
            paragraph_indices=g["paragraph_indices"],
            representative_index=g["representative_index"],
            reason=g.get("reason", ""),
        )
        for g in raw_groups
    ]

    # paragraph_index -> group_id 매핑
    para_to_group: dict[int, int] = {}
    for sg in scene_groups:
        for pi in sg.paragraph_indices:
            para_to_group[pi] = sg.group_id

    # BrollItem에 scene_group_id 설정
    updated_items = []
    for item in plan.broll_items:
        gid = para_to_group.get(item.paragraph_index) if item.paragraph_index else None
        updated_items.append(item.model_copy(update={"scene_group_id": gid}))

    updated_plan = BrollPlan(broll_items=updated_items)

    # 절감 통계 로그
    total = len(paragraphs)
    groups = len(scene_groups)
    saved_pct = (1 - groups / total) * 100 if total > 0 else 0
    logger.info(
        "씬 그룹핑 적용: %d개 문단 -> %d개 씬 (%.0f%% 절감)",
        total,
        groups,
        saved_pct,
    )

    return updated_plan, scene_groups


def _get_paragraph_context(
    paragraphs: list[Paragraph],
    current_idx: int,
    stride: int = 1,
) -> str:
    """±stride 범위 문단 컨텍스트. 현재 문단은 【】 표시.

    Args:
        paragraphs: 문단 리스트.
        current_idx: 현재 문단 인덱스 (0-based).
        stride: 앞뒤로 포함할 문단 수.

    Returns:
        컨텍스트 문자열.
    """
    parts: list[str] = []
    start = max(0, current_idx - stride)
    end = min(len(paragraphs), current_idx + stride + 1)

    for i in range(start, end):
        if i == current_idx:
            parts.append(f"【{paragraphs[i].text}】")
        else:
            parts.append(paragraphs[i].text)

    return " ".join(parts)
