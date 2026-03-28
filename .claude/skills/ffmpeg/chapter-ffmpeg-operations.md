# FFmpeg 래퍼 함수

> 소스: `shared/lib/ffmpeg.py`

## Duration & Info

| 함수 | 설명 |
|------|------|
| `check_ffmpeg() -> bool` | FFmpeg 설치 확인 |
| `get_duration(media_path) -> float` | 미디어 길이 (초, ffprobe) |

## Audio

| 함수 | 설명 |
|------|------|
| `concat_audio(audio_files, output_path) -> Path` | 오디오 파일 연결 (concat demuxer + copy) |

## Video

| 함수 | 설명 |
|------|------|
| `concat_videos(video_files, output_path) -> Path` | 영상 연결 (동일 코덱/해상도/fps 필요) |
| `trim_video(input, output, start, end, accurate=False) -> Path` | 영상 트리밍 |
| `compose_slideshow(pairs, output, fps=30) -> Path` | 이미지+오디오 → 영상 (Marp용) |
| `compose_video_slideshow(slides, audio_clips, output, fps=30) -> Video` | Slide+AudioClip → 영상 (Remotion용) |

## trim_video 상세

```python
# 빠른 트리밍 (keyframe 기준, 부정확)
trim_video(input, output, start=10.0, end=25.0)

# 정확한 트리밍 (재인코딩, 느림, 쇼츠용)
trim_video(input, output, start=10.0, end=25.0, accurate=True)
```

## Windows 주의사항

### concat list 파일
- **파일명만 사용** (`s.name`), 전체 경로 사용 금지
- FFmpeg는 list 파일 디렉토리 기준으로 경로 해석
- 전체/상대 경로 → Windows에서 경로 중복 오류

```python
# CORRECT
f"file '{s.name}'"

# WRONG (Windows에서 경로 중복)
f"file '{s.file_path}'"
```

### 기타
- `shell=True` 사용 (Windows 호환)
- 4GB 초과 오디오는 pydub 대신 ffmpeg 직접 사용
- encoding='utf-8' 명시 (subprocess output)

## 오디오 추출 (쇼츠용)

```python
# Whisper 25MB 제한 회피: MP3 64kbps 16kHz mono
ffmpeg -i video.mp4 -vn -acodec libmp3lame -b:a 64k -ar 16000 -ac 1 output.mp3
```
