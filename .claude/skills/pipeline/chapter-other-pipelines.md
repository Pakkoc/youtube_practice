# 기타 파이프라인

## script-to-shorts (6단계)

> 소스: `pipelines/script_to_shorts/lib.py` → `run_script_to_shorts()`

```
1. 대본 문단 분리 + 씬 분할 → 1.5 TTS 사전 자동 강화 (enhance_tts_dictionary)
2. TTS 생성 (ElevenLabs)
3. Whisper 워드 타임스탬프 → 원본 대본 정렬 → 표시 정규화
4. 훅 타이틀 로드 (hook_titles.json, Claude Code가 스킬로 사전 생성)
5. Remotion ShortsSlotPool 병렬 렌더링 (기존 TSX 사용, 4슬롯)
6. FFmpeg 합성 → final_shorts.mp4
```

### 훅 타이틀 (3-Layer, 스킬 전용)

`/generate-shorts-title` 스킬로 사전 생성 필수. API 호출하지 않음.

```json
{"index": 1, "line1": "한 줄이면 세팅 끝", "line2": "", "subDetail": "/init 사용법"}
```

- `line1`: 민트(#A2FFEB) 메인 타이틀, 최대 16자 (auto-scaled)
- `line2`: 빈 문자열 `""` (사용하지 않음)
- `subDetail`: 손글씨체 부제, 최대 15자
- 채널명("샘호트만 : AI 엔지니어의 시선")은 코드에 고정 (props 불필요)

### 병렬 렌더링 안전 규칙

ShortsSlotPool / FreeformSlotPool 공통:

- **원자적 쓰기 필수**: `write_slot()`은 `write_text(tmp) + os.replace()` 사용. 직접 `write_text()` 호출 금지.
  - 이유: 4프로세스가 동시 번들링 시, 한 슬롯이 쓰는 도중 다른 번들러가 불완전한 파일을 읽어 실패
- **렌더 재시도**: 실패 시 최대 2회 재시도 (2초 간격). 일시적 번들 경쟁 대응.
- **렌더 중단 후 재시작**: `taskkill //F //IM node.exe` 필수 (Windows 좀비 node 방지)

---

## video-to-shorts (4단계)

> 소스: `pipelines/video_to_shorts/lib.py` → `run_video_to_shorts()`

```
1. Whisper word timestamps 추출 (MP3 64kbps 16kHz, 25MB 제한 회피)
2. LLM 바이럴 구간 선정 (gpt-5-mini, 15-60초)
3. FFmpeg trim (accurate=True, 재인코딩)
4. Remotion 1080x1920 쇼츠 렌더링
```

### 주요 함수
- `_step_word_timestamps()` -- Whisper 전사 + MP3 추출
- `_step_viral_plan()` -- LLM이 SRT+대본에서 바이럴 구간 선정
- `_correct_word_timestamps()` -- corrected_subtitles.srt로 Whisper 오류 보정
- `_filter_and_convert_words()` -- 구간 필터링 + 프레임 변환 (30 FPS)

### 레이아웃 (샌드위치)
- hookY=310, videoY=460 (1080x608 contain), subtitleY=1120
- 검은 배경 + 16:9 원본 비율 유지
- 3단어 청크 자막, 72px 이탤릭 훅 제목

### Config
```yaml
shorts:
  max_shorts: 3
  min_duration: 15
  max_duration: 60
  model: "gpt-5-mini"
  accent_color: "#A2FFEB"
```

### CLI
```bash
uv run video-automation pipeline video-to-shorts \
    --input video.mp4 --project my-video
```

---

## script-to-carousel (4단계)

> 소스: `pipelines/script_to_carousel/lib.py` → `run_script_to_carousel()`

```
1. 대본 읽기
2. LLM 카루셀 계획 생성 (gpt-5-mini, carousel_plan.json 캐싱)
3. SerperDev 배경 이미지 검색 + 4:5 센터크롭
4. Remotion still PNG 렌더링 (npx remotion still CarouselCard)
```

### 카드 타입 (discriminated union on cardType)
`cover` | `list` | `steps` | `compare` | `highlight` | `ending`

### 출력
- `carousel/card_001.png`, `card_002.png`, ...
- 1080x1350 (4:5 비율)

### Config
```yaml
carousel:
  max_cards: 10
  width: 1080
  height: 1350
  model: "gpt-5-mini"
```

### CLI
```bash
uv run video-automation pipeline script-to-carousel \
    --input script.txt --project my-video
```

---

## add-subtitles

> Whisper STT 기반 자막 추가 (script-to-video의 결정론적 자막과 다름)

```bash
uv run video-automation pipeline add-subtitles \
    --input video.mp4 --project my-video
```

- Whisper로 음성 → SRT 전사
- LLM으로 자막 교정 (`subtitle_correction.txt` 프롬프트)
- FFmpeg로 자막 합성 (burn)
