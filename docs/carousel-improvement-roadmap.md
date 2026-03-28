# Carousel 고도화 로드맵

> 출처: `old_doc/carousel_strategy.md` (JJ의 5에이전트 HTML/CSS 카드뉴스 시스템) 분석 후
> 우리 Remotion TSX 시스템에 적용할 개선 사항을 ROI 기준으로 정리.

---

## ROI 우선순위 요약

| 순위 | 개선 | Impact | Effort | ROI | 변경 범위 |
|------|------|--------|--------|-----|-----------|
| 1 | 감정 곡선 + 다양성 규칙 | ★★★★★ | ★☆☆☆☆ | 최고 | 스킬 프롬프트만 수정 |
| 2 | 자동 검증 스크립트 | ★★★★☆ | ★★★☆☆ | 높음 | Python 스크립트 신규 |
| 3 | 패턴 카탈로그 확대 | ★★★☆☆ | ★★☆☆☆ | 중상 | 문서만 추가 |
| 4 | 디자인 시스템 3레이어 | ★★★☆☆ | ★★★★☆ | 중간 | theme.ts + 스킬 수정 |
| 5 | 스킬 크기 최적화 | ★★☆☆☆ | ★☆☆☆☆ | 중간 | 스킬 파일 분할 |

---

## Phase 1: 감정 곡선 + 카드 다양성 규칙

### 배경

JJ 시스템의 가장 강력한 차별화 포인트. 카드를 "기획(plan) → 카피(copy)"로 분리하고, 기획 단계에서 **슬라이드별 감정 온도**를 매핑한다. 우리는 레이아웃/밀도만 계획하고 감정 설계가 없어, 같은 톤의 카드가 연속되는 문제가 있다.

### 목표

`/generate-carousel` Step 3에 **감정 곡선 테이블**과 **인접 카드 다양성 검증** 추가.

### 구현 상세

#### 1a. 감정 곡선 테이블 (Step 3a 확장)

기존 카드 테이블에 2개 컬럼 추가:

```
| # | Role | Layout | Emotion Phase | Intensity | Key Visual |
|---|------|--------|--------------|-----------|------------|
| 1 | Cover | cover | 호기심 유발 | ●●●●○ | Title + glow |
| 2 | 문제 제기 | quote | 공감 (막막함) | ●○○○○ | Pain point |
| 3 | 전환점 | split-top | 전환 (다른 방법) | ●●●○○ | Pivot moment |
| 4 | 핵심 설명 | icon-grid | 이해 (체험) | ●●○○○ | Features |
| 5 | 데이터 증거 | bar-chart | 확신 (증거) | ●●●●○ | Numbers |
| 6 | 사례/후기 | quote | 신뢰 (증거) | ●●●●● | Testimonial |
| 7 | 실천 방법 | numbered-list | 실천 (행동) | ●●●○○ | Steps |
| 8 | CTA | cta-ending | 여운 + 행동 | ●●●●● | Button |
```

#### 1b. 감정 곡선 4단계 프레임워크

```
공감 → 전환 → 증거 → 실천

- 공감 (카드 2-3): 독자의 현재 상황/고민 인정. 낮은 감정 온도.
- 전환 (카드 3-4): "하지만 다른 방법이 있다." 온도 상승 시작.
- 증거 (카드 5-7): 데이터, 사례, 비교. 최고 온도 도달.
- 실천 (카드 7-8): 구체적 행동 유도 → CTA. 온도 유지 또는 여운.
```

#### 1c. 다양성 규칙 (Step 3c 확장)

기존 규칙에 추가:

```
기존:
3. No 3+ consecutive same layout

추가:
8. 같은 레이아웃 2연속 금지 (기존 3연속 → 2연속으로 강화)
9. 같은 감정 온도 3장 연속 금지
10. 인접 카드의 Emotion Phase가 동일하면 최소 Layout이 다를 것
```

#### 1d. 감정 검증 체크리스트 (Step 3e 확장)

