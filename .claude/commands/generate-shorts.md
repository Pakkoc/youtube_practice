---
name: generate-shorts
description: "모든 쇼츠 생성을 통합 처리. 대본 기반 쇼츠(9:16), CC 교육 쇼츠, 외부 영상 쇼츠까지 자동 경로 감지. '쇼츠 만들어줘' 등 요청 시 이 커맨드 사용."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
argument-hint: "<project-name> [--from-video <path>]"
---

# /generate-shorts -- 통합 쇼츠 생성

모든 쇼츠 생성 경로를 하나의 커맨드로 통합.

## 경로 자동 감지

```
--from-video 제공? → YES → Video-to-shorts 경로 (Step A)
프로젝트명 cc-* 패턴? → YES → CC Shorts 경로 (Step C)
그 외 → General Shorts 경로 (Step B)
```

---

## 경로 A: Video-to-Shorts (외부 영상 → 쇼츠)

> **Skill**: `.claude/skills/pipeline/chapter-video-to-shorts.md`

이 경로는 외부 영상에서 바이럴 구간을 선정하여 쇼츠를 생성합니다.
skill의 전체 워크플로(Whisper → SRT → 교정 → 바이럴 선정 → 파이프라인 → 캡션)를 따릅니다.

**Argument**: `<project-name> --from-video <video-path>`

### A1: 프로젝트 확인 + 소스 영상 탐색

1. `projects/$PROJECT/` 존재 확인
2. `--from-video`로 지정된 영상 사용. 미지정 시 디렉토리 내 `.mp4` 탐색 (1개면 바로, 여러 개면 AskUserQuestion)
3. 캐시 확인:
   - `shorts/word_timestamps.json` → Whisper skip
   - `output/corrected_subtitles.srt` → SRT skip
   - `shorts/viral_plan.json` → 바이럴 선정 skip

### A2: Whisper → SRT → 교정 → 바이럴 선정

skill 워크플로를 순서대로 따른다:
1. Word Timestamps 추출 (Whisper API)
2. SRT 자동 생성 + 품질 확인 → corrections.txt (선택)
3. 바이럴 구간 선정 (Claude 직접 분석, 3초 훅 임팩트 최우선)
4. 사용자 승인 → `shorts/viral_plan.json` 저장

### A3: 파이프라인 실행

```bash
uv run video-automation pipeline video-to-shorts \
  --project "$PROJECT" --input "<영상 경로>"
```

캐시 재사용: word_timestamps, SRT, viral_plan.json → API skip

### A4: 결과 확인 + 캡션 생성

1. 생성된 쇼츠 목록 테이블 표시
2. `docs/shorts/caption-guideline.md` 참조하여 캡션 작성
3. `projects/$PROJECT/shorts/short_NNN_caption.txt`로 저장

---

## 경로 B: General Script-to-Shorts (대본 → 9:16 쇼츠)

대본 기반 일반 쇼츠. 파이프라인 1차 (TTS+씬분할) → TSX+훅타이틀 생성 → 파이프라인 2차 (렌더링).

### Step B1: 프로젝트 확인

1. `projects/$PROJECT/` 존재 확인
2. `script.txt` 존재 확인
3. 기존 산출물 확인:
   - `paragraphs/*.txt` + `audio/*.wav` → 있으면 파이프라인 1차 skip
   - `shorts_slides/slides/*.tsx` → 있으면 TSX 생성 skip
   - `shorts_slides/slides/hook_titles.json` → 있으면 훅 타이틀 skip
   - `animation-memory.json` → 있으면 시각 연속성 활용 (chapter-animation-memory.md)

### Step B1.5: TTS 발음 사전 강화

> **Skill**: `.claude/skills/tts/chapter-dictionary-enhancement.md`

1. `config/tts_dictionary.yaml` 로드 → 대본의 영어/숫자 토큰 스캔
2. 미등록 단어 발견 시 → 한글 발음 생성 → 사용자 확인 → 사전에 추가
3. 미등록 단어 0개 → skip

> 파이프라인 Step 1.5의 GPT-5.1 API 호출을 사전에 불필요하게 만듭니다.

### Step B2: 파이프라인 1차 실행 (TTS + 씬 분할)

paragraphs/ 또는 audio/가 없으면:
```bash
uv run video-automation pipeline script-to-shorts \
  --input projects/$PROJECT/script.txt --project $PROJECT
```
파이프라인이 씬 분할 + TTS까지 수행 후 TSX가 없어서 멈춤. 이 시점에서 수동 중단 (Ctrl+C) 또는 파이프라인이 TSX 부재로 대기.

### Step B3: TSX 슬라이드 + 훅 타이틀 생성

> **Skill**: `.claude/skills/slide-generation/SKILL.md` → `chapter-shorts-tsx.md`
> Also: `chapter-art-direction.md` (Shorts 확장), `chapter-hook-titles.md`, `chapter-batch-dispatch.md`

Art direction 수행 → 슬라이드 테이블 계획 → TSX 작성 → 훅 타이틀 JSON 저장.

