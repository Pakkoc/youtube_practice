# 프로젝트 분석 대시보드 -- Pipeline Integration Plan

## 1. 통합 전략

기존 파이프라인 코드에 최소한의 변경만 가한다. 핵심 원칙:

1. **context manager로 감싸기**: 파이프라인 함수 본문을 `track_pipeline()` 블록으로 감싼다
2. **step timer**: 각 단계를 `tracker.step()` context manager로 감싼다
3. **결과 수집**: 단계별 결과물에서 메트릭을 추출하여 `tracker.set_result()`로 기록
4. **실패 안전**: analytics 코드 실패가 파이프라인을 방해하지 않음

## 2. script_to_video 통합 (상세)

### 2.1 현재 코드 구조 (pipelines/script_to_video/lib.py)

```
def run_script_to_video(project, config, *, include_broll=True) -> Video:
    # Step 1: 대본 문단 분리
    script = load_script_and_split(...)

    # Step 1.5: TTS 사전 강화
    enhance_tts_dictionary(...)

    # Step 2: TTS + B-roll + props 병렬
    slides, audio_clips = _step2_remotion_parallel(...)

    # Step 4: 영상 합성
    raw_video = compose_video(...)

    # Step 5: 자막 생성 + 합성
    ...

    # Step 6-7: 아바타 + 최종 출력
    ...
    return video
```

### 2.2 수정 후 코드 구조

```python
import os
import time

def run_script_to_video(project, config, *, include_broll=True) -> Video:
    from features.track_analytics import track_pipeline

    profile = os.getenv("CONFIG_PROFILE", "base")

    with track_pipeline(project.name, "script_to_video", profile) as tracker:

        # Step 1: 대본 문단 분리
        with tracker.step("split_paragraphs"):
            script = load_script_and_split(...)
        tracker.set_result(paragraph_count=len(script.paragraphs))

        # Step 1.5: TTS 사전 강화
        with tracker.step("enhance_tts_dictionary"):
            enhance_tts_dictionary(...)

        # 씬 분할
        if config.pipeline.scenes.enabled:
            with tracker.step("split_scenes"):
                scenes = split_paragraphs_into_scenes(...)
            tracker.set_result(scene_count=len(scenes))

        # Step 2: TTS + B-roll + props 병렬
        with tracker.step("parallel_generation"):
            slides, audio_clips = _step2_remotion_parallel(...)
        tracker.set_result(
            slide_count=len(slides),
            tts_total_duration=sum(c.duration for c in audio_clips),
        )

        # B-roll 카운트 (broll_dir에서 파일 수 계산)
        broll_dir = project.broll_dir / "generated"
        if broll_dir.exists():
            broll_files = list(broll_dir.glob("*.png")) + list(broll_dir.glob("*.jpg"))
            tracker.set_result(broll_count=len(broll_files))

        # Step 4: 영상 합성
        with tracker.step("video_compositing"):
            raw_video = compose_video(...)

        # Step 5: 자막
        with tracker.step("subtitle_generation"):
            subtitle_result = generate_subtitles(...)

        with tracker.step("subtitle_burn"):
            burn_subtitles(...)

        # 아바타 (선택)
        if include_avatar:
            with tracker.step("avatar_overlay"):
                ...  # 기존 아바타 코드

        # 최종 결과
        tracker.set_result(
            final_video_duration=video.duration,
            final_video_size_bytes=final_path.stat().st_size,
            output_format="16:9",
        )

        return video
```

### 2.3 변경 규모

- `with track_pipeline(...) as tracker:` 로 전체 함수 본문을 감쌈 (들여쓰기 1레벨 추가)
- 각 주요 단계에 `with tracker.step(...):`  추가 (7-10곳)
- 단계 완료 후 `tracker.set_result(...)` 호출 (4-5곳)
- 기존 로직은 변경 없음

## 3. 다른 파이프라인 통합

### 3.1 script_to_shorts

```python
with track_pipeline(project.name, "script_to_shorts", profile) as tracker:
    with tracker.step("split_paragraphs"): ...
    with tracker.step("tts_generation"): ...
    with tracker.step("whisper_alignment"): ...
    with tracker.step("shorts_rendering"): ...
    with tracker.step("ffmpeg_compositing"): ...

    tracker.set_result(
        slide_count=..., tts_total_duration=...,
        output_format="9:16",
    )
```

### 3.2 script_to_carousel

```python
with track_pipeline(project.name, "script_to_carousel", profile) as tracker:
    with tracker.step("carousel_rendering"): ...

    tracker.set_result(
        slide_count=len(cards),
        output_format="4:5",
    )
```

### 3.3 video_to_shorts

```python
with track_pipeline(project.name, "video_to_shorts", profile) as tracker:
    with tracker.step("transcribe"): ...
    with tracker.step("select_segments"): ...
    with tracker.step("trim_videos"): ...
    with tracker.step("render_shorts"): ...

    tracker.set_result(
        slide_count=len(videos),
        output_format="9:16",
    )
```

## 4. Step Timer 구현

```python
class _StepTimer:
    """단계 소요 시간 측정용 context manager."""

    def __init__(self, tracker: PipelineTracker, step_name: str):
        self.tracker = tracker
        self.step_name = step_name
        self._start: float = 0.0

    def __enter__(self):
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.monotonic() - self._start
        status = "failed" if exc_type else "success"
        self.tracker._step_order += 1
        record_step(
            run_id=self.tracker.run_id,
            step_name=self.step_name,
            step_order=self.tracker._step_order,
            duration_seconds=elapsed,
            status=status,
        )
        return False  # 예외를 삼키지 않음
```

## 5. 병렬 실행 단계 처리

`_step2_remotion_parallel()`은 내부에서 ThreadPoolExecutor를 사용한다. 이 전체를 하나의 `parallel_generation` step으로 묶어 총 소요 시간만 기록한다.

개별 태스크 (TTS, B-roll, props) 타이밍이 필요하면 향후 `metadata_json` 필드에 JSON으로 기록할 수 있으나, v1에서는 병렬 블록 전체 시간만 추적한다.

## 6. 기존 프로젝트 히스토리 백필 (비포함)

이미 완료된 프로젝트의 결과물로부터 메트릭을 역추산하는 기능은 v1 범위 밖이다. analytics는 파이프라인 실행 시점에만 기록된다.
