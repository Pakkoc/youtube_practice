# add-emotion-tts 구현 계획

## 기술 스택

- Python 3.13, Pydantic v2 (기존 모델 확장)
- 정규식 기반 태그 파싱 (새 라이브러리 불필요)
- 기존 Qwen3-TTS `instruct` 파라미터 활용
- 기존 ElevenLabs `voice_settings` 파라미터 조정

## 파일 구조 계획

### 수정

- `entities/script/model.py` -- `Paragraph`에 `emotion: str | None = None` 필드 추가
- `features/split_paragraphs/lib.py` -- `split_script()` 내 감정 태그 파싱 및 제거 로직 추가
- `features/generate_tts/model.py` -- `TTSRequest`에 `emotion: str | None = None` 필드 추가
- `features/generate_tts/lib.py` -- `generate_tts_for_paragraphs()`에서 `Paragraph.emotion` -> `TTSRequest.instruct` 매핑, `generate_tts_for_text()`에 `emotion` 파라미터 전달
- `features/generate_tts/backends/elevenlabs_api.py` -- `emotion` 기반 `voice_settings` 동적 조정

### 신규 생성 없음

감정 매핑 상수(`EMOTION_MAP`)는 `features/generate_tts/lib.py` 내 모듈 상수로 정의한다. 별도 파일 불필요.

## 작업 분해

| # | TODO | 위험도 | 요구사항 |
|---|------|--------|----------|
| 1 | `Paragraph` 모델에 `emotion: str \| None = None` 필드 추가 | LOW | REQ-01 |
| 2 | `split_script()`에 감정 태그 파싱 함수 추가: `_extract_emotion(text) -> tuple[str \| None, str]` -- 문단 텍스트에서 `[감정]` 태그를 추출하고 제거된 텍스트를 반환 | LOW | REQ-02 |
| 3 | `split_script()` 내 `Paragraph` 생성 시 `_extract_emotion()` 호출하여 `emotion` 필드 설정 | LOW | REQ-02 |
| 4 | `EMOTION_MAP` 상수 정의 -- 한국어 감정 -> 영어 instruct 문자열 매핑 (화남, 기쁨, 슬픔, 놀람, 진지, 흥분) | LOW | REQ-04 |
| 5 | `TTSRequest` 모델에 `emotion: str \| None = None` 필드 추가 | LOW | REQ-03 |
| 6 | `generate_tts_for_paragraphs()`에서 `Paragraph.emotion` -> `TTSRequest.instruct` 변환 로직 추가 (EMOTION_MAP 조회, 미등록 태그 시 경고 로그 + 폴백) | MEDIUM | REQ-03, REQ-N03 |
| 7 | `generate_tts_for_text()`에 `emotion` 파라미터 추가 및 `TTSRequest` 생성 시 전달 | LOW | REQ-03 |
| 8 | ElevenLabs 백엔드에서 `request.emotion` 기반 `voice_settings` 동적 조정 로직 추가 | MEDIUM | REQ-06 |
| 9 | Custom Voice 백엔드에서 `emotion` 설정 시 경고 로그 출력 | LOW | 제약조건 |
| 10 | TTS sidecar에 `emotion` 필드 기록 | LOW | REQ-O02 |
| 11 | 기존 테스트 확인 + 감정 태그 파싱 단위 테스트 작성 | LOW | 전체 |

## 위험 분석

| 위험 | 영향 | 완화 전략 |
|------|------|-----------|
| ElevenLabs `voice_settings` 조정 값이 감정을 제대로 반영하지 못할 수 있음 | MEDIUM | stability/style 파라미터를 감정별로 경험적 값 설정 후, 실제 음성 출력으로 검증. 부적절하면 사용자가 YAML로 오버라이드 가능하도록 REQ-O01 구현. |
| Qwen3-TTS `instruct` 파라미터의 영어 문자열이 한국어 음성에 정확히 반영되지 않을 수 있음 | MEDIUM | Qwen3-TTS 공식 문서/예제의 instruct 문자열을 참고하여 매핑. 실제 출력 청취 후 반복 조정. |
| `Paragraph.emotion` 필드 추가 시 기존 직렬화/역직렬화 코드 호환성 | LOW | Pydantic v2 `Optional` 필드는 기본값 `None`으로 역직렬화 시 자동 처리됨. 기존 JSON에 `emotion` 키가 없어도 문제없음. |
| 감정 태그 정규식이 대본의 다른 대괄호 구문과 충돌 | LOW | 태그 위치를 **문단 시작**으로 한정(`^\[(.+?)\]`). 문단 중간의 대괄호는 무시. |

## 의존성 분석

- `Paragraph` 모델은 `split_paragraphs`, `split_scenes`, `generate_tts`, `generate_slides` 등 다수 feature에서 참조한다. `emotion` 필드는 `Optional`이므로 기존 코드에 영향 없음.
- `TTSRequest` 모델은 `generate_tts` feature 내부에서만 사용. 변경 범위가 한정적.
- FSD import 규칙: `features/split_paragraphs/` -> `entities/script/` (허용), `features/generate_tts/` -> `entities/script/` (허용). 위반 없음.
- `features/split_paragraphs/`는 `features/generate_tts/`를 import하지 않음 -- 감정 매핑(`EMOTION_MAP`)은 `generate_tts`에만 위치하므로 순환 의존성 없음.

## 구현 순서 상세

### Step 1-3: 엔티티 + 파싱 (entities + split_paragraphs)

`entities/script/model.py`:
```python
class Paragraph(BaseModel):
    index: int
    text: str
    emotion: str | None = None  # 추가
```

`features/split_paragraphs/lib.py` -- 신규 헬퍼:
```python
_EMOTION_TAG_RE = re.compile(r"^\[(.+?)\]\s*")

def _extract_emotion(text: str) -> tuple[str | None, str]:
    m = _EMOTION_TAG_RE.match(text)
    if m:
        return m.group(1), text[m.end():]
    return None, text
```

`split_script()` 내 Paragraph 생성부 변경:
```python
emotion, clean_text = _extract_emotion(text)
paragraphs.append(Paragraph(index=idx, text=clean_text, emotion=emotion))
```

### Step 4-7: TTS 감정 매핑 (generate_tts)

`features/generate_tts/lib.py` -- 모듈 상수:
```python
EMOTION_MAP: dict[str, str] = {
    "화남": "Speak with anger and frustration",
    "기쁨": "Speak with joy and happiness",
    "슬픔": "Speak with sadness and melancholy",
    "놀람": "Speak with surprise and astonishment",
    "진지": "Speak in a serious and solemn tone",
    "흥분": "Speak with excitement and enthusiasm",
}
```

`generate_tts_for_paragraphs()` 내 감정 -> instruct 변환:
```python
instruct = ""
if paragraph.emotion:
    instruct = EMOTION_MAP.get(paragraph.emotion, "")
    if not instruct:
        logger.warning("미등록 감정 태그 '%s' -- 기본 파라미터로 폴백", paragraph.emotion)
```

### Step 8: ElevenLabs 감정 근사

`_EMOTION_VOICE_SETTINGS` 매핑으로 `stability` / `style` 오버라이드:
```python
_EMOTION_VOICE_SETTINGS: dict[str, dict[str, float]] = {
    "화남": {"stability": 0.3, "style": 0.8},
    "기쁨": {"stability": 0.5, "style": 0.7},
    "슬픔": {"stability": 0.9, "style": 0.3},
    ...
}
```
