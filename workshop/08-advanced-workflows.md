# 고급 워크플로우 & 복구

> 부분 재실행, 배치 생산, 중간 산출물 활용법

> 난이도: 중급 | 소요: 읽기 15분

---

## Part 1: 왜 부분 재실행이 필요한가?

Full 파이프라인은 문단 수에 따라 5~15분이 걸립니다. 슬라이드 하나 수정했는데 TTS부터 다시 돌리면 시간과 API 크레딧이 낭비됩니다.

다행히 파이프라인은 중간 산출물(`audio/`, `slides/`, `broll/`)을 프로젝트 폴더에 보존합니다. 이미 만들어진 파일이 있으면 해당 단계를 건너뛰므로, **변경된 부분만 재실행**하는 것이 가능합니다.

> **핵심:** "전체 재실행"은 대본이 바뀌었을 때만 필요합니다. 나머지는 유틸리티 스크립트로 부분만 돌리세요.

---

## Part 2: 유틸리티 스크립트 총정리

`scripts/` 폴더에 있는 5가지 유틸리티 스크립트입니다:

| 스크립트 | 기능 | 사용 시점 | 소요 시간 |
|----------|------|----------|:---------:|
| `regenerate_slides.py` | TSX → MP4 재렌더링 | 슬라이드 디자인 수정 후 | ~3분 |
| `regenerate_broll.py` | B-roll 이미지 재생성 | 배경 이미지 교체 | ~2분 |
| `recompose_video.py` | 중간 파일로 최종영상 재합성 | 자막/순서 변경 | ~1분 |
| `continue_pipeline.py` | Step 3(렌더링)부터 재시작 | TTS 수정 후 | ~5분 |
| `regenerate_carousel.py` | 캐러셀 TSX → PNG 재렌더링 | 카드 디자인 수정 | ~1분 |

### 각 스크립트 실행 명령어

**슬라이드 재렌더링** — 전체 또는 특정 슬라이드만 가능:

```bash
# 프로젝트의 모든 슬라이드 재렌더링
uv run python scripts/regenerate_slides.py my-project

# 특정 슬라이드만 재렌더링 (예: 3번, 5번)
uv run python scripts/regenerate_slides.py my-project 003 005

# 기존 MP4 강제 재렌더링
uv run python scripts/regenerate_slides.py my-project --force
```

**B-roll 재생성** — 이미지를 새로 생성하고 슬라이드까지 재렌더링:

```bash
uv run python scripts/regenerate_broll.py my-project
```

**영상 재합성** — 기존 슬라이드 MP4 + 오디오로 최종 영상만 다시 합성:

```bash
uv run python scripts/recompose_video.py my-project
```

**파이프라인 이어하기** — TTS 변경 후 Step 3(영상 합성)부터 재실행:

```bash
uv run python scripts/continue_pipeline.py my-project
```

**캐러셀 재렌더링** — TSX 카드를 PNG로 다시 렌더링:

```bash
# 전체 카드 재렌더링
uv run python scripts/regenerate_carousel.py my-project

# 특정 카드만 재렌더링 (예: 1번, 3번)
uv run python scripts/regenerate_carousel.py my-project 1 3
```

> API 모드에서 파이프라인을 실행할 때는 `CONFIG_PROFILE=api`를 앞에 붙이세요. 유틸리티 스크립트는 프로필 지정이 불필요합니다.

---

## Part 3: 의사결정 트리 -- "뭘 다시 돌려야 하지?"

수정한 내용에 따라 어떤 스크립트를 실행해야 하는지 판단합니다:

```
뭘 수정했나?
├── 대본(script.txt) 변경
│   └── /generate-video부터 전체 재실행
├── 슬라이드 디자인(TSX)만 수정
│   └── regenerate_slides.py → recompose_video.py
├── B-roll 이미지만 교체
│   └── regenerate_broll.py → regenerate_slides.py → recompose_video.py
├── TTS 발음/속도 변경
│   └── continue_pipeline.py (Step 3부터 재실행)
├── 자막 설정 변경
│   └── recompose_video.py (자막만 재합성)
└── 캐러셀 카드 수정
    └── regenerate_carousel.py
```

