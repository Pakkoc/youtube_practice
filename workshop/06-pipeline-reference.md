# 파이프라인 레퍼런스 (API 모드)

> 각 파이프라인의 단계별 상세 설명과 CLI 명령어

---

## Part 1: API 모드 지원 현황

| 파이프라인 | API 모드 | 비활성화 기능 | 비고 |
|-----------|:--------:|-------------|------|
| script-to-video | ✅ | B-roll, 아바타 | TTS + 슬라이드 + 자막만 |
| script-to-shorts | ✅ | B-roll, 아바타 | TTS + 슬라이드 + 자막만 |
| video-to-shorts | ✅ | — | 기존 영상 기반 |
| script-to-carousel | ✅ | — | 이미지 출력 (영상 아님) |
| add-subtitles | ✅ | — | 자막만 추가 |

> **API 모드 (`CONFIG_PROFILE=api`)**: GPU 없이 실행 가능. B-roll 이미지 생성과 아바타(Ditto)는 완전 비활성화됩니다.

---

## Part 2: script-to-video (7단계)

유튜브 본편 영상을 만드는 메인 파이프라인입니다.

### 전체 흐름

```
[Step 1] 대본 문단 분리
    ↓
[Step 1.5] TTS 발음 사전 강화
    ↓
[Step 2] 3가지 동시 생성
    ├── TTS 음성 (ElevenLabs)
    ├── 슬라이드 TSX 수집
    └── B-roll 배경 이미지 (Gemini)
    ↓
[Step 3] 슬라이드 렌더링 (Remotion)
    ↓
[Step 4] 영상 합성 (FFmpeg) → video_raw.mp4
    ↓
[Step 5] 자막 생성 → corrected_subtitles.srt
    ↓
[Step 6] 아바타 오버레이 → (API 모드: 건너뜀)
    ↓
[Step 7] 자막 합성 → final_video.mp4
```

### 각 단계 상세

#### Step 1: 대본 문단 분리
- `script.txt`의 **빈 줄**을 기준으로 문단 분리
- 1 문단 = 1 슬라이드 = 1 TTS 음성 클립
- 출력: `paragraphs/001.txt`, `paragraphs/002.txt`, ...
- 씬 분할: 긴 문단을 문장 단위로 재분할 (짧은 문장은 병합, 기준값은 프로필에 따라 다름 -- base: 25자, api: 30자, 스키마 기본값: 30자)

#### Step 1.5: TTS 발음 사전 강화
- 영어 단어(Claude, GPT 등)의 한글 발음을 사전에 등록
- 예: `Claude → 클로드`, `GitHub → 깃허브`
- 저장 위치: `config/tts_dictionary.yaml`
- `/generate-video` 스킬이 이미 처리한 경우 자동 건너뜀

#### Step 2: 3가지 동시 생성 (병렬)
동시에 세 가지가 만들어집니다:

| 작업 | 담당 | 출력 | API 모드 |
|------|------|------|:--------:|
| TTS 음성 합성 | ElevenLabs API | `audio/001.wav`, ... | ✅ |
| 슬라이드 수집 | 기존 TSX 파일 수집 | `slides/001.tsx`, ... | ✅ |
| B-roll 이미지 | Gemini API (NanoBanana) | `broll/generated/broll_001.png`, ... | ❌ 비활성화 |

> `/generate-video` 스킬이 이미 슬라이드 TSX와 B-roll 프롬프트를 생성해두었으므로, 파이프라인은 **수집만** 합니다.

#### Step 3: 슬라이드 렌더링
- TSX 코드 + 오디오 길이 + 배경 이미지 → MP4 영상 클립
- Remotion이 4개 슬롯으로 **병렬 렌더링** (동시에 4개 슬라이드)
- 출력: `slides/001.mp4`, `slides/002.mp4`, ...

#### Step 4: 영상 합성
- 모든 슬라이드 클립 + 음성을 하나로 연결
- FFmpeg concat demuxer 사용
- 출력: `output/video_raw.mp4`

