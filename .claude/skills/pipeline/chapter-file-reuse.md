# 파일 재사용 로직

파이프라인은 기존 아티팩트를 자동 감지하여 재사용한다.
특정 문단만 재생성하려면 해당 파일을 삭제하면 된다.

## 재사용 조건표

| 아티팩트 | 파일 패턴 | 재사용 조건 | 소스 |
|----------|-----------|-------------|------|
| TTS | `audio/001.wav` | `output_path.exists()` + `get_duration() > 0` | `generate_tts/lib.py` |
| Slides (Freeform TSX) | `slides/001.tsx` | TSX 존재 → TSX 생성 skip | `generate_slides/lib.py` |
| Slides (Remotion) video | `slides/001.mp4` | MP4 존재 + duration ±0.5초 이내 → 렌더링 skip | `remotion_backend.py` |
| B-roll | `broll/generated/broll_001.*` | glob 매칭 → skip | `fetch_broll/lib.py` |
| Avatar clips | `avatar/clips/avatar_001.mp4` | `os.path.exists()` → skip | `inference_batch.py` |
| Carousel plan | `carousel/carousel_plan.json` | JSON 존재 → LLM 호출 skip | `generate_carousel/lib.py` |

## 재생성 방법

### 특정 문단만 재생성
```bash
# 3번 문단의 TTS만 재생성
rm projects/my-video/audio/003.wav

# 3번 문단의 슬라이드만 재생성
rm projects/my-video/slides/003.tsx projects/my-video/slides/003.mp4

# 3번 문단의 B-roll만 재생성
rm projects/my-video/broll/generated/broll_003.*
```

### 전체 재생성 스크립트
```bash
# B-roll만 전체 재생성
uv run python scripts/regenerate_broll.py my-video

# 슬라이드만 전체 재생성
uv run python scripts/regenerate_slides.py my-video

# 기존 slides+audio로 영상 재합성
uv run python scripts/recompose_video.py my-video

# Step 3~ 재실행 (TTS 변경 후)
uv run python scripts/continue_pipeline.py my-video
```

## 프로젝트 디렉토리 구조

```
projects/my-video/
├── script.txt           # 입력 대본
├── paragraphs/          # 001.txt, 002.txt, ...
├── slides/              # 001.tsx + 001.mp4 (Freeform) / 001.py + 001.mp4 (Manim)
├── audio/               # 001.wav, 002.wav, ...
├── broll/generated/     # broll_001.png, ...
├── avatar/
│   ├── clips/           # avatar_001.mp4, ...
│   └── avatar.mp4       # 연결된 최종
├── carousel/            # card_001.png, ...
└── output/
    ├── video_raw.mp4
    ├── video_with_avatar.mp4
    ├── video_with_subtitles.mp4
    └── final_video.mp4
```
