# Claude Code Skills로 카드뉴스 자동 생성 시스템 구축하기

> 라이브 워크숍 가이드 | 2026-03-19
> 대상: Claude Code 설치 완료된 입문자

---

## Part 1: 오늘 만들 것

### 1.1 완성 결과

대본(텍스트)을 넣으면 인스타그램 카드뉴스 이미지가 자동으로 나오는 시스템을 만듭니다.

```
script.txt (대본)
    ↓ Claude Code에 프롬프트 입력
card_001.tsx ~ card_010.tsx (디자인 코드)
    ↓ 렌더링 명령어 실행
card_001.png ~ card_010.png (완성 이미지, 1080x1350)
```

여러분이 하는 일은 **2가지**뿐입니다:
1. Claude Code에 "카드뉴스 만들어줘"라고 프롬프트 입력
2. 렌더링 명령어 복붙

### 1.2 핵심 아이디어

Claude Code에 **Skill(스킬)**을 하나 만들어두면, 이후에는 한 줄 명령으로 카드뉴스를 반복 생성할 수 있습니다.

```
/generate-carousel my-project
```

이 한 줄 뒤에서 일어나는 일:

1. Claude Code가 대본을 읽음
2. 스킬 파일에 적힌 규칙대로 카드별 디자인 코드(TSX)를 생성
3. Remotion(렌더링 도구)이 코드를 이미지로 변환

> **스킬이란?** Claude Code에게 "이런 상황에서는 이렇게 행동해"라고 미리 적어둔 **지시서**입니다. 매번 긴 프롬프트를 쓸 필요 없이, `/스킬이름`으로 호출하면 됩니다.

---

## Part 2: Claude Code Skills & Commands

### 2.1 Commands란?

`.claude/commands/` 폴더에 마크다운 파일을 넣으면, Claude Code에서 **슬래시 명령어**로 호출할 수 있습니다.

```
.claude/
└── commands/
    └── generate-carousel.md    ← 이 파일이 곧 /generate-carousel 명령어
```

파일 이름이 곧 명령어 이름입니다:
- `generate-carousel.md` → `/generate-carousel`
- `review-code.md` → `/review-code`
- `translate-docs.md` → `/translate-docs`

### 2.2 Command 파일의 구조

```markdown
---
name: generate-carousel
description: "인스타 카드뉴스 생성기"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "<프로젝트명>"
---

# 여기부터가 Claude Code에게 주는 지시문

Step 1: projects/$ARGUMENTS/script.txt를 읽어라
Step 2: 콘텐츠 유형을 분류해라
Step 3: 카드별 레이아웃을 계획해라
Step 4: TSX 파일을 작성해라
...
```

- **상단 (frontmatter)**: 명령어 이름, 설명, 사용할 도구 권한
- **본문**: Claude Code가 따라야 할 단계별 지시. 프롬프트 엔지니어링의 핵심
- **`$ARGUMENTS`**: 명령어 뒤에 적는 인자. `/generate-carousel my-project`에서 `my-project`

### 2.3 왜 Command로 만드는가?

**매번 이렇게 쓰는 대신:**

```
projects/my-project/script.txt를 읽고 인스타그램 카드뉴스를 만들어줘.
8~10장, 다크 테마, 커버는 임팩트 있게, 마지막은 CTA,
각 카드는 card_001.tsx 형식으로 저장하고, 같은 레이아웃
2연속 금지, SVG 아이콘 필수, ... (이하 50줄)
```

**한 줄로 끝:**

```
/generate-carousel my-project
```

50줄짜리 프롬프트가 Command 파일 안에 저장되어 있으니, 매번 다시 쓸 필요가 없습니다. 팀원에게 공유하면 누구나 같은 품질로 카드뉴스를 만들 수 있습니다.

### 2.4 참조 문서의 역할

Command 파일 안에서 "이 문서를 참고해라"고 지시할 수 있습니다:

```markdown
# Command 파일 안에서:
Step 4: TSX 파일을 작성해라

아래 문서를 먼저 읽고 규칙을 따를 것:
- remotion/docs/carousel-patterns.md (23종 레이아웃 패턴)
- remotion/docs/tsx-contract.md (코드 작성 규약)
```

이 참조 문서들이 카드 품질을 결정합니다. 레이아웃 패턴이 풍부할수록, 규약이 정교할수록 결과물이 좋아집니다.

