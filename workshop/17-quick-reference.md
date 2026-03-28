# 빠른 참조 카드 (Quick Reference)

> 실습 중 필요할 때마다 펼쳐보는 치트시트

---

## 1. Commands 치트시트

| 명령어 | 용도 | API 모드 | 예시 |
|--------|------|:--------:|------|
| `/generate-video <project>` | 16:9 유튜브 영상 생성 | ✅ | `/generate-video my-video` |
| `/generate-shorts <project>` | 9:16 쇼츠 생성 | ✅ | `/generate-shorts my-shorts` |
| `/generate-carousel <project>` | 4:5 카드뉴스 생성 | ✅ | `/generate-carousel my-card` |
| `/generate-script <project>` | 대본 생성 | ✅ | `/generate-script my-video` |
| `/carousel-copywriting <project>` | 캐러셀 카드별 카피라이팅 | ✅ | `/carousel-copywriting my-card` |
| `/detect-releases` | CC 릴리즈 감지 (쇼츠 소재) | ✅ | `/detect-releases` |
| `/voice-clone-setup` | 보이스 프로필 설정 | ✅ | `/voice-clone-setup` |
| `/skill-creator` | 나만의 스킬 만들기 (Claude Code 내장 기능) | ✅ | `/skill-creator` |
| `/spec-writer` | 기능 명세 자동 생성 (스킬: `.claude/skills/spec-writer/`) | ✅ | `/spec-writer` |

> **API 모드 (`CONFIG_PROFILE=api`)**: 모든 커맨드 실행 가능. 단, B-roll 이미지와 아바타(Ditto)는 비활성화.

---

## 2. CLI 명령어

### 영상 파이프라인 실행

```bash
# 16:9 영상 (기본)
uv run video-automation pipeline script-to-video \
    --input projects/<project>/script.txt --project <project>

# B-roll 없이 빠른 테스트
uv run video-automation pipeline script-to-video \
    --input projects/<project>/script.txt --project <project> --no-broll

# 9:16 쇼츠
uv run video-automation pipeline script-to-shorts \
    --input projects/<project>/script.txt --project <project>

# 환경 확인
uv run video-automation info
```

### 유틸리티 스크립트

```bash
# 슬라이드만 재렌더링
uv run python scripts/regenerate_slides.py <project>

# B-roll만 재생성
uv run python scripts/regenerate_broll.py <project>

# 영상 재합성 (슬라이드 수정 후)
uv run python scripts/recompose_video.py <project>

# Step 3(렌더링)부터 재실행
uv run python scripts/continue_pipeline.py <project>

# 카드뉴스 렌더링
uv run python scripts/regenerate_carousel.py <project>
```

---

## 3. 환경변수 (.env)

| 변수 | 용도 | API 모드 필수 | 비고 |
|------|------|:------------:|------|
| `ANTHROPIC_API_KEY` | Claude API (슬라이드/분석) | ✅ | Claude Code 실행에 필요 |
| `OPENAI_API_KEY` | Whisper STT, GPT Vision | ✅ | 자막 생성 등 |
| `ELEVENLABS_API_KEY` | TTS 음성 합성 | ✅ | API/base 모두 사용 |
| `GOOGLE_API_KEY` | Gemini 이미지 생성 (B-roll) | 선택 | API 모드에서 B-roll 비활성화 |
| `SERPER_API_KEY` | 구글 이미지 검색 | 선택 | B-roll 검색용 |
| `PEXELS_API_KEY` | 무료 스톡 이미지 | 선택 | B-roll 검색용 |

### 실행 시 오버라이드

```bash
# Mac/Linux
ENABLE_BROLL=false uv run video-automation ...        # B-roll 비활성화
uv run video-automation ...         # API 모드

# Windows PowerShell
$env:ENABLE_BROLL='false'
$env:CONFIG_PROFILE='api'
uv run video-automation ...
```

---

## 4. 프로젝트 디렉토리 구조

