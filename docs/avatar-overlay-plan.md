# Avatar Overlay 통합 계획

> **상태**: 대기 중 (Ditto 테스트 완료 후 진행)
> **작성일**: 2026-02-05
> **선행 조건**: 별도 레포에서 Ditto 립싱크 테스트 성공

---

## 1. 개요

### 1.1 목표
- 아바타 이미지 + TTS 오디오 → 립싱크 영상 생성
- 메인 영상 우측 하단에 원형 오버레이로 합성
- 기존 파이프라인에 옵션으로 통합 (활성화/비활성화 가능)

### 1.2 기술 스택
- **Ditto**: Motion-Space Diffusion 기반 Talking Head Synthesis
- **FFmpeg**: 원형 마스크 + 오버레이 합성
- **HuBERT**: 오디오 특징 추출 (언어 무관)

### 1.3 하드웨어 요구사항
- RTX 5090 32GB VRAM
- PyTorch 백엔드 (TensorRT 옵션)

---

## 2. 아키텍처

### 2.1 Feature 구조 (FSD 패턴)

```
features/
└── generate_avatar/
    ├── __init__.py              # public exports
    ├── model.py                 # AvatarConfig, AvatarClip
    ├── api.py                   # generate_avatar_video()
    ├── lib.py                   # overlay_avatar_circular()
    └── backends/
        ├── __init__.py
        ├── ditto_pytorch.py     # PyTorch 추론
        └── ditto_trt.py         # TensorRT 추론 (optional)
```

### 2.2 의존성 흐름

```
app/
  └── config (AvatarConfig 로드)
pipelines/
  └── script_to_video (아바타 단계 호출)
features/
  └── generate_avatar/
        ├── api.py → backends/ditto_*.py
        └── lib.py → shared/lib/ffmpeg.py
```

---

## 3. 데이터 모델

### 3.1 Config Schema 확장

```python
# shared/config/schema.py

class AvatarConfig(BaseModel):
    """아바타 오버레이 설정."""

    enabled: bool = False
    image_path: str | None = None           # 아바타 이미지 경로
    position: str = "bottom-right"          # bottom-right, bottom-left, top-right, top-left
    size: int = 200                         # 원형 지름 (px)
    margin: int = 20                        # 화면 가장자리 여백 (px)
    opacity: float = 1.0                    # 투명도 (0.0-1.0)
    border_width: int = 3                   # 테두리 두께 (px)
    border_color: str = "white"             # 테두리 색상
    force_backend: str | None = None        # pytorch | tensorrt | None(자동)


# AppConfig에 추가
class AppConfig(BaseModel):
    # ... 기존 필드 ...
    avatar: AvatarConfig = Field(default_factory=AvatarConfig)
```

### 3.2 Feature 내부 모델

```python
# features/generate_avatar/model.py

from pydantic import BaseModel
from pathlib import Path

class AvatarClip(BaseModel):
    """생성된 아바타 영상 정보."""
    video_path: Path
    duration: float
    resolution: tuple[int, int]  # (width, height)
```

---

## 4. Config 파일 확장

```yaml
# config/config.yaml

avatar:
  enabled: false                    # 기본 비활성화
  image_path: null                  # 프로젝트별 또는 전역 이미지
  position: "bottom-right"
  size: 200
  margin: 20
  opacity: 1.0
  border_width: 3
  border_color: "white"
  force_backend: null               # null=자동, "pytorch", "tensorrt"
```

---

## 5. 파이프라인 통합

### 5.1 수정 대상 파일
- `pipelines/script_to_video.py`

### 5.2 실행 순서

```
기존:
1. 문단 분리
2. 슬라이드 + TTS 생성 (병렬)
3. 영상 합성 (video_raw.mp4)
4. STT + 자막 교정
5. B-roll 삽입 (video_with_broll.mp4)
6. 자막 합성 (video_with_subtitles.mp4)
7. 무음 제거 → final_video.mp4

신규 (아바타 추가 시):
1. 문단 분리
2. 슬라이드 + TTS 생성 (병렬)
3. 영상 합성 (video_raw.mp4)
4. STT + 자막 교정
5. B-roll 삽입 (video_with_broll.mp4)
6. ⭐ 아바타 영상 생성 (avatar.mp4)
7. ⭐ 아바타 오버레이 합성 (video_with_avatar.mp4)
8. 자막 합성 (video_with_subtitles.mp4)
9. 무음 제거 → final_video.mp4
```

