---
name: generate-video
description: "E2E thin orchestrator: script.txt -> final_video.mp4. Dispatches to slide-generation / broll skills for heavy lifting, keeps only orchestration logic inline. '영상 만들어줘', 'E2E', '파이프라인 실행' 등 영상 완성 요청 시 이 커맨드 사용."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
argument-hint: "<project-name>"
---

# /generate-video -- E2E Thin Orchestrator

대본(script.txt) -> final_video.mp4 전 과정 자동화.
슬라이드/B-roll 생성은 스킬에 위임하고, 이 커맨드는 흐름 제어만 담당합니다.

**Argument**: project name (e.g., `003-pricing-strategy`)

## 전체 흐름

```
script.txt
  | Step 1: 프로젝트 확인
  | Step 2: 문단 분리 + 씬 분할
  | Step 2.5: TTS 발음 사전 강화 --> [Skill: tts]
  v
paragraphs/001.txt ~ NNN.txt
  | Step 3: TSX 슬라이드 생성  --> [Skill: slide-generation]
  v
slides/001.tsx ~ NNN.tsx
  | Step 4: 검증 + 정리        --> [Skill: tsx-checklist]
  | Step 4.7: 슬라이드 렌더링 검증 (pre-render)
  | Step 4.5: B-roll 프롬프트   --> [Skill: broll]
  | Step 5: 파이프라인 실행
  v
output/final_video.mp4
```

> **TTS는 파이프라인에 위임**: 수동으로 미리 생성하지 말 것. 미리 생성하면 문단-씬 개수 불일치로 자막 싱크가 깨집니다.

---

## Step 1: 프로젝트 확인

1. `projects/$ARGUMENTS/` 디렉토리 존재 확인
2. `script.txt` 존재 확인 (없으면 오류)
3. 기존 산출물 확인:
   - `slides/*.tsx` -- 있으면 TSX 생성 skip
   - `animation-memory.json` -- 있으면 시각 연속성 활용 (chapter-animation-memory.md)
   - `audio/*.wav` -- 파이프라인이 관리 (수동 생성 금지)
   - `output/final_video.mp4` -- 있으면 기존 파일 덮어쓰고 재생성 (확인 불필요)
4. `audio/*.wav` 존재 시 씬 수와 비교. 불일치하면 `audio/*.wav` 삭제 (파이프라인이 재생성)

---

## Step 2: 문단 분리 + 씬 분할

```bash
cd $PROJECT_ROOT
uv run python3 -c "
from features.split_paragraphs.lib import split_script
from features.split_scenes.lib import split_paragraphs_into_scenes
from app.config import get_config
config = get_config()
threshold = config.pipeline.scenes.merge_threshold
text = open('projects/$ARGUMENTS/script.txt').read()
script = split_script(text)
scenes = split_paragraphs_into_scenes(script.paragraphs, merge_threshold=threshold)
print(f'=== {len(script.paragraphs)}개 문단 -> {len(scenes)}개 씬 (merge_threshold={threshold}) ===')
for s in scenes:
    print(f'Scene {s.index:02d} (para {s.paragraph_index}): {s.text[:80]}')
"
```

