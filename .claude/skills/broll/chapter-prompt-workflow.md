# B-roll 프롬프트 생성 워크플로

Claude Code가 직접 scene grouping, source decision, prompt enhancement를 수행하여 `broll/prompts.json`에 저장.
파이프라인은 이 파일을 감지하면 API 호출을 건너뛰고 이미지 생성만 수행.

## 전체 흐름

```
paragraphs/*.txt + config/config.base.yaml + prompts/*.txt
  → Step 1: 프로젝트 확인
  → Step 2: Config + 가이드라인 읽기
  → Step 3: Scene grouping
  → Step 4: Source decision
  → Step 5: Prompt enhancement
  → broll/prompts.json
```

## Step 1: 프로젝트 확인

1. `projects/$PROJECT/` 디렉토리 존재 확인
2. `projects/$PROJECT/paragraphs/*.txt` 전체 읽기
3. 기존 `broll/prompts.json` 존재 시 → skip (기존 파일 유지). 재생성 필요하면 사용자가 명시적으로 삭제 후 요청

## Step 2: Config + 가이드라인 읽기

### Config

`config/config.base.yaml`에서 추출:
- `broll.character_description` — 캐릭터 설명
- `broll.force_backend` — 백엔드 (프롬프트 스타일 결정)
- `pipeline.broll.scene_grouping` — 씬 그룹핑 활성화
- `broll.image_search.enabled` — 이미지 검색 활성화

### 프롬프트 가이드라인 (참조용)

- flux_kontext: `prompts/broll_prompt_enhancement_kontext.txt`
- 그 외: `prompts/broll_prompt_enhancement.txt`
- `prompts/broll_source_decision.txt`
- `prompts/broll_scene_grouping.txt`

## Step 3: Scene Grouping

연속 문단을 시각적 장면(scene)으로 그룹핑. 같은 그룹은 동일 B-roll 이미지 공유.

> `pipeline.broll.scene_grouping`이 false이면 1:1 매핑

### 규칙
- 그룹은 반드시 **연속** 문단만 포함
- 그룹당 1-3 문단 (1-2 선호)
- 모든 문단이 정확히 1번 등장
- 그룹 수 범위: `ceil(n/3)` ~ `ceil(n*2/3)`, 높은 쪽 목표
- `representative_index`: 그룹 내 시각적으로 가장 대표적인 문단
- 확신 없으면 합치지 말고 **분리**

### 출력 형식
```json
[
  {"group_id": 1, "paragraph_indices": [1, 2], "representative_index": 1, "reason": "AI 기술 소개"}
]
```

## Step 4: Source Decision

각 문단의 B-roll을 AI 생성(generate)할지 웹 검색(search)할지 결정.

> image_search가 false이면 모두 "generate", skip

### Context Chunk 생성
각 문단(0-based idx)에 ±1 문단 컨텍스트. 현재 문단은 【괄호】 표시.

### 판단 기준 (【괄호】 안의 텍스트만)
- **"search"**: 실제 브랜드+제품 또는 유명 랜드마크가 직접 언급
- **"generate"**: 그 외 모든 경우 (80%+ 예상)
- 주변에 브랜드가 있어도 괄호 안에 없으면 → generate

### search 항목 검색 쿼리
- 영어로 작성
- 각 search_query는 고유 (같은 주제도 앵글 변경)

## Step 5: Prompt Enhancement

"generate" 항목에 상세 이미지 프롬프트 작성.

### Flux Kontext 백엔드 (LoRA)
캐릭터가 주인공으로 등장.
형식: `[character_description] [action/pose] in [environment], [mood/lighting]`

규칙:
- 캐릭터가 장면과 **상호작용** (단순 서있기 X)
- 추상 개념 → 시각적 비유 ("성장" → 캐릭터가 나무에 물 주기)
- 치비/카와이 애니메 스타일
- 단순 배경 (그라디언트, 솔리드)
- **텍스트 요소 절대 금지**: text, label, sign, speech bubble, written, typography
- 영어, 1-3문장

### 기본 백엔드 (FLUX.2)
- character_description 모든 프롬프트에 포함
- 【괄호】 텍스트 정확히 반영
- 치비/카와이 스타일, 적절한 배경
- 텍스트 요소 금지
- 영어, 1-3문장

## Step 6: 병렬 에이전트 디스패치

| 문단 수 | 배치 수 |
|--------|--------|
| 1-29 | 1 (직접) |
| 30-59 | 2 |
| 60-89 | 3 |
| 90+ | 4 |

에이전트에 전달: 전체 문단 리스트, 담당 범위, scene grouping 결과, config 요약, 참고 파일 경로.
> Scene grouping은 메인에서 먼저 완성. 에이전트는 source decision + prompt enhancement만 담당.

## Step 7: 출력 — prompts.json

`projects/$PROJECT/broll/prompts.json`:

```json
{
  "version": 1,
  "character_description": "...",
  "backend": "flux_kontext",
  "scene_groups": [...],
  "items": [
    {
      "paragraph_index": 1,
      "keyword": "...",
      "source": "generate",
      "reason": "...",
      "context_chunk": "...【현재 문단】...",
      "scene_group_id": 1
    }
  ]
}
```

> **timing (start_time) 미포함** — TTS 후 파이프라인이 audio duration으로 계산.

## Step 8: 검증

- [ ] items 수 == 문단 수
- [ ] 모든 paragraph_index 정확히 1번 등장
- [ ] scene_groups의 paragraph_indices 연속
- [ ] representative_index가 해당 그룹 내 존재
- [ ] generate 항목: keyword 비어있지 않음, 영어
- [ ] search 항목: keyword 영어 검색 쿼리
- [ ] 텍스트 요소 미포함 ("text", "label", "sign", "speech bubble")

## 재생성 가이드

| 상황 | 방법 |
|------|------|
| 전체 재생성 | prompts.json 삭제 후 다시 실행 |
| 특정 프롬프트 수정 | prompts.json에서 해당 item의 keyword 편집 |
| 씬 그룹 변경 | scene_groups + 관련 scene_group_id 편집 |
| 이미지 재생성 | prompts.json 유지 + broll/generated/*.png 삭제 → 파이프라인 재실행 |
