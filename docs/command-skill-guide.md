# Command & Skill 가이드

> 2026-03-22 리팩토링 완료. 14개 commands → 6개로 통합, 서브스텝 워크플로는 skill로 이동.

---

## 1. Commands 한눈에 보기

| Command | 용도 | 인자 |
|---------|------|------|
| `/generate-video <project>` | E2E 영상: script.txt → final_video.mp4 | 프로젝트명 |
| `/generate-shorts <project>` | 모든 쇼츠 (대본/외부영상/CC 자동 감지) | 프로젝트명 `[--from-video <path>]` |
| `/generate-carousel <project>` | 캐러셀 카드 생성 + 시각 리뷰 | 프로젝트명 |
| `/generate-script <project>` | 모든 대본 (longform/shorts/CC 자동 감지) | 프로젝트명 `[--format shorts\|cc]` |
| `/detect-releases` | CC GitHub 릴리즈 감지 | — |
| `/voice-clone-setup` | 보이스 프로필 설정 | speaker, source |

---

## 2. 자동 경로 감지

### `/generate-shorts`

```
--from-video 제공?
  └─ YES → 외부 영상에서 바이럴 구간 추출 (Whisper + Claude 분석)
  └─ NO
       프로젝트명 cc-* ?
         └─ YES → CC 교육 쇼츠 (정사각형 레이아웃, CC 패턴)
         └─ NO  → 일반 대본 기반 쇼츠 (9:16)
```

### `/generate-script`

```
--card-id 또는 프로젝트명 cc-* ?
  └─ YES → CC 대본 (카드DB + 웹 레퍼런스 수집)
--format shorts ?
  └─ YES → 쇼츠 대본 (45-60초 압축 + 훅 전략)
그 외
  └─ Longform 대본 (포맷은 Step 2에서 결정)
```

---

## 3. Skill 자동 로드 (서브스텝 독립 실행)

Command 없이 **자연어로 요청**하면 Claude가 해당 skill chapter를 자동 로드합니다.

| 이렇게 말하면 | Claude가 로드하는 Skill |
|-------------|----------------------|
| "슬라이드만 다시 만들어줘" | `slide-generation` → 포맷별 chapter |
| "B-roll 프롬프트 생성해줘" | `broll` → `chapter-prompt-workflow.md` |
| "훅 타이틀 수정해줘" | `slide-generation` → `chapter-hook-titles.md` |
| "특정 슬라이드 TSX 수정" | `slide-generation` → 포맷별 chapter |
| "아트 디렉션 변경" | `slide-generation` → `chapter-art-direction.md` |

**포맷 자동 감지 규칙:**
- `shorts_slides/` 디렉토리 존재 → shorts chapter
- 프로젝트명 `cc-*` → CC chapter
- 그 외 → longform chapter

---

## 4. 워크플로 예시

### 4-1. 일반 영상 (16:9) 만들기

```bash
# 1. 대본 생성
/generate-script my-video

# 2. E2E 영상 생성 (슬라이드 + B-roll + TTS + 렌더링 + 자막 + 아바타)
/generate-video my-video
```

또는 한마디로: **"영상 만들어줘"** → `/generate-video` 자동 발동

### 4-2. 쇼츠 (9:16) 만들기 — 대본 기반

```bash
# 1. 쇼츠 대본 생성
/generate-script my-shorts --format shorts

# 2. 파이프라인 1차 (TTS + 씬 분할)
uv run video-automation pipeline script-to-shorts \
  --input projects/my-shorts/script.txt --project my-shorts

# 3. TSX + 훅 타이틀 생성 + 파이프라인 2차 (렌더링)
/generate-shorts my-shorts
```

### 4-3. 쇼츠 — 외부 영상에서 추출

```bash
# MP4를 프로젝트에 넣고 실행
/generate-shorts my-shorts --from-video projects/my-shorts/source.mp4
```

### 4-4. CC 교육 쇼츠

```bash
# 1. CC 대본 생성 (cc-* 자동 감지)
/generate-script cc-002

# 2. 파이프라인 1차
uv run video-automation pipeline script-to-shorts \
  --input projects/cc-002/script.txt --project cc-002

# 3. CC TSX + 훅 타이틀 + 렌더링 (cc-* 자동 감지)
/generate-shorts cc-002
```

### 4-5. 캐러셀

