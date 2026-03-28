# CC Shorts TSX (Claude Code 교육 쇼츠)

CC Shorts는 비개발자 대상 Claude Code 교육 쇼츠. 일반 쇼츠와 다른 점:
- 정사각형 중앙 영역 (1080x1080)
- CC 포맷 패턴 3종 (번역기/구조도/상황카드)
- AnimatedBackground 금지, backdropFilter 금지

## CC 포맷 감지

대본에서 판단:
- **번역기(translator-pairs)**: 용어 비교가 핵심 ("개발자들이 ~라고 하는데요")
- **구조도(flow-steps)**: 단계별 과정이 핵심 ("그래서 → 그러면 → 그다음에")
- **상황카드(situation-flip)**: 문제→해결이 핵심 ("이럴 때 → 이 기능이")

## 정사각형 레이아웃 제약

모든 콘텐츠는 정사각형 중앙 영역 (1080x1080) 안에 배치.
padding: "140px 48px 340px 48px"

- usable content: ~984px x ~880px
- 하단 340px 중 200px = 자막, 140px = 센터링 여백
- 세로 공간이 일반 쇼츠보다 좁음 → 더 compact하게

## 슬라이드 계획 테이블

| # | Content Summary | Layout | Format Pattern | Hook Line1 | Hook Line2 |

Format Pattern Column: translator-pairs, flow-steps, situation-flip, 또는 일반 레이아웃 (title-hero, minimal-text 등).
포맷 패턴은 에피소드 중반부에 집중, 도입/마무리는 일반 레이아웃.

## TSX Boilerplate (CC Shorts 전용)

```tsx
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, Easing } from "remotion";
import { COLORS, FONT } from "../design/theme";
import { useFonts } from "../design/fonts";
import { SHORTS_CONTENT } from "../shorts/types";
import type { FreeformProps } from "./types";

export const Freeform: React.FC<FreeformProps> = ({ slideIndex, totalSlides }) => {
  useFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ width: SHORTS_CONTENT.width, height: SHORTS_CONTENT.height, backgroundColor: "transparent" }}>
      <AbsoluteFill style={{ padding: "140px 48px 340px 48px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
        {/* Content — within ~984x880 usable area */}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

## Reference Files (CC ALWAYS)
```
remotion/docs/tsx-contract.md (§ Common + § Shorts + CC Shorts)
cc-content/docs/cc-shorts-patterns.md (CC 3가지 포맷 — 필수)
remotion/docs/slide-patterns.md + slide-icons.md
remotion/docs/slide-layouts-extras.md (Shorts-Safe)
.claude/skills/remotion-visual-standards/SKILL.md (§ 7)
```

## Rendering-Critical 금지 목록

1. **backdropFilter 절대 금지** — Remotion 렌더 행(hang) 발생
2. **WebkitBackgroundClip: "text" 절대 금지** — 글자 마스킹/깨짐 발생. `color: COLORS.ACCENT_BRIGHT` + `textShadow: GLOW.text` 사용
3. COLORS.CODE_BORDER, COLORS.PRE_BG 등 미정의 상수 금지
3. 허용 COLORS: BG, TEXT, ACCENT, ACCENT_BRIGHT, MUTED, TEAL, CODE_BG
4. 터미널 배경: "#141618", 테두리: "rgba(255,255,255,0.08)"

## Quality Self-Review (CC)
- [ ] 훅 타이틀 각 줄 12자 이내
- [ ] 포맷 패턴이 올바른 슬라이드에 적용
- [ ] 정사각형 제약(padding) 적용
- [ ] SVG/visual 1개 이상 per slide
- [ ] backdropFilter 사용하지 않음
- [ ] 미정의 COLORS 상수 없음
