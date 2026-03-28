# Claude Code Skills 시스템 가이드

> "매번 긴 프롬프트를 쓸 필요 없이, 한 줄이면 됩니다"

---

## Part 1: Skill이란?

Claude Code에게 **"이런 상황에서는 이렇게 행동해"라고 미리 적어둔 지시서**입니다.

> **비유: 요리 레시피북**
> - 매번 "양파를 잘게 썰고 기름을 두르고 중불에서..." 설명할 필요 없이
> - "짜장면 만들어줘" 한마디면 레시피대로 만들어줍니다
> - Skill = 레시피, Command = "짜장면 만들어줘"

### Skill이 없다면

```
대본을 읽고, 각 문단을 분석하고, 콘텐츠 유형을 분류하고,
적절한 레이아웃을 선택하고, TSX 코드를 작성하되
design/theme.ts의 색상을 사용하고,
motifs/ 폴더의 애니메이션을 활용하고,
슬라이드 간 시각적 변화를 주고...
(수백 줄의 지시문)
```

### Skill이 있다면

```
/generate-video workshop-001
```

이 한 줄로 위의 모든 과정이 자동으로 진행됩니다.

---

## Part 2: Commands — 직접 호출하는 명령어

슬래시(`/`)로 시작하는 명령어를 Claude Code 대화창에 입력합니다.

### 7가지 프로젝트 Commands

| 명령어 | 용도 | API 모드 | 사용 예시 |
|--------|------|:--------:|----------|
| `/generate-video <project>` | 16:9 영상 생성 (전체 과정) | ✅ | `/generate-video my-video` |
| `/generate-shorts <project>` | 9:16 쇼츠 생성 (대본/CC/외부영상 자동 감지) | ✅ | `/generate-shorts my-shorts` |
| `/generate-carousel <project>` | 4:5 카드뉴스 생성 | ✅ | `/generate-carousel my-card` |
| `/generate-script <project>` | 대본 생성 (기술문서→영상, 대본→쇼츠, CC카드→교육) | ✅ | `/generate-script my-video` |
| `/carousel-copywriting <project>` | 캐러셀 카드별 카피라이팅 & 콘텐츠 전략 | ✅ | `/carousel-copywriting my-card` |
| `/detect-releases` | CC 릴리즈 감지 → 쇼츠 콘텐츠 후보 선별 | ✅ | `/detect-releases` |
| `/voice-clone-setup` | 보이스 프로필 설정 | ✅ | `/voice-clone-setup` |

> **API 모드 제한사항**: 모든 커맨드는 API 모드(`CONFIG_PROFILE=api`)에서 실행 가능하지만, B-roll 이미지 생성과 아바타(Ditto) 기능은 비활성화됩니다.

### 추가 슬래시 명령어

| 명령어 | 용도 | 비고 |
|--------|------|------|
| `/spec-writer` | 기능 명세 문서 생성 (개발자용) | 프로젝트 스킬 (`.claude/skills/spec-writer/`) |
| `/skill-creator` | 나만의 스킬 만들기 | Claude Code 내장 스킬 |
| `/autoresearch-generate-script` | 대본 생성 스킬 자동 최적화 | 서브커맨드: `changelog`, `generate-script-v2` |

> `<project>`는 프로젝트 이름입니다. `projects/` 폴더 아래에 해당 이름의 폴더가 생깁니다.

### 워크숍에서 주로 쓸 Commands

```
# 오전: 첫 영상
/generate-video workshop-001

# 오후: 쇼츠
/generate-shorts workshop-001

# 오후: 캐러셀 카피 → 카드뉴스
/carousel-copywriting workshop-001
/generate-carousel workshop-001

# 나만의 스킬 만들기
/skill-creator
```

---

## Part 3: Skills — 자동으로 로드되는 지시서

Commands와 달리, **Skills는 대화 맥락에서 자동으로 로드**됩니다.

### 자연어 → Skill 자동 매핑

| 이렇게 말하면 | Claude가 자동 로드하는 Skill |
|-------------|---------------------------|
| "슬라이드만 다시 만들어줘" | `slide-generation` |
| "B-roll 프롬프트 수정해줘" | `broll` |
| "발음 사전에 단어 추가해줘" | `tts` |
| "설정 변경하고 싶어" | `config` |
| "파이프라인 흐름 알려줘" | `pipeline` |

여러분이 할 일은 그냥 자연어로 말하는 것뿐입니다. Claude Code가 알아서 적절한 Skill을 찾아 로드합니다.

---

## Part 4: Commands와 Skills의 관계