```bash
/generate-carousel my-carousel
# → TSX 생성 + 렌더링 + 시각 리뷰까지 한 번에
```

### 4-6. 슬라이드만 재생성 (서브스텝)

Command 없이 자연어로:
> "003 프로젝트 슬라이드 5번, 8번만 다시 만들어줘"

Claude가 `slide-generation` skill을 로드하여 해당 TSX만 재작성.

---

## 5. Skill 구조

### 새로 추가된 `slide-generation` skill

```
.claude/skills/slide-generation/
  SKILL.md                    ← 인덱스 + Decision Flowchart
  chapter-art-direction.md    ← 공통 아트 디렉션 (longform/shorts/CC 각 확장)
  chapter-longform-tsx.md     ← 16:9 TSX 워크플로
  chapter-shorts-tsx.md       ← 9:16 일반 쇼츠 TSX 워크플로
  chapter-cc-shorts.md        ← CC 전용 패턴 + 정사각형 제약
  chapter-hook-titles.md      ← 훅 타이틀 생성 규칙
  chapter-batch-dispatch.md   ← 에이전트 배치 사이징/디스패치
  chapter-tsx-checklist.md    ← TSX 검증 + stale 파일 정리
```

### 확장된 기존 skills

| Skill | 추가된 Chapter | 내용 |
|-------|--------------|------|
| `broll` | `chapter-prompt-workflow.md` | B-roll 프롬프트 사전 생성 워크플로 |
| `pipeline` | `chapter-video-to-shorts.md` | 외부 영상 → 쇼츠 워크플로 |

---

## 6. 이전 명령어 → 새 명령어 매핑

| 이전 Command (삭제됨) | 새 Command / Skill |
|---------------------|-------------------|
| `/generate-slides` | 자연어 요청 → `slide-generation` skill 자동 로드 |
| `/generate-shorts-slides` | `/generate-shorts` (일반 쇼츠 자동 감지) |
| `/build-cc-shorts` | `/generate-shorts` (CC 자동 감지) |
| `/generate-broll-prompts` | 자연어 요청 → `broll` skill 자동 로드, 또는 `/generate-video` 내부 자동 실행 |
| `/generate-shorts-script` | `/generate-script --format shorts` |
| `/generate-cc-script` | `/generate-script cc-XXX` (CC 자동 감지) |
| `/generate-shorts-title` | `/generate-shorts` 내부에서 자동 처리 |
| `/review-carousel` | `/generate-carousel` Step 7에 통합 |

---

## 7. Command가 Skill을 로드하는 방식

Commands는 **thin orchestrator** — 오케스트레이션만 담당하고, 실제 워크플로는 skill chapter를 참조합니다.

```
/generate-video (command)
  ├─ Step 3: "Skill: slide-generation → chapter-longform-tsx.md 로드"
  ├─ Step 4: "Skill: slide-generation → chapter-tsx-checklist.md 로드"
  └─ Step 4.5: "Skill: broll → chapter-prompt-workflow.md 로드"
```

Skill 안에서 에이전트가 해당 chapter를 **직접 Read**하여 워크플로를 따릅니다. 별도의 `@import` 메커니즘은 없고, 파일 경로 참조 방식입니다.

---

## 8. 전체 Skill 목록 (14개)

| Skill | 타입 | 용도 |
|-------|------|------|
| **slide-generation** | Workflow | TSX 슬라이드 생성 (longform/shorts/CC) |
| **broll** | Reference + Workflow | B-roll 아키텍처 + 프롬프트 생성 |
| **pipeline** | Reference + Workflow | 파이프라인 매뉴얼 + video-to-shorts |
| avatar | Reference | Ditto 아바타 통합 |
| config | Reference | Config 프로필 시스템 |
| ffmpeg | Reference | FFmpeg 래퍼 함수 |
| manim-slides | Reference | Manim CE 패턴 라이브러리 |
| manimce-best-practices | Reference | Manim CE API 가이드 |
| remotion-slides | Reference | Remotion 프로젝트 구조 |
| remotion-visual-standards | Reference | 시각 품질 가이드라인 |
| testing | Reference | 테스트/품질 도구 |
| tts | Reference | TTS 백엔드 매뉴얼 |
| commit | Workflow | lint/test → conventional commit |
| verify | Workflow | 구현 후 자가 검증 |
