# Implementation Plan: 감정 태그 기반 TTS 생성

## 구현 순서

FSD 하위 레이어부터 상위로 구현합니다. 각 Phase는 독립적으로 검증 가능합니다.

---

## Phase 1: Entity 레이어 (감정 모델 정의)

### Step 1.1: `Emotion` enum + 태그 매핑 추가

**파일**: `entities/script/model.py`

**변경 내용**:
- `Emotion(str, Enum)` 클래스 추가 (7개 감정)
- `EMOTION_TAG_MAP: dict[str, Emotion]` 상수 추가 (한글 7개 + 영문 7개 = 14개 매핑)
- `Paragraph` 모델에 `emotion: Emotion = Emotion.NEUTRAL` 필드 추가

**주의 사항**:
- `str, Enum` 상속 필수 (Pydantic JSON 직렬화 호환)
- `emotion` 필드에 반드시 기본값 부여 (하위 호환)

**검증**:
```python
# 기존 코드 호환성
p = Paragraph(index=1, text="test")
assert p.emotion == Emotion.NEUTRAL

# 감정 지정
p = Paragraph(index=1, text="test", emotion=Emotion.ANGRY)
assert p.emotion.value == "angry"

# JSON 직렬화
d = p.model_dump()
assert d["emotion"] == "angry"
```

### Step 1.2: Public API 업데이트

**파일**: `entities/script/__init__.py`

**변경 내용**:
- `Emotion`, `EMOTION_TAG_MAP` export 추가

```python
from entities.script.model import Emotion, EMOTION_TAG_MAP, Paragraph, Script

__all__ = ["Emotion", "EMOTION_TAG_MAP", "Paragraph", "Script"]
```

---

## Phase 2: Feature 레이어 - 감정 파싱 (split_paragraphs)

### Step 2.1: 감정 태그 파싱 함수 추가

**파일**: `features/split_paragraphs/lib.py`

**변경 내용**:
- `_EMOTION_TAG_RE` 정규식 패턴 추가 (모듈 레벨)
- `_extract_emotion(text: str) -> tuple[Emotion, str]` 함수 추가
- `split_script()` 내 문단 생성 루프에서 `_extract_emotion()` 호출

**정규식 설계**:
```python
_EMOTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*")
```
- `^\s*` : 문단 시작 (앞 공백 허용)
- `\[([^\]]+)\]` : 대괄호 안 내용 캡처
- `\s*` : 태그 뒤 공백 제거

**파싱 로직**:
1. 정규식 매칭 시도
2. 매칭 실패 -> `(Emotion.NEUTRAL, 원본 텍스트)` 반환
3. 매칭 성공 -> 태그를 `EMOTION_TAG_MAP`에서 조회
4. 매핑 없음 (알 수 없는 태그) -> `(Emotion.NEUTRAL, 원본 텍스트)` 반환 (태그 제거 안 함)
5. 매핑 성공 -> `(감정, 태그 제거된 텍스트)` 반환

**문단 분할과의 순서 주의**:
```
현재 순서: preprocess_script -> _auto_detect_line_paragraphs -> _split_long_paragraphs -> split by separator -> Paragraph 생성

감정 태그 추출 위치: Paragraph 생성 직전 (마지막 단계)
이유: _split_long_paragraphs가 문단을 분할할 때 첫 번째 조각에만 태그가 남으므로,
      분할 후 Paragraph 생성 시점에서 추출하는 것이 가장 안전
```

**검증**:
```python
# 한글 태그
emotion, text = _extract_emotion("[화남] 근데 작업이 길어지면")
assert emotion == Emotion.ANGRY
assert text == "근데 작업이 길어지면"

# 영문 태그
emotion, text = _extract_emotion("[happy] Hello world")
assert emotion == Emotion.HAPPY

# 태그 없음
emotion, text = _extract_emotion("일반 문단입니다")
assert emotion == Emotion.NEUTRAL
assert text == "일반 문단입니다"

# 알 수 없는 태그 (텍스트 보존)
emotion, text = _extract_emotion("[모름] 문단입니다")
assert emotion == Emotion.NEUTRAL
assert text == "[모름] 문단입니다"

# 대소문자 무관
emotion, text = _extract_emotion("[ANGRY] text")
assert emotion == Emotion.ANGRY
```

---

## Phase 3: Feature 레이어 - 감정 파라미터 매핑 (generate_tts)

### Step 3.1: 감정 파라미터 매핑 모듈 생성

**파일**: `features/generate_tts/emotion.py` (신규)

**내용**:
- `QwenEmotionParams` dataclass (instruct 문자열)
- `ElevenLabsEmotionParams` dataclass (voice_settings 오버라이드)
- `QWEN_EMOTION_MAP` 상수
- `ELEVENLABS_EMOTION_MAP` 상수
- `get_qwen_params(emotion: str) -> QwenEmotionParams` 헬퍼
- `get_elevenlabs_params(emotion: str) -> ElevenLabsEmotionParams` 헬퍼

