# Remotion Freeform TSX 슬라이드 생성

> 소스: `.claude/commands/generate-slides.md`, `remotion/src/slides/Freeform.tsx`

## 핵심 원칙

**모든 슬라이드는 Freeform TSX로 생성합니다.**
Claude Code가 대본의 맥락을 이해하고, 각 문단에 최적화된 TSX 슬라이드를 직접 작성합니다.

## 2단계 워크플로

### Step 1: TSX 생성
```bash
# /generate-slides 스킬 실행
/generate-slides 003
```
- Claude Code가 대본 전체를 분석하여 아트 디렉션 수립
- 각 문단별 최적의 레이아웃, 시각 요소, 애니메이션 설계
- TSX 파일 저장: `projects/{name}/slides/001.tsx`, `002.tsx`, ...
- 수학/알고리즘 시각화가 필요한 문단은 Manim CE 모드 선택 가능

### Step 2: 파이프라인 실행
```bash
uv run video-automation pipeline script-to-video \
  --input projects/003/script.txt --project 003 --no-broll
```
- 기존 `.tsx` 파일 자동 감지 -> Freeform 슬롯으로 렌더링
- `.mp4` + duration 일치 시 자동 재사용 (불필요한 재렌더링 방지)

## Freeform TSX 작성 규칙

### 필수
- `useCurrentFrame()` + `interpolate()` 로 애니메이션 (CSS transition/animation 금지)
- `AbsoluteFill` 기반 레이아웃
- 디자인 토큰: `remotion/src/design/theme.ts` 의 `COLORS`, `SPACING`, `TYPOGRAPHY`
- 외부 라이브러리 import 금지 (React + Remotion만)
- SVG inline 사용 (외부 아이콘 라이브러리 불가)
- 한국어 라벨 필수 (영어 라벨 금지)

### 권장
- 레이아웃 참고: `remotion/src/slides/*.tsx` (11개 패턴)
- 패턴 레퍼런스: `remotion/docs/slide-patterns.md` + 서브파일
- 디자인 철학: `remotion/docs/design-philosophy.md` (8 원칙)
- TSX 계약: `remotion/docs/tsx-contract.md` (사이징, 센터링 규칙)
- 시각 다양성: 인접 슬라이드와 2+ 차원에서 차별화

### 금지 (Anti-patterns)
- 나레이션 앵무새: 비유/수사를 화면에 그대로 표시
- 빈 텍스트 슬라이드: 시각 요소 없이 텍스트만
- 템플릿 복제: 기존 템플릿을 그대로 코드로 재현
- 라벨 없는 아이콘: 모든 시각 요소에 한국어 라벨 필수

## 레이아웃 선택 가이드

콘텐츠 유형에 따라 레이아웃 서브파일 참조:
- **데이터/흐름/시간순**: `slide-layouts-diagrams.md`
- **UI/UX 목업**: `slide-layouts-mockups.md`
- **추상 개념/비유**: `slide-layouts-metaphors.md`
- **보조/쇼츠**: `slide-layouts-extras.md`

## 병렬 렌더링

- FreeformSlotPool: 4개 슬롯 (`FreeformSlot1~4.tsx`) 동시 렌더링
- 각 슬롯은 독립 Remotion Composition ID → 진정한 병렬 처리
- Config: `remotion.render_parallel_slots: 4`

## 핵심 교훈

- subprocess로 Claude Code 중첩 호출 불가 (CLAUDECODE 환경변수 충돌)
- 해결: TSX 생성(Step 1)과 렌더링(Step 2)을 완전 분리