```
/generate-video
    ├──→ slide-generation (chapter-longform-tsx — 16:9 슬라이드)
    ├──→ broll (배경 이미지 프롬프트 + 백엔드 선택)
    └──→ tts (발음 사전 보강 + 백엔드 자동 선택)

/generate-shorts
    ├──→ slide-generation (chapter-shorts-tsx 또는 chapter-cc-shorts)
    └──→ broll (배경 이미지 프롬프트)

/carousel-copywriting
    └──→ 훅 엔지니어링 + 카드별 카피 + 8메트릭 자가평가

/generate-carousel
    └──→ slide-generation (카드뉴스용 디자인)

/generate-script
    └──→ 포맷 자동 감지 (기술문서→영상 / 대본→쇼츠 / CC카드→교육)
```

> **비유:** Command = "풀코스 메뉴 주문" / Skill = "개별 요리 레시피"
> - `/generate-video`는 풀코스(전체 영상 생성)를 주문하는 것
> - 개별 Skill은 "디저트만 다시 만들어줘"처럼 일부만 수정할 때 사용

---

## Part 5: 16개 Skills 전체 목록

### 작업 실행용 Skills (Workflow)

| Skill | 역할 | 챕터 수 | 언제 쓰나 |
|-------|------|:-------:|----------|
| `slide-generation` | 슬라이드 디자인 코드(TSX) 생성 | 8 | 영상/쇼츠/CC쇼츠/카드뉴스 만들 때 |
| `broll` | B-roll 배경 이미지 프롬프트 + 백엔드 관리 | 3 | 배경 이미지 만들 때 |
| `tts` | TTS 백엔드 선택 + 발음 사전 보강 | 2 | 음성 생성/품질 개선할 때 |
| `commit` | Git 커밋 + 푸시 | — | 변경사항 저장할 때 |
| `verify` | 코드 검증 (self-review, lint, test, FSD) | — | 구현 완료 후 검증할 때 |
| `spec-writer` | SDD 기능 명세 자동 생성 (EARS 형식) | — | 새 기능 구현 전 설계 |
| `autoresearch` | 스킬 자동 최적화 (eval 기반 반복 개선) | — | 스킬 품질을 반복 개선할 때 |

### 참조 매뉴얼 Skills (Reference)

| Skill | 역할 | 챕터 수 | 언제 쓰나 |
|-------|------|:-------:|----------|
| `pipeline` | 파이프라인 동작 매뉴얼 (4가지 파이프라인) | 4 | 파이프라인 이해/디버깅 |
| `config` | 설정 프로필 + 파이프라인 오버라이드 | 2 | 설정 변경할 때 |
| `remotion-slides` | Remotion Freeform/Template 모드 매뉴얼 | 3 | 렌더링 문제 해결 |
| `remotion-visual-standards` | 시각 품질 가이드라인 | — | 디자인 품질 개선 |
| `ffmpeg` | FFmpeg 래퍼 매뉴얼 | 1 | 영상 합성 문제 해결 |
| `avatar` | Ditto 아바타 통합 매뉴얼 | 1 | 아바타 설정 (GPU 필요) |
| `manim-slides` | Manim CE 슬라이드 패턴 라이브러리 | 4 | 수학/알고리즘 콘텐츠 |
| `manimce-best-practices` | ManimCE 베스트 프랙티스 | — | ManimCE 코드 작성 시 |
| `testing` | 테스트 패턴 + 품질 도구 (ruff, mypy) | 2 | 코드 테스트/품질 점검 |

---

## Part 6: Skill 파일은 어디에 있나?

