# 멀티포맷 콘텐츠 전략

> 대본 하나 → 영상 + 쇼츠 + 캐러셀 동시 제작

> 난이도: 중급 | 소요: 읽기 15분 + 실습 30분

---

## Part 1: 왜 멀티포맷인가?

대본 하나를 작성하는 노력으로 세 가지 콘텐츠를 동시에 만들 수 있습니다. 각 포맷은 서로 다른 알고리즘과 발견 경로를 가지므로, 동일한 메시지가 세 배의 도달 범위를 갖게 됩니다.

"오늘 뭘 올리지?"가 아니라 **"세 개 중 뭘 먼저 올리지?"**로 바뀝니다.

### 3가지 포맷 비교

| | 16:9 영상 | 9:16 쇼츠 | 4:5 캐러셀 |
|---|----------|----------|-----------|
| 플랫폼 | 유튜브 | 유튜브 쇼츠, 인스타 릴스 | 인스타그램 |
| 강점 | 깊이, SEO, 검색 유입 | 바이럴, 신규 유입 | 저장/공유, 브랜딩 |
| 길이 | 3~10분 | 15~60초 | 5~10장 카드 |
| 발견 방식 | 검색, 추천 알고리즘 | 숏폼 피드 | 탐색 탭, 해시태그 |
| 소비 패턴 | 의도적 시청 | 스크롤 중 발견 | 저장 후 재방문 |

> **핵심:** 영상은 "검색하는 사람"을, 쇼츠는 "스크롤하는 사람"을, 캐러셀은 "저장하는 사람"을 잡습니다. 세 포맷이 서로 다른 사용자층에 도달합니다.

---

## Part 2: 대본 설계 -- 멀티포맷을 염두에

처음부터 세 포맷을 염두에 두고 대본을 작성하면 변환 비용이 줄어듭니다.

### 작성 팁

| 규칙 | 이유 |
|------|------|
| 짧은 문단 (50~80자) | 쇼츠 자막에도 잘 맞고, 캐러셀 카드에도 적합 |
| 핵심 포인트 3~5개 명확히 | 각 포인트가 캐러셀 카드 1장으로 직결 |
| 인트로 첫 문장에 훅 | 쇼츠 첫 1초 훅으로 그대로 재활용 가능 |
| 아웃트로 CTA를 포맷별로 분리 | 영상: "구독", 쇼츠: "팔로우", 캐러셀: "저장" |

### Claude Code로 멀티포맷 대본 요청

```
"AI 코딩 도구 비교"를 주제로 유튜브 3분짜리 대본을 작성해줘.
projects/multi-001/script.txt에 저장해줘.

조건:
- 문단은 8~10개, 빈 줄로 구분
- 문단당 50~80자
- 핵심 포인트 5개를 명확하게 구분
- 인트로 첫 문장을 훅으로 작성
```

> **팁:** 핵심 포인트를 명확히 분리해두면 캐러셀 카드 변환이 자연스럽습니다. `12-content-strategy.md`의 대본 작성 팁도 참조하세요.

---

## Part 3: 포맷별 제작 차이

같은 파이프라인 시스템이지만, 포맷에 따라 내부 처리가 다릅니다:

| 항목 | 영상 (16:9) | 쇼츠 (9:16) | 캐러셀 (4:5) |
|------|:----------:|:----------:|:-----------:|
| 명령어 | `/generate-video` | `/generate-shorts` | `/generate-carousel` |
| 파이프라인 | `script-to-video` | `script-to-shorts` | `script-to-carousel` |
| API 모드 | ✅ | ✅ | ✅ |
| 슬라이드 | TSX 자동 생성 (가로) | TSX 자동 생성 (세로) | TSX 자동 생성 (4:5) |
| TTS | 전체 문단 단위 | 전체 문단 단위 | 없음 |
| 자막 | SRT 기반 (글자수 비례) | 단어별 하이라이트 | 텍스트가 카드 내용 |
| Whisper | 미사용 | 워드 타임스탬프 사용 | 미사용 |
| B-roll | 배경 이미지 (API 모드: ❌) | 배경 이미지 (API 모드: ❌) | 선택적 |
| 아바타 | Ditto (API 모드: ❌) | ❌ | ❌ |
| 최종 출력 | `final_video.mp4` | `shorts_slides/output/final_shorts.mp4` | `card_*.png` |

