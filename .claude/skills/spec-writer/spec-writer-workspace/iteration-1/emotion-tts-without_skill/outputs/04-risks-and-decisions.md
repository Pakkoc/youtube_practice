# Risks & Open Decisions: 감정 태그 기반 TTS 생성

---

## 1. 미결 설계 결정 (구현 전 확인 필요)

### Decision 1: 감정 태그 파싱 위치

**옵션 A (권장)**: `split_script()` 내 Paragraph 생성 직전
- 장점: 문단 분할/병합 로직 이후에 처리하므로 태그 손실 위험 없음
- 단점: `_split_long_paragraphs()`가 감정 태그 포함 문단을 분할하면, 분할된 첫 조각만 태그를 가짐

**옵션 B**: `preprocess_script()` 단계에서 조기 추출
- 장점: 전처리 파이프라인 초기에 감정 정보 확보
- 단점: 문단 인덱스가 아직 없는 시점이라 감정-문단 매핑이 복잡

**옵션 C**: 별도 전처리 패스 (2-pass)
- 1st pass: 감정 태그 추출 + 위치 기록
- 2nd pass: 문단 분할 + 감정 매핑
- 장점: 가장 정확
- 단점: 복잡도 증가, 현재 요구사항 대비 과설계

**권장**: 옵션 A. `_split_long_paragraphs()`에 의해 분할된 문단은 첫 조각만 감정 태그를 가지되, 후속 조각은 `neutral`로 처리. 일반적으로 감정 태그 문단이 150자를 초과하여 분할되는 경우는 드뭄.

### Decision 2: 알 수 없는 태그 처리 정책

**옵션 A (권장)**: 무시하고 텍스트에 그대로 유지
- `[참고]`, `[BGM]` 같은 비감정 태그가 음성에 포함될 수 있음
- 하지만 대본 작성자의 의도를 훼손하지 않음

**옵션 B**: 경고 로그 출력 후 태그 제거
- 태그가 음성에 읽히는 것을 방지
- 하지만 대본에 의도적으로 넣은 대괄호 텍스트를 제거할 위험

**권장**: 옵션 A. 지원 태그 목록을 문서화하여 대본 작성자가 참고하도록 함.

### Decision 3: ElevenLabs 감정 파라미터 수치

현재 제안한 수치는 이론적 추정값임:
```
HAPPY:      stability=0.70, style_exaggeration=0.45, speed=1.05
ANGRY:      stability=0.60, style_exaggeration=0.55, speed=1.10
SAD:        stability=0.90, style_exaggeration=0.20, speed=0.90
```

**결정 필요**: 이 수치들은 실제 음성 생성 후 청취 테스트를 통해 튜닝해야 함. 초기 구현에서는 위 수치를 사용하되, 이후 조정이 필요할 수 있음.

**대안**: `shared/config/schema.py`에 감정별 파라미터를 config 항목으로 추가하여, YAML에서 오버라이드 가능하게 만드는 것. 다만 Phase 1에서는 하드코딩된 매핑으로 충분.

### Decision 4: CustomVoice 백엔드 감정 지원

`generate_voice_clone()` API에 `instruct` 파라미터가 없으므로 현재 지원 불가.

**옵션**:
1. Phase 1에서는 미지원, sidecar에만 기록 (권장)
2. qwen_tts 라이브러리 소스를 확인하여 instruct 주입 가능 여부 조사

---

## 2. 기술 리스크

### Risk 1: Qwen3-TTS instruct 파라미터의 실효성 (높음)

**문제**: `generate_custom_voice(instruct=...)` 파라미터가 감정 제어에 얼마나 효과적인지 검증되지 않음. Qwen3-TTS는 주로 스타일 지시("Read slowly", "Whisper") 용도로 설계되었으며, 감정 뉘앙스 제어는 모델 학습 데이터에 의존.

**영향**: 감정 태그를 지정해도 음성 차이가 미미할 수 있음

**대응**:
1. 구현 전 Qwen3-TTS로 다양한 instruct 문구 테스트
2. 효과가 미미할 경우:
   - instruct 문구를 더 구체적으로 조정 (예: "Read as if you are very angry, with raised voice and fast pace")
   - Qwen 백엔드에서는 감정 기능을 "best-effort"로 표기

