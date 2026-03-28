# Affected Files: 감정 태그 기반 TTS 생성

## 수정 파일 목록

### entities/ (도메인 모델)

| 파일 | 변경 유형 | 변경 내용 |
|------|----------|----------|
| `entities/script/model.py` | **수정** | `Emotion` enum 추가, `EMOTION_TAG_MAP` 추가, `Paragraph.emotion` 필드 추가 |
| `entities/script/__init__.py` | **수정** | `Emotion`, `EMOTION_TAG_MAP` export 추가 |

### features/ (기능 모듈)

| 파일 | 변경 유형 | 변경 내용 |
|------|----------|----------|
| `features/split_paragraphs/lib.py` | **수정** | `_EMOTION_TAG_RE` 패턴 추가, `_extract_emotion()` 함수 추가, `split_script()` 내 호출 |
| `features/generate_tts/emotion.py` | **신규** | 감정별 TTS 파라미터 매핑 모듈 (`QwenEmotionParams`, `ElevenLabsEmotionParams`, 매핑 dict) |
| `features/generate_tts/model.py` | **수정** | `TTSRequest.emotion` 필드 추가 |
| `features/generate_tts/lib.py` | **수정** | `generate_tts_for_text()` emotion 파라미터 추가, `generate_tts_for_paragraphs()` emotion 전달 |
| `features/generate_tts/backends/qwen_cuda.py` | **수정** | `emotion.py`에서 instruct 매핑 적용 |
| `features/generate_tts/backends/qwen_mps.py` | **수정** | 동일 |
| `features/generate_tts/backends/elevenlabs_api.py` | **수정** | `emotion.py`에서 voice_settings 오버라이드 적용 |
| `features/generate_tts/backends/custom_voice.py` | **수정 (최소)** | 향후 확장 포인트 주석만 추가 |
| `features/generate_tts/sidecar.py` | **수정** | `sync_tts_sidecar()` emotion 파라미터 추가, JSON에 emotion 기록 |
| `features/generate_tts/__init__.py` | **수정 (선택)** | emotion 모듈 export 추가 |

### tests/ (테스트)

| 파일 | 변경 유형 | 변경 내용 |
|------|----------|----------|
| `tests/features/test_emotion_tts.py` | **신규** | 감정 파싱 + 파라미터 매핑 단위 테스트 |
| `tests/entities/test_script_model.py` | **수정 또는 신규** | Paragraph emotion 필드 직렬화 테스트 |

---

## 변경 없는 파일 (하위 호환 확인 대상)

| 파일 | 이유 |
|------|------|
| `pipelines/script_to_video/lib.py` | `Paragraph` 인터페이스 불변 (emotion 기본값) |
| `pipelines/script_to_shorts/lib.py` | 동일 |
| `features/generate_tts/preprocess.py` | 전처리 로직 불변 (감정 태그는 파싱 시 이미 제거) |
| `shared/config/schema.py` | Phase 1에서는 변경 불필요 (향후 config에서 감정 파라미터 오버라이드 시 변경) |
| `scripts/continue_pipeline.py` | `Paragraph(index=, text=)` 기존 호출 호환 |
| `scripts/recompose_video.py` | 동일 |
| `scripts/regenerate_broll.py` | 동일 |

---

## FSD Import 영향도

```
entities/script/model.py (Emotion enum 정의)
    ^
    |--- features/split_paragraphs/lib.py (import Emotion, EMOTION_TAG_MAP)
    |--- features/generate_tts/emotion.py (import Emotion)
    |--- features/generate_tts/lib.py     (import Paragraph -- 기존)

features/generate_tts/emotion.py (감정 파라미터 매핑)
    ^
    |--- features/generate_tts/backends/qwen_cuda.py
    |--- features/generate_tts/backends/qwen_mps.py
    |--- features/generate_tts/backends/elevenlabs_api.py
```

모든 import 방향이 하위 -> 상위 (entities -> features) 또는 동일 feature 내부이므로 **FSD import 규칙 위반 없음**.

---

## 파일별 변경 크기 추정

| 파일 | 추가 줄 | 수정 줄 | 삭제 줄 |
|------|---------|---------|---------|
| `entities/script/model.py` | ~25 | 0 | 0 |
| `entities/script/__init__.py` | 2 | 1 | 0 |
| `features/split_paragraphs/lib.py` | ~25 | 3 | 0 |
| `features/generate_tts/emotion.py` | ~70 | 0 | 0 |
| `features/generate_tts/model.py` | 1 | 0 | 0 |
| `features/generate_tts/lib.py` | 5 | 5 | 0 |
| `features/generate_tts/backends/qwen_cuda.py` | 6 | 2 | 0 |
| `features/generate_tts/backends/qwen_mps.py` | 6 | 2 | 0 |
| `features/generate_tts/backends/elevenlabs_api.py` | 10 | 5 | 0 |
| `features/generate_tts/backends/custom_voice.py` | 2 | 0 | 0 |
| `features/generate_tts/sidecar.py` | 3 | 2 | 0 |
| `tests/features/test_emotion_tts.py` | ~80 | 0 | 0 |
| **합계** | **~235** | **~20** | **0** |