> 쇼츠는 Whisper를 사용해 단어별 타이밍을 추출하므로, 영상보다 한 단계 더 정밀한 자막 처리가 이루어집니다.

---

## Part 4: 최적 제작 순서

세 포맷을 효율적으로 생산하는 순서입니다. TTS 오디오가 영상과 쇼츠에서 재사용되므로 순서가 중요합니다.

```
[1] 대본 작성 (1회)
    ↓
[2] /generate-video → 슬라이드 + B-roll + TTS 사전 생성
    ↓
[3] 파이프라인: script-to-video 실행 (16:9 영상)
    ↓
[4] /generate-shorts → 쇼츠용 슬라이드 생성
    ↓
[5] 파이프라인: script-to-shorts 실행 (9:16 쇼츠)
    ↓
[6] /generate-carousel → 캐러셀 카드 생성
    ↓
[7] regenerate_carousel.py 실행 (4:5 카드뉴스)
```

### 전체 명령어

**Step 1: 대본 작성** (이미 있으면 건너뛰기)

```
"AI 코딩 도구 비교"를 주제로 대본을 작성해줘.
projects/multi-001/script.txt에 저장해줘.
```

**Step 2-3: 영상 생성**

```
/generate-video multi-001
```

```bash
uv run video-automation pipeline script-to-video \
    --input projects/multi-001/script.txt --project multi-001
```

**Step 4-5: 쇼츠 생성**

```
/generate-shorts multi-001
```

```bash
# script-to-shorts는 기본 프로필이 shorts이므로 CONFIG_PROFILE 불필요
uv run video-automation pipeline script-to-shorts \
    --input projects/multi-001/script.txt --project multi-001
```

**Step 6-7: 캐러셀 생성**

```
/generate-carousel multi-001
```

```bash
uv run python scripts/regenerate_carousel.py multi-001
```

> **왜 이 순서인가?** Step 3에서 생성된 TTS 오디오(`audio/`)가 Step 5에서 재사용됩니다. 영상을 먼저 만들면 쇼츠에서 TTS를 다시 생성하지 않아도 되므로 시간과 API 크레딧을 절약합니다.

---

## Part 5: 플랫폼별 업로드 전략

세 콘텐츠를 **같은 날 동시에 올리면 서로 cannibalize**(잠식)합니다. 날짜를 분산시키세요.

### 추천 업로드 일정

| 날짜 | 업로드 콘텐츠 | 이유 |
|------|-------------|------|
| Day 1 (월) | 유튜브 본편 (16:9) | 검색 인덱싱 시간 확보 |
| Day 2 (화) | 유튜브 쇼츠 + 인스타 릴스 (9:16) | 본편에서 유입된 관심 활용 |
| Day 3 (수) | 인스타 캐러셀 (4:5) | 릴스 시청자를 프로필로 유도 |

### 플랫폼별 최적화 팁

**유튜브 본편:**
- 제목에 검색 키워드 포함 (SEO 중심)
- 설명란 첫 2줄에 핵심 내용 요약
- 챕터 타임스탬프 추가 (시청 지속 시간 향상)

**유튜브 쇼츠 / 인스타 릴스:**
- 첫 1초에 강한 훅 (텍스트 + 음성 동시)
- 해시태그 3~5개 (과하면 스팸 판정)
- 영상 끝에 "더 자세한 내용은 본편에서" CTA

**인스타 캐러셀:**
- 첫 번째 카드(표지)가 탐색 탭 노출의 핵심
- 마지막 카드에 "저장하면 나중에 다시 볼 수 있어요" CTA
- 캡션에 핵심 내용 텍스트 요약 (검색 노출용)

> **핵심:** 각 플랫폼의 알고리즘이 선호하는 형식이 다릅니다. 같은 내용이라도 플랫폼에 맞게 CTA와 형식을 조정하세요.

---

## Part 6: 캐러셀 카피라이팅 (프리프로덕션)

`/generate-carousel` 전에 `/carousel-copywriting`을 먼저 실행하면 카드별 텍스트 품질이 올라갑니다.

### 워크플로우

```
[1] /carousel-copywriting multi-001
    ↓ 훅 엔지니어링 → 카드별 카피 → 8가지 메트릭 자가평가
[2] 카피 검토 및 수정
    ↓
[3] /generate-carousel multi-001
    ↓ 확정된 카피 기반으로 TSX 생성
[4] uv run python scripts/regenerate_carousel.py multi-001
```