---

## Part 3: 시스템 구성 요소

빈 폴더에서 시작합니다. 이 시스템은 **3가지 구성 요소**로 이루어져 있습니다.

### 3.1 전체 구조

```
carousel-workshop/                 ← 워크숍 루트 폴더
│
├── .claude/commands/
│   └── generate-carousel.md       ← [A] Command: 카드 생성 지시서
│
├── remotion/docs/
│   ├── carousel-patterns.md       ← [B] 참조 문서: 레이아웃 패턴
│   ├── carousel-patterns-layouts.md
│   └── tsx-contract.md            ← [B] 참조 문서: 코드 규약
│
├── remotion/                      ← [C] 렌더링 엔진 (Remotion 프로젝트)
│   ├── package.json
│   ├── tsconfig.json
│   ├── remotion.config.ts
│   ├── src/
│   │   ├── Root.tsx               ← 렌더링 진입점
│   │   ├── carousel/
│   │   │   ├── FreeformCard.tsx   ← AI 코드가 여기에 들어감
│   │   │   └── types.ts          ← 카드 규격 (1080x1350)
│   │   └── design/
│   │       ├── theme.ts          ← 색상, 폰트, 테마
│   │       └── fonts.ts          ← 폰트 로딩
│   └── public/fonts/              ← 폰트 7종 (Pretendard 6종 + NanumGaramYeonkkot 1종)
│
├── render.bat                     ← [D] 렌더링 실행 스크립트
│
└── projects/                      ← 작업 폴더
    └── my-carousel/
        ├── script.txt             ← 대본
        └── carousel/              ← 생성된 .tsx + .png
```

### 3.2 각 구성 요소의 역할

#### [A] Command 파일 — Claude Code 지시서

```
.claude/commands/generate-carousel.md
```

**이 파일이 시스템의 두뇌입니다.** Claude Code가 카드뉴스를 만들 때 따르는 모든 규칙이 여기에 있습니다:

- 대본을 어떻게 분석할지 (콘텐츠 유형 분류)
- 커버 제목을 어떻게 쓸지 (10자 이내, 스크롤 멈추는 전략)
- 카드 배치 규칙 (같은 레이아웃 2연속 금지, 감정 곡선)
- 코드를 어떤 형식으로 생성할지 (TSX 작성 규약)

#### [B] 참조 문서 — 패턴 라이브러리

```
remotion/docs/carousel-patterns.md         ← 23종 레이아웃 인덱스
remotion/docs/carousel-patterns-layouts.md ← 기본 9종 상세 패턴
remotion/docs/tsx-contract.md     ← 코드 작성 규칙
```

Claude Code가 카드를 만들 때 참고하는 **디자인 패턴 책**입니다. 커버, 리스트, 비교, 차트, 타임라인 등 23가지 레이아웃의 구체적인 코드 패턴이 들어 있습니다.

#### [C] 렌더링 엔진 — Remotion 프로젝트

```
remotion/
```

디자인 코드(TSX)를 실제 이미지(PNG)로 변환하는 도구입니다.

> Remotion = **디자인 설계도(코드)를 사진(이미지)으로 찍어주는 카메라**

내부적으로 보이지 않는 브라우저(headless Chrome)를 띄워서, 코드를 화면에 그린 후 스크린샷을 찍습니다. 여러분이 Remotion을 직접 다룰 일은 없습니다.

#### [D] 렌더링 실행 스크립트 — render.bat

TSX 파일을 하나씩 꺼내서 Remotion으로 렌더링하는 자동화 스크립트입니다. 카드 10장을 자동으로 연속 처리합니다.

### 3.3 구성 요소 관계도

```
여러분이 하는 일          시스템이 하는 일
─────────────          ─────────────────────────────────

1. 대본 작성    ──→    [A] Command가 Claude Code에 규칙 전달
   (script.txt)              ↓
                       [B] 참조 문서에서 레이아웃 패턴 선택
                              ↓
2. 프롬프트 입력 ──→   Claude Code가 card_001.tsx ~ card_010.tsx 생성
   (/generate-               ↓
    carousel)         [C] Remotion이 TSX를 PNG로 변환
                              ↓
3. 렌더링 실행  ──→   [D] render.bat이 카드 10장 자동 처리
   (render.bat)              ↓
                       card_001.png ~ card_010.png 완성!
```

