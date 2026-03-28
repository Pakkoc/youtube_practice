# Video Automation

AI 영상 자동화 시스템 — 대본(`script.txt`) 하나로 유튜브 영상을 자동 생성합니다.

Freeform TSX 슬라이드, TTS 음성 합성, B-roll 삽입, 아바타 립싱크, 자막 합성까지 end-to-end 자동화.

5개 파이프라인 (영상 · 쇼츠 · 카루셀 · 영상→쇼츠 · 자막 합성), 21개 Feature 모듈, 4개 Config 프로필 지원.

## Quick Start

### API-Only 모드 (macOS / GPU 없는 환경)

GPU 없이 클라우드 API만으로 영상을 생성합니다.

```bash
# 1. 설치
git clone <repo-url> && cd video-automation
uv sync --extra genai

# 2. 시스템 도구 설치
brew install ffmpeg node           # macOS
cd remotion && npm install && cd ..

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력 (아래 "환경 변수" 섹션 참고)

# 4. 에셋 준비 (아래 "에셋 준비" 섹션 참고)

# 5. 실행
CONFIG_PROFILE=api uv run video-automation pipeline script-to-video \
    --input script.txt --project my-video
```

### Full 모드 (Windows + CUDA GPU)

로컬 모델(커스텀 TTS, FLUX.2, Ditto 아바타)을 활용하여 최고 품질 영상을 생성합니다.

```bash
# 1. 설치
git clone <repo-url> && cd video-automation
uv sync --extra cuda --extra genai

# FLUX.2 Klein 사용 시
uv pip install git+https://github.com/huggingface/diffusers.git

# 2. 시스템 도구 설치
# FFmpeg, Node.js + Remotion (cd remotion && npm install), Pretendard 폰트

# 3. 환경변수 설정
cp .env.example .env

# 4. 실행 (기본 프로필 = base)
uv run video-automation pipeline script-to-video \
    --input script.txt --project my-video
```

## 운영 모드 비교

| 기능 | API-Only (`api`) | Full (`base`) |
|------|:-:|:-:|
| TTS 음성 합성 | ElevenLabs API | 로컬 커스텀 보이스 (Qwen3-TTS) |
| 슬라이드 생성 | Remotion Freeform TSX | Remotion Freeform TSX |
| B-roll 이미지 | Gemini API (NanoBanana) | FLUX.2 Klein (로컬 GPU) |
| 아바타 립싱크 | 비활성화 | Ditto (로컬 GPU) |
| 자막 생성 | 결정론적 (Whisper 불필요) | 결정론적 (Whisper 불필요) |
| **GPU 필요** | **불필요** | **CUDA GPU 필수** |
| **소요 시간** (10문단) | ~5분 | ~15분 |

## 5개 파이프라인

| 파이프라인 | CLI 명령 | 입력 | 출력 |
|----------|---------|------|------|
| `script_to_video` | `pipeline script-to-video` | `script.txt` | 16:9 `final_video.mp4` |
| `script_to_shorts` | `pipeline script-to-shorts` | `script.txt` | 9:16 쇼츠 MP4 |
| `video_to_shorts` | `pipeline video-to-shorts` | video file | 9:16 쇼츠 클립 |
| `script_to_carousel` | `pipeline script-to-carousel` | `script.txt` | 카루셀 PNG |
| `add_subtitles` | `pipeline add-subtitles` | video file | 자막 합성 영상 |

### script_to_video 흐름 (7단계)

```
script.txt
  │
  ├── 1.  문단 분리
  │
  ├── 2.  ┌─ Freeform TSX 생성 (/generate-slides) ─┐
  │       ├─ TTS 생성 (ElevenLabs / 로컬) ──────────┤  [3-way 병렬]
  │       └─ B-roll 이미지 생성 ────────────────────┘
  │       B-roll 이미지 → Remotion 슬라이드 배경 (20% opacity)
  │
  ├── 3.  Remotion 슬라이드 렌더링 (TSX + duration + B-roll)
  │
  ├── 4.  영상 합성 (FFmpeg)
  │
  ├── 5.  자막 생성 (결정론적, 글자수 비례 시간 할당)
  │
  ├── 6.  아바타 배치 (Ditto clips + concat + overlay) [선택]
  │
  └── 7.  자막 합성 → final_video.mp4
```