### 5.3 병렬화 고려

```
Option A: 순차 실행 (안전)
  B-roll 완료 → 아바타 생성 → 오버레이

Option B: 병렬 실행 (빠름, GPU 메모리 주의)
  ┌─ B-roll 생성 ─┐
  └─ 아바타 생성 ─┘ → 오버레이 합성

권장: Option A (VRAM 충돌 방지)
```

---

## 6. 핵심 함수 명세

### 6.1 generate_avatar_video()

```python
def generate_avatar_video(
    avatar_image: Path,
    audio_path: Path,
    output_path: Path,
    backend: str | None = None,
) -> AvatarClip:
    """
    아바타 이미지 + 오디오 → 립싱크 영상 생성.

    Args:
        avatar_image: 아바타 소스 이미지 (PNG/JPG)
        audio_path: TTS 오디오 파일 (WAV)
        output_path: 출력 영상 경로 (MP4)
        backend: 추론 백엔드 ("pytorch" | "tensorrt" | None)

    Returns:
        AvatarClip: 생성된 영상 정보

    Raises:
        AvatarGenerationError: Ditto 추론 실패 시
    """
```

### 6.2 overlay_avatar_circular()

```python
def overlay_avatar_circular(
    base_video: Path,
    avatar_video: Path,
    output_path: Path,
    size: int = 200,
    margin: int = 20,
    position: str = "bottom-right",
    opacity: float = 1.0,
    border_width: int = 3,
    border_color: str = "white",
) -> Path:
    """
    원형 아바타를 메인 영상에 오버레이.

    Args:
        base_video: 메인 영상 (B-roll 적용 완료)
        avatar_video: 아바타 립싱크 영상
        output_path: 출력 경로
        size: 원형 지름 (px)
        margin: 화면 가장자리 여백 (px)
        position: 위치 ("bottom-right" | "bottom-left" | "top-right" | "top-left")
        opacity: 투명도 (0.0-1.0)
        border_width: 테두리 두께 (px)
        border_color: 테두리 색상

    Returns:
        Path: 출력 영상 경로
    """
```

---

## 7. FFmpeg 필터 상세

### 7.1 원형 마스크 + 오버레이

```bash
ffmpeg -i base_video.mp4 -i avatar.mp4 -filter_complex "
  [1:v]scale=200:200,format=yuva420p,
  geq=lum='p(X,Y)':a='if(gt(pow(X-100,2)+pow(Y-100,2),98*98),0,255)'[avatar];
  [0:v][avatar]overlay=W-w-20:H-h-20:format=auto
" -c:a copy output.mp4
```

### 7.2 테두리 추가 버전

```bash
ffmpeg -i base_video.mp4 -i avatar.mp4 -filter_complex "
  [1:v]scale=200:200,format=yuva420p,
  geq=lum='p(X,Y)':a='if(gt(pow(X-100,2)+pow(Y-100,2),98*98),0,255)'[avatar_masked];
  color=white:s=206x206,format=yuva420p,
  geq=lum='p(X,Y)':a='if(gt(pow(X-103,2)+pow(Y-103,2),100*100),0,if(lt(pow(X-103,2)+pow(Y-103,2),97*97),0,255))'[border];
  [border][avatar_masked]overlay=3:3[avatar_with_border];
  [0:v][avatar_with_border]overlay=W-w-20:H-h-20:format=auto
" -c:a copy output.mp4
```

### 7.3 위치 매핑

| position | overlay 좌표 |
|----------|-------------|
| bottom-right | `W-w-{margin}:H-h-{margin}` |
| bottom-left | `{margin}:H-h-{margin}` |
| top-right | `W-w-{margin}:{margin}` |
| top-left | `{margin}:{margin}` |

---

## 8. 프로젝트 디렉토리 구조

