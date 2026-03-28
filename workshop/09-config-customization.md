# 설정 & 커스터마이징 가이드

> 목소리, 이미지 스타일, 자막 등 원하는 대로 바꾸는 법

---

## Part 1: 설정 시스템 개요

### 설정 파일 위치

```
config/
├── config.api.yaml       ← API 모드 (워크숍용)
├── config.base.yaml      ← Full 모드 (GPU 있는 분)
├── config.asmr.yaml      ← ASMR 스타일
├── config.shorts.yaml    ← 쇼츠 최적화
└── tts_dictionary.yaml   ← TTS 발음 사전
```

### 워크숍 기본 설정 (API 모드)

| 항목 | 설정 | API 모드 | 설명 |
|------|------|:--------:|------|
| TTS | ElevenLabs API | ✅ | 클라우드 음성 합성 |
| 슬라이드 | Remotion | ✅ | 로컬 렌더링 (Node.js) |
| 자막 | Whisper + FFmpeg | ✅ | 자막 생성 및 합성 |
| B-roll | — | ❌ 비활성화 | `pipeline.broll.enabled: false` |
| 아바타 | — | ❌ 비활성화 | Ditto는 로컬 GPU 필요 |

### 설정 적용 순서

```
1. 프로필 YAML (config.api.yaml)
    ↓
2. 환경변수 오버라이드 (ENABLE_BROLL=false 등)
    ↓
3. 최종 설정 적용
```

---

## Part 2: TTS (음성) 커스터마이징

### Voice ID 변경

현재 설정된 목소리:

```yaml
# config/config.api.yaml
tts:
  elevenlabs:
    voice_id: "WzMnDIgiICcj1oXbUBO0"    # 현재 설정된 목소리
    model_id: "eleven_multilingual_v2"
```

다른 목소리로 바꾸려면:

