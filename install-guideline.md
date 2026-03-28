# AI 영상 자동화 팩토리 - 설치 가이드

> 이 문서는 **컴퓨터에 익숙하지 않은 분**도 따라할 수 있도록 작성되었습니다.

---

## 클로드코드가 처음이신 분들은 아래 영상이 제일 초보 친화적이라서 영상 시간 조금 들여서 학습해주시고 와주시면 감사하겠습니다! (32분까지 보셔도 됩니다)

https://youtu.be/1_bRmkUvjHA

---

## 전체 설치 요약

| 구분 | 내용 | 누가 하나요? | 언제? |
|------|------|-------------|-------|
| **숙제 1** | 계정 가입 + 핵심 소프트웨어 설치 | **본인이 직접** | 수업 전 |
| **숙제 2** | FFmpeg, uv 설치 | **Claude Code에게 자연어로 요청** | 수업 전 |
| **수업 당일** | GitHub 연결 + 패키지 설치 + API 키 설정 | **강사와 함께** | 수업 시작 시 |

> **숙제가 어려우신 분은 오프라인 강의 당일 1시간 일찍 오시면 도움을 드립니다.**
> 숙제만 완료해 오시면 나머지는 수업 시작할 때 함께 진행합니다.

---

# 숙제 1: 계정 가입 + 소프트웨어 설치 (예상 30~40분)

> 이 부분은 **반드시 본인이 직접** 해야 합니다.
> Claude Code가 대신할 수 없는 영역입니다.

## 1. 권장 사양

- **RAM 16GB 이상** 권장
- **Windows**: RAM 16GB 이상의 노트북
- **Mac**: M 시리즈 맥북 (M1 이상)
- 저사양 노트북은 영상 렌더링 시 속도가 느려질 수 있습니다

## 2. 서비스 가입 (무료)

아래 서비스들은 **무료 티어**로 사용합니다. 미리 가입해 주세요.

