# Remotion 프로젝트 구조

> 소스: `remotion/`

## 디렉토리 구조

```
remotion/
├── package.json          # Remotion v4.0.417
├── remotion.config.ts    # 빌드 설정
├── src/
│   ├── Root.tsx          # 전체 Composition 등록
│   ├── slides/           # Freeform 슬라이드
│   │   ├── Freeform.tsx       # Freeform 메인 (single render)
│   │   ├── FreeformSlot1.tsx  # 병렬 렌더링 슬롯 1
│   │   ├── FreeformSlot2.tsx  # 병렬 렌더링 슬롯 2
│   │   ├── FreeformSlot3.tsx  # 병렬 렌더링 슬롯 3
│   │   └── FreeformSlot4.tsx  # 병렬 렌더링 슬롯 4
│   ├── design/           # 디자인 시스템
│   │   ├── theme.ts      # 색상, 간격, 타이포그래피
│   │   ├── animations.ts # 애니메이션 유틸리티
│   │   └── fonts.ts      # Pretendard 폰트
│   ├── motifs/           # 시각 강화 모티프
│   │   ├── entries/      # 진입 애니메이션
│   │   ├── emphasis/     # 강조 효과
│   │   └── decorations/  # 장식 요소
│   ├── shorts/           # 쇼츠 컴포지션
│   │   ├── ShortsComposition.tsx
│   │   ├── HookTitle.tsx
│   │   ├── StyledSubtitle.tsx
│   │   └── types.ts
│   └── carousel/         # 카루셀 카드
└── public/               # 정적 에셋 (B-roll 배경 복사 위치)
```

## CLI 명령어

```bash
# 슬라이드 렌더링 (Python에서 subprocess로 호출)
npx remotion render Freeform output.mp4 --props='{"durationInFrames":150,...}'

# Still 렌더링 (카루셀)
npx remotion still CarouselCard output.png --props='{...}'

# 쇼츠 렌더링
npx remotion render ShortsComposition output.mp4 --props='{...}'

# TypeScript 검증
npx tsc --noEmit
```

## Python에서 렌더링 호출

`RemotionSlideBackend.render()`:
1. props에 `durationInFrames`, `slideIndex`, `totalSlides` 주입
2. B-roll → `remotion/public/_bg_*` 복사
3. `subprocess.run(["npx", "remotion", "render", ...])`
4. 출력: `slides/001.mp4`

## 디자인 시스템

### theme.ts
- `COLORS` -- 배경, 텍스트, 악센트 색상
- `SPACING` -- 패딩, 마진
- `TYPOGRAPHY` -- 폰트 크기, 행간

### animations.ts
- `fadeIn()`, `slideUp()`, `scaleIn()` 등 유틸리티
- `interpolate()` 기반 (CSS transition은 렌더링 시 동작 안함)

### fonts.ts
- Pretendard 폰트 로딩 (`assets/fonts/` 참조)

## 병렬 렌더링 SlotPool 패턴

`FreeformSlotPool` / `ShortsSlotPool`은 4개의 SlotN.tsx 파일을 독립 렌더링 슬롯으로 관리한다.

**핵심 제약 — 원자적 쓰기 필수:**
- 4슬롯이 동시에 `npx remotion render`를 실행하면, 각 프로세스가 **전체 프로젝트를 번들링**
- 슬롯 A가 TSX 파일을 쓰는 도중 슬롯 B의 번들러가 읽으면 **불완전한 파일로 번들 실패**
- `write_slot()`은 반드시 `write_text(tmp) + os.replace(tmp, target)` 원자적 쓰기 사용
- 렌더 실패 시 최대 2회 재시도 (2초 간격) — 일시적 번들 경쟁에 대응

**적용 위치:**
- `features/generate_slides/remotion_backend.py` — FreeformSlotPool (일반 영상)
- `features/render_shorts_slides/lib.py` — ShortsSlotPool (쇼츠)

**SlotPool 새로 만들 때 체크리스트:**
- [ ] `write_slot()`이 원자적 쓰기(tmp+rename)인가?
- [ ] 렌더 함수에 재시도 로직이 있는가?
- [ ] 실패 시 에러 로그에 stderr가 포함되는가?

## 주의사항

- Remotion에서는 **CSS transition/animation 사용 금지** -- `interpolate()` 사용
- 외부 라이브러리 import 불가 (React + Remotion만)
- B-roll 배경은 `public/` 폴더에 복사되어 20% opacity로 적용
- `npm install` 선행 필요 (`cd remotion && npm install`)
- **렌더 중단 후 재시작 시** `taskkill //F //IM node.exe` 필수 (좀비 node 방지)