1. 씬 개수를 간단히 출력 후 **확인 대기 없이** 다음 스텝 즉시 진행
2. **기존 audio/*.wav가 있으면** 씬 수와 wav 파일 수 비교. 불일치 시 전체 삭제.

---

## Step 2.5: TTS 발음 사전 강화

> **Skill**: `.claude/skills/tts/chapter-dictionary-enhancement.md`

1. `config/tts_dictionary.yaml` 로드 → 대본의 영어/숫자 토큰 스캔
2. 미등록 단어 발견 시 → 한글 발음 생성 → **확인 없이 바로 사전에 추가** (발음이 애매한 경우만 간단히 보고)
3. 미등록 단어 0개 → "사전 강화 불필요" → skip

> 이 스텝으로 파이프라인 Step 1.5의 GPT-5.1 API 호출이 불필요해집니다.

---

## Step 3: TSX 슬라이드 생성

> **Skill**: `.claude/skills/slide-generation/SKILL.md` -> `chapter-longform-tsx.md` 라우팅
> Also read: `chapter-art-direction.md`, `chapter-batch-dispatch.md`

**Context to carry into skill:**
- Scene data: `projects/$ARGUMENTS/paragraphs/*.txt` + Step 2 씬 분할 결과
- Total slide count = 씬 수
- Output path: `projects/$ARGUMENTS/slides/NNN.tsx`

스킬 문서를 로드하여 그 지시를 따릅니다. 이 커맨드에서 TSX 작성 규칙을 반복하지 않습니다.

---

## Step 4: 검증 + 충돌 파일 정리

> **Skill**: `.claude/skills/slide-generation/chapter-tsx-checklist.md`

```bash
# 1) TSX 카운트 확인 (씬 수와 일치해야 함)
ls projects/$ARGUMENTS/slides/*.tsx | wc -l

# 2) stale json/mp4 삭제
cd projects/$ARGUMENTS/slides
for f in *.tsx; do base="${f%.tsx}"; rm -f "${base}.json" "${base}.mp4"; done

# 3) audio 파일 수 != 씬 수이면 전체 삭제
TSX_COUNT=$(ls projects/$ARGUMENTS/slides/*.tsx 2>/dev/null | wc -l)
WAV_COUNT=$(ls projects/$ARGUMENTS/audio/*.wav 2>/dev/null | wc -l)
if [ "$WAV_COUNT" -gt 0 ] && [ "$WAV_COUNT" -ne "$TSX_COUNT" ]; then
  echo "audio($WAV_COUNT) != slides($TSX_COUNT) -> audio 전체 삭제"
  rm -f projects/$ARGUMENTS/audio/*.wav
fi
```

---

## Step 4.7: 슬라이드 렌더링 검증 (Pre-render)

`npx tsc --noEmit`는 타입 에러만 잡습니다. Remotion 런타임 에러(interpolate inputRange 위반, spring config 오류, 무한 리렌더 등)는 실제 렌더링을 해봐야 발견됩니다. 이 단계에서 전체 슬라이드를 MP4로 미리 렌더링하여, TTS·B-roll·아바타 등 비용이 큰 파이프라인 스텝 전에 렌더링 실패를 잡습니다.

```bash
uv run python scripts/regenerate_slides.py $ARGUMENTS
```

1. 전체 TSX/Manim → MP4 렌더링 (Remotion 4-slot 병렬)
2. 결과 확인: `Success: N, Failed: M`
3. **Failed > 0이면**: 실패한 슬라이드 번호를 확인하고 TSX를 수정한 뒤 해당 슬라이드만 재렌더링
   ```bash
   uv run python scripts/regenerate_slides.py $ARGUMENTS NNN  # 특정 슬라이드만
   ```
4. 전체 성공 확인 후 다음 스텝 진행

> 파이프라인(Step 5)은 이미 렌더링된 MP4를 skip하므로 이 단계의 시간 비용은 파이프라인 전체에서 제로입니다.

---

## Step 4.5: B-roll 프롬프트 사전 생성

> **Skill**: `.claude/skills/broll/chapter-prompt-workflow.md`

1. `projects/$ARGUMENTS/broll/prompts.json` 존재 -> skip, 없으면 스킬 워크플로 실행
2. **검증**: items 수 == 문단 수

> 파이프라인이 prompts.json을 감지하면 API 호출 없이 이미지 생성만 수행합니다.

---

## Step 5: 파이프라인 실행

```bash
uv run video-automation pipeline script-to-video \
  --input projects/$ARGUMENTS/script.txt \
  --project $ARGUMENTS
```

> **B-roll 기본 활성화**: `--no-broll`은 빠른 테스트 시에만.

파이프라인 자동 처리: 문단+씬 분할 -> TSX freeform 감지 -> TTS -> B-roll 이미지 생성 -> Remotion 4-slot 렌더링 -> 합성 + 자막 + 아바타

### 완료 확인
```bash
ls -la projects/$ARGUMENTS/output/final_video.mp4
```
최종 결과 보고: 파일 경로, 영상 길이, 씬 수, 슬라이드 수

---

## 빠른 재생성 가이드

| 상황 | 명령 |
|------|------|
| TSX만 재생성 | `slides/*.tsx` 삭제 후 Step 3 다시 |
| 특정 슬라이드 수정 | 해당 `NNN.tsx` 편집 + `NNN.mp4` 삭제 -> Step 5 |
| TTS 재생성 | `audio/*.wav` 삭제 -> Step 5 (파이프라인이 재생성) |
| 전체 재생성 | `slides/`, `audio/`, `output/` 삭제 -> 전체 다시 |

ARGUMENTS: $ARGUMENTS