---

## Part 4: 환경 준비

### 4.1 사전 조건

이미 설치되어 있어야 하는 것:

| 도구 | 확인 방법 |
|------|-----------|
| **Claude Code** | `claude --version` |
| **Node.js** (v18+) | `node --version` |

### 4.2 스타터 킷 설치

강사가 제공하는 스타터 킷(zip)을 바탕화면에 압축 해제한 후:

```powershell
# 1. 폴더로 이동
cd C:\Users\사용자이름\Desktop\carousel-workshop

# 2. Remotion 의존성 설치 (1~2분 소요)
cd remotion
npm install
cd ..
```

### 4.3 설치 확인

```powershell
# Remotion 정상 동작 확인 (버전 번호가 나오면 OK)
cd remotion && npx remotion --version && cd ..
```

### 4.4 스타터 킷에 들어있는 것

| 폴더/파일 | 구성 요소 | 설명 |
|-----------|----------|------|
| `.claude/commands/generate-carousel.md` | [A] Command | 카드 생성 지시서 |
| `remotion/docs/carousel-patterns*.md` | [B] 참조 문서 | 23종 레이아웃 패턴 |
| `remotion/docs/tsx-contract.md` | [B] 참조 문서 | TSX 코드 규약 |
| `remotion/` | [C] 렌더링 엔진 | Remotion + React 프로젝트 |
| `remotion/public/fonts/` | [C] 폰트 | 7종 (Pretendard 6종 + NanumGaramYeonkkot 1종) |
| `render.bat` | [D] 실행 스크립트 | 렌더링 자동화 |
| `projects/` | 작업 폴더 | 비어 있음 (여기서 실습) |

---

## Part 5: 핸즈온 실습

### Step 1 — 대본 준비

프로젝트 폴더를 만들고 대본을 작성합니다.

```powershell
mkdir projects\my-carousel\carousel
```

`projects/my-carousel/script.txt`를 만들고 내용을 작성합니다. **빈 줄로 문단을 구분**하세요.

```
AI 자동화로 월 500만원 벌기

많은 사람들이 AI를 "신기한 장난감"으로만 생각합니다.
하지만 이미 AI로 수익을 만드는 사람들이 있습니다.

핵심은 반복 작업을 AI에게 맡기는 것입니다.
콘텐츠 제작, 데이터 분석, 고객 응대 — 모두 자동화 가능합니다.

실제 사례: 1인 쇼핑몰 운영자 A씨.
상품 설명 작성에 하루 4시간 → AI 도입 후 30분.

시작하는 데 코딩 지식은 필요 없습니다.
오늘 소개하는 3가지 도구면 충분합니다.

지금 시작하세요. 6개월 후의 나에게 감사할 겁니다.
```

> **생성 파일**: `projects/my-carousel/script.txt`

### Step 2 — Command로 카드뉴스 생성

`carousel-workshop/` 폴더에서 Claude Code를 실행합니다.

#### 방법 A: Command 호출 (추천)

```
/generate-carousel my-carousel
```

이 한 줄이면 Claude Code가:
1. `projects/my-carousel/script.txt`를 읽고
2. Command 파일의 규칙에 따라 콘텐츠 유형 분석
3. `remotion/docs/carousel-patterns*.md`를 참고하여 레이아웃 결정
4. `card_001.tsx` ~ `card_008.tsx` 생성

#### 방법 B: 직접 프롬프트 (Command 없이)

Command 파일 없이도 직접 프롬프트로 지시할 수 있습니다. 다만 매번 상세하게 적어야 합니다.

```
projects/my-carousel/script.txt 를 읽고 인스타그램 카드뉴스를 만들어줘.

조건:
- 8~10장 카드
- 다크 테마 (어두운 배경)
- 커버는 스크롤 멈추게 하는 임팩트 제목
- 마지막은 CTA (팔로우 유도)
- 각 카드는 projects/my-carousel/carousel/card_001.tsx, card_002.tsx, ... 로 저장

참고할 패턴 문서: remotion/docs/carousel-patterns.md
TSX 규약: remotion/docs/tsx-contract.md
```

> **Command의 가치**: 방법 B의 긴 프롬프트를 매번 쓸 필요 없이, Command 파일에 한 번 저장해두면 `/generate-carousel`로 반복 호출할 수 있습니다.

