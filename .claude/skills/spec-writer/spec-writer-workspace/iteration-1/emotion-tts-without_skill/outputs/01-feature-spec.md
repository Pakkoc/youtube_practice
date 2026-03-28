# Feature Spec: 감정 태그 기반 TTS 생성

## 1. 개요

대본(`script.txt`)에 `[화남]`, `[기쁨]` 등의 감정 태그를 삽입하면, 해당 문단의 TTS 생성 시 감정에 맞는 음성 파라미터를 자동 적용하는 기능.

### 목표
- 대본 작성자가 문단별 감정을 명시적으로 제어
- 감정 태그 없는 문단은 기존과 동일하게 동작 (하위 호환성 보장)
- 모든 TTS 백엔드(Qwen CUDA/MPS, ElevenLabs, CustomVoice)에서 감정 파라미터 적용

### 비목표 (Scope 밖)
- AI 기반 자동 감정 감지 (대본 텍스트에서 감정을 추론)
- 감정 전환 그라데이션 (문단 내 감정 변화)
- 감정별 화자(speaker) 자동 전환

---

## 2. 대본 형식 설계

### 2.1 태그 문법

```
[감정태그] 문단 텍스트...
```

- 문단 시작 부분에 대괄호(`[]`)로 감정을 지정
- 태그는 **문단의 첫 번째 토큰**이어야 함 (앞에 공백 허용)
- 태그가 없으면 `neutral` (기본 감정)
- 대소문자 무관, 한글/영문 모두 허용

### 2.2 지원 감정 목록

| 태그 (한글) | 태그 (영문) | Enum 값 | 설명 |
|-------------|------------|---------|------|
| `[중립]` | `[neutral]` | `neutral` | 기본 내레이션 톤 (기본값) |
| `[기쁨]` | `[happy]` | `happy` | 밝고 활기찬 톤 |
| `[화남]` | `[angry]` | `angry` | 강하고 단호한 톤 |
| `[슬픔]` | `[sad]` | `sad` | 차분하고 가라앉은 톤 |
| `[놀람]` | `[surprised]` | `surprised` | 놀라거나 흥분한 톤 |
| `[진지]` | `[serious]` | `serious` | 무겁고 진지한 톤 |
| `[유머]` | `[humorous]` | `humorous` | 가볍고 재미있는 톤 |

### 2.3 대본 예시

```
여러분 AI한테 긴 작업 시켜보신 적 있으시죠? 처음 몇 단계까지는 꼼꼼합니다.

[화남] 근데 작업이 길어지면 슬슬 이상해집니다. "나머지도 유사한 패턴이므로 동일하게 적용하시면 됩니다"라면서요.

[진지] 결론부터 말씀드리면, 이건 여러분 프롬프트가 부족해서가 아닙니다. 모델 자체의 구조적 한계에서 오는 현상입니다.

[기쁨] 안녕하세요. 저는 AI로 만들어진 샘호트만입니다!
```

---

## 3. 변경 대상 파일 및 영향 범위

### 3.1 FSD 레이어별 변경 요약

| 레이어 | 파일 | 변경 유형 | 설명 |
|--------|------|----------|------|
| `entities` | `entities/script/model.py` | 수정 | `Paragraph.emotion` 필드 추가 |
| `entities` | `entities/script/__init__.py` | 수정 | `Emotion` enum export 추가 |
| `features` | `features/generate_tts/model.py` | 수정 | `TTSRequest.emotion` 필드 추가 |
| `features` | `features/generate_tts/lib.py` | 수정 | 감정 -> 음성 파라미터 매핑 로직 |
| `features` | `features/generate_tts/emotion.py` | **신규** | 감정 파라미터 매핑 모듈 |
| `features` | `features/generate_tts/backends/qwen_cuda.py` | 수정 | `instruct` 파라미터에 감정 지시 적용 |
| `features` | `features/generate_tts/backends/qwen_mps.py` | 수정 | 동일 |
| `features` | `features/generate_tts/backends/elevenlabs_api.py` | 수정 | `voice_settings` 감정별 조정 |
| `features` | `features/generate_tts/backends/custom_voice.py` | 수정 | (향후 확장 포인트) |
| `features` | `features/generate_tts/sidecar.py` | 수정 | sidecar JSON에 `emotion` 필드 추가 |
| `features` | `features/split_paragraphs/lib.py` | 수정 | 감정 태그 파싱 + `Paragraph.emotion` 세팅 |
| `shared` | `shared/config/schema.py` | 수정 | `EmotionPreset` 설정 추가 (선택) |

### 3.2 변경 없는 파일 (하위 호환)