### Risk 2: ElevenLabs voice_settings 부작용 (중간)

**문제**: `stability`, `style_exaggeration` 값을 극단적으로 변경하면 음성 품질이 저하될 수 있음 (떨림, 부자연스러운 발음 등).

**영향**: 특정 감정 프리셋이 예상과 다른 결과를 낼 수 있음

**대응**:
1. 보수적인 수치 범위 사용 (기본값에서 +/-30% 이내)
2. `style_exaggeration`은 0.0~0.6 범위로 제한 (공식 문서 권장)
3. 각 감정별 A/B 테스트 수행

### Risk 3: 문단 분할 시 태그 손실 (낮음)

**문제**: `_split_long_paragraphs()`가 150자 초과 문단을 분할할 때, 감정 태그가 첫 번째 조각에만 남고 나머지 조각은 `neutral`이 됨.

**시나리오**:
```
[화남] 이것은 매우 긴 문단으로서 150자를 초과하는 내용을 담고 있습니다...
```
분할 후:
```
Paragraph(text="이것은 매우 긴 문단으로서...", emotion=ANGRY)
Paragraph(text="150자를 초과하는 내용을...", emotion=NEUTRAL)  # 태그 손실
```

**영향**: 긴 문단의 뒷부분이 다른 감정으로 읽힐 수 있음

**대응**:
1. 대부분의 감정 태그 문단은 짧은 편 (감정 표현 -> 강조 -> 짧은 문장)
2. 필요 시 분할된 조각에 원본 감정을 전파하는 로직 추가 (Phase 2)

### Risk 4: 기존 대본의 대괄호 텍스트 오인식 (낮음)

**문제**: 기존 대본에 `[참고]`, `[BGM 삽입]` 같은 대괄호 텍스트가 있으면 감정 태그로 오인할 수 있음.

**영향**: 매핑되지 않는 태그는 옵션 A 정책에 의해 무시되므로, 실제 오동작 가능성은 낮음. 다만 `[sad]` 같은 영문이 의도치 않게 감정 태그로 해석될 가능성은 있음.

**대응**:
1. 알 수 없는 태그는 텍스트에 그대로 유지 (안전)
2. 매핑 가능한 태그만 감정으로 처리
3. 기존 프로젝트 대본 스캔하여 충돌 가능한 패턴 확인

### Risk 5: Sidecar 캐시 무효화 (낮음)

**문제**: 기존에 생성된 TTS 파일의 sidecar JSON에 `emotion` 키가 없음. 감정 태그를 추가한 후 재생성할 때, sidecar의 `text` 비교로 캐시 hit/miss를 판단하는데, 감정 태그가 제거된 `text`가 기존 `text`와 동일하면 캐시를 재사용할 수 있음.

**영향**: 감정 태그를 변경해도 기존 TTS가 재사용되어 감정 미적용

**대응**: sidecar 비교 시 `emotion` 필드도 확인하도록 `generate_tts_for_paragraphs()`의 캐시 로직 수정

```python
# 현재
text_match = sidecar and sidecar.get("text") == paragraph.text

# 변경
text_match = (
    sidecar
    and sidecar.get("text") == paragraph.text
    and sidecar.get("emotion", "neutral") == paragraph.emotion.value
)
```

---

## 3. 검증 체크리스트

구현 완료 후 아래 항목을 모두 확인:

- [ ] `Paragraph(index=1, text="test")` -- emotion 기본값으로 에러 없이 생성
- [ ] `split_script()` -- 감정 태그 없는 기존 대본이 변경 없이 동작
- [ ] `split_script()` -- 감정 태그 포함 대본에서 태그 파싱 + 텍스트 분리 정상
- [ ] `split_script()` -- 알 수 없는 태그 `[모름]`이 텍스트에 그대로 유지
- [ ] `generate_tts_for_paragraphs()` -- emotion 값이 TTSRequest까지 전달
- [ ] Qwen CUDA 백엔드 -- instruct에 감정 문구 적용
- [ ] ElevenLabs 백엔드 -- voice_settings에 감정 수치 적용
- [ ] Sidecar JSON -- emotion 필드 기록
- [ ] 기존 TTS 캐시 -- emotion 변경 시 재생성
- [ ] `ruff check .` 통과
- [ ] `lint-imports` 통과
- [ ] `pytest` 전체 통과