#### Step 5: 자막 생성
- 문단 텍스트 + 오디오 길이 기반으로 자막 타이밍 계산
- **Whisper 미사용** (결정론적 알고리즘으로 더 정확)
- 출력: `output/corrected_subtitles.srt`

#### Step 6: 아바타 오버레이
- **API 모드에서는 건너뜀** (로컬 GPU 필요)
- Full 모드에서는 Ditto 립싱크 아바타가 화면 오른쪽 하단에 오버레이

#### Step 7: 자막 합성
- video_raw.mp4 + corrected_subtitles.srt → final_video.mp4
- 폰트: Pretendard, 크기: 20px, 배경: 반투명 검정

### 출력 파일 체인

```
video_raw.mp4                  ← 슬라이드 + 음성 합성
    ↓
video_with_avatar.mp4          ← 아바타 오버레이 (Full 모드만, API 모드 건너뜀)
    ↓
video_with_subtitles.mp4       ← 자막 추가
    ↓
video_with_outro.mp4           ← 아웃트로 추가 (설정 시만, 선택적)
    ↓
final_video.mp4                ← 최종 영상
```

> API 모드에서는 아바타 단계가 없으므로 `video_with_avatar.mp4`가 생성되지 않습니다. 아웃트로가 설정되지 않은 경우 `video_with_outro.mp4` 단계도 건너뜁니다. 각 조건부 단계가 생략되면 이전 단계의 출력이 다음 단계로 바로 전달됩니다.

### 소요 시간 (참고)

| 문단 수 | TTS | 렌더링 | 합성 | 전체 |
|---------|-----|--------|------|------|
| 8개 (3분) | ~1분 | ~3분 | ~1분 | ~5분 |
| 15개 (5분) | ~2분 | ~5분 | ~1분 | ~8분 |
| 30개 (10분) | ~3분 | ~10분 | ~2분 | ~15분 |

---

## Part 3: script-to-shorts (6단계)

유튜브 쇼츠/인스타 릴스용 세로 영상을 만듭니다.

### 전체 흐름

```
[Step 1] 대본 문단 분리 + 씬 분할
    ↓
[Step 1.5] TTS 발음 사전 강화
    ↓
[Step 2] TTS 음성 생성 (ElevenLabs)
    ↓
[Step 3] Whisper 워드 타임스탬프 추출
    ↓
[Step 4] 훅 타이틀 로드 (hook_titles.json)
    ↓
[Step 5] Remotion ShortsSlotPool 병렬 렌더링
    ↓
[Step 6] FFmpeg 합성 → final_shorts.mp4
```

### 영상과의 차이점

| 항목 | script-to-video | script-to-shorts |
|------|----------------|-----------------|
| 비율 | 16:9 (1920x1080) | 9:16 (1080x1920) |
| 자막 방식 | SRT 파일 기반 | 단어별 실시간 하이라이트 |
| Whisper | 미사용 | 사용 (워드 타임스탬프) |
| 훅 타이틀 | 없음 | 상단에 큰 글씨 타이틀 |

### 실행 명령어

```bash
# /generate-shorts 먼저 실행 후
uv run video-automation pipeline script-to-shorts \
    --input projects/<project>/script.txt --project <project>
```

> `script-to-shorts`는 기본 프로필이 `shorts`이므로 `CONFIG_PROFILE` 지정 불필요. 필요 시 `CONFIG_PROFILE=api`로 오버라이드 가능.

---

## Part 4: script-to-carousel

인스타그램 카드뉴스를 만듭니다.

```
script.txt
    ↓ /generate-carousel 스킬로 TSX 생성
card_001.tsx ~ card_010.tsx
    ↓ 렌더링
card_001.png ~ card_010.png (1080x1350, 4:5 비율)
```

### 실행 방법

```bash
# Claude Code에서:
/generate-carousel my-project

# 렌더링:
uv run python scripts/regenerate_carousel.py my-project
```

---

## Part 5: video-to-shorts

기존 영상에서 바이럴 구간을 자동 추출하여 쇼츠를 만듭니다.