### Claude Code 프롬프트

```
/carousel-copywriting multi-001
```

이 명령어가 수행하는 작업:
- 대본에서 핵심 포인트 추출
- 카드별 훅과 본문 텍스트 기획
- 8가지 메트릭(가독성, 임팩트, CTA 등)으로 자가평가
- 점수가 낮은 항목 자동 개선

> **팁:** 캐러셀 카피라이팅은 선택 사항이지만, 텍스트 품질이 캐러셀의 저장률에 직접 영향을 줍니다. 중요한 콘텐츠라면 이 단계를 건너뛰지 마세요.

---

## Part 7: 실습 -- 3종 세트 만들기

하나의 대본으로 영상 + 쇼츠 + 캐러셀을 직접 만들어 봅니다.

### 준비

기존 프로젝트의 대본을 활용하거나, 자신의 도메인에 맞는 대본을 새로 작성합니다:

```
"개발자가 아닌 사람도 AI로 영상을 만들 수 있다"는 주제로
3분짜리 대본을 작성해줘.
projects/practice-multi/script.txt에 저장.
문단 8개, 핵심 포인트 4개 명확히 구분.
```

**도메인별 멀티포맷 대본 예시 (골라서 사용하세요):**

```
"직장인 퇴근 후 30분 자기계발 루틴 4가지"를 주제로
3분짜리 대본을 작성해줘. 자기계발/생산성 채널용.
핵심 포인트 4개를 캐러셀 카드로도 쓸 수 있게 명확히 분리.
projects/practice-multi/script.txt에 저장.
```

```
"초보도 따라하는 AI 이미지 생성 3단계"를 주제로
3분짜리 대본을 작성해줘. 디자인/크리에이터 채널용.
각 단계를 쇼츠 1개씩으로도 쪼갤 수 있게 독립적으로 작성.
projects/practice-multi/script.txt에 저장.
```

```
"부동산 초보가 반드시 알아야 할 용어 5가지"를 주제로
3분짜리 대본을 작성해줘. 재테크/부동산 채널용.
용어 5개가 캐러셀 카드 1장씩으로 직결되도록 문단 분리.
projects/practice-multi/script.txt에 저장.
```

### 실습 순서

**1단계: 영상 제작 (~10분)**

```
/generate-video practice-multi
```

```bash
uv run video-automation pipeline script-to-video \
    --input projects/practice-multi/script.txt --project practice-multi
```

결과 확인:
```bash
# Windows
start projects\practice-multi\output\final_video.mp4
```

**2단계: 쇼츠 제작 (~8분)**

```
/generate-shorts practice-multi
```

```bash
# script-to-shorts는 기본 프로필이 shorts이므로 CONFIG_PROFILE 불필요
uv run video-automation pipeline script-to-shorts \
    --input projects/practice-multi/script.txt --project practice-multi
```

결과 확인:
```bash
# Windows
start projects\practice-multi\shorts_slides\output\final_shorts.mp4
```

**3단계: 캐러셀 제작 (~5분)**

```
/carousel-copywriting practice-multi
```

```
/generate-carousel practice-multi
```

```bash
uv run python scripts/regenerate_carousel.py practice-multi
```

### 결과물 비교 체크리스트

| 확인 항목 | 영상 | 쇼츠 | 캐러셀 |
|----------|:----:|:----:|:-----:|
| 파일 생성 여부 | `output/final_video.mp4` | `output/final_shorts.mp4` | `carousel/card_*.png` |
| 가로/세로 비율 | 16:9 | 9:16 | 4:5 |
| 음성 포함 여부 | O | O | X |
| 자막 스타일 | 하단 SRT | 단어별 하이라이트 | 카드 내 텍스트 |

세 결과물을 나란히 놓고 비교하면, 같은 대본이 각 포맷에서 어떻게 다르게 표현되는지 확인할 수 있습니다.

> **핵심:** 대본 1회 작성 → 콘텐츠 3개 생산. 이 패턴이 익숙해지면 주간 콘텐츠 생산량이 3배로 늘어납니다. 부분 수정이 필요하면 `08-advanced-workflows.md`의 유틸리티 스크립트를 활용하세요.