```
.claude/skills/
├── slide-generation/               ← 가장 큰 스킬 (8 챕터)
│   ├── SKILL.md                      ← 메인 (인덱스)
│   ├── chapter-longform-tsx.md       ← 16:9 영상 슬라이드 규칙
│   ├── chapter-shorts-tsx.md         ← 9:16 쇼츠 슬라이드 규칙
│   ├── chapter-cc-shorts.md          ← CC 교육 쇼츠 전용 규칙
│   ├── chapter-art-direction.md      ← 아트 디렉션 (색상, 분위기)
│   ├── chapter-hook-titles.md        ← 훅 타이틀 생성 규칙
│   ├── chapter-batch-dispatch.md     ← 병렬 생성 전략
│   ├── chapter-animation-memory.md   ← 애니메이션 패턴 기억
│   └── chapter-tsx-checklist.md      ← 검증 체크리스트
├── broll/
│   ├── SKILL.md
│   ├── chapter-architecture.md       ← B-roll 아키텍처 개요
│   ├── chapter-backends.md           ← 4가지 이미지 백엔드
│   └── chapter-prompt-workflow.md    ← 프롬프트 생성 워크플로
├── tts/
│   ├── SKILL.md
│   ├── chapter-backends-and-selection.md  ← 4가지 TTS 백엔드 + 자동 선택
│   └── chapter-dictionary-enhancement.md  ← 발음 사전 보강 워크플로
├── pipeline/
│   ├── SKILL.md
│   ├── chapter-script-to-video.md    ← script-to-video 상세
│   ├── chapter-video-to-shorts.md    ← video-to-shorts 상세
│   ├── chapter-other-pipelines.md    ← 기타 파이프라인
│   └── chapter-file-reuse.md         ← 파일 재사용 로직
├── config/
│   ├── SKILL.md
│   ├── chapter-profile-system.md     ← 프로필 시스템 (base/api/asmr)
│   └── chapter-pipeline-overrides.md ← 파이프라인 설정 오버라이드
├── remotion-slides/
│   ├── SKILL.md
│   ├── chapter-freeform-mode.md      ← Freeform TSX 작성법
│   ├── chapter-template-mode.md      ← Template 모드
│   └── chapter-remotion-project.md   ← Remotion 프로젝트 구조
├── manim-slides/
│   ├── SKILL.md
│   ├── chapter-design-system.md      ← 디자인 토큰
│   ├── chapter-animation-patterns.md ← 애니메이션 패턴 (설명)
│   ├── chapter-animation-patterns-code.md  ← 패턴 코드 예제
│   └── chapter-practical-guide.md    ← 실전 가이드
├── autoresearch/
│   └── SKILL.md
├── spec-writer/
│   └── SKILL.md
└── ... (총 16개 Skill 폴더)
```

### SKILL.md의 구조

```markdown
---
name: slide-generation
description: "Remotion Freeform TSX 슬라이드 생성 워크플로 — longform 16:9, shorts 9:16, CC shorts"
---

## 활성화 조건
- 키워드: 슬라이드, TSX, 렌더링
- 파일: slides/*.tsx

## Chapters
1. chapter-longform-tsx.md — 16:9 영상
2. chapter-shorts-tsx.md — 9:16 쇼츠
3. chapter-cc-shorts.md — CC 교육 쇼츠
...
```

> **핵심:** SKILL.md가 "목차"이고, chapter 파일들이 "본문"입니다. Claude Code는 상황에 맞는 chapter를 자동으로 골라서 읽습니다.

---

## Part 7: 나만의 Skill 만들기

오후 세션에서 `/skill-creator`를 사용해 나만의 Skill을 만듭니다.

### 기본 사용법

```
/skill-creator
```

Claude Code에게 이렇게 요청합니다:

```
"내 채널은 IT 뉴스 채널이야. 매번 영상을 만들 때
다크 테마 + 파란색 포인트 + 뉴스 앵커 스타일로 슬라이드를 만들고 싶어.
이 스타일을 자동으로 적용하는 스킬을 만들어줘."
```

### 활용 아이디어

| 아이디어 | 설명 |
|---------|------|
| 채널 전용 스타일 | 내 채널만의 색상/폰트/레이아웃 규칙 |
| 특정 포맷 대본 | "3분 뉴스 요약", "5분 튜토리얼" 등 대본 템플릿 |
| 자동 썸네일 | 영상에서 핵심 장면을 뽑아 썸네일 생성 |
| 시리즈 패턴 | 시리즈물의 인트로/아웃트로 자동화 |

> **핵심:** Skill을 만드는 것 = "나만의 자동화 레시피를 만드는 것". 한번 만들면 계속 재사용할 수 있고, 시간이 갈수록 자산이 됩니다.

---

## Part 8: 실전 흐름 정리

### 처음 영상 만들기 (Command)
```
/generate-video my-project
→ Claude Code가 slide-generation + broll + tts 스킬을 자동 로드
→ 슬라이드 + B-roll + 발음사전 생성
→ 파이프라인 실행 명령어 안내
```

### 결과물 수정하기 (자연어 → Skill 자동)
```
나: "5번 슬라이드를 차트 레이아웃으로 바꿔줘"
Claude: → slide-generation 스킬 자동 로드 → 해당 슬라이드만 수정
```

### 나만의 패턴 만들기 (/skill-creator)
```
/skill-creator
→ 내 채널 스타일, 대본 템플릿, 자주 쓰는 설정을 스킬로 저장
→ 다음부터는 한 줄로 호출
```