**핵심 참조 문서** (TSX 작성 전 반드시 로드):
```
remotion/docs/tsx-contract.md          -- § Common Rules + § Shorts Contract
remotion/docs/design-philosophy.md     -- 앵무새 규칙, 점진적 공개
remotion/docs/slide-patterns.md        -- 패턴 레퍼런스
remotion/docs/slide-patterns-motion.md -- Exit, Camera, Ambient, Spring Guide
remotion/docs/slide-icons.md           -- SVG 아이콘 라이브러리
remotion/docs/slide-layouts.md         -- 레이아웃 인덱스
remotion/docs/slide-layouts-extras.md  -- Shorts-Safe 패턴 필수
remotion/docs/slide-examples.md        -- 콘텐츠 타입별 few-shot 예제
.claude/skills/remotion-visual-standards/SKILL.md -- § 7 safe zones + spring presets
```

Output:
- `projects/$PROJECT/shorts_slides/slides/*.tsx`
- `projects/$PROJECT/shorts_slides/slides/hook_titles.json`

### Step B4: 검증

> **Skill**: `.claude/skills/slide-generation/chapter-tsx-checklist.md`

1. Import 검증: `python scripts/validate_tsx_imports.py projects/$PROJECT/shorts_slides/slides/`
2. Type check: TSX를 ShortsContentSlot에 복사 후 `npx tsc --noEmit`
3. 파일 수 = 슬라이드 수, hook_titles.json 엔트리 수 일치 확인

### Step B5: 파이프라인 2차 실행 (렌더링)

```bash
uv run video-automation pipeline script-to-shorts \
  --input projects/$PROJECT/script.txt --project $PROJECT
```
이번에는 TSX + hook_titles.json이 있으므로 LLM 생성을 skip하고 렌더링 진행.

---

## 경로 C: CC Shorts (Claude Code 교육 쇼츠)

CC 프로젝트(cc-001, cc-002 등)용 교육 쇼츠. 일반 쇼츠와 동일한 2-pass 흐름이지만 CC 전용 아트 디렉션/레이아웃 사용.

### Step C1: 프로젝트 확인

경로 B1과 동일. 추가로 `cc-content/cards.json`에서 해당 카드 존재 확인.

### Step C1.5: TTS 발음 사전 강화

경로 B1.5와 동일.

### Step C2: 파이프라인 1차 실행

경로 B2와 동일.

### Step C3: CC TSX + 훅 타이틀 생성

> **Skill**: `.claude/skills/slide-generation/SKILL.md` → `chapter-cc-shorts.md`
> Also: `chapter-art-direction.md` (CC 확장), `chapter-hook-titles.md` (CC 규칙), `chapter-batch-dispatch.md`

CC 포맷 감지 (translator/flow/situation) → CC 아트 디렉션 → 슬라이드 계획 → TSX 작성 → 훅 타이틀 저장.

**CC 전용 참조 문서** (일반 문서 + 추가):
```
cc-content/docs/cc-shorts-patterns.md  -- CC 3가지 포맷 패턴 (필수)
remotion/docs/tsx-contract.md          -- § Common + § Shorts + CC Shorts 서브섹션
```

**CC 고유 제약**:
- 정사각형 중앙 영역 (padding: `"140px 48px 340px 48px"`)
- `backdropFilter` 절대 금지 (Remotion 렌더 행 발생)
- 허용 COLORS: `BG`, `TEXT`, `ACCENT`, `ACCENT_BRIGHT`, `MUTED`, `TEAL`, `CODE_BG`
- 터미널 배경: `"#141618"`, 테두리: `"rgba(255,255,255,0.08)"` 직접 사용
- 훅 타이틀: 모든 슬라이드에 동일 적용 (CC는 에피소드 단위)

### Step C4: 검증

경로 B4와 동일. 추가로:
- padding `"140px 48px 340px 48px"` 적용 확인
- `backdropFilter` 미사용 확인
- 미정의 COLORS 상수 미사용 확인

### Step C5: 파이프라인 2차 실행

경로 B5와 동일.

---

## 빠른 재생성 가이드

| 상황 | 방법 |
|------|------|
| TSX만 재생성 | `shorts_slides/slides/*.tsx` 삭제 후 Step B3/C3 다시 |
| 훅 타이틀만 변경 | `hook_titles.json` 편집 → Step B5/C5 |
| TTS 재생성 | `audio/*.wav` 삭제 → Step B2/C2 |
| 전체 재생성 | `paragraphs/`, `audio/`, `shorts_slides/` 삭제 → 처음부터 |
| SRT 교정 후 재생성 (경로 A) | `rm output/corrected_subtitles.srt shorts/viral_plan.json` |
| 바이럴 구간만 재선정 (경로 A) | `rm shorts/viral_plan.json` |
| 영상 쇼츠 전체 재생성 (경로 A) | `rm -rf shorts/ output/` |

---

## 주의사항

- **word_timestamps.json 보존** -- Whisper API 비용 절약
- **slides JSON, audio sidecar JSON 절대 삭제 금지**
- 경로 A: `script.txt` 없는 외부 영상도 정상 동작 (SRT만으로 바이럴 선정)
- 경로 A: `viral_plan.json`은 `ViralSegmentPlan` 모델 호환 (`features/select_viral_segments/model.py`)
- 경로 B/C: 파이프라인 1차에서 `scenes.enabled=true`로 문장 단위 씬 분할 수행 -- paragraphs 수 = 슬라이드 수
- 경로 C: `cc-*` 패턴 감지는 프로젝트명이 `cc-`로 시작하고 뒤에 숫자가 오는 경우

ARGUMENTS: $ARGUMENTS