> **생성 파일**: `projects/my-carousel/carousel/card_001.tsx` ~ `card_008.tsx`

### Step 3 — 수정 요청

TSX가 생성되면 Claude Code에 자연어로 수정을 요청합니다. 코드를 직접 볼 필요 없습니다.

```
card_003.tsx 카드가 텍스트가 너무 많아. 핵심만 남기고 아이콘 그리드로 바꿔줘.
```

```
커버 카드 제목을 "AI 자동화의 비밀"에서 "월 500만원 자동화"로 바꿔줘.
```

```
5번 카드와 6번 카드 사이에 비교 카드(Before/After) 하나 추가해줘.
```

```
전체 카드를 밝은 테마로 바꿔줘. 화이트 배경에 미니멀한 느낌.
```

수정 요청은 **몇 번이든 반복 가능**합니다. 대화하듯 수정하세요.

### Step 4 — PNG 렌더링

TSX 파일이 완성되면 이미지로 변환합니다.

```powershell
# 전체 카드 렌더링
render.bat my-carousel

# 특정 카드만 렌더링 (수정한 카드만)
render.bat my-carousel 3 7
```

> **생성 파일**: `projects/my-carousel/carousel/card_001.png` ~ `card_008.png`
> 카드 1장에 약 3~5초, 10장이면 약 30~50초 소요.

### Step 5 — 결과 확인 & 재수정

PNG 이미지를 열어보고, 마음에 안 드는 부분을 Claude Code에 다시 요청합니다.

```
card_007.tsx 글자가 너무 작아. 폰트 크기를 1.5배로 키워줘.
```

```
3번 카드 배경에 보라색-파란색 그라데이션 추가해줘.
```

수정 후 해당 카드만 다시 렌더링:

```powershell
render.bat my-carousel 3 7
```

**TSX 수정 → 렌더링 → 확인**을 만족할 때까지 반복합니다.

---

## Part 6: 커스터마이징 프롬프트 모음

Claude Code에 그대로 입력하면 됩니다.

### 색상/테마

```
전체 카드를 다크 테마로 바꿔줘. 배경은 #0B0C0E, 포인트 색상은 보라색(#7C7FD9).
```

```
전체 카드를 quiet-luxury 테마로 바꿔줘. 화이트 배경에 미니멀한 느낌.
```

```
포인트 색상을 초록색(#3CB4B4)으로 바꿔줘. 나머지는 그대로.
```

### 레이아웃

```
4번 카드를 번호 리스트 레이아웃으로 바꿔줘. 3가지 항목을 순서대로 보여주는 형태.
```

```
5번 카드를 Before/After 비교 레이아웃으로 바꿔줘.
```

```
6번 카드에 막대 차트 추가해줘. 수동 작업 4시간 vs AI 작업 30분 비교.
```

### 개별 카드 수정

```
card_002.tsx에서 "많은 사람들이"를 "아직 90%가"로 바꿔줘.
```

```
card_005.tsx를 아이콘 그리드로 바꿔줘. 4개 아이콘+라벨 형태.
```

```
card_001.tsx 커버 제목에 글로우 효과 추가해줘.
```

### 카드 추가/삭제/순서 변경

```
8번과 9번 사이에 "고객 후기" 카드를 추가해줘.
```

```
card_004.tsx가 중복 내용이야. 삭제해줘.
```

```
6번과 7번 카드 순서를 바꿔줘.
```

---

## Part 7: 심화 — 직접 구축하기

> 스타터 킷 없이 빈 폴더에서 이 시스템을 직접 만들고 싶은 분들을 위한 가이드입니다.

### 7.1 시스템의 핵심 원리

Claude Code가 생성하는 TSX(디자인 코드)는 React 컴포넌트입니다. Remotion은 이 React 컴포넌트를 headless 브라우저에서 렌더링하여 스크린샷을 찍는 방식으로 이미지를 만듭니다.

```
TSX 코드 (텍스트 배치, 색상, 아이콘 정보)
    ↓ Remotion
headless Chrome이 1080x1350 화면에 렌더링
    ↓
스크린샷 → PNG 저장
```

한글 텍스트가 항상 선명하고, 수정도 텍스트만 바꾸면 되니 AI 이미지 생성보다 안정적입니다.

