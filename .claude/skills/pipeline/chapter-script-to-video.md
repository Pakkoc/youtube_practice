# script-to-video 파이프라인 (7단계)

> 소스: `pipelines/script_to_video/lib.py` → `run_script_to_video()`

## 전체 흐름

```
1. 문단 분리 (split_paragraphs) → 1.5 TTS 사전 자동 강화 (enhance_tts_dictionary)
2. 3-way 병렬 실행 (ThreadPoolExecutor, max_workers=3)
   ├─ 기존 TSX/PY 수집 (API 호출 없음, Claude Code가 스킬로 사전 생성)
   ├─ TTS 생성 (ElevenLabs/로컬)
   └─ B-roll 이미지 생성 (TTS 완료 대기 후)
3. Remotion 슬라이드 렌더링 (TSX/Manim + duration + B-roll 배경)
4. 영상 합성 (FFmpeg concat)
5. 자막 생성 (결정론적, Whisper 미사용)
6. 아바타 배치 생성 + 오버레이 (선택, Ditto)
7. 자막 합성 → final_video.mp4
```

## 출력 체인

```
video_raw.mp4
  → video_with_avatar.mp4 (아바타 ON일 때)
    → video_with_subtitles.mp4
      → final_video.mp4
```

## Step 2 병렬 처리 상세

`_step2_remotion_parallel()` 함수가 3개 태스크를 동시 실행:

| Task | 함수 | 의존성 |
|------|------|--------|
| TTS 생성 | `_generate_tts_task()` | 없음 |
| TSX/PY 수집 | `_generate_remotion_props_task()` | 없음 (기존 파일 수집, API 미호출) |
| B-roll 이미지 | `_generate_broll_images_task()` | TTS 완료 대기 (duration 필요) |

- TSX/PY 파일은 Claude Code가 `/generate-slides` 스킬 참고하여 사전 생성. 파이프라인은 수집만.
- B-roll은 TTS future를 받아서 `future.result()`로 duration 대기
- `concurrent.futures.as_completed()`로 결과 수집

## Step 3: Remotion 렌더링

- `RemotionSlideBackend.render()` 호출
- props에 `durationInFrames`, `slideIndex`, `totalSlides`, `backgroundImage` 자동 주입
- B-roll 이미지 → `remotion/public/_bg_*` 복사 → 20% opacity 배경

## Step 5: 자막 생성 (Whisper 미사용)

- `generate_subtitles()` in `features/generate_subtitles/lib.py`
- 문단 텍스트 + 오디오 duration → SRT (글자 수 비례 시간 할당)
- API 호출 없는 결정론적 알고리즘

## Step 6: 아바타 (선택)

- `generate_avatar_clips(audio_dir)` → 문단별 개별 클립 → `concat_videos()` → `avatar.mp4`
- `overlay_avatar_circular()` → 원형 마스크, 우측 하단 (margin_y=120)
- WSL2 subprocess, timeout 7200초

## 핵심 Config

```python
config.pipeline.slides.backend  # "remotion" | "remotion-ai" | "api"(=marp)
config.pipeline.broll.enabled   # B-roll on/off
config.pipeline.avatar.enabled  # 아바타 on/off
config.slides.backend           # 실제 사용되는 값 (pipeline이 덮어씀)
```

## CLI 실행

```bash
uv run video-automation pipeline script-to-video \
    --input script.txt --project my-video

# B-roll 없이 빠른 테스트
uv run video-automation pipeline script-to-video \
    --input script.txt --project my-video --no-broll

# API-Only 모드
CONFIG_PROFILE=api uv run video-automation pipeline script-to-video \
    --input script.txt --project my-video
```