```
기존 체크리스트에 추가:
- [ ] 감정 곡선이 단조롭지 않은가 (최소 2번 온도 변화)
- [ ] 같은 감정 온도(Intensity) 3장 연속 없음
- [ ] 같은 레이아웃 2장 연속 없음
- [ ] 공감→전환→증거→실천 흐름이 자연스러운가
```

### 수정 파일

- `.claude/commands/generate-carousel.md` — Step 3 섹션 수정 (약 40줄 추가)

### 완료 기준

- Step 3 카드 테이블에 Emotion Phase + Intensity 컬럼 존재
- 다양성 규칙 3개 추가
- 감정 검증 체크리스트 4개 항목 추가

---

## Phase 2: 자동 검증 스크립트

### 배경

JJ 시스템의 `validate_slide.py`는 캔버스 크기, overflow, 폰트 크기, 토큰 사용 등을 **인간 검수 전에** 기계적으로 체크한다. 우리는 `/review-carousel`(시각 수동 검수)만 있고, 코드 레벨 자동 검증이 없어 같은 실수가 반복된다.

### 목표

`scripts/validate_carousel.py` 신규 생성. TSX 파일의 구조적 규칙 위반을 자동 감지.

### 구현 상세

#### 2a. 검증 항목 (정적 분석)

```python
# scripts/validate_carousel.py

검증 카테고리:

1. 구조 규칙 (CRITICAL)
   - export const FreeformCard 선언 존재
   - useFonts() 호출 존재
   - PageDots 컴포넌트가 마지막 child
   - FreeformCardProps 타입 import 존재

2. 금지 항목 (CRITICAL)
   - useCurrentFrame, spring, interpolate, Sequence 사용 금지
   - CSS animation, @keyframes 사용 금지
   - ../motifs/, ../design/animations 임포트 금지
   - 외부 URL (http://, https://) 참조 금지

3. 디자인 토큰 (WARNING)
   - 하드코딩된 색상값 검출 (#으로 시작하는 6자리 hex)
     → COLORS.*, QUIET_LUXURY.* 토큰 사용 권장
   - 하드코딩된 폰트 크기 중 28px 미만 검출
     → 모바일 최소 가독성 경고

4. 콘텐츠 밀도 (WARNING)
   - 텍스트 노드 수 카운트 (JSX 내 한글 문자열)
   - 3개 미만이면 "Low density" 경고

5. 연속 레이아웃 (WARNING)
   - 파일명 순서대로 주요 레이아웃 키워드 추출
   - 동일 패턴 2연속 시 경고
```

#### 2b. CLI 인터페이스

```bash
# 전체 검증
uv run python scripts/validate_carousel.py my-project

# 출력 예시:
# ✅ card_001.tsx — PASS (0 errors, 0 warnings)
# ❌ card_002.tsx — FAIL
#    [CRITICAL] Missing PageDots as last child
#    [WARNING] Hardcoded color #FF5733 at line 45 → use COLORS token
# ⚠️ card_003.tsx — WARN (0 errors, 2 warnings)
#    [WARNING] Low density: only 2 text items found
#    [WARNING] Font size 14px below minimum 28px at line 67
#
# Summary: 10 cards, 8 PASS, 1 FAIL, 1 WARN
```

#### 2c. `/generate-carousel` 통합

Step 5 (Validate) 수정:

```
기존: cp + npx tsc --noEmit (수동 spot-check)

변경:
1. uv run python scripts/validate_carousel.py $PROJECT  (자동 규칙 검증)
2. CRITICAL 에러 있으면 즉시 수정
3. 그 후 tsc spot-check (기존 유지)
```

#### 2d. `/review-carousel` 통합

Step 1 앞에 자동 검증 추가:

```
Step 0 (신규): 자동 검증
1. uv run python scripts/validate_carousel.py $PROJECT
2. CRITICAL 에러가 있으면 시각 검수 전에 코드 수정 요구
3. WARNING만 있으면 시각 검수에서 해당 카드 주의 표시
```

### 수정 파일

