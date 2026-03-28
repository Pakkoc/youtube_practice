# add-emotion-tts -- 문단별 감정 태그 TTS 생성

## 배경

현재 TTS 파이프라인은 모든 문단을 동일한 음성 파라미터로 생성한다. 유튜브 영상에서 내레이션의 감정 변화는 시청자 몰입도에 직접적인 영향을 미치지만, 현재 구조에서는 문단별로 다른 감정을 적용할 방법이 없다.

대본(`script.txt`)에 `[화남]`, `[기쁨]`, `[슬픔]` 같은 감정 태그를 삽입하면, 해당 문단의 TTS 생성 시 감정에 맞는 음성 파라미터를 자동으로 적용하는 기능이 필요하다.

## 요구사항 (EARS 형식)

### 핵심 요구사항

- **[REQ-01]** `Paragraph` 모델은 `emotion: str | None` 필드를 가져야 한다. 기본값은 `None`(= 중립/기본 감정).
- **[REQ-02]** WHEN 대본 텍스트에 `[감정태그]` 패턴(정규식: `^\[(.+?)\]`)이 문단 시작에 존재하면, THEN 해당 태그를 `Paragraph.emotion` 필드에 파싱하여 저장하고, 태그 자체는 `Paragraph.text`에서 제거해야 한다.
- **[REQ-03]** WHEN `generate_tts_for_paragraphs()`가 `emotion`이 설정된 `Paragraph`를 처리하면, THEN `TTSRequest.instruct`에 해당 감정에 매핑된 영어 instruct 문자열을 설정해야 한다.
- **[REQ-04]** 시스템은 감정 태그와 instruct 문자열의 매핑을 `EMOTION_MAP: dict[str, str]` 형태로 관리해야 한다. 최소 지원 감정: `화남`, `기쁨`, `슬픔`, `놀람`, `진지`, `흥분`.
- **[REQ-05]** WHEN Qwen CUDA 백엔드가 TTS를 생성하면, THEN `TTSRequest.instruct` 값을 `generate_custom_voice(instruct=...)` 파라미터로 전달해야 한다. (현재 이미 `request.instruct`를 전달하고 있으므로, `TTSRequest`에 값만 설정하면 된다.)
- **[REQ-06]** WHEN ElevenLabs 백엔드가 TTS를 생성하면, THEN `emotion` 값에 따라 `voice_settings`의 `stability`와 `style`(style_exaggeration) 파라미터를 조정해야 한다.

### 금지사항

- **[REQ-N01]** 감정 태그 텍스트(예: `[화남]`)는 TTS 입력 텍스트(`tts_text`)에 포함되면 안 된다. 태그는 파싱 후 완전히 제거되어야 한다.
- **[REQ-N02]** 감정 태그가 없는 기존 대본의 동작이 변경되면 안 된다. `emotion=None`일 때 기존과 동일한 음성 파라미터를 사용해야 한다.
- **[REQ-N03]** `EMOTION_MAP`에 없는 감정 태그가 입력되면 에러를 발생시키지 않고, 경고 로그 후 기본(중립) 파라미터로 폴백해야 한다.

### 선택사항

- **[REQ-O01]** 가능하다면, `TTSConfig`에 `emotion_map` 오버라이드 필드를 추가하여 YAML 설정으로 감정 매핑을 커스터마이징할 수 있어야 한다.
- **[REQ-O02]** 가능하다면, TTS sidecar JSON에 `emotion` 필드를 기록하여 재생성 판단에 활용할 수 있어야 한다.

## 제약 조건

- FSD import 규칙 준수: `features/` -> `entities/` -> `shared/` 방향만 허용.
- 기존 `Paragraph` 사용처(`split_paragraphs`, `split_scenes`, `generate_slides` 등)에서 `emotion` 필드는 선택적(Optional)이므로 하위 호환성 유지.
- Qwen3-TTS `instruct` 파라미터는 영어 문자열만 지원 (한국어 감정 태그 -> 영어 instruct 매핑 필수).
- ElevenLabs API는 `instruct` 파라미터가 없으므로, `voice_settings` 수치 조정으로 감정을 근사해야 한다.
- Custom Voice 백엔드(`generate_voice_clone`)는 `instruct` 파라미터를 지원하지 않으므로, 이 백엔드에서는 감정 태그를 무시하고 경고 로그만 출력한다.

## FSD 레이어 매핑

| 레이어 | 슬라이스 | 변경 유형 |
|--------|----------|-----------|
| entities/ | script/ | 수정 -- `Paragraph`에 `emotion` 필드 추가 |
| features/ | generate_tts/ | 수정 -- `TTSRequest`에 emotion 전달, 백엔드별 감정 파라미터 적용 |
| features/ | split_paragraphs/ | 수정 -- 문단 파싱 시 감정 태그 추출 로직 추가 |

## 의존성

- 내부: `entities.script.model.Paragraph`, `features.generate_tts.model.TTSRequest`, `features.generate_tts.lib`, `features.generate_tts.backends.*`, `features.split_paragraphs.lib`
- 외부: 없음 (기존 라이브러리만 사용)