- `pipelines/script_to_video/lib.py` -- `Paragraph` 인터페이스 불변
- `pipelines/script_to_shorts/lib.py` -- 동일
- `features/generate_tts/preprocess.py` -- 전처리 로직 불변 (감정 태그는 파싱 단계에서 이미 제거됨)
- `scripts/continue_pipeline.py`, `scripts/recompose_video.py` -- `Paragraph(index=, text=)` 호출부는 emotion 기본값(`neutral`)으로 동작

---

## 4. 상세 설계

### 4.1 `entities/script/model.py` 변경

```python
from enum import Enum

class Emotion(str, Enum):
    """TTS 감정 태그."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    ANGRY = "angry"
    SAD = "sad"
    SURPRISED = "surprised"
    SERIOUS = "serious"
    HUMOROUS = "humorous"

# 한글 태그 -> Emotion 매핑
EMOTION_TAG_MAP: dict[str, Emotion] = {
    "중립": Emotion.NEUTRAL,
    "기쁨": Emotion.HAPPY,
    "화남": Emotion.ANGRY,
    "슬픔": Emotion.SAD,
    "놀람": Emotion.SURPRISED,
    "진지": Emotion.SERIOUS,
    "유머": Emotion.HUMOROUS,
    # 영문 태그도 지원
    "neutral": Emotion.NEUTRAL,
    "happy": Emotion.HAPPY,
    "angry": Emotion.ANGRY,
    "sad": Emotion.SAD,
    "surprised": Emotion.SURPRISED,
    "serious": Emotion.SERIOUS,
    "humorous": Emotion.HUMOROUS,
}

class Paragraph(BaseModel):
    """대본의 단일 문단."""
    index: int
    text: str
    emotion: Emotion = Emotion.NEUTRAL  # 기본값: 중립

    @property
    def filename(self) -> str:
        return f"{self.index:03d}.txt"
```

**핵심 포인트:**
- `emotion` 필드에 기본값 `Emotion.NEUTRAL`을 두어, 기존 코드에서 `Paragraph(index=1, text="...")` 호출이 깨지지 않음
- `str, Enum` 상속으로 JSON 직렬화 시 문자열로 저장됨

### 4.2 `features/split_paragraphs/lib.py` 감정 태그 파싱

```python
import re
from entities.script.model import Emotion, EMOTION_TAG_MAP

_EMOTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*")

def _extract_emotion(text: str) -> tuple[Emotion, str]:
    """문단 텍스트에서 감정 태그를 추출.

    Returns:
        (감정 enum, 태그가 제거된 텍스트)
    """
    match = _EMOTION_TAG_RE.match(text)
    if not match:
        return Emotion.NEUTRAL, text

    tag = match.group(1).strip().lower()
    emotion = EMOTION_TAG_MAP.get(tag, None)

    if emotion is None:
        # 알 수 없는 태그는 무시하고 텍스트에 그대로 유지
        return Emotion.NEUTRAL, text

    # 태그 제거한 텍스트 반환
    clean_text = text[match.end():].strip()
    return emotion, clean_text
```

`split_script()` 함수의 문단 생성 루프에서 `_extract_emotion()` 호출:

```python
for raw in raw_paragraphs:
    text = raw.strip()
    if len(text) < config.min_length:
        continue
    emotion, clean_text = _extract_emotion(text)
    paragraphs.append(Paragraph(index=idx, text=clean_text, emotion=emotion))
    idx += 1
```

### 4.3 `features/generate_tts/emotion.py` (신규 모듈)

감정별 백엔드 파라미터 매핑을 중앙화하는 모듈.

```python
"""감정별 TTS 파라미터 매핑."""
from __future__ import annotations
from dataclasses import dataclass
from entities.script.model import Emotion


@dataclass(frozen=True)
class QwenEmotionParams:
    """Qwen3-TTS instruct 파라미터."""
    instruct: str  # generate_custom_voice()의 instruct 인자


@dataclass(frozen=True)
class ElevenLabsEmotionParams:
    """ElevenLabs voice_settings 오버라이드."""
    stability: float | None = None
    similarity_boost: float | None = None
    style_exaggeration: float | None = None
    speed: float | None = None


# Qwen3-TTS: instruct 문자열로 감정 제어
QWEN_EMOTION_MAP: dict[Emotion, QwenEmotionParams] = {
    Emotion.NEUTRAL: QwenEmotionParams(instruct=""),
    Emotion.HAPPY: QwenEmotionParams(instruct="Read with a cheerful and bright tone"),
    Emotion.ANGRY: QwenEmotionParams(instruct="Read with a strong and assertive tone"),
    Emotion.SAD: QwenEmotionParams(instruct="Read with a calm and subdued tone"),
    Emotion.SURPRISED: QwenEmotionParams(instruct="Read with an excited and surprised tone"),
    Emotion.SERIOUS: QwenEmotionParams(instruct="Read with a serious and grave tone"),
    Emotion.HUMOROUS: QwenEmotionParams(instruct="Read with a light and playful tone"),
}

# ElevenLabs: voice_settings 수치 조정으로 감정 제어
ELEVENLABS_EMOTION_MAP: dict[Emotion, ElevenLabsEmotionParams] = {
    Emotion.NEUTRAL: ElevenLabsEmotionParams(),
    Emotion.HAPPY: ElevenLabsEmotionParams(
        stability=0.70, style_exaggeration=0.45, speed=1.05
    ),
    Emotion.ANGRY: ElevenLabsEmotionParams(
        stability=0.60, style_exaggeration=0.55, speed=1.10
    ),
    Emotion.SAD: ElevenLabsEmotionParams(
        stability=0.90, style_exaggeration=0.20, speed=0.90
    ),
    Emotion.SURPRISED: ElevenLabsEmotionParams(
        stability=0.55, style_exaggeration=0.50, speed=1.15
    ),
    Emotion.SERIOUS: ElevenLabsEmotionParams(
        stability=0.90, style_exaggeration=0.10, speed=0.95
    ),
    Emotion.HUMOROUS: ElevenLabsEmotionParams(
        stability=0.65, style_exaggeration=0.40, speed=1.05
    ),
}
```