## 슬라이드 시스템 (2 모드)

### Freeform TSX (기본)

Claude Code가 대본 맥락에 맞는 커스텀 TSX 슬라이드를 매번 새롭게 생성합니다. SVG 아이콘, 차트, 다이어그램, 다양한 레이아웃을 자유롭게 활용.

```bash
# Step 1: TSX 슬라이드 생성 (Claude Code 스킬)
/generate-slides 003

# Step 2: 파이프라인 실행 (기존 TSX 자동 감지 → 렌더링)
uv run video-automation pipeline script-to-video \
  --input projects/003/script.txt --project 003 --no-broll
```

### Manim CE (수학/과학 전용)

`/generate-slides` 스킬이 자동 판별하여 수학 수식, 좌표 그래프, 알고리즘 시각화에 Manim CE를 사용합니다.

## 환경 변수

`.env.example`을 `.env`로 복사 후 API 키를 설정합니다.

| 변수 | 용도 | API-Only | Full |
|------|------|:---:|:---:|
| `ANTHROPIC_API_KEY` | 슬라이드 생성, 자막 교정, B-roll 분석 | 필수 | 필수 |
| `OPENAI_API_KEY` | Whisper STT, GPT Vision 검증 | 필수 | 필수 |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS | 필수 | 선택 |
| `ELEVENLABS_SECOND_API_KEY` | ElevenLabs 보조 계정 (음성 소유 계정) | 선택 | 선택 |
| `GOOGLE_API_KEY` | NanoBanana (Gemini) 이미지 생성 | 필수 | 선택 |
| `SERPER_API_KEY` | B-roll 이미지 검색 (SerperDev) | 선택 | 선택 |
| `PEXELS_API_KEY` | B-roll 스톡 이미지 (Pexels) | 선택 | 선택 |

### 런타임 환경변수 오버라이드

```bash
ENABLE_AVATAR=false uv run video-automation ...           # 아바타 on/off
ENABLE_BROLL=false uv run video-automation ...            # B-roll on/off
IMAGE_GEN_BACKEND=nanobanana uv run video-automation ...  # 이미지 백엔드
CONFIG_PROFILE=api uv run video-automation ...            # 프로필 전환
```

## 에셋 준비

```
assets/
├── fonts/                       # 자막용 폰트 (필수)
│   ├── Pretendard-Bold.otf
│   ├── Pretendard-SemiBold.otf
│   └── ...                      # Pretendard 폰트 패밀리
├── references/                  # B-roll 레퍼런스 이미지 (선택)
│   └── chibi/                   # 스타일 참조용 이미지
└── avatar_image/                # 아바타 소스 이미지 (Full 모드만)
    └── vtuber-avatar.png
```

