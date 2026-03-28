# add-emotion-tts 인수 기준

## 시나리오

### [REQ-01] Paragraph 모델 emotion 필드

**Scenario 1: emotion 필드가 있는 Paragraph 생성**
- **Given** `entities.script.model.Paragraph` 클래스가 존재한다
- **When** `Paragraph(index=1, text="안녕하세요", emotion="기쁨")`을 생성한다
- **Then** `paragraph.emotion`이 `"기쁨"`이어야 한다

**Scenario 2: emotion 필드 기본값 None**
- **Given** `entities.script.model.Paragraph` 클래스가 존재한다
- **When** `Paragraph(index=1, text="안녕하세요")`을 생성한다 (emotion 미지정)
- **Then** `paragraph.emotion`이 `None`이어야 한다

**Scenario 3: 기존 JSON 역직렬화 호환성**
- **Given** `{"index": 1, "text": "안녕하세요"}` JSON이 존재한다 (emotion 키 없음)
- **When** `Paragraph.model_validate(json_data)`를 호출한다
- **Then** `paragraph.emotion`이 `None`이어야 하고 에러가 발생하지 않아야 한다

### [REQ-02] 감정 태그 파싱

**Scenario 1: 문단 시작에 감정 태그가 있는 경우**
- **Given** 대본 텍스트에 `"[화남] 이건 정말 화가 나는 상황이다."` 문단이 있다
- **When** `split_script()`를 실행한다
- **Then** 해당 `Paragraph.emotion`이 `"화남"`이고, `Paragraph.text`가 `"이건 정말 화가 나는 상황이다."`이어야 한다 (태그 제거됨)

**Scenario 2: 감정 태그가 없는 일반 문단**
- **Given** 대본 텍스트에 `"평범한 문단입니다."` 문단이 있다
- **When** `split_script()`를 실행한다
- **Then** 해당 `Paragraph.emotion`이 `None`이고, `Paragraph.text`가 `"평범한 문단입니다."`이어야 한다

**Scenario 3: 문단 중간의 대괄호는 감정 태그로 인식하지 않음**
- **Given** 대본 텍스트에 `"이것은 [참고] 중간에 괄호가 있는 문단이다."` 문단이 있다
- **When** `split_script()`를 실행한다
- **Then** 해당 `Paragraph.emotion`이 `None`이고, `Paragraph.text`에 `"[참고]"`가 그대로 포함되어야 한다

**Scenario 4: 태그와 텍스트 사이 공백 처리**
- **Given** 대본 텍스트에 `"[기쁨]  오늘은 정말 좋은 날이다."` 문단이 있다 (태그 뒤 공백 2개)
- **When** `split_script()`를 실행한다
- **Then** `Paragraph.text`가 `"오늘은 정말 좋은 날이다."`이어야 한다 (앞뒤 공백 제거)

### [REQ-03] TTS 생성 시 감정 -> instruct 매핑

**Scenario 1: 감정이 설정된 문단의 TTS 생성**
- **Given** `Paragraph(index=1, text="화가 납니다", emotion="화남")` 문단이 있다
- **When** `generate_tts_for_paragraphs()`를 실행한다
- **Then** 해당 TTS 요청의 `TTSRequest.instruct`가 `"Speak with anger and frustration"`이어야 한다

**Scenario 2: 감정이 없는 문단의 TTS 생성**
- **Given** `Paragraph(index=1, text="안녕하세요", emotion=None)` 문단이 있다
- **When** `generate_tts_for_paragraphs()`를 실행한다
- **Then** 해당 TTS 요청의 `TTSRequest.instruct`가 빈 문자열 `""`이어야 한다

### [REQ-04] EMOTION_MAP 정의

**Scenario 1: 필수 감정 태그 매핑 존재 확인**
- **Given** `EMOTION_MAP` 상수가 정의되어 있다
- **When** `["화남", "기쁨", "슬픔", "놀람", "진지", "흥분"]` 각 키를 조회한다
- **Then** 모든 키에 대해 비어있지 않은 영어 문자열이 반환되어야 한다

### [REQ-06] ElevenLabs 백엔드 감정 적용