- `scripts/validate_carousel.py` — 신규 생성 (~150줄)
- `.claude/commands/generate-carousel.md` — Step 5 수정 (5줄 추가)
- `.claude/commands/review-carousel.md` — Step 0 추가 (10줄 추가)

### 완료 기준

- `validate_carousel.py`가 5개 검증 카테고리 커버
- CRITICAL / WARNING 분류 출력
- generate-carousel Step 5에 통합
- review-carousel Step 0에 통합

---

## Phase 3: 패턴 카탈로그 확대

### 배경

JJ: 29개 패턴 (정보 7, 절차 5, 비교 3, 데이터 3, 강조 4, 코드 2, 혼합 2, 도입 2). 우리: 9개 (A~I). 특히 데이터 시각화, 코드, 혼합 유형이 부족하다.

### 목표

`remotion/docs/carousel-patterns-layouts.md`에 **카테고리별 패턴 추가**.

### 추가할 패턴 (14개)

```
기존 9개: cover(A), icon-grid(B), numbered-list(C), split-top-bottom(D),
          quote(E), bar-chart(F), donut-chart(G), before-after(H), cta-ending(I)

추가 패턴:
데이터 카테고리:
  J. stat-dashboard — 3~4개 KPI 카드 (숫자+라벨) 격자 배치
  K. progress-tracker — 목표 대비 진행률 바 (3~5개)
  L. ranking-list — 순위표 (1~5위, 바 길이로 시각화)

코드/기술 카테고리:
  M. code-snippet — 코드 블록 + 설명 (개발 튜토리얼용)
  N. terminal-output — CLI 출력 형태 (명령어 + 결과)

비교 카테고리:
  O. feature-matrix — 기능 비교 체크마크 테이블 (2~3 옵션)
  P. pros-cons — 장단점 좌우 분할 (초록/빨강 아이콘)

강조 카테고리:
  Q. big-number — 큰 숫자 1개 + 컨텍스트 (임팩트)
  R. highlight-box — 핵심 메시지 1개 박스 강조
  S. testimonial — 사용자 후기 (아바타 + 인용문)

혼합 카테고리:
  T. timeline — 시간순 3~5개 이벤트 세로 배치
  U. split-image-text — 이미지 50% + 텍스트 50% 분할
  V. accordion — 질문-답변 형태 (FAQ 카드)

도입 카테고리:
  W. chapter-divider — 섹션 구분 카드 (번호 + 제목만)
```

### 수정 파일

- `remotion/docs/carousel-patterns-layouts.md` — 14개 패턴 TSX 예시 추가 (~500줄)
- `.claude/commands/generate-carousel.md` — Step 3b Layout Options 목록 업데이트 (10줄)

### 완료 기준

- 14개 신규 패턴 각각 TSX 코드 예시 포함
- 총 23개 패턴으로 카테고리별 커버리지 확보
- Step 3b에 전체 패턴 목록 반영

---

## Phase 4: 디자인 시스템 3레이어 상속 -- DONE

### 배경

JJ: shared → 시리즈(series) → 슬라이드 3단 상속. 시리즈별로 line-height, letter-spacing 등을 오버라이드. 우리: `theme.ts` 89줄 flat 구조에 dark/QL 2가지만 존재. 새 시리즈마다 색상/폰트를 바꾸려면 스킬 전체를 수정해야 한다.

### 목표

`theme.ts`를 확장해 **시리즈별 프리셋**을 지원하고, 스킬에서 프리셋 이름으로 선택 가능하게 한다.

### 구현 상세

#### 4a. theme.ts 확장

```typescript
// remotion/src/design/theme.ts

// Layer 1: Shared (변경 불가)
export const LAYOUT = { ... };  // 기존 유지
export const FONT = { ... };    // 기존 유지

// Layer 2: Theme Presets (시리즈별)
export const THEME_PRESETS = {
  dark: {
    name: "Dark Tech",
    colors: { background: "#0B0C0E", text: "#EDEDEF", accent: "#7C7FD9", ... },
    typography: { titleWeight: 800, bodyWeight: 500, letterSpacing: "normal" },
    effects: { glow: true, glass: true, gradients: true },
  },
  "quiet-luxury": {
    name: "Quiet Luxury",
    colors: { background: "#FFFFFF", text: "#1A1A1A", accent: "#2C2C2C", ... },
    typography: { titleWeight: 800, bodyWeight: 300, letterSpacing: "-0.03em" },
    effects: { glow: false, glass: false, gradients: false },
  },
  // 향후 추가 가능:
  "warm-editorial": { ... },
  "neon-pop": { ... },
  "minimal-mono": { ... },
} as const;

// Layer 3: Per-card override (FreeformCardProps.colors로 전달)
```

