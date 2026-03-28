# Carousel AI Background Images Reference

`carousel.background.enabled: true`일 때 적용되는 AI 배경 이미지 생성 가이드.
`/carousel-copywriting`(image_prompt 작성)과 `/generate-carousel`(생성+TSX 통합)에서 참조.

---

## 카드 선택 기준

모든 카드가 아닌 **3~5장만** 배경 이미지를 받는다.

| 카드 유형 | 배경 이미지? | 이유 |
|-----------|-------------|------|
| Cover | **항상** | 첫인상, 스크롤 멈춤 |
| CTA (마지막) | **항상** | 행동 유도 임팩트 |
| Quote / 감정 카드 | 강력 추천 | 분위기 강화, 공간 채움 |
| 저밀도 (1-2 아이템) | 추천 | 빈 공간 해결 |
| 고밀도 (5+ 아이템) | **안됨** | 가독성 방해 |
| 차트/데이터 카드 | **안됨** | 시각적 간섭 |

---

## image_prompt 작성법 (copy_deck.md용)

- 영문으로 작성 (Gemini 모델이 영문 프롬프트에 최적화)
- 인물 없이 배경/분위기 중심으로 묘사
- 하단 40%는 텍스트 오버레이 영역 → 상단/중앙에 주요 피사체 배치
- 다크 톤 시네마틱 장면이 기본 (dark 테마와 어울림)

**좋은 예시:**
```
"Futuristic dark workspace with holographic data visualizations, cinematic blue accent lighting"
"Abstract neural network glowing nodes connected by light trails, deep purple tones"
"Minimalist dark desk setup with single glowing monitor, volumetric light rays"
```

**피해야 할 것:**
- 텍스트/글자 포함 지시 (AI가 글자를 잘못 생성)
- 과도하게 밝은 배경 (다크 그라디언트 오버레이 효과 감소)
- 복잡한 인물 묘사 (인물 레퍼런스 없이 생성)

---

## 배경 이미지 생성 CLI

```bash
# copy_deck.md에서 image_prompt 파싱 → 생성
uv run python scripts/generate_carousel_backgrounds.py $PROJECT

# 특정 카드만 재생성
uv run python scripts/generate_carousel_backgrounds.py $PROJECT 1 3

# 전체 재생성
uv run python scripts/generate_carousel_backgrounds.py $PROJECT --force
```

- 출력: `projects/$PROJECT/carousel/backgrounds/bg_NNN.png`
- 카드간 2초 대기 (rate limit 방지), 실패 시 자동 1회 재시도

---

## TSX 통합

배경 이미지가 있는 카드는 TSX에 `backgroundImage` prop 핸들링 포함.
-> `carousel-patterns-fills.md` § J-AI 패턴 참조.

핵심:
1. `import { AbsoluteFill, Img, staticFile } from "remotion";`
2. props에서 `backgroundImage` 디스트럭처링
3. `backgroundImage && (...)` 조건부 렌더링 (이미지 + 다크 그라디언트)
4. 나머지 콘텐츠는 위에 쌓임

배경 이미지가 **없는** 카드는 기존과 동일 — `backgroundImage` 코드 불필요.
