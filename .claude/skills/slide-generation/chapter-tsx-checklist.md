# TSX Validation & Checklist

## Import Validation (렌더 실패 사전 차단)

```bash
python scripts/validate_tsx_imports.py projects/$PROJECT/slides/
# or for shorts:
python scripts/validate_tsx_imports.py projects/$PROJECT/shorts_slides/slides/
```

잘못된 import 경로, 금지 패턴(backdropFilter 등)을 즉시 잡아냄.

## Type Check (spot-check)

Generated .tsx files are outside tsconfig scope. Copy and check:

```bash
# Longform
cp projects/$PROJECT/slides/001.tsx remotion/src/slides/Freeform.tsx
cd remotion && npx tsc --noEmit

# Shorts
cp projects/$PROJECT/shorts_slides/slides/001.tsx remotion/src/slides/ShortsContentSlot1.tsx
cd remotion && npx tsc --noEmit
```

Spot-check 3-4 representative files (first, middle, last, most complex).
Fix errors in originals, re-copy, re-check.

Common issues:
- Duplicate style properties (e.g., two `transform` keys)
- Wrong import paths (use exact paths from tsx-contract.md)
- Non-existent exports

## TSX 자동 삭제 경고 (CRITICAL)

파이프라인(`features/generate_slides/lib.py:380-391`)은 Remotion 렌더가 RuntimeError로 실패하면
**해당 `.tsx` 파일을 즉시 삭제**한다. 폰트 404, spring config 오류 등 환경 문제가 원인이어도 삭제됨.

**결과**: tsx 없음 → 다음 파이프라인 실행 시 "슬라이드 파일 없음" → cascade 실패

**방어책**:
1. 파이프라인 실행 **전** `regenerate_slides.py` pre-render로 렌더 오류를 먼저 잡는다
2. tsx가 갑자기 사라졌다면 이전 파이프라인의 렌더 실패 흔적 — tsx를 재작성해야 함
3. `remotion/public/fonts/` 디렉토리와 Pretendard 폰트 파일 존재 여부를 먼저 확인

---

## Stale File Cleanup (CRITICAL)

Before running pipeline, delete .json and .mp4 for all slides with .tsx/.py:

```bash
cd projects/$PROJECT/slides
for f in *.tsx *.py; do
  base="${f%.*}"
  rm -f "${base}.json" "${base}.mp4"
done
```

WHY: Pipeline may silently reuse old template-rendered MP4s (duration match ±0.5s).
This is the #1 cause of "pipeline ignored my TSX files" issues.

## Audio Count Verification

```bash
TSX_COUNT=$(ls projects/$PROJECT/slides/*.tsx 2>/dev/null | wc -l)
WAV_COUNT=$(ls projects/$PROJECT/audio/*.wav 2>/dev/null | wc -l)
if [ "$WAV_COUNT" -gt 0 ] && [ "$WAV_COUNT" -ne "$TSX_COUNT" ]; then
  echo "audio($WAV_COUNT) ≠ slides($TSX_COUNT) → audio 전체 삭제"
  rm -f projects/$PROJECT/audio/*.wav
fi
```

## Manim Validation

For .py files:
```bash
# AST syntax check
python -c "import ast; ast.parse(open('projects/$PROJECT/slides/NNN.py', encoding='utf-8').read())"

# Structure check
grep -q "class ManimSlide(Scene)" projects/$PROJECT/slides/NNN.py
grep -q "def construct" projects/$PROJECT/slides/NNN.py
grep -q "DURATION_PLACEHOLDER" projects/$PROJECT/slides/NNN.py

# Security check (must NOT contain)
! grep -qE "^(import os|import subprocess|from os |from subprocess )" projects/$PROJECT/slides/NNN.py
! grep -qE "(eval\(|exec\(|__import__\(|open\()" projects/$PROJECT/slides/NNN.py
```

## Quality Self-Review Checklist (Longform, 15개)

### 레이아웃 (3개)
- [ ] No 3+ consecutive same layout
- [ ] No layout type > 3 times total
- [ ] Every slide has SVG/diagram/chart (not just glass card)

### 애니메이션 (5개)
- [ ] Motion variety: fadeSlideIn ≤ 40% (clipReveal/wordStagger/charSplit 활용)
- [ ] Exit variety: 2종+ 사용
- [ ] Entry 3종+ 사용
- [ ] Spring 3종+ 사용
- [ ] Adjacent slides different spring

### 콘텐츠 (5개)
- [ ] Content fidelity (지어낸 이름/수치 없음)
- [ ] **페르소나 검증**: 텍스트에 "Sam Altman", "샘 올트만", "샘알트만" 등이 있으면 → 반드시 원본 대본과 대조. 채널 호스트 = **샘호트만** (@ai.sam_hottman) ≠ Sam Altman (OpenAI CEO). 대본에 '샘호트만'이면 절대 Sam Altman으로 바꾸지 않는다.
- [ ] 음소거 테스트 통과
- [ ] 한글 라벨 필수
- [ ] 앵무새 균형 검사 (나레이션 그대로 옮기지 않음)

### 기술 (3개)
- [ ] Visual rhythm 2:1
- [ ] Opening/ending 시각적 차별화
- [ ] inputRange strictly increasing

### SAVE/RECALL 사용 시
→ [chapter-animation-memory.md](chapter-animation-memory.md) § 가드레일 참조
