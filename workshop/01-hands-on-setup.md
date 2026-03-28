# 실습 가이드: 첫 영상 만들기

> 목표: 30분 안에 script.txt → final_video.mp4 완성

---

## Step 0: 사전 확인 (3분)

아래 명령어가 모두 버전 번호를 출력하는지 확인합니다:

```bash
node --version      # v22 이상
python --version    # 3.13 이상
claude --version    # 버전 출력
ffmpeg -version     # 버전 출력
uv --version        # 버전 출력
```

> 하나라도 안 되면 손을 들어주세요. 강사/보조강사가 도와드립니다.

---

## Step 1: 프로젝트 설정 (5분)

### 1-1. 저장소 Fork + Clone

강사와 함께 진행합니다. 상세 가이드: `install-guideline.md`의 "수업 당일" 섹션.

```bash
# Mac — 바탕화면으로 이동 후
cd ~/Desktop
git clone https://github.com/내아이디/저장소이름.git
cd 저장소이름

# Windows — 명령 프롬프트에서
cd %USERPROFILE%\Desktop
git clone https://github.com/내아이디/저장소이름.git
cd 저장소이름
```

### 1-2. 패키지 설치

```bash
cd remotion && npm install && cd ..
uv sync --extra genai && uv sync --extra dev
```

> 처음 실행하면 수 분이 걸립니다. 기다려 주세요.

### 1-3. 환경 변수(.env) 설정

```bash
# Mac
cp .env.example .env

# Windows
copy .env.example .env
```

VS Code에서 `.env` 파일을 열고, 각 서비스에서 발급받은 API 키를 입력합니다:

```
ANTHROPIC_API_KEY=sk-ant-여기에_내_키
OPENAI_API_KEY=sk-여기에_내_키
ELEVENLABS_API_KEY=여기에_내_키
GOOGLE_API_KEY=여기에_내_키
SERPER_API_KEY=여기에_내_키
```

> API 키를 아직 발급받지 않았다면 이 시간에 함께 발급합니다.

### 1-4. ElevenLabs Voice ID 설정

강사가 공유하는 Voice ID를 확인합니다. 설정 파일에 이미 포함되어 있으므로 별도 수정은 불필요합니다.

> **Voice ID란?** ElevenLabs에서 특정 목소리를 식별하는 고유 번호입니다. 오늘은 강사의 목소리를 사용합니다.

---

## Step 2: 대본 작성 (5분)

### 2-1. Claude Code 실행

프로젝트 폴더에서 Claude Code를 실행합니다:

```bash
claude --dangerously-skip-permissions
```

> `--dangerously-skip-permissions`는 매번 "허락하시겠습니까?"를 건너뛰는 옵션입니다. 워크숍에서는 편의상 사용합니다.

### 2-2. 대본 생성

오전 실습은 **아주 짧은 대본**(3~4문단, 약 300자)으로 영상 생성 파이프라인을 빠르게 체험하는 것이 목표입니다. 대본 품질은 중요하지 않습니다 — 불완전해도 괜찮아요!

> **왜 짧게?** 여러 명이 동시에 API를 호출하면 속도가 느려질 수 있습니다. 짧은 대본으로 파이프라인 전체 흐름을 빠르게 확인한 뒤, 오후에 본격적으로 만들어 봅니다.

**claude.ai에서 대본 샘플 만들기**