**Scenario 1: 감정에 따른 voice_settings 변경**
- **Given** ElevenLabs 백엔드가 활성화되어 있다
- **When** `emotion="화남"`인 `TTSRequest`로 `generate()`를 호출한다
- **Then** API 요청의 `voice_settings.stability`와 `voice_settings.style`이 기본값과 다른 감정별 값으로 설정되어야 한다

**Scenario 2: 감정 없는 요청은 기본 voice_settings 유지**
- **Given** ElevenLabs 백엔드가 활성화되어 있다
- **When** `emotion=None`인 `TTSRequest`로 `generate()`를 호출한다
- **Then** API 요청의 `voice_settings`가 config에서 설정한 기본값과 동일해야 한다

### [REQ-N01] 감정 태그 텍스트 제거 확인

**Scenario 1: TTS 입력에 태그 미포함**
- **Given** 대본에 `"[흥분] 대단한 발견입니다!"` 문단이 있다
- **When** 전체 파이프라인(split -> preprocess -> TTS)을 실행한다
- **Then** TTS 엔진에 전달되는 `tts_text`와 `text` 어디에도 `"[흥분]"` 문자열이 포함되지 않아야 한다

### [REQ-N02] 하위 호환성

**Scenario 1: 기존 대본 동작 불변**
- **Given** 감정 태그가 전혀 없는 기존 `script.txt`가 있다
- **When** 기존과 동일하게 파이프라인을 실행한다
- **Then** 생성되는 TTS 음성 파일이 기존과 동일한 파라미터로 생성되어야 한다 (instruct 빈 문자열, voice_settings 기본값)

### [REQ-N03] 미등록 감정 태그 폴백

**Scenario 1: EMOTION_MAP에 없는 태그**
- **Given** 대본에 `"[졸림] 피곤한 하루였다."` 문단이 있다 (졸림은 EMOTION_MAP에 미등록)
- **When** `generate_tts_for_paragraphs()`를 실행한다
- **Then** 경고 로그가 출력되고, 해당 문단은 기본 음성 파라미터(instruct 빈 문자열)로 TTS가 생성되어야 한다. 에러가 발생하면 안 된다.

## 엣지 케이스

- [ ] 빈 감정 태그: `"[] 텍스트"` -- 빈 문자열 태그는 감정으로 인식하지 않아야 한다
- [ ] 감정 태그만 있는 문단: `"[화남]"` (텍스트 없음) -- `min_length` 필터에 의해 문단 자체가 제거되어야 한다
- [ ] 중첩 대괄호: `"[[화남]] 텍스트"` -- 외부 대괄호만 감정 태그로 파싱하거나, 무시해야 한다
- [ ] 태그 내 공백: `"[화 남] 텍스트"` -- 공백 포함 태그도 정상 파싱되어야 한다 (EMOTION_MAP에 "화 남"이 없으면 REQ-N03에 의해 폴백)
- [ ] 여러 개 태그: `"[화남][기쁨] 텍스트"` -- 첫 번째 태그만 사용해야 한다
- [ ] sidecar에 emotion이 다른 경우 재생성: 기존 TTS 파일이 있지만 emotion이 변경된 경우, sidecar의 emotion과 비교하여 재생성 여부를 판단해야 한다

## 품질 게이트

- [ ] `ruff check .` 통과
- [ ] `ruff format --check .` 통과
- [ ] `mypy entities shared` 타입 체크 통과
- [ ] `lint-imports` FSD 규칙 통과
- [ ] `pytest tests/` 관련 테스트 통과
- [ ] 감정 태그 파싱 단위 테스트: `_extract_emotion()` 함수의 정상/엣지 케이스
- [ ] EMOTION_MAP 매핑 단위 테스트: 필수 감정 키 존재 확인
- [ ] 하위 호환성 테스트: 감정 태그 없는 대본 정상 처리 확인

## 성능 기준

- 감정 태그 파싱은 정규식 1회 실행 -- 문단당 추가 지연 무시 가능 (<1ms).
- TTS 생성 시간은 감정 파라미터 변경으로 인해 유의미하게 증가하지 않아야 한다 (instruct 문자열 추가에 의한 토큰 증가분은 무시 가능).
