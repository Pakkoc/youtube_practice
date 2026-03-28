"""Claude API를 이용한 B-roll 구간 분석."""

from __future__ import annotations

import json
import math
from typing import TYPE_CHECKING

from shared.api.claude import ask
from shared.constants import PROMPTS_DIR
from shared.lib.file_io import read_text
from shared.lib.logger import get_logger

if TYPE_CHECKING:
    from entities.script.model import Paragraph

    from .model import BrollPlan

logger = get_logger()

_ENHANCE_PROMPT_PATH = PROMPTS_DIR / "broll_prompt_enhancement.txt"
_ENHANCE_PROMPT_KONTEXT_PATH = PROMPTS_DIR / "broll_prompt_enhancement_kontext.txt"
_SOURCE_DECISION_PROMPT_PATH = PROMPTS_DIR / "broll_source_decision.txt"
_SCENE_GROUPING_PROMPT_PATH = PROMPTS_DIR / "broll_scene_grouping.txt"


def _extract_json(text: str) -> str:
    """응답에서 JSON 객체 또는 배열을 추출."""
    if "```json" in text:
        start = text.index("```json") + len("```json")
        end = text.index("```", start)
        return text[start:end].strip()
    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        return text[start:end].strip()
    # JSON 배열 또는 객체 감지
    if "[" in text and "]" in text:
        arr_start = text.index("[")
        arr_end = text.rindex("]") + 1
        if "{" in text:
            obj_start = text.index("{")
            if arr_start < obj_start:
                return text[arr_start:arr_end]
        else:
            return text[arr_start:arr_end]
    start = text.index("{")
    end = text.rindex("}") + 1
    return text[start:end]


def enhance_broll_prompts(
    plan: BrollPlan,
    character_description: str,
    *,
    backend: str | None = None,
) -> BrollPlan:
    """B-roll 키워드를 이미지 생성용 상세 프롬프트로 변환.

    Args:
        plan: B-roll 계획 (단순 키워드 포함).
        character_description: 캐릭터 설명 (프롬프트에 포함됨).
        backend: 이미지 생성 백엔드 (None=기본, "flux_kontext"=Kontext 전용 템플릿).

    Returns:
        프롬프트가 강화된 BrollPlan.
    """
    from .model import BrollItem
    from .model import BrollPlan as BrollPlanModel

    if not character_description:
        logger.warning("캐릭터 설명이 없어 프롬프트 강화를 건너뜁니다.")
        return plan

    if not plan.broll_items:
        return plan

    # B-roll 항목을 JSON으로 변환 (context_chunk 포함)
    items_for_prompt = [
        {
            "index": i,
            "keyword": item.keyword,
            "reason": item.reason,
            "context_chunk": item.context_chunk,  # 해당 시점 주변 대본 컨텍스트
        }
        for i, item in enumerate(plan.broll_items)
    ]

    # 백엔드에 따라 프롬프트 템플릿 선택
    if backend == "flux_kontext":
        template_path = _ENHANCE_PROMPT_KONTEXT_PATH
    else:
        template_path = _ENHANCE_PROMPT_PATH

    prompt_template = read_text(template_path)

    # 항목 수가 많으면 배치로 분할 (40개 단위)
    batch_size = 40
    all_items = plan.broll_items
    total = len(all_items)

    if total <= batch_size:
        batches = [items_for_prompt]
    else:
        batches = []
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batches.append(items_for_prompt[start:end])
        logger.info(
            "B-roll 프롬프트 강화: %d개 항목을 %d개 배치로 분할",
            total,
            len(batches),
        )

    all_enhanced: list[dict] = []
    for batch_idx, batch in enumerate(batches):
        batch_prompt = prompt_template.format(
            character_description=character_description,
            broll_items_json=json.dumps(batch, ensure_ascii=False, indent=2),
        )
        estimated_tokens = len(batch) * 180 + 512
        max_tok = max(4096, estimated_tokens)

        logger.info(
            "Claude B-roll 프롬프트 강화 요청 중... (배치 %d/%d, %d개 항목, max_tokens=%d)",
            batch_idx + 1,
            len(batches),
            len(batch),
            max_tok,
        )
        response = ask(batch_prompt, max_tokens=max_tok, timeout=300.0)

        try:
            cleaned = _extract_json(response)
            enhanced_list = json.loads(cleaned)
            all_enhanced.extend(enhanced_list)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error("배치 %d 프롬프트 강화 실패, 원본 유지: %s", batch_idx + 1, e)

    # 강화된 프롬프트로 BrollItem 업데이트
    enhanced_items: list[BrollItem] = []
    for item in all_items:
        # 원본 복사
        new_item = BrollItem(
            start_time=item.start_time,
            duration=item.duration,
            keyword=item.keyword,
            source=item.source,
            reason=item.reason,
        )

        # 해당 인덱스의 강화된 프롬프트 찾기
        for enhanced in all_enhanced:
            if enhanced.get("original_keyword") == item.keyword:
                new_item.keyword = enhanced.get("enhanced_prompt", item.keyword)
                break

        enhanced_items.append(new_item)

    logger.info("B-roll 프롬프트 강화 완료 (%d개)", len(enhanced_items))
    return BrollPlanModel(broll_items=enhanced_items)