### 7.2 필요한 파일 목록

#### [A] Command 파일 (1개)

```
.claude/commands/generate-carousel.md
```

Command 파일의 핵심 내용:
- frontmatter: `name`, `description`, `allowed-tools`, `argument-hint`
- Step 1: 대본 읽기 + 기존 파일 확인
- Step 2: 콘텐츠 유형 분류 + 테마 선택 + 커버 훅 전략
- Step 3: 카드별 레이아웃 계획 (감정 곡선, 징검다리 전략)
- Step 4: 참조 문서 읽기 + TSX 코드 작성
- Step 5: 검증 (TypeScript 체크)
- Step 6: 렌더링 안내

#### [B] 참조 문서 (12개)

| 파일 | 내용 |
|------|------|
| `remotion/docs/carousel-patterns.md` | 레이아웃 패턴 인덱스 + 공통 규칙 |
| `remotion/docs/carousel-patterns-layouts.md` | 기본 9종 패턴 코드 (커버, 리스트, 비교 등) |
| `remotion/docs/carousel-patterns-layouts-extended.md` | 확장 14종 패턴 코드 (대시보드, 타임라인 등) |
| `remotion/docs/carousel-patterns-fills.md` | 배경/장식 패턴 |
| `remotion/docs/carousel-patterns-icons.md` | SVG 아이콘 라이브러리 |
| `remotion/docs/carousel-tsx-contract.md` | 캐러셀 전용 TSX 규약 |
| `remotion/docs/carousel-patterns-ql.md` | Quiet-Luxury 테마 패턴 |
| `remotion/docs/carousel-copywriting-rubric.md` | 카피라이팅 평가 루브릭 |
| `remotion/docs/carousel-editorial-strategy.md` | 에디토리얼 전략 |
| `remotion/docs/carousel-ai-backgrounds.md` | AI 배경 가이드 |
| `remotion/docs/carousel-visual-review.md` | 비주얼 리뷰 체크리스트 |
| `remotion/docs/tsx-contract.md` | TSX 공통 규칙 |

이 문서들의 품질이 곧 카드 품질입니다. 패턴이 구체적이고 예시 코드가 많을수록, Claude Code가 더 좋은 카드를 만듭니다.

#### [C] Remotion 프로젝트 (최소 파일)

```
remotion/
├── package.json              # remotion v4 + react 19 + typescript
├── tsconfig.json             # strict, ES2022, react-jsx
├── remotion.config.ts        # Chrome GL, 덮어쓰기 허용, 타임아웃 30초
├── src/
│   ├── Root.tsx              # FreeformCard 컴포지션 등록 (1080x1350, 1프레임)
│   ├── carousel/
│   │   ├── FreeformCard.tsx  # Claude Code가 덮어쓸 진입점 컴포넌트
│   │   └── types.ts         # FreeformCardProps, CAROUSEL_LAYOUT(1080x1350)
│   └── design/
│       ├── theme.ts          # 색상 토큰, 폰트 크기, 테마 프리셋(dark/quiet-luxury)
│       └── fonts.ts          # Pretendard FontFace 로딩 + useFonts() 훅
└── public/fonts/             # 폰트 7종 (Pretendard 6종 .otf + NanumGaramYeonkkot 1종 .ttf)
```

핵심 파일 역할:

| 파일 | 역할 |
|------|------|
| `FreeformCard.tsx` | AI가 생성한 코드가 이 파일에 덮어씌워짐 (빈 캔버스) |
| `types.ts` | 카드 크기(1080x1350), props 타입 정의 |
| `theme.ts` | 색상, 폰트 크기, dark/quiet-luxury 테마 프리셋 |
| `fonts.ts` | Pretendard 폰트를 브라우저에 로딩하는 훅 |
| `Root.tsx` | "FreeformCard를 1080x1350으로 찍어라" 등록 |

#### [D] 렌더링 스크립트 (1개)

`render.bat`이 내부적으로 하는 일:

```
for each card_NNN.tsx:
    1. card_NNN.tsx → remotion/src/carousel/FreeformCard.tsx 복사
    2. npx remotion still FreeformCard "card_NNN.png" --width=1080 --height=1350
    3. 원본 FreeformCard.tsx 복원
```

### 7.3 내 프로젝트에 적용하려면