**대본 변경**은 모든 중간 산출물에 영향을 주므로 전체 재실행이 필요합니다. 반면 **슬라이드 TSX만 수정**했다면 렌더링 + 합성 두 단계만 돌리면 됩니다.

> **핵심:** 트리 아래로 갈수록 재실행 범위가 좁아집니다. 가능하면 가장 좁은 범위의 스크립트를 선택하세요.

---

## Part 4: 중간 산출물 이해하기

파이프라인이 생성하는 중간 산출물과 의존 관계입니다:

| 폴더/파일 | 생성 주체 | 의존하는 후속 단계 |
|-----------|----------|-------------------|
| `paragraphs/` | 문단 분리 (split_paragraphs) | TTS, 슬라이드, B-roll 전부 |
| `audio/*.wav` | ElevenLabs TTS | 영상 합성 (compose_video) |
| `slides/*.tsx` | Claude Code (스킬) | 슬라이드 렌더링 (Remotion) |
| `slides/*.mp4` | Remotion 렌더링 | 영상 합성 (compose_video) |
| `broll/generated/` | 이미지 생성 API | 슬라이드 렌더링 (배경) |
| `output/video_raw.mp4` | FFmpeg 합성 | 자막 합성 |
| `output/final_video.mp4` | FFmpeg 자막 합성 | 최종 출력 |

파일 의존 관계를 다이어그램으로 표현하면:

```
paragraphs/
    ├── → audio/          (TTS 생성)
    ├── → slides/*.tsx    (슬라이드 디자인)
    └── → broll/          (B-roll 이미지 프롬프트)
              │
              ▼
         slides/*.mp4     (TSX + B-roll → 렌더링)
              │
         audio/ ──┐
              │   │
              ▼   ▼
         video_raw.mp4    (슬라이드 + 오디오 합성)
              │
              ▼
         final_video.mp4  (자막 합성)
```

> **핵심:** 파일 의존 관계를 알면 최소한의 재실행으로 수정이 가능합니다. `paragraphs/`가 바뀌면 전부 다시, `slides/*.tsx`만 바뀌면 렌더링부터만 다시 돌리면 됩니다.

---

## Part 5: 배치 생산 워크플로우

한 세션에서 영상 3개를 연속으로 생산하는 방법입니다.

### Step 1: 대본 3개 먼저 생성

Claude Code에서 연속으로 요청합니다:

```
"AI 자동화 입문"을 주제로 대본을 작성해줘.
projects/batch-001/script.txt에 저장해줘.
```

```
"AI로 쇼츠 만들기"를 주제로 대본을 작성해줘.
projects/batch-002/script.txt에 저장해줘.
```

```
"AI 영상 편집 도구 비교"를 주제로 대본을 작성해줘.
projects/batch-003/script.txt에 저장해줘.
```

### Step 2: 슬라이드 + B-roll 미리 생성

Claude Code에서 `/generate-video`를 3개 프로젝트에 대해 실행합니다. 이 단계에서 TSX 슬라이드, B-roll 프롬프트, TTS 사전이 미리 준비됩니다:

```
/generate-video batch-001
```

```
/generate-video batch-002
```

```
/generate-video batch-003
```

### Step 3: 파이프라인 3개 연속 실행

```bash
uv run video-automation pipeline script-to-video \
    --input projects/batch-001/script.txt --project batch-001

uv run video-automation pipeline script-to-video \
    --input projects/batch-002/script.txt --project batch-002

uv run video-automation pipeline script-to-video \
    --input projects/batch-003/script.txt --project batch-003
```

### Step 4: 결과 확인 및 부분 수정

각 프로젝트의 결과물을 확인하고, 필요하면 Part 3의 의사결정 트리에 따라 부분만 수정합니다.

> **팁:** 슬라이드를 먼저 다 생성해두고(`/generate-video` x 3) 파이프라인을 연달아 돌리면 대기 시간이 줄어듭니다. `/generate-video`는 Claude Code가 TSX를 작성하는 시간이 필요하지만, 파이프라인은 자동으로 진행되므로 다른 작업과 병행할 수 있습니다.