| 서비스 | 링크 | 용도 | 비고 |
|--------|------|------|------|
| **GitHub** | [github.com](https://github.com/) | 코드 관리 | 필수 |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) | Claude Code + API | 필수 (API 키 발급) |
| **Vercel** | [vercel.com](https://vercel.com/) | 배포 | GitHub 계정으로 가입 |
| **Google AI Studio** | [aistudio.google.com](https://aistudio.google.com/) | Gemini AI 모델 | API 키 발급 |
| **Serper** | [serper.dev](https://serper.dev/) | 구글 이미지 검색 | API 키 발급 |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) | Whisper STT, GPT | API 키 발급 |
| **ElevenLabs** | [elevenlabs.io](https://elevenlabs.io/) | TTS 음성 합성 | API 키 발급 |

> **API 키란?** 외부 AI 서비스를 사용하기 위한 비밀번호 같은 것입니다. 각 서비스에 가입하면 "API Key" 메뉴에서 발급받을 수 있습니다.

## 3. 핵심 소프트웨어 설치

아래 5개를 순서대로 설치해 주세요.

### (1) Node.js (LTS 22 이상)

- 다운로드: [nodejs.org](https://nodejs.org/)
- **LTS** 버전을 다운로드하세요 (왼쪽 초록색 버튼)
- 설치 후 확인:

```bash
node --version
# v22.16.0 이상이 나오면 성공
```

### (2) Git

- 다운로드: [git-scm.com](https://git-scm.com/)
- 설치 시 모든 옵션 **기본값 그대로** Next 클릭
- 설치 후 확인:

```bash
git --version
# git version 2.x.x 가 나오면 성공
```

### (3) Python 3.13 이상

- 다운로드: [python.org/downloads](https://www.python.org/downloads/)
- 최신 버전 다운로드

> **Windows 사용자 필독 (매우 중요!)**
>
> 설치 첫 화면에서 반드시 **"Add python.exe to PATH"** 체크박스를 체크하세요!
> 이걸 안 하면 이후 모든 과정에서 오류가 납니다.
>
> ![Python PATH 설정](https://docs.python.org/3/_images/win_installer.png)

- 설치 후 확인:

```bash
python --version
# Python 3.13.x 가 나오면 성공
```

> Windows에서 `python`이 안 되면 `python3`으로 시도해 보세요.

- Python과 uv 설치는 [이 블로그 글](https://m.blog.naver.com/math717/223984322849)도 참고해 주세요.

### (4) VS Code

- 다운로드: [code.visualstudio.com](https://code.visualstudio.com/)
- 설치 후 열어주세요

**VS Code 확장 프로그램 2개 설치:**

VS Code 왼쪽 사이드바에서 확장 프로그램 아이콘(네모 4개 모양)을 클릭하고 검색합니다.
이를 익스텐션이라고 부릅니다.

| 확장 프로그램 | 검색어 | 용도 |
|-------------|--------|------|
| **Claude Code for VS Code** | `Anthropic.claude-code` | AI 코딩 도우미 |
| **Markdown Preview Enhanced** | `shd101wyy.markdown-preview-enhanced` | 문서 미리보기 |

### (5) Claude Code CLI 설치

> 출처: [Claude Code 공식 문서](https://code.claude.com/docs/en/overview)

**Mac 사용자** — 터미널을 열고:

```bash
# 방법 1: 공식 설치 스크립트 (권장 — 자동 업데이트 지원)
curl -fsSL https://claude.ai/install.sh | bash

# 방법 2: Homebrew
brew install --cask claude-code
```

**Windows 사용자** — PowerShell을 열고:

```powershell
# 방법 1: 공식 설치 스크립트 (권장 — 자동 업데이트 지원)
irm https://claude.ai/install.ps1 | iex

# 방법 2: WinGet
winget install Anthropic.ClaudeCode
```

> **Windows는 Git이 먼저 설치되어 있어야 합니다.** (위 2번에서 이미 설치했다면 OK)

설치 후 확인:

```bash
claude --version
# 버전 번호가 나오면 성공
```

**첫 실행 & 로그인:**

```bash
claude
# 처음 실행하면 브라우저가 열리면서 로그인 화면이 나옵니다.
# Anthropic 계정으로 로그인하세요.
```

> **설치가 안 될 때:**
> - Mac: 터미널을 완전히 닫고 다시 열어서 `claude --version` 재시도
> - Windows: PowerShell을 **관리자 권한**으로 실행 후 재시도
> - 공식 트러블슈팅: https://code.claude.com/docs/en/troubleshooting

## 4. 숙제 1 완료 체크리스트

터미널에서 아래 명령어를 하나씩 실행해 보세요. **모두 버전 번호가 나오면 숙제 1 완료!**

```bash
node --version      # v22.x.x 이상
git --version       # git version 2.x.x
python --version    # Python 3.13.x 이상
claude --version    # 버전 번호 출력
```

- [ ] 위 4개 명령어 모두 버전 번호가 나온다
- [ ] GitHub, Anthropic 등 서비스에 가입했다
- [ ] VS Code + 확장 프로그램 2개를 설치했다
- [ ] Claude Code에 로그인했다 (`claude` 실행 후 브라우저 로그인)

---

# 숙제 2: Claude Code에게 자연어로 설치 맡기기 (예상 5~10분)

> 숙제 1이 완료되어야 진행할 수 있습니다.
> **Claude Code를 실행하고 프롬프트를 복사-붙여넣기만 하면 됩니다.**
> 이 과정을 통해 "AI에게 자연어로 설치를 맡기는" 경험을 해보세요!

## 1. Claude Code 실행

터미널(Mac) 또는 PowerShell(Windows)을 열고 아래 명령어를 실행합니다:

```bash
claude --dangerously-skip-permissions
```

> **`--dangerously-skip-permissions`란?**
> Claude Code가 파일 설치/수정을 할 때마다 일일이 허락을 구하지 않도록 하는 옵션입니다.
> 매번 "허락하시겠습니까?"가 뜨면 혼란스러우므로 이 옵션을 사용합니다.

Claude Code가 실행되면 대화창이 나타납니다. 아래 프롬프트를 **복사해서 붙여넣기** 하세요.

## 2. FFmpeg + uv + yt-dlp 설치

### Mac 사용자 — 아래를 복사해서 붙여넣으세요

```
현재 저는 Mac을 사용하고 있습니다. 아래 3가지를 설치해 주세요:
1. FFmpeg (자막 합성에 libass 포함 필요 — 아래 명령어 순서대로 실행)
   brew tap homebrew-ffmpeg/ffmpeg
   brew install homebrew-ffmpeg/ffmpeg/ffmpeg
2. uv (Python 패키지 매니저)
3. yt-dlp (YouTube 영상 다운로드 도구)
   brew install yt-dlp

설치 후 각각 버전을 확인하고, ffmpeg -filters 2>&1 | grep subtitles 로 자막 필터가 있는지도 확인해 주세요.
```

> Mac에서 Homebrew가 없다면 Claude Code가 Homebrew도 자동으로 설치해줍니다.

> **중요:** 기본 `brew install ffmpeg`에는 자막 필터(libass)가 없습니다.
> 반드시 `homebrew-ffmpeg` tap을 사용하세요:
> ```bash
> brew tap homebrew-ffmpeg/ffmpeg
> brew install homebrew-ffmpeg/ffmpeg/ffmpeg
> ```
> 기존에 ffmpeg이 설치되어 있으면 먼저 `brew uninstall ffmpeg` 후 위 명령어를 실행하세요.

### Windows 사용자 — 아래를 복사해서 붙여넣으세요

```
현재 저는 Windows를 사용하고 있습니다. 아래 3가지를 설치해 주세요:
1. FFmpeg (winget install Gyan.FFmpeg) — full 버전 권장 (자막 필터 포함)
2. uv (Python 패키지 매니저)
3. yt-dlp (YouTube 영상 다운로드 도구)
   winget install yt-dlp.yt-dlp

설치 후 각각 버전을 확인해서 알려주세요.
```

## 3. 설치 확인

Claude Code가 작업을 끝내면 아래처럼 버전이 출력되었는지 확인하세요:

```
ffmpeg -version     # 버전 정보가 나오면 성공
uv --version        # 예: uv 0.x.x 가 나오면 성공
yt-dlp --version    # 예: 2025.x.x 가 나오면 성공
```

**자막 필터 확인 (중요!):**
```bash
ffmpeg -filters 2>&1 | grep subtitles
# "subtitles" 가 나오면 자막 합성 가능
# 아무것도 안 나오면 FFmpeg를 재설치해야 합니다 (libass 필요)
```

> 만약 실패했다면 Claude Code에게 "오류를 해결해 주세요"라고 말하면 됩니다.

## 4. 숙제 2 완료 체크리스트

- [ ] Claude Code를 `--dangerously-skip-permissions`로 실행했다
- [ ] FFmpeg가 설치되었다 (`ffmpeg -version`)
- [ ] uv가 설치되었다 (`uv --version`)
- [ ] yt-dlp가 설치되었다 (`yt-dlp --version`)

> **숙제 1 + 숙제 2까지 해오시면 됩니다!** 아래는 수업 당일에 강사와 함께 진행합니다.

---

# 수업 당일: 샘호트만 + 보조강사와 함께 진행

> 이 부분은 **왕초보도 막히지 않도록 강사가 화면을 보여주며 함께** 진행합니다.
> 혼자 하실 필요 없습니다. 수업 시간에 같이 합니다.

## 1. 프로젝트 파일 다운로드

### zip 파일 다운로드 + 압축 해제

1. 강사가 안내하는 다운로드 링크에서 `youtube-automation-workshop.zip`을 다운로드합니다
2. 바탕화면에 압축을 해제합니다

**Mac 사용자** — 터미널에서:

```bash
# 바탕화면의 프로젝트 폴더로 이동
cd ~/Desktop/youtube-automation-workshop

# Git 저장소 초기화 (선택 — 버전 관리를 원하면)
git init
```

**Windows 사용자** — 명령 프롬프트(cmd)에서:

```cmd
# 바탕화면의 프로젝트 폴더로 이동
cd %USERPROFILE%\Desktop\youtube-automation-workshop

# Git 저장소 초기화 (선택 — 버전 관리를 원하면)
git init
```

### VS Code에서 프로젝트 열기

```bash
code .
```

또는 VS Code를 열고 **File > Open Folder**로 압축 해제한 폴더를 선택합니다.

## 2. Remotion 설치 (영상 렌더링 엔진)

> Clone 후에야 `remotion/` 폴더가 생기므로, 이 단계는 수업 당일에 진행합니다.

VS Code 터미널에서 아래 명령어를 실행합니다:

```bash
cd remotion
npm install
cd ..
```

> Remotion은 코드로 영상을 만드는 도구입니다. React 기반이라 Node.js 패키지를 따로 설치해야 합니다.

또는 Claude Code에게 자연어로 요청해도 됩니다:

```
remotion 폴더로 이동해서 npm install을 실행해 주세요.
설치가 제대로 되었는지 확인해 주세요.
```

## 3. Python 패키지 전체 설치 (uv sync)

> `uv sync`는 이 프로젝트에 필요한 Python 라이브러리 수십 개를 한 번에 설치하는 명령어입니다.

VS Code 터미널에서 아래 명령어를 순서대로 실행합니다:

```bash
uv sync --extra genai
uv sync --extra dev
```

> 각 명령어가 끝날 때까지 기다려 주세요. 처음 실행 시 수 분이 걸릴 수 있습니다.

## 4. 환경 변수 파일(.env) 설정

### .env 파일 만들기

**Mac:**
```bash
cp .env.example .env
```

**Windows:**
```cmd
copy .env.example .env
```

### API 키 입력하기

VS Code에서 `.env` 파일을 열고, 각 서비스에서 발급받은 API 키를 입력합니다:

```
OPENAI_API_KEY=sk-여기에_내_키_입력
GOOGLE_API_KEY=여기에_내_키_입력
ELEVENLABS_API_KEY=여기에_내_키_입력
SERPER_API_KEY=여기에_내_키_입력
```

> API 키를 아직 발급받지 않았다면 이 시간에 함께 발급합니다.

## 5. 전체 설치 검증

모든 설치가 끝나면 터미널에서 아래를 확인합니다:

```bash
ffmpeg -version          # FFmpeg 버전 출력
uv --version             # uv 버전 출력
yt-dlp --version         # yt-dlp 버전 출력
python --version         # Python 3.13.x
node --version           # v22.x.x
```

---

# 문제 해결 (Troubleshooting)

## 자주 발생하는 문제

### "python을 찾을 수 없습니다" (Windows)

**원인:** Python 설치 시 PATH를 추가하지 않음

**해결:**
1. Python 설치 프로그램을 다시 실행
2. "Modify" 선택
3. "Add python.exe to PATH" 체크 후 설치

### "npm: command not found"

**원인:** Node.js가 설치되지 않았거나 터미널을 재시작하지 않음

**해결:**
1. Node.js가 설치되었는지 확인
2. 터미널(명령 프롬프트)을 **완전히 닫고 다시 열기**

### "claude: command not found"

**원인:** Claude Code CLI가 설치되지 않았거나 터미널을 재시작하지 않음

**해결:**
1. 터미널을 **완전히 닫고 다시 열기**
2. 그래도 안 되면 다시 설치:

**Mac:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://claude.ai/install.ps1 | iex
```

> 공식 문서: https://code.claude.com/docs/en/overview

### "uv sync" 실행 시 오류

**원인:** Python 버전이 3.13 미만이거나 uv가 설치되지 않음

**해결:**
```bash
python --version    # 3.13 미만이면 Python을 최신 버전으로 재설치
uv --version        # 명령어가 안 되면 uv를 먼저 설치 (숙제 2 참고)
```

### Mac에서 "brew: command not found"

**원인:** Homebrew가 설치되지 않음

**해결:** Claude Code에게 요청하세요:
```
Homebrew를 설치해 주세요.
```

### "remotion: not found" 또는 npm install 오류

**원인:** Node.js 버전이 낮거나 remotion 폴더에서 npm install을 하지 않음

**해결:** Claude Code에게 요청하세요:
```
remotion 폴더에서 npm install을 다시 실행해 주세요. 오류가 나면 원인을 파악해서 해결해 주세요.
```

---

# 전체 완료 체크리스트

| 구분 | 항목 | 확인 |
|------|------|------|
| **숙제 1** | GitHub, Anthropic 등 서비스 가입 | [ ] |
| **숙제 1** | Node.js 22+, Git, Python 3.13+, VS Code 설치 | [ ] |
| **숙제 1** | Claude Code CLI 설치 + 로그인 | [ ] |
| **숙제 2** | FFmpeg 설치 (`ffmpeg -version`) | [ ] |
| **숙제 2** | uv 설치 (`uv --version`) | [ ] |
| **숙제 2** | yt-dlp 설치 (`yt-dlp --version`) | [ ] |
| **수업 당일** | zip 다운로드 + 압축 해제 완료 | [ ] |
| **수업 당일** | Remotion npm install 완료 | [ ] |
| **수업 당일** | `uv sync` Python 패키지 설치 완료 | [ ] |
| **수업 당일** | `.env` 파일 생성 + API 키 입력 | [ ] |

---

> **그래도 막히면?** 강의 당일 **1시간 일찍** 오시면 설치를 도와드립니다.
> 숙제 1 + 숙제 2만 완료해 오시면 나머지는 수업 시작할 때 함께 10분이면 끝납니다!