#### 4b. 프리셋 연동

- `FreeformCardProps`에 `themeName?: string` 추가
- `regenerate_carousel.py`가 프로젝트 config에서 테마명 읽어 props에 주입
- 카드 내부에서 `THEME_PRESETS[themeName]`으로 접근

#### 4c. 스킬 연동

Step 2b에서 테마 선택 시 프리셋 이름을 지정하면, 해당 프리셋의 규칙이 자동 적용.

### 수정 파일

- `remotion/src/design/theme.ts` — 프리셋 시스템 추가 (~60줄)
- `remotion/src/carousel/types.ts` — `themeName` prop 추가
- `scripts/regenerate_carousel.py` — 테마 props 주입 로직
- `.claude/commands/generate-carousel.md` — Step 2b 프리셋 연동

### 완료 기준

- `THEME_PRESETS` 객체에 dark, quiet-luxury 포함
- 프리셋 추가가 theme.ts 한 파일 수정으로 가능
- 카드 TSX에서 `THEME_PRESETS` 참조 가능

---

## Phase 5: 스킬 크기 최적화 -- DONE

### 배경

JJ: 스킬당 150줄 상한. 우리: `generate-carousel.md`가 406줄로 위반. LLM은 긴 컨텍스트에서 앞 내용을 잊는다.

### 목표

`generate-carousel.md`를 **핵심 프로세스(~200줄)**로 줄이고, 상세 레퍼런스는 외부 파일로 분리.

### 구현 상세

현재 406줄 구성:
- Step 1-6 프로세스: ~180줄 (유지)
- Design System Quick Reference: ~45줄 (외부 분리)
- TSX Component Contract: ~45줄 (외부 분리)
- Color Strategy 상세: ~40줄 (외부 분리)
- Agent Dispatch 상세: ~30줄 (외부 분리)
- Batch Sizing: ~15줄 (유지)

분리 후:
- `generate-carousel.md`: ~220줄 (프로세스 + 핵심 규칙)
- `remotion/docs/carousel-tsx-contract.md`: ~90줄 (TSX 규칙 + 색상 레퍼런스, 에이전트 지시 시 첨부)

스킬 내 참조:
```
📎 TSX 작성 규칙: remotion/docs/carousel-tsx-contract.md (에이전트 dispatch 시 이 파일 첨부)
📎 레이아웃 패턴: remotion/docs/carousel-patterns-layouts.md
```

### 수정 파일

- `.claude/commands/generate-carousel.md` — 축소 (~220줄)
- `remotion/docs/carousel-tsx-contract.md` — 신규 (~90줄)

### 완료 기준

- generate-carousel.md 250줄 이하
- TSX contract가 독립 문서로 존재
- 에이전트 dispatch 시 contract 파일 참조 지시 포함

---

## 구현 순서 가이드

각 Phase는 독립적으로 구현 가능. 아래 순서로 진행 권장:

```
Phase 1 (감정 곡선)     → 프롬프트만 수정, 즉시 효과
Phase 2 (자동 검증)     → 스크립트 작성, 반복 오류 방지
Phase 3 (패턴 확대)     → 문서 작성, 시각적 다양성 확보
Phase 4 (디자인 시스템)  → 코드 변경, 확장성 확보
Phase 5 (스킬 최적화)   → Phase 1~4 완료 후 정리
```

각 Phase 시작 시 이 문서의 해당 섹션을 읽고, "구현 상세"와 "수정 파일"을 따라 작업하면 됩니다.