1. [elevenlabs.io](https://elevenlabs.io) 접속
2. **Voice Library**에서 원하는 목소리 선택
3. Voice ID 복사 (Settings에서 확인 가능)
4. `config/config.api.yaml`에서 `voice_id` 수정

또는 Claude Code에게 요청:
```
TTS voice_id를 "새로운ID"로 바꿔줘
```

### 음성 속도 조절

```yaml
tts:
  elevenlabs:
    speed: 1.0         # 1.0=보통, 1.15=약간 빠르게, 0.9=느리게
    stability: 0.85     # 0.0~1.0 (높을수록 안정적, 낮을수록 감정적)
    similarity_boost: 0.58  # 0.0~1.0 (높을수록 원본 목소리에 가까움)
```

| 설정 | 값 | 효과 |
|------|-----|------|
| `speed` | 0.9 | 차분한 설명 영상 |
| `speed` | 1.0 | 기본 (자연스러운 속도) |
| `speed` | 1.15 | 빠른 정보 전달 |
| `stability` | 0.5 | 감정 풍부 (스토리텔링) |
| `stability` | 0.85 | 안정적 (뉴스/튜토리얼) |

### TTS 발음 사전

AI 관련 용어를 자연스러운 한글 발음으로 등록해두면 TTS 품질이 올라갑니다.

```yaml
# config/tts_dictionary.yaml
tts_pronunciation:
  Claude: 클로드
  ChatGPT: 챗지피티
  GitHub: 깃허브
  Anthropic: 앤트로픽
  ElevenLabs: 일레븐랩스
  # 나만의 단어 추가 가능!
```

Claude Code로 추가:
```
발음 사전에 "Kubernetes=쿠버네티스" 추가해줘
```

또는 자동 보강:
```
발음 사전을 자동으로 보강해줘
```

---

## Part 3: B-roll (배경 이미지) 커스터마이징

> 나만의 채널 비주얼 아이덴티티 구축은 **10-visual-identity.md**에서 자세히 다룹니다.

### 활성화/비활성화

```yaml
# config/config.api.yaml
pipeline:
  broll:
    enabled: false      # true로 바꾸면 배경 이미지 생성
```

> 워크숍 API 프로필은 기본적으로 B-roll이 꺼져 있습니다(`false`). 활성화하려면 `true`로 변경하거나 환경변수를 사용합니다:

```bash
# B-roll 활성화하여 실행
ENABLE_BROLL=true uv run video-automation pipeline script-to-video ...
```

### 캐릭터 설명 변경

B-roll 이미지에 등장하는 캐릭터 스타일을 바꿀 수 있습니다:

```yaml
# config/config.api.yaml
broll:
  character_description: "cute male chibi anime character with dark brown hair and gray jacket, kawaii style, simple clean background"
```

원하는 스타일로 변경:
```yaml
  character_description: "professional female business character, modern flat illustration style, clean minimal background"
```

---

## Part 4: 자막 커스터마이징

```yaml
# config/config.api.yaml
subtitles:
  font: "Pretendard"            # 폰트 (한국어 지원)
  font_size: 20                 # 크기
  color: "white"                # 텍스트 색상
  background: "rgba(0,0,0,0.6)" # 배경 (반투명 검정)
  position: "bottom"            # 위치 (bottom/top)
  margin_v: 10                  # 하단 여백 (px)
```

> 위 값(`font_size: 20`, `margin_v: 10`)은 `config.api.yaml` 프로필 값입니다. 스키마 기본값은 `font_size: 28`, `margin_v: 50`이며, 프로필에서 오버라이드하지 않으면 기본값이 적용됩니다.

| 설정 | 예시 | 효과 |
|------|------|------|
| `font_size: 16` | 작은 텍스트 | 화면 방해 최소화 |
| `font_size: 24` | 큰 텍스트 | 가독성 우선 |
| `background: "rgba(0,0,0,0)"` | 투명 배경 | 배경 없는 자막 |
| `margin_v: 50` | 큰 여백 | 자막 위치 조정 |

---

## Part 5: 환경변수 오버라이드

설정 파일을 수정하지 않고 일시적으로 설정을 바꿀 수 있습니다.

### Mac / Linux

```bash
# B-roll 비활성화
ENABLE_BROLL=false uv run video-automation ...

# B-roll 활성화
ENABLE_BROLL=true uv run video-automation ...
```

### Windows PowerShell

```powershell
# 환경변수 설정
$env:ENABLE_BROLL='false'
$env:CONFIG_PROFILE='api'

# 실행
uv run video-automation pipeline script-to-video ...
```

### 주요 환경변수

| 변수 | 기본값 (API) | 설명 |
|------|:----------:|------|
| `CONFIG_PROFILE` | (파이프라인별 상이) | 기본 프로필은 파이프라인마다 다름: script-to-video→`base`, script-to-shorts→`shorts`. `@requires_profile()` 데코레이터로 자동 설정됨 |
| `ENABLE_BROLL` | false (API) | B-roll 이미지 생성 on/off |
| `ENABLE_AVATAR` | false (API) | 아바타 on/off (API에서 항상 off) |
| `IMAGE_GEN_BACKEND` | nanobanana | 이미지 생성 백엔드 |

---

## Part 6: 프로필 전환

### API 모드 (워크숍 기본)

```bash
uv run video-automation ...
```

- TTS: ElevenLabs (클라우드)
- B-roll: Gemini (클라우드)
- 아바타: 비활성화
- GPU 불필요

### Base 모드

```bash
uv run video-automation ...    # script-to-video의 기본 프로필
```

- TTS: ElevenLabs (API) — 오픈소스 로컬 모델(Qwen)도 설정 변경으로 사용 가능
- B-roll: Flux Kontext + LoRA (로컬) — API 모드(`config.api.yaml`)에서는 B-roll 비활성화
- 아바타: Ditto (로컬 GPU)
- B-roll/아바타 사용 시 NVIDIA GPU 필요 (VRAM 12GB+)

---

## Part 7: 자주 쓰는 설정 변경 프롬프트

| 목적 | Claude Code에 입력 |
|------|-------------------|
| 목소리 변경 | `TTS voice_id를 "새ID"로 바꿔줘` |
| 속도 변경 | `TTS 속도를 1.15로 올려줘` |
| B-roll 켜기 | `B-roll을 활성화해줘` |
| 자막 크기 | `자막 폰트 크기를 24로 바꿔줘` |
| 발음 추가 | `발음 사전에 "React=리액트" 추가해줘` |
| 설정 확인 | `현재 전체 설정을 보여줘` |
| 프로필 확인 | `지금 어떤 프로필로 실행되고 있어?` |

> **핵심:** 설정 파일을 직접 열어서 수정할 수도 있지만, Claude Code에게 자연어로 요청하는 것이 더 쉽고 안전합니다. Claude Code가 올바른 파일을 찾아서 수정해줍니다.

### 도메인별 커스터마이징 프롬프트 (집에서 고도화용)

**재테크/금융 채널용:**
```
TTS 속도를 1.1로, stability를 0.85로 바꿔줘. 신뢰감 있는 톤이 필요해.
발음 사전에 "ETF=이티에프", "S&P500=에스앤피오백", "KOSPI=코스피", "PER=피이알" 추가해줘.
```

**건강/운동 채널용:**
```
TTS 속도를 1.0으로, stability를 0.65로 바꿔줘. 에너지 넘치지만 차분한 코치 톤.
발음 사전에 "HIIT=힛", "BMI=비엠아이", "kcal=킬로칼로리" 추가해줘.
```

**교육/강의 채널용:**
```
TTS 속도를 0.95로, stability를 0.75로 바꿔줘. 천천히 설명하되 딱딱하지 않게.
발음 사전에 "TOEIC=토익", "IELTS=아이엘츠", "syntax=신택스" 추가해줘.
```

**요리/라이프스타일 채널용:**
```
TTS 속도를 0.95로, stability를 0.55로 바꿔줘. 따뜻하고 감성적인 톤.
B-roll 캐릭터를 "cozy kitchen scene with warm lighting, watercolor illustration style" 로 바꿔줘.
```

**마케팅/비즈니스 채널용:**
```
TTS 속도를 1.1로, stability를 0.80으로 바꿔줘. 전문적이지만 접근하기 쉬운 톤.
발음 사전에 "ROI=알오아이", "CPC=씨피씨", "CTR=씨티알", "KPI=케이피아이" 추가해줘.
```

**여행 채널용:**
```
TTS 속도를 1.0으로, stability를 0.60으로 바꿔줘. 친근하고 설레는 톤.
B-roll 캐릭터를 "cheerful traveler with backpack, clean flat illustration, pastel warm colors" 로 바꿔줘.
```

---

## 더 알아보기

| 주제 | 참고 문서 |
|------|----------|
| 부분 재실행으로 빠르게 반복 | **08-advanced-workflows.md** |
| 채널 디자인 시스템 구축 | **10-visual-identity.md** |
| 체계적 품질 개선 | **11-quality-iteration.md** |
| 설정을 스킬로 자산화 | **13-custom-skills.md** |