---

## Part 6: 환경변수 조합으로 실험하기

같은 대본으로 다른 설정을 비교하면 최적의 조합을 찾을 수 있습니다.

### 자주 쓰는 환경변수 조합

| 비교 항목 | 조합 A | 조합 B |
|----------|--------|--------|
| B-roll 유무 | `ENABLE_BROLL=true` | `ENABLE_BROLL=false` |
| 이미지 백엔드 | `IMAGE_GEN_BACKEND=local` | `IMAGE_GEN_BACKEND=nanobanana` |
| 프로필 전환 | `CONFIG_PROFILE=base` (GPU) | `CONFIG_PROFILE=api` (클라우드) |
| 아바타 유무 | `ENABLE_AVATAR=true` | `ENABLE_AVATAR=false` |

### 실험 예시: B-roll 있는/없는 버전 비교

같은 대본으로 두 가지 버전을 만들어 비교합니다:

```bash
# 버전 A: B-roll 활성화
ENABLE_BROLL=true uv run video-automation pipeline script-to-video \
    --input projects/test-001/script.txt --project test-001-with-broll

# 버전 B: B-roll 비활성화
ENABLE_BROLL=false uv run video-automation pipeline script-to-video \
    --input projects/test-001/script.txt --project test-001-no-broll
```

> 두 결과물을 비교하면 내 콘텐츠 스타일에 B-roll이 어울리는지 판단할 수 있습니다. 환경변수 상세는 `09-config-customization.md` 참조.

---

## Part 7: 실전 시나리오 워크스루

### "3번 슬라이드가 마음에 안 들어요"

가장 흔한 수정 시나리오를 처음부터 끝까지 따라합니다.

**상황:** 파이프라인 실행 후 영상을 확인했는데, 3번 슬라이드의 디자인이 마음에 들지 않습니다.

#### 1단계: Claude Code에서 슬라이드 수정 요청

```
3번 슬라이드의 배경을 어두운 남색으로 바꾸고,
제목 텍스트를 더 크게 만들어줘.
프로젝트는 my-project야.
```

Claude Code가 `projects/my-project/slides/003.tsx` 파일을 수정합니다.

> **더 구체적인 수정 프롬프트 예시 (집에서 활용):**
>
> ```
> 3번 슬라이드 배경을 #0f1923으로, 제목을 96px Bold로 키우고, 포인트 텍스트에 #00d4ff 그라데이션 적용해줘. 프로젝트는 my-project.
> ```
>
> ```
> 5번 슬라이드를 3단 카드 레이아웃으로 바꿔줘. 각 카드에 아이콘+제목+설명, 카드 배경 #1a1a2e, radius 16px. 프로젝트는 my-project.
> ```
>
> ```
> 8번 슬라이드의 리스트 항목들이 0.3초 간격으로 stagger 등장하도록 애니메이션 추가해줘. 프로젝트는 my-project.
> ```

#### 2단계: 수정된 슬라이드만 재렌더링

```bash
uv run python scripts/regenerate_slides.py my-project 003
```

이 명령어는 3번 슬라이드의 TSX만 다시 MP4로 렌더링합니다. 나머지 슬라이드는 그대로 유지됩니다. 약 30초면 완료됩니다.

#### 3단계: 영상 재합성

```bash
uv run python scripts/recompose_video.py my-project
```

기존 오디오 + 수정된 슬라이드 MP4로 최종 영상을 다시 합성합니다. 약 1분이면 완료됩니다.

#### 4단계: 결과 확인

```bash
# Windows
start projects\my-project\output\final_video.mp4

# Mac
open projects/my-project/output/final_video.mp4
```

> **핵심:** 전체 파이프라인(5~15분) 대신 재렌더링 + 재합성(~2분)으로 수정이 완료됩니다. 이 패턴을 익히면 반복 수정이 훨씬 빨라집니다.

---

## 관련 문서

- `07-multi-format-strategy.md` -- 하나의 대본으로 영상 + 쇼츠 + 캐러셀을 동시에 만드는 멀티포맷 전략
- `09-config-customization.md` -- 환경변수, 프로필, 설정 커스터마이징 상세
