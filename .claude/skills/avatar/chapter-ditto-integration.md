# Ditto 아바타 통합

> 소스: `features/generate_avatar/lib.py`, `ditto-talkinghead/inference_batch.py`

## 배치 모드 (기본)

```
audio/001.wav, 002.wav, ...
  → generate_avatar_clips(audio_dir)
    → inference_batch.py (WSL2 subprocess)
      → SDK 1회 로드, N개 클립 순차 처리
        → avatar/clips/avatar_001.mp4, avatar_002.mp4, ...
          → concat_videos()
            → avatar/avatar.mp4
```

### 핵심 특징
- SDK 1회 로드 후 N개 클립 순차 처리 (로드 시간 절약)
- `skip_existing`: 기존 클립 자동 건너뜀
- Timeout: **7200초 (2시간)** -- 배치 처리용
- WSL2 subprocess + conda 환경 활성화 필수

### 경로 변환 주의
```python
# 반드시 이 순서로!
path = audio_dir.resolve()       # 1. 절대 경로 변환
wsl_path = to_wsl_path(path)     # 2. WSL 경로 변환
```
- `to_wsl_path()`는 절대 경로만 변환 가능
- 상대 경로는 변환 없이 통과됨 → 버그 원인

## 원형 오버레이

`overlay_avatar_circular(base_video, avatar_video, output_path)`:

```
FFmpeg filter chain:
  [1:v] scale → format=yuva420p → geq(원형 마스크) → drawbox(테두리) [avatar]
  [0:v][avatar] overlay=W-w-margin_x:H-h-margin_y:shortest=1
```

### 파라미터
| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `size` | 180 | 원형 지름 |
| `margin_x` | 30 | 우측 여백 |
| `margin_y` | 120 | 하단 여백 (자막 피함) |
| `border_width` | 3 | 테두리 두께 |
| `border_color` | "white" | 테두리 색상 |

### 주의
- `stream_loop -1` + `shortest` -- 아바타가 짧으면 루프
- 코덱: H.264 medium preset, CRF 18
- 오디오: copy (재인코딩 없음)

## Config

```yaml
avatar:
  enabled: false  # 기본 비활성화
  image_path: "path/to/avatar.png"
  size: 180
  margin_y: 120
  ditto_project_path: "path/to/ditto-talkinghead"

pipeline:
  avatar:
    enabled: true  # pipeline에서 활성화
```

## 레거시 함수

`generate_avatar_video()` -- 단일 오디오 → 단일 비디오 (하위호환용 유지)