```
기존 영상 (.mp4)
    ↓ Whisper 전사 (음성→텍스트)
    ↓ LLM이 "바이럴 될 만한 구간" 선택
    ↓ FFmpeg 트림 (해당 구간만 잘라냄)
    ↓ Remotion 9:16 렌더링
shorts_001.mp4, shorts_002.mp4, ...
```

### 실행 명령어

```bash
uv run video-automation pipeline video-to-shorts \
    --input video.mp4 --project my-shorts
```

---

## Part 6: CLI 명령어 레퍼런스

### 파이프라인 실행 (기본 형식)

```bash
uv run video-automation pipeline <파이프라인> \
    --input <입력파일> --project <프로젝트명>
```

### 전체 명령어

```bash
# ① 16:9 영상 (기본)
uv run video-automation pipeline script-to-video \
    --input projects/my-video/script.txt --project my-video

# ② B-roll 없이 빠른 테스트
uv run video-automation pipeline script-to-video \
    --input projects/my-video/script.txt --project my-video --no-broll

# ③ 9:16 쇼츠 (기본 프로필: shorts, CONFIG_PROFILE 불필요)
uv run video-automation pipeline script-to-shorts \
    --input projects/my-shorts/script.txt --project my-shorts

# ④ 기존 영상 → 쇼츠
uv run video-automation pipeline video-to-shorts \
    --input video.mp4 --project my-shorts

# ⑤ 자막 추가
uv run video-automation pipeline add-subtitles \
    --input video.mp4 --project my-video

# ⑥ 환경 확인
uv run video-automation info
```

### 유틸리티 스크립트 (부분 재실행)

```bash
# 슬라이드만 재렌더링
uv run python scripts/regenerate_slides.py <project>

# B-roll만 재생성
uv run python scripts/regenerate_broll.py <project>

# 영상 재합성 (중간 파일 활용)
uv run python scripts/recompose_video.py <project>

# Step 3(렌더링)부터 재실행
uv run python scripts/continue_pipeline.py <project>

# 카드뉴스 렌더링
uv run python scripts/regenerate_carousel.py <project>
```

> **팁:** 슬라이드 디자인만 수정했으면 `regenerate_slides.py`로 재렌더링 후 `recompose_video.py`로 재합성하면 됩니다. 전체 파이프라인을 다시 돌릴 필요 없습니다.

---

## Part 7: script.txt 작성법

### 기본 규칙

| 규칙 | 설명 |
|------|------|
| 빈 줄로 문단 구분 | 연속된 줄이 아닌 빈 줄이 구분자 |
| 1 문단 = 1 슬라이드 | 한 문단이 하나의 영상 클립이 됨 |
| 1 문단 = 1 음성 | 한 문단이 하나의 TTS 오디오가 됨 |
| 첫 문단 = 인트로 | 시청자 관심을 끄는 도입부 |
| 마지막 문단 = 아웃트로 | 정리 + 구독/좋아요 유도 |

### 권장 분량

| 영상 길이 | 문단 수 | 문단당 글자 수 |
|----------|---------|--------------|
| 3분 | 8~12개 | 50~100자 |
| 5분 | 15~20개 | 50~100자 |
| 10분 | 25~35개 | 50~100자 |

### 예시

```text
오늘은 AI가 유튜브 영상을 자동으로 만드는 방법을 알아보겠습니다. 많은 분들이 궁금해하셨죠.

첫 번째로, 대본을 작성합니다. 빈 줄로 문단을 나누면, 각 문단이 하나의 슬라이드가 됩니다.

두 번째로, 명령어 하나면 됩니다. 음성 합성부터 영상 렌더링까지 자동으로 진행됩니다.

세 번째로, 수정이 쉽습니다. 마음에 안 드는 슬라이드만 골라서 바꿀 수 있습니다.

이렇게 간단하게 유튜브 영상을 만들 수 있습니다. 다음 영상에서 더 자세히 알아보겠습니다. 구독 부탁드립니다.
```

> 위 예시는 5개 문단 = 약 1분 30초 영상이 됩니다.
