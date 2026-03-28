# B-roll 아키텍처

> 소스: `features/analyze_broll/lib.py`, `features/analyze_broll/api.py`

## 문단 기반 1:1:1 매핑

```
문단 1개 = 슬라이드 1개 = TTS 1개 = B-roll 이미지 1개
```

- 이전의 interval 기반 시스템에서 문단 기반으로 변경됨
- `generate_paragraph_broll_plan()` in `features/analyze_broll/lib.py`

## 컨텍스트 윈도우

- **범위**: 현재 문단 ± 1 문단
- `_get_paragraph_context()`: 현재 문단을 【brackets】로 표시

```
이전 문단 텍스트

【현재 문단 텍스트 (B-roll 대상)】

다음 문단 텍스트
```

## 소스 결정 흐름

```
문단 텍스트 + 컨텍스트
  → gpt-5-nano (decide_broll_sources)
    → "generate" (추상적 개념, 캐릭터, 비유)
    → "search" (실제 제품, 장소, 인물)
```

- `features/analyze_broll/api.py` → `decide_broll_sources()`
- `image_search.enabled: true` 일 때만 search 가능
- `false`면 전부 generate

## 프롬프트 강화

- `prompts/broll_prompt_enhancement.txt` -- 일반 백엔드용
- `prompts/broll_prompt_enhancement_kontext.txt` -- Kontext 백엔드 전용
- `character_description` 주입 -- 일관된 캐릭터 스타일 유지

## 모델

- `BrollItem`: `{start_time, duration, keyword, source, reason, context_chunk}`
- `BrollPlan`: `{broll_items: list[BrollItem]}`

## B-roll → 슬라이드 배경 주입

- B-roll 이미지는 Remotion 슬라이드의 배경으로 사용 (20% opacity)
- `remotion/public/_bg_*`에 복사 → props의 `backgroundImage`로 참조