def decide_broll_sources(
    plan: BrollPlan,
    *,
    model: str = "gpt-5-nano",
) -> BrollPlan:
    """각 B-roll 항목의 이미지 소스(generate/search)를 결정.

    컨텍스트를 분석하여 실제 존재하는 대상(제품, 장소 등)은 search,
    추상적 개념이나 캐릭터는 generate로 분류합니다.

    Args:
        plan: B-roll 계획.
        model: 사용할 모델 (기본: gpt-4.1-nano, 비용 효율적).

    Returns:
        source와 search_query가 업데이트된 BrollPlan.
    """
    from .model import BrollItem
    from .model import BrollPlan as BrollPlanModel

    if not plan.broll_items:
        return plan

    # B-roll 항목을 JSON으로 변환
    items_for_prompt = [
        {
            "index": i,
            "keyword": item.keyword,
            "context_chunk": item.context_chunk,
        }
        for i, item in enumerate(plan.broll_items)
    ]

    prompt_template = read_text(_SOURCE_DECISION_PROMPT_PATH)
    prompt = prompt_template.format(
        broll_items_json=json.dumps(items_for_prompt, ensure_ascii=False, indent=2),
    )

    logger.info("B-roll 소스 판단 요청 중... (%d개 항목, 모델: %s)", len(plan.broll_items), model)
    response = ask(prompt, model=model)

    try:
        cleaned = _extract_json(response)
        decisions = json.loads(cleaned)

        # 결정 결과로 BrollItem 업데이트
        updated_items: list[BrollItem] = []
        for item in plan.broll_items:
            new_item = BrollItem(
                start_time=item.start_time,
                duration=item.duration,
                keyword=item.keyword,
                source=item.source,
                reason=item.reason,
                context_chunk=item.context_chunk,
            )

            # 해당 인덱스의 결정 찾기
            for decision in decisions:
                if decision.get("index") == plan.broll_items.index(item):
                    new_source = decision.get("source", "generate")
                    new_item.source = new_source

                    # search인 경우 search_query를 keyword에 저장 (나중에 검색에 사용)
                    if new_source == "search":
                        search_query = decision.get("search_query", "")
                        if search_query:
                            # 원본 keyword 보존, search_query 추가
                            new_item.keyword = search_query
                            new_item.reason = f"search: {decision.get('reason', '')}"

                    logger.debug(
                        "B-roll #%d: %s → %s",
                        decision.get("index"),
                        "search" if new_source == "search" else "generate",
                        new_item.keyword[:50] if new_source == "search" else "(will enhance)",
                    )
                    break

            updated_items.append(new_item)

        # 통계 로그
        search_count = sum(1 for item in updated_items if item.source == "search")
        generate_count = len(updated_items) - search_count
        logger.info(
            "B-roll 소스 판단 완료: %d개 검색, %d개 생성",
            search_count,
            generate_count,
        )

        return BrollPlanModel(broll_items=updated_items)

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error("소스 판단 실패, 모두 generate로 처리: %s", e)
        return plan