이 시스템을 다른 프로젝트에 가져가려면 **[A] + [B] + [C] + [D]** 전부 복사해야 합니다.

```
내-프로젝트/
├── .claude/commands/generate-carousel.md   ← [A] 복사
├── remotion/docs/carousel-patterns*.md      ← [B] 복사
├── remotion/docs/tsx-contract.md            ← [B] 복사
├── remotion/                               ← [C] 전체 복사 후 npm install
├── render.bat                              ← [D] 복사
└── projects/                               ← 빈 폴더 생성
```

`npm install` 후 바로 사용 가능합니다.

### 7.4 Command를 발전시키는 방법

Command 파일은 **반복적으로 개선**합니다.

1. `/generate-carousel`로 카드 생성
2. 결과물에서 부족한 점 발견 (예: 차트가 너무 작음)
3. Command 파일에 규칙 추가: "차트는 카드 면적의 40% 이상 차지해야 한다"
4. 다시 `/generate-carousel` 실행 → 품질 개선

이 과정을 반복하면 Command가 점점 정교해지고, 결과물 품질이 올라갑니다. **프롬프트 엔지니어링의 자산화**입니다.

---

## 부록: 자주 묻는 질문

### Q. Claude Code가 만든 카드가 마음에 안 들면?

자연어로 수정 요청하면 됩니다. "더 크게", "색상 바꿔줘", "다른 레이아웃으로" 등 말로 지시하세요. 수정 횟수 제한은 없습니다.

### Q. 코딩을 전혀 모르는데 가능한가요?

네. TSX 코드를 직접 작성하거나 읽을 필요가 없습니다. 대본 작성 + 프롬프트 입력 + 렌더링 명령어 복붙만 합니다.

### Q. 카드 한 세트 만드는 데 시간이 얼마나 걸리나요?

| 단계 | 소요 시간 |
|------|----------|
| 대본 작성 | 대본이 있다면 0분 |
| TSX 생성 (Claude Code) | 2~5분 |
| 수정 + 피드백 반복 | 5~15분 (만족할 때까지) |
| PNG 렌더링 | 30초~1분 |

### Q. 어떤 레이아웃을 선택할 수 있나요?

23가지 레이아웃 패턴이 참조 문서에 정의되어 있습니다.

| 카테고리 | 패턴 |
|---------|------|
| **기본 9종** | 커버, 아이콘 그리드, 번호 리스트, 상하 분할, 인용, 막대 차트, 도넛 차트, Before/After, CTA |
| **확장 14종** | 스탯 대시보드, 진행 트래커, 랭킹, 코드 스니펫, 터미널, 기능 매트릭스, 장단점, 큰 숫자, 하이라이트, 후기, 타임라인, 이미지+텍스트, 아코디언, 챕터 구분 |

직접 골라도 되고, Claude Code에게 맡겨도 됩니다.

### Q. 테마는 몇 가지인가요?

| 테마 | 느낌 | 적합한 콘텐츠 |
|------|------|-------------|
| **dark** | 어두운 배경, 글로우 효과 | 테크, AI, 개발 |
| **quiet-luxury** | 흰 배경, 미니멀, 여백 | 브랜드, 라이프스타일, 교육 |

### Q. 카드뉴스 외에 다른 것도 이 방식으로 만들 수 있나요?

같은 원리(Command + 참조 문서 + Remotion)로 영상 슬라이드, 유튜브 쇼츠, 썸네일 등도 만들 수 있습니다. Command 파일과 참조 문서를 바꾸면 됩니다.

---

## 실습 체크리스트

```
[ ] 1. Node.js, Claude Code 설치 확인
[ ] 2. 스타터 킷 압축 해제 + cd remotion && npm install
[ ] 3. 프로젝트 폴더 생성 (projects/my-carousel/carousel/)
[ ] 4. script.txt 대본 작성
[ ] 5. /generate-carousel my-carousel 실행
[ ] 6. TSX 파일 생성 확인 (card_001.tsx ~ card_XXX.tsx)
[ ] 7. 자연어로 수정 요청 1회 이상 해보기
[ ] 8. render.bat my-carousel 로 PNG 렌더링
[ ] 9. PNG 이미지 확인 (card_001.png ~ card_XXX.png)
[ ] 10. 피드백 → TSX 수정 → 해당 카드 재렌더링 해보기
```
