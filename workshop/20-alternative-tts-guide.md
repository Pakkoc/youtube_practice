# 대체 TTS 백엔드 연동 가이드

> ElevenLabs 외 MiniMax, Fish Audio 등으로 TTS를 교체하는 응용 매뉴얼

---

## 왜 대체 TTS를 고려하나요?

| 서비스 | 강점 | 가격대 | 음성 복제 |
|--------|------|--------|-----------|
| **ElevenLabs** | 최고 품질, 한국어 우수 | $5~22/월 | 가능 (30초 샘플) |
| **MiniMax** | 저렴, 감정 표현 우수, 한국어 지원 | ~$0.1/10만자 | 가능 (10초 샘플) |
| **Fish Audio** | 오픈소스 기반, 초저렴 | $0.015/1000자 | 가능 (15초 샘플) |

특히 **음성 복제(Voice Cloning)**를 저렴하게 시도하고 싶은 분들에게 MiniMax와 Fish Audio는 좋은 대안입니다.

---

## 이 프로젝트의 TTS 구조 (이해하기)

```
features/generate_tts/
├── model.py          ← TTSBackend 추상 클래스 (인터페이스)
├── lib.py            ← 백엔드 선택 & 실행 (팩토리)
├── preprocess.py     ← 발음 사전 + 숫자 정규화
├── sidecar.py        ← 오디오 메타데이터 캐시
└── backends/
    ├── qwen_cuda.py      ← NVIDIA GPU 로컬
    ├── qwen_mps.py       ← Apple Silicon 로컬
    ├── elevenlabs_api.py ← ElevenLabs API ✅ 워크숍 기본
    └── custom_voice.py   ← 파인튜닝 음성 복제
```

**핵심 포인트**: 새 TTS를 추가하려면 `TTSBackend` 추상 클래스를 구현하는 파일 1개 + 설정 몇 줄이면 됩니다. Claude Code에게 시키면 자동으로 해줍니다.

### TTSBackend 인터페이스 (3개 메서드만 구현하면 됨)

```python
class TTSBackend(ABC):
    def generate(self, request: TTSRequest) -> TTSResult:  # 텍스트 → 오디오
    def is_available(self) -> bool:                          # API 키 있는지 확인
    def name(self) -> str:                                   # 백엔드 이름
```

---

## Part 1: Claude Code에게 요청하는 법

### 기본 원칙

**Claude Code는 이 프로젝트의 TTS 구조를 이미 알고 있습니다.** CLAUDE.md와 스킬 시스템에 아키텍처가 기술되어 있기 때문에, "MiniMax 백엔드 추가해줘"라고만 해도 어디에 어떤 파일을 만들어야 하는지 파악합니다.

### 핵심 프롬프트 패턴

```
[무엇을] + [어떤 서비스로] + [필요한 정보]
```

---

## Part 2: MiniMax TTS 연동

### MiniMax 사전 준비