def group_paragraphs_into_scenes(
    paragraphs: list[Paragraph],
    *,
    model: str = "gpt-5-mini",
) -> list[dict]:
    """연속 문단을 시각적 장면(scene)으로 그룹핑.

    LLM이 문단 내용을 분석하여 같은 주제/장면의 연속 문단을 묶습니다.
    같은 씬의 문단은 동일한 B-roll 이미지를 공유합니다.

    Args:
        paragraphs: 대본 문단 리스트.
        model: 사용할 모델 (기본: gpt-5-nano).

    Returns:
        씬 그룹 딕셔너리 리스트.
        [{"group_id": 1, "paragraph_indices": [1,2,3], "representative_index": 2, "reason": "..."}]
    """
    if len(paragraphs) <= 2:
        return _fallback_grouping(paragraphs)

    # 문단 텍스트 준비 (앞 100자)
    lines = []
    for p in paragraphs:
        truncated = p.text[:100] + ("..." if len(p.text) > 100 else "")
        lines.append(f"{p.index}. {truncated}")
    paragraphs_text = "\n".join(lines)

    # 그룹 수 범위 계산
    n = len(paragraphs)
    min_groups = max(2, math.ceil(n / 3))
    max_groups = max(min_groups, math.ceil(n * 2 / 3))

    prompt_template = read_text(_SCENE_GROUPING_PROMPT_PATH)
    prompt = prompt_template.format(
        paragraphs_text=paragraphs_text,
        min_groups=min_groups,
        max_groups=max_groups,
    )

    logger.info(
        "씬 그룹핑 요청: %d개 문단 → %d~%d개 그룹 (모델: %s)",
        n,
        min_groups,
        max_groups,
        model,
    )
    # 그룹당 ~80토큰 예상 + JSON 오버헤드
    estimated_tokens = max_groups * 80 + 512
    max_tok = max(8192, estimated_tokens)
    response = ask(prompt, model=model, max_tokens=max_tok, timeout=300.0)

    try:
        cleaned = _extract_json(response)
        groups = json.loads(cleaned)

        # 검증: 모든 paragraph index가 정확히 1번 등장하는지
        expected_indices = {p.index for p in paragraphs}
        seen_indices: set[int] = set()
        for group in groups:
            for idx in group["paragraph_indices"]:
                if idx in seen_indices:
                    logger.warning("씬 그룹핑: 중복 인덱스 %d, fallback 사용", idx)
                    return _fallback_grouping(paragraphs)
                seen_indices.add(idx)

        if seen_indices != expected_indices:
            missing = expected_indices - seen_indices
            extra = seen_indices - expected_indices
            logger.warning(
                "씬 그룹핑: 인덱스 불일치 (누락: %s, 초과: %s), fallback 사용",
                missing,
                extra,
            )
            return _fallback_grouping(paragraphs)

        # 연속성 검증
        for group in groups:
            indices = sorted(group["paragraph_indices"])
            if indices != list(range(indices[0], indices[-1] + 1)):
                logger.warning("씬 그룹핑: 비연속 인덱스 %s, fallback 사용", indices)
                return _fallback_grouping(paragraphs)

            # representative_index가 그룹 내에 있는지 확인
            if group["representative_index"] not in indices:
                group["representative_index"] = indices[0]

        logger.info("씬 그룹핑 완료: %d개 그룹", len(groups))
        return groups

    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        logger.error("씬 그룹핑 실패, fallback 사용: %s", e)
        return _fallback_grouping(paragraphs)


def _fallback_grouping(paragraphs: list[Paragraph]) -> list[dict]:
    """LLM 실패 시 1:1 매핑 fallback (각 문단이 독립 씬)."""
    return [
        {
            "group_id": i + 1,
            "paragraph_indices": [p.index],
            "representative_index": p.index,
            "reason": "fallback (1:1)",
        }
        for i, p in enumerate(paragraphs)
    ]