### 4.4 `features/generate_tts/model.py` 변경

```python
class TTSRequest(BaseModel):
    """TTS 생성 요청."""
    text: str
    tts_text: str = ""
    speaker: str = "Sohee"
    language: str = "Korean"
    output_path: Path
    instruct: str = ""
    emotion: str = "neutral"  # Emotion enum의 value (str 타입으로 직렬화 호환)
```

### 4.5 `features/generate_tts/lib.py` 변경

`generate_tts_for_text()`:
```python
def generate_tts_for_text(
    text: str,
    output_path: Path,
    config: TTSConfig,
    backend: TTSBackend | None = None,
    tts_text: str = "",
    emotion: str = "neutral",  # 새 파라미터
) -> TTSResult:
    ...
    request = TTSRequest(
        text=text,
        tts_text=tts_text,
        speaker=config.speaker,
        language=config.language,
        output_path=output_path,
        emotion=emotion,
    )
    ...
```

`generate_tts_for_paragraphs()`:
```python
for paragraph in paragraphs:
    ...
    result = generate_tts_for_text(
        text=paragraph.text,
        output_path=output_path,
        config=config,
        backend=backend,
        tts_text=tts_text,
        emotion=paragraph.emotion.value,  # Paragraph.emotion 전달
    )
```

### 4.6 백엔드별 감정 적용

#### Qwen CUDA/MPS (`qwen_cuda.py`, `qwen_mps.py`)

기존 `instruct` 필드를 감정 매핑에서 가져온 값으로 설정:

```python
from ..emotion import QWEN_EMOTION_MAP, QwenEmotionParams
from entities.script.model import Emotion

def generate(self, request: TTSRequest) -> TTSResult:
    ...
    # 감정 -> instruct 매핑 (request.instruct가 이미 있으면 우선)
    emotion_params = QWEN_EMOTION_MAP.get(
        Emotion(request.emotion), QwenEmotionParams(instruct="")
    )
    instruct = request.instruct or emotion_params.instruct

    wavs, sr = self._model.generate_custom_voice(
        text=speak_text,
        language=language,
        speaker=speaker,
        instruct=instruct,
    )
```

#### ElevenLabs (`elevenlabs_api.py`)

감정에 따라 `voice_settings` 수치를 오버라이드:

```python
from ..emotion import ELEVENLABS_EMOTION_MAP, ElevenLabsEmotionParams
from entities.script.model import Emotion

def _call_api(self, request: TTSRequest, api_key_env: str) -> TTSResult:
    ...
    emotion_params = ELEVENLABS_EMOTION_MAP.get(
        Emotion(request.emotion), ElevenLabsEmotionParams()
    )

    payload = {
        "text": speak_text,
        "model_id": self._model_id,
        "language_code": lang_code,
        "voice_settings": {
            "stability": emotion_params.stability or self._stability,
            "similarity_boost": emotion_params.similarity_boost or self._similarity_boost,
            "style": emotion_params.style_exaggeration or self._style_exaggeration,
            "use_speaker_boost": self._use_speaker_boost,
            "speed": emotion_params.speed or self._speed,
        },
    }
```

#### CustomVoice (`custom_voice.py`)

현재 `generate_voice_clone()`에는 `instruct` 파라미터가 없음. 향후 확장 포인트만 남기고, 감정 정보는 sidecar에만 기록:

```python
# TODO: generate_voice_clone에 instruct 파라미터 지원 시 감정 적용
# 현재는 sidecar에 emotion 기록만 수행
```

### 4.7 Sidecar 변경 (`sidecar.py`)

