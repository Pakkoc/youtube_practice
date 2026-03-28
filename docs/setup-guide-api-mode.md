# 개발 환경 설정 가이드 (API Mode)

이 문서는 **GPU 없이 클라우드 API만으로** AI 영상 자동화 시스템을 실행하기 위한 환경 설정 가이드입니다.
API Mode에서는 ElevenLabs(TTS), OpenAI(GPT-5), Anthropic(Claude) 등 클라우드 API를 사용하므로 고성능 GPU가 필요 없습니다.

---

## 1. 시스템 요구 사항

| 항목 | 권장 사양 |
|------|----------|
| **RAM** | 16GB 이상 |
| **OS** | Windows 10/11 또는 macOS (M1 이상) |
| **저장 공간** | 10GB 이상 여유 공간 |

> 저사양 노트북에서도 동작하지만, Remotion 영상 렌더링 시 속도가 느려질 수 있습니다.

---

## 2. 외부 서비스 가입 (무료 티어)

아래 서비스들은 **무료 티어**로 사용합니다. 미리 가입하고 API 키를 발급받아 주세요.

| 서비스 | 링크 | 용도 | 필요한 것 |
|--------|------|------|----------|
| **GitHub** | [github.com](https://github.com/) | 코드 관리 | 계정 |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) | 슬라이드 생성 (GPT-5) | API 키 |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) | Claude Code (개발 도구) | API 키 |
| **ElevenLabs** | [elevenlabs.io](https://elevenlabs.io/) | TTS 음성 합성 | API 키 |
| **Google AI Studio** | [aistudio.google.com](https://aistudio.google.com/) | B-roll 이미지 생성 (Gemini) | API 키 (선택) |

> B-roll 이미지 생성은 선택 사항입니다. 없어도 영상 생성이 가능합니다.

---

## 3. 소프트웨어 설치

### 필수 소프트웨어

| 소프트웨어 | 링크 | 설치 확인 명령어 |
|-----------|------|----------------|
| **Python 3.13+** | [python.org](https://www.python.org/downloads/) | `python --version` |
| **Node.js** (LTS 22+) | [nodejs.org](https://nodejs.org/) | `node --version` |
| **Git** | [git-scm.com](https://git-scm.com/) | `git --version` |
| **FFmpeg** | [ffmpeg.org](https://ffmpeg.org/download.html) | `ffmpeg -version` |
| **uv** (Python 패키지 매니저) | [docs.astral.sh/uv](https://docs.astral.sh/uv/) | `uv --version` |
| **VS Code** | [code.visualstudio.com](https://code.visualstudio.com/) | — |

### FFmpeg 설치 방법

> **중요:** FFmpeg에 자막 필터(libass)가 포함되어야 자막 합성이 됩니다.

**Windows:**
```powershell
# winget으로 설치 (권장, full 버전에 libass 포함)
winget install Gyan.FFmpeg

# 또는 scoop으로 설치
scoop install ffmpeg
```

**macOS:**
```bash
# 기본 brew install ffmpeg에는 libass(자막 필터)가 없습니다.
# homebrew-ffmpeg tap을 사용하세요:
brew tap homebrew-ffmpeg/ffmpeg
brew install homebrew-ffmpeg/ffmpeg/ffmpeg

# 설치 후 자막 필터 확인:
ffmpeg -filters 2>&1 | grep subtitles
# "subtitles" 가 나오면 정상
```

### uv 설치 방법

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 4. VS Code 확장 프로그램

| 확장 프로그램 | ID | 용도 |
|-------------|-----|------|
| **Claude Code** | `Anthropic.claude-code` | AI 코딩 어시스턴트 |
| **Markdown Preview Enhanced** | `shd101wyy.markdown-preview-enhanced` | 마크다운 미리보기 |

VS Code에서 `Ctrl+Shift+X` → 위 ID로 검색하여 설치합니다.

---

## 5. 프로젝트 설정

### 5-1. 저장소 클론

```bash
git clone https://github.com/<your-org>/Youtube-Automation.git
cd Youtube-Automation
```

### 5-2. Python 의존성 설치

```bash
# 기본 의존성 (API mode에 필요한 전부)
uv sync
```

> GPU/CUDA 관련 패키지(`torch`, `diffsynth` 등)는 설치하지 않아도 됩니다.

### 5-3. Remotion (영상 렌더링 엔진) 설치

```bash
cd remotion
npm install
cd ..
```

### 5-4. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일을 열고 API 키를 입력합니다:

```env
# 필수
OPENAI_API_KEY=sk-...           # OpenAI API 키 (GPT-5, 슬라이드 생성)
ELEVENLABS_API_KEY=sk_...       # ElevenLabs API 키 (TTS 음성 합성)

# 선택 (B-roll 이미지 생성 시 필요)
GOOGLE_API_KEY=AI...            # Google AI Studio API 키
```

---

## 6. 실행

### 환경 확인

```bash
uv run video-automation info
```

### 영상 생성 (API Mode)

```bash
# script.txt 파일을 준비한 후:
CONFIG_PROFILE=community uv run video-automation pipeline script-to-video \
    --input script.txt --project my-first-video
```

> `community` 프로필은 아바타와 B-roll을 비활성화하여 가장 빠르게 영상을 생성합니다.
> 추가 API 키가 있다면 `api` 프로필을 사용할 수도 있습니다.

### Windows PowerShell에서 실행 시

```powershell
$env:CONFIG_PROFILE='community'
uv run video-automation pipeline script-to-video --input script.txt --project my-first-video
```

### script.txt 형식

빈 줄로 문단을 구분합니다. **1 문단 = 1 슬라이드 = 1 TTS 오디오.**

```text
인공지능이 우리 일상을 어떻게 바꾸고 있는지 알아보겠습니다.

첫 번째로, AI 챗봇은 이제 고객 서비스의 핵심입니다. 24시간 응대가 가능하고, 비용도 크게 절감됩니다.

두 번째로, AI 기반 추천 시스템은 넷플릭스, 유튜브 등에서 이미 널리 사용되고 있습니다.
```

---

## 7. 트러블슈팅

| 증상 | 해결 방법 |
|------|----------|
| `uv: command not found` | uv 설치 후 터미널 재시작 |
| `ffmpeg: command not found` | FFmpeg 설치 후 PATH에 추가, 터미널 재시작 |
| `npm install` 실패 | Node.js LTS 버전 확인 (`node --version` → 22+) |
| ElevenLabs 401 에러 | `.env`의 `ELEVENLABS_API_KEY` 확인 |
| 빈 슬라이드 생성 | `.env`의 `OPENAI_API_KEY` 확인 |
| Remotion 렌더링 느림 | 정상입니다. 문단 수에 비례하여 시간이 걸립니다 |
| 자막 합성 실패 (subtitles filter) | `brew reinstall ffmpeg` (Mac) 또는 FFmpeg full 버전 재설치 (Win). `ffmpeg -filters 2>&1 \| grep subtitles`로 확인 |