**설계 원칙**:
- 감정 파라미터를 한 곳에서 관리 (백엔드에 분산시키지 않음)
- `None` 값은 "백엔드 기본값 사용"을 의미
- 헬퍼 함수가 알 수 없는 emotion 값에 대해 neutral 기본값 반환

### Step 3.2: `TTSRequest` 모델 수정

**파일**: `features/generate_tts/model.py`

**변경 내용**:
- `emotion: str = "neutral"` 필드 추가

### Step 3.3: `lib.py` 수정 - 감정 전달 경로

**파일**: `features/generate_tts/lib.py`

**변경 내용**:

1. `generate_tts_for_text()`: `emotion` 매개변수 추가 -> `TTSRequest.emotion`에 전달
2. `generate_tts_for_paragraphs()`: `paragraph.emotion.value`를 `generate_tts_for_text()`에 전달
3. 로그 메시지에 감정 정보 포함

```python
logger.info(
    "TTS 생성 중: 문단 %d/%d (emotion=%s)",
    paragraph.index, len(paragraphs), paragraph.emotion.value
)
```

### Step 3.4: 백엔드별 감정 적용

#### `backends/qwen_cuda.py`, `backends/qwen_mps.py`:
- `emotion.py`에서 `get_qwen_params()` 호출
- `request.instruct`가 비어있을 때만 감정 instruct 적용 (명시적 instruct 우선)

#### `backends/elevenlabs_api.py`:
- `emotion.py`에서 `get_elevenlabs_params()` 호출
- `None`이 아닌 값만 기본 설정을 오버라이드

#### `backends/custom_voice.py`:
- 변경 없음. `generate_voice_clone()`에 instruct 파라미터가 없으므로 Phase 2로 연기
- 코드 주석으로 향후 확장 포인트 표시

### Step 3.5: Sidecar 수정

**파일**: `features/generate_tts/sidecar.py`

**변경 내용**:
- `sync_tts_sidecar()`에 `emotion: str = "neutral"` 매개변수 추가
- sidecar JSON에 `"emotion"` 키 추가
- 호출부 (lib.py, elevenlabs_api.py) 업데이트

---

## Phase 4: 테스트 작성

### Step 4.1: 단위 테스트

**신규 파일**: `tests/features/test_emotion_tts.py`

```
테스트 케이스:
1. _extract_emotion() 한글 태그 7종
2. _extract_emotion() 영문 태그 7종
3. _extract_emotion() 대소문자 혼합
4. _extract_emotion() 태그 없음
5. _extract_emotion() 알 수 없는 태그
6. _extract_emotion() 태그 뒤 공백 정리
7. get_qwen_params() 각 감정
8. get_elevenlabs_params() 각 감정
9. get_*_params() 알 수 없는 감정 -> neutral 폴백
```

### Step 4.2: 기존 테스트 회귀 확인

```bash
set -a && source .env && set +a && pytest tests/ -v
```

- 기존 `Paragraph` 생성 코드가 emotion 기본값으로 동작하는지 확인
- `split_script()` 기존 테스트가 감정 태그 없는 대본에서 통과하는지 확인

---

## Phase 5: 검증 및 마무리

### Step 5.1: Lint + Type check

```bash
ruff check . && ruff format .
npx tsc --noEmit  # TSX 관련 없으므로 생략 가능
lint-imports  # FSD import 규칙 확인
```

### Step 5.2: 수동 음성 품질 확인

1. 테스트 대본 작성 (감정 태그 포함)
2. Qwen CUDA 백엔드로 TTS 생성 -> instruct 효과 청취
3. ElevenLabs 백엔드로 TTS 생성 -> voice_settings 효과 청취
4. 효과가 미미할 경우 파라미터 수치 조정

---

## 예상 작업량

| Phase | 예상 시간 | 난이도 |
|-------|----------|--------|
| Phase 1 (Entity) | 15분 | 낮음 |
| Phase 2 (파싱) | 20분 | 낮음 |
| Phase 3 (TTS 적용) | 40분 | 중간 |
| Phase 4 (테스트) | 30분 | 낮음 |
| Phase 5 (검증) | 20분 | 낮음 |
| **합계** | **~2시간** | |

---

## 의존성 그래프

```
Phase 1 (Entity: Emotion enum)
  |
  +---> Phase 2 (파싱: _extract_emotion)
  |
  +---> Phase 3 (TTS: emotion 파라미터 매핑)
          |
          +---> Phase 4 (테스트)
                  |
                  +---> Phase 5 (검증)
```

Phase 2와 Phase 3은 Phase 1 완료 후 병렬 작업 가능.