1. [minimaxi.com](https://www.minimaxi.com) 가입
2. API Key 발급 (무료 크레딧 제공)
3. `.env` 파일에 추가:
   ```
   MINIMAX_API_KEY=your_api_key_here
   MINIMAX_GROUP_ID=your_group_id_here
   ```

### 프롬프트 예시 1: 기본 MiniMax 백엔드 추가

```
MiniMax TTS 백엔드를 추가해줘.

- API: MiniMax T2A v2 (https://www.minimaxi.com/document/T2A%20V2)
- 엔드포인트: POST https://api.minimaxi.com/v1/t2a_v2
- 인증: Authorization: Bearer {MINIMAX_API_KEY}
- 요청 body: { "model": "speech-02-hd", "text": "...", "voice_setting": { "voice_id": "..." } }
- 응답: MP3 바이너리
- 환경변수: MINIMAX_API_KEY, MINIMAX_GROUP_ID
- config에 minimax 섹션 추가하고, force_backend: minimax로 전환 가능하게 해줘
```

### 프롬프트 예시 2: MiniMax 음성 복제

```
MiniMax 백엔드가 추가된 상태에서, Voice Clone 기능도 연동해줘.

- Voice Clone API: POST https://api.minimaxi.com/v1/voice_clone
- 10초짜리 WAV 샘플을 업로드하면 voice_id를 발급해줌
- 발급받은 voice_id를 config.api.yaml의 minimax.voice_id에 넣으면 됨
- 참고 문서: https://www.minimaxi.com/document/Voice%20Clone
```

### 프롬프트 예시 3: 간단 버전 (문서 직접 참조 요청)

```
MiniMax의 T2A v2 API로 TTS 백엔드를 만들어줘.
API 문서 URL: https://www.minimaxi.com/document/T2A%20V2
elevenlabs_api.py를 참고해서 같은 패턴으로 만들면 돼.
환경변수는 MINIMAX_API_KEY.
```

---

## Part 3: Fish Audio TTS 연동

### Fish Audio 사전 준비

1. [fish.audio](https://fish.audio) 가입
2. API Key 발급
3. `.env` 파일에 추가:
   ```
   FISH_AUDIO_API_KEY=your_api_key_here
   ```

### 프롬프트 예시 1: 기본 Fish Audio 백엔드 추가

```
Fish Audio TTS 백엔드를 추가해줘.

- API: Fish Audio TTS v1
- 엔드포인트: POST https://api.fish.audio/v1/tts
- 인증: Authorization: Bearer {FISH_AUDIO_API_KEY}
- 요청 body: { "text": "...", "reference_id": "모델ID", "format": "mp3" }
- 응답: 오디오 바이너리 스트림
- 환경변수: FISH_AUDIO_API_KEY
- config에 fish_audio 섹션 추가하고 force_backend: fish_audio로 전환 가능하게
```

### 프롬프트 예시 2: Fish Audio 음성 복제

```
Fish Audio 백엔드에서 Voice Clone을 쓰고 싶어.

- 15초짜리 WAV 참조 음성을 Fish Audio 대시보드에서 업로드하면 reference_id 발급됨
- 또는 API로 reference audio를 업로드: POST https://api.fish.audio/model
- 발급받은 reference_id를 config에 넣으면 끝
- config/config.api.yaml의 fish_audio.reference_id 필드로 관리해줘
```

### 프롬프트 예시 3: 오픈소스 로컬 버전

```
Fish Audio의 Fish Speech v1.5 모델을 로컬에서 돌리는 백엔드도 만들어줘.
- GitHub: https://github.com/fishaudio/fish-speech
- pip install fish-speech로 설치
- VRAM 4GB면 충분
- 로컬 서버 모드: python -m fish_speech.serve --port 8080
- 엔드포인트: POST http://localhost:8080/v1/tts
- force_backend: fish_local로 선택 가능하게
```

---

## Part 4: 범용 프롬프트 (어떤 TTS든)

### 패턴 A: API 문서 URL만 주기

```
[서비스명] TTS를 이 프로젝트에 연동해줘.
API 문서: [URL]
환경변수: [API_KEY_NAME]
elevenlabs_api.py 패턴을 참고해서 동일한 구조로 만들어줘.
```

이것만으로도 Claude Code가 다음을 자동 수행합니다:
1. `features/generate_tts/backends/[서비스명].py` 생성
2. `shared/config/schema.py`에 Config 클래스 추가
3. `features/generate_tts/lib.py`의 `_load_backend()`에 등록
4. `config/config.api.yaml`에 설정 섹션 추가

### 패턴 B: 기존 백엔드 교체

```
현재 ElevenLabs로 되어있는 TTS를 MiniMax로 바꿔줘.
config/config.api.yaml에서 force_backend를 minimax로 설정하면 돼.
```

### 패턴 C: A/B 테스트

```
같은 script.txt로 ElevenLabs와 MiniMax 두 가지 TTS로 각각 음성을 생성해서 비교하고 싶어.

1. ElevenLabs로 projects/test-el/ 에 생성
2. MiniMax로 projects/test-mm/ 에 생성
3. 각각 force_backend 환경변수로 전환해줘
```

### 패턴 D: 음성 복제 후 파이프라인 연결

```
MiniMax로 내 목소리를 복제했어. voice_id는 "xxx"야.
이걸 config.api.yaml에 설정하고, /generate-video로 영상 만들어줘.
```

---

## Part 5: 설정 파일 구조 미리보기

Claude Code가 작업을 완료하면 이런 구조가 됩니다:

### config/config.api.yaml (추가되는 부분)

```yaml
tts:
  force_backend: minimax    # elevenlabs → minimax로 변경

  # 기존 ElevenLabs (그대로 유지)
  elevenlabs:
    voice_id: "WzMnDIgiICcj1oXbUBO0"
    model_id: "eleven_multilingual_v2"

  # 새로 추가됨
  minimax:
    model: "speech-02-hd"
    voice_id: "your_voice_id"
    api_key_env: "MINIMAX_API_KEY"
    group_id_env: "MINIMAX_GROUP_ID"
    speed: 1.0
    emotion: "neutral"    # happy, sad, angry, neutral 등

  # 새로 추가됨
  fish_audio:
    reference_id: "your_reference_id"
    format: "mp3"
    api_key_env: "FISH_AUDIO_API_KEY"
```

### 백엔드 전환 방법 (3가지)

```bash
# 방법 1: config YAML에서 직접 변경
# config/config.api.yaml → tts.force_backend: minimax

# 방법 2: 환경변수로 일시 오버라이드
TTS_FORCE_BACKEND=minimax uv run video-automation pipeline script-to-video ...

# 방법 3: Claude Code에게 요청
# "TTS를 MiniMax로 바꿔줘" → config 수정해줌
```

---

## Part 6: 트러블슈팅

### 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| `알 수 없는 TTS 백엔드: minimax` | `_load_backend()`에 미등록 | "minimax 백엔드가 lib.py에 등록 안 됐어. 추가해줘" |
| `API key not set` | `.env`에 키 미설정 | `.env`에 `MINIMAX_API_KEY=...` 추가 |
| 음성이 영어로 나옴 | 언어 코드 미설정 | "MiniMax 백엔드에 한국어 language_code 설정해줘" |
| MP3 → WAV 변환 실패 | ffmpeg 미설치 | `brew install ffmpeg` 또는 `choco install ffmpeg` |
| 음성 길이가 0초 | API 응답이 빈 파일 | "generate 함수에서 응답 크기 체크 로직 추가해줘" |

### 디버깅 프롬프트

```
MiniMax TTS 백엔드를 테스트해줘.
"안녕하세요, 테스트 음성입니다" 한 문장만 생성해서
projects/tts-test/audio/ 에 저장해봐.
```

```
MiniMax 백엔드에서 에러가 나. 로그 보고 원인 찾아줘.
```

---

## Part 7: 서비스별 API 빠른 비교

### MiniMax T2A v2

```
엔드포인트: POST https://api.minimaxi.com/v1/t2a_v2
인증: Authorization: Bearer {API_KEY}
모델: speech-02-hd (고품질), speech-02-turbo (저지연)
음성 복제: Voice Clone API로 10초 샘플 → voice_id 발급
한국어: 지원 (language_code 불필요, 자동 감지)
출력: MP3 바이너리
가격: ~$0.1/10만 글자
```

### Fish Audio

```
엔드포인트: POST https://api.fish.audio/v1/tts
인증: Authorization: Bearer {API_KEY}
모델: 자체 Fish Speech 모델
음성 복제: 대시보드에서 15초 WAV 업로드 → reference_id
한국어: 지원
출력: MP3/WAV 스트림
가격: $0.015/1000 글자
오픈소스: fish-speech (로컬 실행 가능, VRAM 4GB)
```

---

## 요약: 한 줄 프롬프트로 시작하기

| 목표 | Claude Code 프롬프트 |
|------|---------------------|
| MiniMax 연동 | `MiniMax T2A v2 TTS 백엔드 추가해줘. API 키는 MINIMAX_API_KEY.` |
| Fish Audio 연동 | `Fish Audio TTS 백엔드 추가해줘. API 키는 FISH_AUDIO_API_KEY.` |
| 백엔드 전환 | `TTS를 minimax로 바꿔줘` |
| 음성 복제 적용 | `MiniMax voice_id를 "xxx"로 설정해줘` |
| 되돌리기 | `TTS를 다시 ElevenLabs로 바꿔줘` |
| 테스트 | `MiniMax TTS로 테스트 문장 하나 생성해봐` |

> **Tip**: API 문서 URL을 함께 주면 Claude Code가 최신 API 스펙에 맞춰 더 정확하게 구현합니다.
> 예: `MiniMax TTS 연동해줘. 문서: https://www.minimaxi.com/document/T2A%20V2`