```
projects/my-video/
├── script.txt
├── paragraphs/
├── slides/
├── audio/
│   ├── 001.wav
│   ├── 002.wav
│   └── full_audio.wav          # 전체 오디오 (아바타용)
├── broll/
├── avatar/                      # NEW
│   ├── source.png              # 아바타 원본 이미지 (옵션)
│   └── avatar.mp4              # 생성된 립싱크 영상
└── output/
    ├── video_raw.mp4
    ├── video_with_broll.mp4
    ├── video_with_avatar.mp4   # NEW
    ├── video_with_subtitles.mp4
    └── final_video.mp4
```

---

## 9. 에러 처리

### 9.1 예외 클래스

```python
# features/generate_avatar/exceptions.py

class AvatarError(Exception):
    """아바타 관련 기본 예외."""
    pass

class AvatarImageError(AvatarError):
    """아바타 이미지 로드/처리 실패."""
    pass

class AvatarGenerationError(AvatarError):
    """Ditto 추론 실패."""
    pass

class AvatarOverlayError(AvatarError):
    """FFmpeg 오버레이 실패."""
    pass
```

### 9.2 Fallback 전략

```
1. TensorRT 실패 → PyTorch로 fallback
2. PyTorch 실패 → 아바타 없이 진행 (warning 로그)
3. 오버레이 실패 → video_with_broll.mp4 그대로 사용
```

---

## 10. 테스트 계획

### 10.1 단위 테스트

```python
# tests/features/test_generate_avatar.py

def test_generate_avatar_video():
    """Ditto 추론 테스트."""
    pass

def test_overlay_avatar_circular():
    """FFmpeg 오버레이 테스트."""
    pass

def test_overlay_positions():
    """4개 위치 옵션 테스트."""
    pass
```

### 10.2 통합 테스트

```python
# tests/pipelines/test_script_to_video_with_avatar.py

def test_full_pipeline_with_avatar():
    """아바타 포함 전체 파이프라인."""
    pass

def test_pipeline_avatar_disabled():
    """아바타 비활성화 시 기존 동작 유지."""
    pass
```

---

## 11. 구현 체크리스트

### Phase 1: 기반 구축
- [ ] `features/generate_avatar/` 디렉토리 생성
- [ ] `model.py` 작성 (AvatarConfig, AvatarClip)
- [ ] `shared/config/schema.py`에 AvatarConfig 추가
- [ ] `config/config.yaml`에 avatar 섹션 추가

### Phase 2: Ditto 통합
- [ ] `backends/ditto_pytorch.py` 구현
- [ ] `api.py` 구현 (generate_avatar_video)
- [ ] Ditto 모델 로딩 및 싱글톤 관리

### Phase 3: 오버레이 구현
- [ ] `lib.py` 구현 (overlay_avatar_circular)
- [ ] FFmpeg 필터 테스트 (원형 마스크, 테두리)
- [ ] 4개 위치 옵션 검증

### Phase 4: 파이프라인 통합
- [ ] `pipelines/script_to_video.py` 수정
- [ ] 전체 오디오 추출 로직 추가
- [ ] 아바타 단계 삽입

### Phase 5: 테스트 및 문서화
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] CLAUDE.md 업데이트
- [ ] README 업데이트

---

## 12. 예상 이슈 및 해결책

| 이슈 | 해결책 |
|------|--------|
| Ditto 모델 로딩 시간 | 싱글톤 패턴으로 1회만 로드 |
| VRAM 부족 | B-roll과 순차 실행, 모델 언로드 후 실행 |
| TensorRT Blackwell 미지원 | PyTorch 백엔드로 fallback |
| 아바타-오디오 싱크 불일치 | Ditto 출력 FPS 확인 후 리샘플링 |
| 긴 영상 처리 | 청크 단위 생성 후 concat |

---

## 13. 참고 자료

- [Ditto GitHub](https://github.com/antgroup/ditto-talkinghead)
- [Ditto Paper](https://arxiv.org/abs/2411.19509)
- [Ditto HuggingFace](https://huggingface.co/digital-avatar/ditto-talkinghead)
- [FFmpeg geq filter](https://ffmpeg.org/ffmpeg-filters.html#geq)