```python
def sync_tts_sidecar(
    wav_path: Path,
    text: str,
    tts_text: str,
    duration: float,
    language_code: str = "ko",
    emotion: str = "neutral",  # 새 파라미터
) -> None:
    meta = {
        "audio": str(wav_path.resolve()),
        "text": text,
        "tts_text": tts_text,
        "language_code": language_code,
        "duration": round(duration, 2),
        "emotion": emotion,  # 감정 태그 기록
    }
```

---

## 5. 데이터 흐름

```
script.txt
  |
  v
[split_paragraphs] -- _extract_emotion() 호출
  |                    "[화남] 근데 작업이..."
  |                    -> emotion=Emotion.ANGRY, text="근데 작업이..."
  v
Paragraph(index=2, text="근데 작업이...", emotion=Emotion.ANGRY)
  |
  v
[generate_tts_for_paragraphs] -- paragraph.emotion.value 전달
  |
  v
TTSRequest(text="근데 작업이...", emotion="angry")
  |
  v
[Backend.generate()]
  |-- Qwen: instruct="Read with a strong and assertive tone"
  |-- ElevenLabs: stability=0.60, style_exaggeration=0.55
  |-- CustomVoice: (향후 확장)
  |
  v
TTSResult + sidecar.json (emotion="angry" 기록)
```

---

## 6. 하위 호환성 보장

| 시나리오 | 동작 |
|---------|------|
| 감정 태그 없는 기존 대본 | `emotion=Emotion.NEUTRAL` 기본값, 기존과 동일 |
| `Paragraph(index=1, text="...")` 직접 생성 | `emotion` 기본값 적용, 에러 없음 |
| `generate_tts_for_text()` 기존 호출부 | `emotion` 기본값 "neutral" 적용 |
| 기존 sidecar JSON 읽기 | `emotion` 키 없어도 정상 동작 |
| 알 수 없는 태그 `[모름]` | 태그 무시, 텍스트에 `[모름]` 그대로 유지 |

---

## 7. 테스트 계획

### 7.1 단위 테스트

| 테스트 | 파일 | 검증 내용 |
|--------|------|----------|
| 감정 태그 파싱 | `tests/features/test_split_paragraphs.py` | `_extract_emotion()` 한글/영문/미지정 케이스 |
| Paragraph 직렬화 | `tests/entities/test_script_model.py` | emotion 필드 JSON 직렬화/역직렬화 |
| TTSRequest emotion 전달 | `tests/features/test_generate_tts.py` | emotion 값이 백엔드까지 전달되는지 |
| Qwen instruct 매핑 | `tests/features/test_emotion.py` | 감정별 instruct 문자열 정확성 |
| ElevenLabs params 매핑 | `tests/features/test_emotion.py` | 감정별 voice_settings 수치 |
| Sidecar emotion 기록 | `tests/features/test_sidecar.py` | JSON에 emotion 필드 포함 확인 |

### 7.2 통합 테스트

| 테스트 | 검증 내용 |
|--------|----------|
| E2E 파이프라인 | 감정 태그 포함 대본 -> TTS 생성 -> sidecar 확인 |
| 기존 대본 회귀 | 감정 태그 없는 대본이 변경 없이 동작 |
| 혼합 대본 | 일부 문단만 감정 태그 있는 대본 |

### 7.3 수동 검증 (음성 품질)

- 동일 텍스트에 다른 감정 태그 적용 후 음성 비교 청취
- Qwen `instruct` 파라미터의 실제 효과 확인 (모델에 따라 효과 미미할 수 있음)
- ElevenLabs `style_exaggeration` 수치별 변화 확인

---

## 8. 리스크 및 미결 사항

| 항목 | 리스크 | 대응 |
|------|--------|------|
| Qwen instruct 효과 | Qwen3-TTS의 instruct가 감정 제어에 효과적인지 미확인 | 사전 실험 필요. 효과 미미 시 instruct 문구 튜닝 |
| ElevenLabs 수치 튜닝 | stability/style 수치가 감정 표현에 적합한지 미확인 | A/B 테스트로 수치 조정. config에서 오버라이드 가능하게 설계 |
| CustomVoice 지원 | `generate_voice_clone()`에 instruct 미지원 | Phase 2로 연기. sidecar 기록만 우선 적용 |
| 문단 분할과의 상호작용 | `_split_long_paragraphs()`가 감정 태그 포함 문단을 분할 시 태그 손실 | 감정 태그 추출을 문단 분할보다 먼저 수행 (전처리 순서 주의) |
| 감정 태그가 TTS 텍스트에 남는 경우 | 파싱 실패 시 `[화남]`이 음성에 읽힐 수 있음 | 정규식 매칭 후 제거 보장. preprocess_for_tts에서 이중 체크 |
