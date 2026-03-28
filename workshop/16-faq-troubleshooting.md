# FAQ & 트러블슈팅

> 자주 묻는 질문과 흔한 에러 해결법

---

## 설치 관련

### Q. Python 버전이 3.12인데 괜찮나요?

**A.** 3.13 이상이 필요합니다. [python.org/downloads](https://www.python.org/downloads/)에서 최신 버전을 설치해주세요.

```bash
python --version    # 3.13.x 이상이어야 함
```

### Q. Mac M1/M2에서 동작하나요?

**A.** 네, API 모드는 M1 이상이면 충분합니다. RAM 16GB 이상 권장.

### Q. Windows에서 `uv: command not found`

**A.** 터미널(PowerShell)을 완전히 닫고 다시 열어주세요. 안 되면 재설치:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Q. `claude: command not found`

**A.** 터미널을 완전히 닫고 다시 열어보세요. 안 되면 재설치:

```bash
# Mac
curl -fsSL https://claude.ai/install.sh | bash

# Windows (PowerShell)
irm https://claude.ai/install.ps1 | iex
```

### Q. `npm install`에서 에러가 납니다

**A.** Node.js 버전이 22 이상인지 확인하세요:

```bash
node --version    # v22.x.x 이상
```

안 되면 Claude Code에게 요청:
```
remotion 폴더에서 npm install을 다시 실행해줘. 오류가 나면 해결해줘.
```

---

## 파이프라인 관련

### Q. "빈 슬라이드"가 나옵니다 (텅 빈 영상)

**A.** `/generate-video`를 **먼저** 실행해야 합니다. 파이프라인만 돌리면 Claude Code가 만든 TSX 파일이 없어서 빈 영상이 나옵니다.

**올바른 순서:**
```
1. /generate-video my-project          ← 먼저! (TSX + B-roll 생성)
2. uv run video-automation pipeline ... ← 이후에 파이프라인 실행
```

### Q. B-roll 이미지가 생성되지 않습니다

**A.** 두 가지 확인:

1. `.env`에 `GOOGLE_API_KEY`가 설정되었는지 확인
2. `config.api.yaml`에서 B-roll이 `enabled: false`일 수 있음

B-roll 없이 실행하려면:
```bash
uv run video-automation pipeline script-to-video \
    --input projects/my-project/script.txt --project my-project --no-broll
```

B-roll을 활성화하려면:
```bash
ENABLE_BROLL=true uv run video-automation pipeline script-to-video \
    --input projects/my-project/script.txt --project my-project
```

### Q. ElevenLabs `401 Unauthorized`

**A.**
1. `.env`의 `ELEVENLABS_API_KEY` 재확인
2. [elevenlabs.io](https://elevenlabs.io) 접속 → 크레딧 잔액 확인
3. 키를 새로 발급받아 `.env`에 다시 입력

### Q. Remotion 렌더링이 매우 느립니다

**A.** 정상입니다. 슬라이드 개수에 비례하여 시간이 걸립니다.

| 문단 수 | 예상 렌더링 시간 |
|---------|----------------|
| 5개 | 약 2~3분 |
| 10개 | 약 3~5분 |
| 20개 | 약 6~10분 |
| 30개 | 약 10~15분 |

### Q. 영상 합성 중 FFmpeg 오류

**A.** Claude Code에게 에러 메시지를 보여주세요:

```
이 에러를 해결해줘: [에러 메시지 전체를 복사 붙여넣기]
```

흔한 원인:
- 파일 경로에 한글/공백이 포함된 경우
- FFmpeg 미설치 → `ffmpeg -version` 확인

### Q. `FileNotFoundError: script.txt`

**A.** 대본 파일이 올바른 위치에 있는지 확인:

```
projects/<project>/script.txt
```

파일 경로를 확인:
```bash
ls projects/my-project/    # Mac/Linux
dir projects\my-project\   # Windows
```

---

## Claude Code 관련

### Q. Claude Code가 응답을 멈췄습니다

**A.**
1. Enter를 한 번 눌러보세요
2. 그래도 안 되면 `Ctrl + C`로 중단 후 다시 실행:
```bash
claude --dangerously-skip-permissions
```

### Q. "이 작업은 권한이 필요합니다"

**A.** `--dangerously-skip-permissions` 옵션으로 실행했는지 확인:

```bash
# 이렇게 실행해야 합니다
claude --dangerously-skip-permissions
```

### Q. Skill 명령어(/generate-video 등)가 동작하지 않습니다

**A.**
1. 프로젝트 **루트 디렉토리**에서 Claude를 실행했는지 확인
2. `.claude/commands/` 폴더가 있는지 확인 (`/generate-video` 등의 커맨드는 `.claude/commands/`에 위치)
3. Claude Code에게 확인 요청:
```
사용 가능한 스킬 목록을 보여줘
```

---

## API 비용 관련

### Q. API 비용이 얼마나 드나요?

영상 1개 (10문단 기준) 예상 비용:

| 서비스 | 비용 | 비고 |
|--------|------|------|
| ElevenLabs | ~$0.10 | 약 800자 소모 |
| Gemini (B-roll) | ~$0.05 | 이미지 10장 |
| OpenAI (Whisper) | ~$0.01 | 쇼츠에만 사용 |
| Anthropic (Claude) | ~$0.20 | 슬라이드 생성 |
| **합계** | **~$0.36** | 약 500원 |

> Claude Code 사용 비용(Anthropic API)은 별도입니다. 슬라이드 생성, 분석 등에 사용됩니다.

### Q. 무료로 사용할 수 있나요?

**A.** 각 서비스의 무료 티어만으로 워크숍 실습은 충분합니다:

| 서비스 | 무료 티어 | 생성 가능 영상 |
|--------|----------|---------------|
| ElevenLabs | 월 10,000자 | ~12편 |
| Gemini | 일 50회 호출 | 충분 |
| OpenAI Whisper | Pay-as-you-go | 쇼츠에만 소량 |

지속적인 생산에는 유료 플랜이 필요할 수 있습니다.

---

## 공통 에러 메시지 & 해결법

| 에러 메시지 | 원인 | 해결 |
|------------|------|------|
| `ModuleNotFoundError` | Python 패키지 미설치 | `uv sync` 실행 |
| `FileNotFoundError: script.txt` | 대본 파일 없음 | 경로 확인, 파일 생성 |
| `ANTHROPIC_API_KEY not set` | 환경변수 미설정 | `.env` 파일 확인 |
| `npm ERR!` | Remotion 미설치 | `cd remotion && npm install` |
| `TimeoutError` | 렌더링 시간 초과 | 문단 수 줄이기 또는 재시도 |
| `401 Unauthorized` | API 키 오류 | 키 재확인, 크레딧 확인 |
| `ConnectionError` | 네트워크 문제 | 인터넷 연결 확인 |
| `TSX compilation error` | 슬라이드 코드 오류 | Claude Code에 "오류 수정해줘" |
| `ffmpeg: command not found` | FFmpeg 미설치 | `ffmpeg -version` 확인 후 재설치 |

---

---

## 고급 워크플로우 관련

### Q. 슬라이드 하나만 수정하고 싶은데 전체를 다시 돌려야 하나요?

**A.** 아닙니다. 부분 재실행이 가능합니다:

```bash
# 슬라이드만 재렌더링
uv run python scripts/regenerate_slides.py <project>

# 영상만 재합성 (자막/순서 변경 시)
uv run python scripts/recompose_video.py <project>
```

> 자세한 의사결정 트리는 **08-advanced-workflows.md**를 참조하세요.

### Q. 캐러셀 텍스트 품질을 높이고 싶어요

**A.** `/generate-carousel` 전에 `/carousel-copywriting`을 먼저 실행하세요. 카드별 카피라이팅과 8가지 메트릭 자가평가를 거칩니다.

---

## 그래도 안 될 때

### 방법 1: Claude Code에게 맡기기

```
이 에러를 해결해줘:
[에러 메시지 전체를 여기에 붙여넣기]
```

### 방법 2: 강사/보조강사에게 질문

워크숍 중에는 손을 들어주세요.

### 방법 3: 커뮤니티 오카방 (수업 후)

결제 후 별도 오카방에서 질문하시면 됩니다.

> **가장 중요한 팁:** 에러 메시지를 **전체 복사**해서 Claude Code에 보여주세요. 대부분의 문제를 Claude Code가 스스로 해결할 수 있습니다.