[Pretendard 폰트](https://github.com/orioncactus/pretendard)를 `assets/fonts/`에 배치하세요.

## Config 프로필 시스템

`config/` 폴더에 프로필별 YAML 파일로 설정을 관리합니다.

| 프로필 | 파일 | TTS | B-roll | 아바타 | 용도 |
|--------|------|-----|--------|--------|------|
| `base` (기본) | `config.base.yaml` | Qwen3-TTS (로컬) | FLUX.2 Klein | Ditto | CUDA GPU 환경 |
| `api` | `config.api.yaml` | ElevenLabs | NanoBanana (Gemini) | 비활성화 | macOS / GPU 없는 환경 |
| `asmr` | `config.asmr.yaml` | Custom Voice | NanoBanana | 선택 | ASMR 콘텐츠 |
| `shorts` | `config.shorts.yaml` | ElevenLabs | NanoBanana | 선택 | 9:16 쇼츠 전용 |

추가 설정: `config/tts_dictionary.yaml` — TTS 발음 교정 사전 (한글 + 오버라이드 매핑)

```bash
CONFIG_PROFILE=api uv run video-automation pipeline script-to-video \
    --input script.txt --project my-video
```

## 대본 형식

대본은 **빈 줄로 문단을 구분**하는 평문 텍스트입니다. 1 문단 = 1 슬라이드 = 1 TTS = 1 B-roll.

```text
첫 번째 문단입니다. 이 문단이 하나의 슬라이드와 TTS가 됩니다.

두 번째 문단입니다. 빈 줄로 구분하면 자동으로 새 문단으로 인식됩니다.

세 번째 문단입니다. 각 문단마다 B-roll 이미지도 1개씩 생성됩니다.
```

**자동 전처리:** Markdown 헤더, 구분선, 타임스탬프, 번호 매기기 자동 제거. 300자 이상 문단은 한국어 문장 단위 자동 분할.

## CLI 사용법

```bash
# 환경 정보 확인
uv run video-automation info

# 전체 파이프라인 (16:9 영상)
uv run video-automation pipeline script-to-video \
    --input script.txt --project my-video

# B-roll 없이 빠른 테스트
uv run video-automation pipeline script-to-video \
    --input script.txt --project my-video --no-broll

# 대본 기반 쇼츠 (9:16)
uv run video-automation pipeline script-to-shorts \
    --input script.txt --project my-shorts

# 영상에서 쇼츠 추출 (바이럴 구간 자동 선정)
uv run video-automation pipeline video-to-shorts \
    --input video.mp4 --project my-video

# 카루셀 카드뉴스
uv run video-automation pipeline script-to-carousel \
    --input script.txt --project my-video

# 자막 합성
uv run video-automation pipeline add-subtitles \
    --input video.mp4 --project my-video

# 개별 명령어
uv run video-automation tts generate --input paragraph.txt
uv run video-automation subtitles transcribe --input video.mp4
uv run video-automation subtitles burn --video video.mp4 --srt subtitles.srt

# 유틸리티 스크립트
uv run python scripts/regenerate_broll.py <project>         # B-roll만 재생성
uv run python scripts/regenerate_slides.py <project>        # 슬라이드 재렌더링
uv run python scripts/regenerate_carousel.py <project>      # 카루셀 재생성
uv run python scripts/recompose_video.py <project>          # 영상 재합성
uv run python scripts/validate_carousel.py <project>        # 카루셀 유효성 검증
uv run python scripts/validate_tsx_imports.py <project>     # TSX import 검증
uv run python scripts/split_long_paragraphs.py <project>    # 긴 문단 자동 분할
uv run python scripts/continue_pipeline.py <project>        # 중단된 파이프라인 재개
```

## 프로젝트 출력 구조

```
projects/my-video/
├── script.txt              # 입력 대본
├── paragraphs/             # 분리된 문단 (001.txt, 002.txt, ...)
├── slides/                 # Freeform TSX + MP4 (001.tsx, 001.mp4, ...)
├── audio/                  # TTS 음성 (001.wav, 002.wav, ...)
├── broll/
│   └── generated/          # B-roll 이미지 (슬라이드 배경으로 주입)
├── avatar/                 # (Full 모드만)
│   ├── clips/              # 문단별 아바타 클립
│   └── avatar.mp4          # 연결된 최종 아바타
├── carousel/               # 카루셀 카드뉴스 PNG
├── shorts_slides/          # 쇼츠 슬라이드 (9:16)
│   ├── *.tsx               # Shorts TSX 파일
│   ├── hook_titles.json    # 훅 타이틀 데이터
│   └── output/
│       └── final_shorts.mp4
└── output/
    ├── video_raw.mp4
    ├── video_with_avatar.mp4       # (Full 모드만)
    ├── video_with_subtitles.mp4
    └── final_video.mp4             # 최종 결과
```

## 파일 재사용 로직

파이프라인은 기존 파일을 자동 감지하여 재사용합니다. 특정 문단만 재생성하려면 해당 파일을 삭제하세요.

| 항목 | 재사용 조건 | 재생성하려면 |
|------|------------|-------------|
| TTS 음성 | `audio/001.wav` 존재 | 해당 wav 삭제 |
| Freeform TSX | `slides/001.tsx` 존재 | tsx 삭제 |
| 슬라이드 MP4 | `slides/001.mp4` + duration 일치 | mp4 삭제 |
| B-roll 이미지 | `broll/generated/broll_001.*` 존재 | 해당 파일 삭제 |
| 아바타 클립 | `avatar/clips/avatar_001.mp4` 존재 | 해당 mp4 삭제 |

## 아키텍처

[Feature-Sliced Design (FSD)](https://feature-sliced.design/) 5계층 구조를 따릅니다.

```
app/            → [Layer 1] CLI 진입점, 전역 설정, DI
pipelines/      → [Layer 2] 파이프라인 오케스트레이션
features/       → [Layer 3] 개별 기능 단위
entities/       → [Layer 4] 비즈니스 도메인 모델 (Pydantic)
shared/         → [Layer 5] 공용 코드 (API 클라이언트, FFmpeg, 유틸리티)
```

Import 규칙: **상위 -> 하위만 허용** (`import-linter`로 강제)

### 주요 Feature (21개)

| Feature | 설명 | 백엔드 |
|---------|------|--------|
| **텍스트 처리** | | |
| `split_paragraphs` | 대본 문단 분리 | Pure Python |
| `split_scenes` | 문장 단위 씬 분할 | Pure Python |
| `normalize_text` | 한국어 텍스트 정규화 | Pure Python |
| **음성 처리** | | |
| `generate_tts` | TTS 음성 합성 | ElevenLabs / Qwen3-TTS / Custom Voice |
| `validate_tts` | TTS 품질 검증 (STT 비교) | Whisper |
| `transcribe_audio` | 음성→텍스트 전사 | Whisper |
| `correct_subtitles` | STT 오류 교정 | GPT-5 |
| **시각 생성** | | |
| `generate_slides` | Freeform TSX + Manim CE 슬라이드 | Remotion / Manim |
| `analyze_broll` | B-roll 문단별 분석 | GPT-5 |
| `fetch_broll` | B-roll 이미지 생성 | FLUX.2 Klein / Flux Kontext / NanoBanana |
| `search_image` | B-roll 이미지 검색 | SerperDev + Vision |
| `generate_carousel` | 카루셀 카드뉴스 | Remotion |
| `generate_carousel_backgrounds` | 카루셀 배경 이미지 | FLUX.2 / NanoBanana |
| `generate_avatar` | 아바타 립싱크 | Ditto (로컬) |
| **영상 합성** | | |
| `compose_video` | 슬라이드쇼 합성 | FFmpeg |
| `generate_subtitles` | 결정론적 자막 생성 | Pure Python |
| `burn_subtitles` | 자막 합성 | FFmpeg |
| **쇼츠** | | |
| `select_viral_segments` | 바이럴 구간 선정 | GPT-5 |
| `render_shorts` | 쇼츠 9:16 렌더링 | Remotion |
| `render_shorts_slides` | 쇼츠 슬라이드 + 훅 타이틀 | Remotion |

## 시스템 요구사항

| 도구 | 용도 | API-Only | Full |
|------|------|:---:|:---:|
| Python 3.13+ | 런타임 | 필수 | 필수 |
| FFmpeg | 영상 합성 | 필수 | 필수 |
| Node.js + Remotion | 슬라이드/쇼츠/카루셀 렌더링 | 필수 | 필수 |
| Pretendard 폰트 | 자막/슬라이드 렌더링 | 필수 | 필수 |
| CUDA GPU | 로컬 모델 | 불필요 | 필수 |
| WSL2 | Ditto 아바타 | 불필요 | 필수 |

## 개발

```bash
# 의존성 설치 (개발)
uv sync --extra dev
cd remotion && npm install && cd ..

# Lint & Format
ruff check . && ruff format .

# Type check
mypy app shared entities

# Import 규칙 검증 (FSD 계층 위반 탐지)
lint-imports

# TypeScript 체크 (Remotion)
cd remotion && npx tsc --noEmit

# 테스트
pytest
pytest tests/features/test_generate_tts.py -v    # 단일 테스트
```

### 기술 스택

| 카테고리 | 기술 |
|---------|------|
| 언어 | Python 3.13+, TypeScript 5.9 |
| 빌드 | uv (Hatch backend), npm |
| 영상 렌더링 | Remotion 4.0, FFmpeg |
| AI/LLM | OpenAI GPT-5, Anthropic Claude |
| TTS | Qwen3-TTS (로컬), ElevenLabs (API) |
| 이미지 생성 | FLUX.2 Klein, Flux Kontext, NanoBanana (Gemini) |
| 아바타 | Ditto (lip-sync) |
| 설정 | Pydantic + YAML 프로필 |
| 품질 | ruff, mypy, pytest, import-linter |
| CLI | Click + Rich |

## 디렉토리 맵

```
video-automation/
├── app/                        # CLI 진입점, 전역 설정, DI
├── pipelines/
│   ├── script_to_video/        # 메인 파이프라인 (7단계, 16:9)
│   ├── script_to_shorts/       # 대본 → 쇼츠 (9:16)
│   ├── video_to_shorts/        # 영상 → 쇼츠 리퍼포징
│   ├── script_to_carousel/     # 카루셀 카드뉴스
│   └── add_subtitles/          # 자막 합성
├── features/
│   ├── split_paragraphs/       # 대본 문단 분리
│   ├── split_scenes/           # 문장 단위 씬 분할
│   ├── normalize_text/         # 한국어 텍스트 정규화
│   ├── generate_slides/        # Freeform TSX + Manim CE 슬라이드
│   ├── generate_tts/           # TTS 음성 합성
│   │   └── backends/           # elevenlabs, qwen_cuda, qwen_mps, custom_voice
│   ├── validate_tts/           # TTS 품질 검증
│   ├── transcribe_audio/       # STT (Whisper)
│   ├── correct_subtitles/      # STT 오류 교정
│   ├── compose_video/          # 영상 합성
│   ├── generate_subtitles/     # 결정론적 자막 생성
│   ├── analyze_broll/          # B-roll 분석 (문단 기반 1:1:1)
│   ├── fetch_broll/            # B-roll 이미지 생성
│   │   └── backends/           # flux2_klein, flux_kontext, nanobanana
│   ├── search_image/           # B-roll 이미지 검색 (SerperDev)
│   ├── generate_avatar/        # 아바타 립싱크 (Ditto)
│   ├── generate_carousel/      # 카루셀 카드 생성
│   ├── generate_carousel_backgrounds/  # 카루셀 배경 이미지
│   ├── burn_subtitles/         # 자막 합성
│   ├── select_viral_segments/  # 쇼츠 바이럴 구간 선정
│   ├── render_shorts/          # 쇼츠 렌더링 (영상 기반)
│   └── render_shorts_slides/   # 쇼츠 슬라이드 + 훅 타이틀
├── entities/                   # Pydantic 도메인 모델
├── shared/                     # 공용 유틸리티, API 클라이언트
├── config/                     # 프로필별 설정 YAML
├── prompts/                    # LLM 프롬프트 파일
├── remotion/                   # Remotion 프로젝트 (React 19 + Remotion 4.0)
│   └── src/
│       ├── slides/             # Freeform TSX 슬라이드 (16:9)
│       ├── shorts/             # 9:16 쇼츠 컴포넌트
│       ├── carousel/           # 카루셀 카드 (1080x1350)
│       ├── design/             # 디자인 시스템 (테마, 폰트, 애니메이션)
│       └── motifs/             # 재사용 가능한 모션 라이브러리
├── voice-fine-tuning/          # 음성 클론 스피커 프로필 파이프라인
├── assets/
│   ├── fonts/                  # Pretendard 폰트
│   └── references/             # B-roll 스타일 레퍼런스
├── projects/                   # 영상 프로젝트 데이터
├── scripts/                    # 유틸리티 스크립트 (12개)
├── docs/                       # 기술 문서
├── workshop/                   # 워크숍 교육 자료 (21개 가이드)
└── tests/                      # 테스트 (FSD 미러링)
```

## 문서

- **`docs/`** — 기술 문서 (아바타, B-roll, 카루셀, Remotion, 쇼츠, API 모드 설정)
- **`workshop/`** — 워크숍 교육 자료 (21개 가이드: 환경 설정부터 콘텐츠 전략까지)
  - 기초 (00-05): 환경 설정, 아키텍처, Claude Code, 스킬, 슬라이드
  - 워크플로 (06-10): 파이프라인, 멀티 포맷, 고급 워크플로, 설정, 비주얼
  - 심화 (11-20): 품질, 전략, 커스텀 스킬, 실전 시나리오, 배포, FAQ, 개발 방법론