본인의 [claude.ai](https://claude.ai) 계정에서 아래 프롬프트를 복사해서 대본을 생성합니다:

```
유튜브 1분짜리 짧은 대본을 만들어줘.
주제는 내가 관심 있는 아무거나 좋아.
(내 메모리/사전 정보를 참고해서 주제를 골라줘)

조건:
- 문단 3~4개, 총 300자 내외
- 문단 사이는 빈 줄로 구분
- 첫 문단은 시선을 끄는 인트로, 마지막은 마무리
- 완벽하지 않아도 괜찮아. 간결하게!
```

생성된 대본을 복사한 뒤, Claude Code 대화창에 붙여넣기합니다:

```
projects/workshop-001/script.txt에 아래 내용으로 대본을 저장해줘:

(여기에 claude.ai에서 만든 대본 붙여넣기)
```

> **팁:** claude.ai에 메모리나 사전 정보가 있으면 본인 관심 분야에 맞는 주제를 알아서 골라줍니다. 없어도 아무 주제나 나오니 그대로 쓰면 됩니다.

### 2-3. 대본 확인 및 수정

```
대본을 읽어줘
```

수정이 필요하면:
```
3번째 문단이 너무 길어. 반으로 줄여줘
```

```
인트로가 약해. "여러분, 이거 모르면 손해봅니다"처럼 훅을 강하게 바꿔줘
```

```
5번째 문단에 구체적인 숫자나 통계를 추가해줘
```

### script.txt 작성 규칙

| 규칙 | 설명 |
|------|------|
| 빈 줄로 문단 구분 | 1 문단 = 1 슬라이드 = 1 음성 |
| 문단당 50~100자 | 너무 길면 슬라이드가 빈약, 너무 짧으면 흐름 끊김 |
| 첫 문단 = 인트로 | 시청자 관심 끌기 |
| 마지막 문단 = 아웃트로 | 정리 + 구독 유도 |

---

## Step 3: 영상 생성 (15분)

### 3-1. /generate-video 실행

Claude Code 대화창에 입력합니다:

```
/generate-video workshop-001
```

이 한 줄로 Claude Code가 자동으로:
1. 대본을 분석하고 슬라이드 디자인 코드(TSX) 작성
2. B-roll 배경 이미지 프롬프트 생성
3. TTS 발음 사전 보강

> 이 과정은 약 3~5분 소요됩니다. Claude Code가 작업하는 동안 기다려 주세요.

### 3-2. 파이프라인 실행

Claude Code가 안내하는 명령어를 실행합니다:

```bash
uv run video-automation pipeline script-to-video \
    --input projects/workshop-001/script.txt \
    --project workshop-001
```

> `CONFIG_PROFILE=api`는 API 모드로 실행한다는 뜻입니다.

### 3-3. 진행 상황 확인

터미널에 `[1/7]`, `[2/7]` 등 진행 단계가 표시됩니다:

```
[1/7] 문단 분리 중...
[2/7] TTS + 슬라이드 + B-roll 생성 중...  ← 가장 오래 걸림
[3/7] 슬라이드 렌더링 중...
[4/7] 영상 합성 중...
[5/7] 자막 생성 중...
[6/7] (아바타 — API 모드에서 건너뜀)
[7/7] 자막 합성 중...
```

> 전체 소요: 약 5~15분 (문단 수에 따라 다름)

---

## Step 4: 결과 확인 (5분)

### 4-1. 영상 파일 확인

Claude Code에게 물어봅니다:
```
projects/workshop-001/output/ 폴더에 어떤 파일이 있는지 보여줘
```

### 4-2. 영상 재생

```bash
# Mac
open projects/workshop-001/output/final_video.mp4

# Windows
start projects\workshop-001\output\final_video.mp4
```

### 4-3. 중간 산출물 확인

| 폴더 | 내용 | 확인할 것 |
|------|------|----------|
| `audio/` | TTS 음성 파일 | 음성 품질, 발음 |
| `slides/` | TSX 코드 + MP4 클립 | 슬라이드 디자인 |
| `broll/` | AI 생성 배경 이미지 | 이미지 스타일 |
| `output/` | 최종 영상 + 자막 | final_video.mp4 |

---

## Step 5: 수정 & 재생성 (선택)

### 특정 슬라이드 수정 (복사해서 바로 쓸 수 있는 프롬프트)

```
5번 슬라이드의 배경색을 파란색으로 바꿔줘
```

```
3번 슬라이드를 리스트 3개짜리 레이아웃으로 바꿔줘. 각 항목에 번호와 아이콘 추가.
```

```
전체 슬라이드 포인트 색상을 시안(#00d4ff)에서 골드(#d4a726)로 바꿔줘
```

```
7번 슬라이드를 A vs B 비교 레이아웃으로 바꿔줘. 왼쪽은 장점, 오른쪽은 단점.
```

```
1번 슬라이드(인트로) 제목을 96px로 키우고, 배경에 미세한 그라데이션(#0a0a1a → #1a1a3e) 넣어줘
```

### 슬라이드만 재렌더링

```bash
uv run python scripts/regenerate_slides.py workshop-001
```

### 전체 영상 재합성

```bash
uv run python scripts/recompose_video.py workshop-001
```

> **팁:** 대본을 수정하면 `/generate-video`부터 다시 실행해야 합니다. 슬라이드 디자인만 수정했으면 `regenerate_slides.py`만 돌리면 됩니다.

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `API key not found` | .env 파일 미설정 | `.env` 파일 확인, 키 재입력 |
| ElevenLabs `401 Unauthorized` | API 키 오류 또는 크레딧 소진 | 키 재확인, 크레딧 잔액 확인 |
| Remotion 렌더링 실패 | TSX 문법 오류 | Claude Code에게 "오류 수정해줘" |
| 빈 슬라이드 (텅 빈 영상) | `/generate-video` 미실행 | 파이프라인 전에 반드시 `/generate-video` 먼저 실행 |
| 매우 느린 렌더링 | 정상 동작 (문단 수 비례) | 기다리기 (10문단 ≈ 5분) |
| `ModuleNotFoundError` | Python 패키지 미설치 | `uv sync --extra genai` 재실행 |

---

## 실습 완료 체크리스트

- [ ] `.env` 파일에 API 키 설정 완료
- [ ] `projects/workshop-001/script.txt` 대본 생성 완료
- [ ] `/generate-video workshop-001` 실행 완료 (슬라이드 + B-roll + TTS 사전)
- [ ] 파이프라인 실행 완료
- [ ] `final_video.mp4` 재생 확인

> **축하합니다!** 첫 AI 자동 생성 영상을 만들었습니다.

### 다음 단계

| 하고 싶은 것 | 다음 문서 |
|-------------|----------|
| 쇼츠 + 캐러셀도 만들기 | **07-multi-format-strategy.md** |
| 슬라이드 수정 후 빠르게 반영 | **08-advanced-workflows.md** |
| 결과물 품질 개선하기 | **11-quality-iteration.md** |
| 나만의 채널 스타일 만들기 | **10-visual-identity.md** |
| 채널 유형별 실전 가이드 | **14-real-world-scenarios.md** |