```
projects/<project>/
├── script.txt              ← 대본 (여러분이 작성)
├── paragraphs/             ← 문단 분리 (시스템 자동)
│   ├── 001.txt
│   ├── 002.txt
│   └── ...
├── audio/                  ← TTS 음성 (ElevenLabs)
│   ├── 001.wav
│   └── ...
├── slides/                 ← 슬라이드 (Claude Code → Remotion)
│   ├── 001.tsx             ← 디자인 코드
│   ├── 001.mp4             ← 렌더링된 영상 클립
│   └── ...
├── broll/                  ← 배경 이미지 (Gemini)
│   ├── prompts.json        ← 이미지 생성 프롬프트
│   └── generated/
│       ├── broll_001.png
│       └── ...
├── output/                 ← 최종 출력
│   ├── video_raw.mp4
│   ├── video_with_subtitles.mp4
│   ├── corrected_subtitles.srt
│   └── final_video.mp4     ← 최종 영상
├── shorts_slides/          ← 쇼츠 슬라이드 (9:16)
├── shorts/                 ← 쇼츠 출력
└── carousel/               ← 카드뉴스 (4:5)
    ├── card_001.tsx
    └── card_001.png
```

---

## 5. 자주 쓰는 Claude Code 프롬프트

| 상황 | 프롬프트 |
|------|---------|
| 대본 생성 | `"AI 자동화" 주제로 3분짜리 유튜브 대본 써줘` |
| 대본 수정 | `3번째 문단 줄여줘` |
| 설정 확인 | `현재 TTS 설정 보여줘` |
| 슬라이드 수정 | `5번 슬라이드 배경색 파란색으로 바꿔줘` |
| 전체 스타일 | `모든 슬라이드를 어두운 테마로 통일해줘` |
| 오류 해결 | `이 에러 해결해줘: [에러 메시지]` |
| 파일 확인 | `output 폴더에 뭐 있어?` |
| 발음 사전 | `발음 사전에 "Anthropic=앤트로픽" 추가해줘` |

---

## 6. Skill 자동 매핑

| 이렇게 말하면 | 자동 로드되는 Skill |
|-------------|-------------------|
| "슬라이드 수정해줘" | slide-generation |
| "B-roll 프롬프트 바꿔줘" | broll |
| "발음 사전 보강해줘" | tts |
| "설정 변경해줘" | config |
| "캐러셀 카피 기획해줘" | carousel-copywriting |
| "스킬 최적화해줘" | autoresearch |
| "기능 구현해줘" | spec-writer |

---

## 7. 설정 프로필

| 프로필 | 실행법 | TTS | B-roll | 아바타 | GPU 필요 |
|--------|--------|-----|--------|--------|:--------:|
| `api` | `CONFIG_PROFILE=api` | ElevenLabs | **비활성화** | **비활성화** | ❌ |
| `base` | (기본값) | ElevenLabs (API) | Flux Kontext + LoRA | Ditto | ✅ |

> **API 모드**에서는 B-roll 이미지 생성과 아바타(Ditto)가 완전히 비활성화됩니다. GPU 없이 TTS + 슬라이드 + 자막만으로 영상을 생성합니다. `base` 프로필은 B-roll과 아바타에 로컬 GPU가 필요하며, 로컬 Qwen TTS도 설정 변경으로 사용 가능합니다.

---

## 8. script.txt 작성 규칙

```
첫 번째 문단은 인트로입니다. 시청자의 관심을 끄는 문장으로 시작합니다.

두 번째 문단부터 본문입니다. 한 문단이 하나의 슬라이드가 됩니다.

문단 사이에 빈 줄을 꼭 넣어주세요. 이것이 문단 구분 기준입니다.

마지막 문단은 아웃트로입니다. 내용을 정리하고 구독을 유도합니다.
```

| 영상 길이 | 문단 수 | 문단당 글자 |
|----------|---------|-----------|
| 3분 | 8~12개 | 50~100자 |
| 5분 | 15~20개 | 50~100자 |
| 10분 | 25~35개 | 50~100자 |

---

## 9. 출력 파일 체인 (script-to-video)

```
video_raw.mp4          ← 슬라이드 + 음성 합성
    ↓
video_with_subtitles.mp4  ← 자막 추가
    ↓
final_video.mp4        ← 최종 영상
```

> API 모드에서는 아바타가 비활성화되어 `video_with_avatar.mp4` 단계를 건너뜁니다.
