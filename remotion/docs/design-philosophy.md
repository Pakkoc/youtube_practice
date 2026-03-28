# Design Philosophy (인포그래픽 전문가 원칙)

이 원칙들은 VOX 스타일 모션 인포그래픽, Tufte의 정보 디자인, Gestalt 시각 인지 이론에서 도출되었습니다.
"AI가 만든 티"를 없애는 핵심은 **전문가의 디자인 판단을 규칙으로 번역**하는 것입니다.

## 상보성 (Complementary, Not Redundant)

> **핵심 원칙: 화면은 나레이션의 자막이 아니라, 나레이터가 말로 설명하기 어려운 것을 대신 보여주는 것이다.**

나레이터와 화면은 **서로 다른 레이어의 정보**를 전달해야 합니다:
- 나레이션이 "왜"를 설명 → 슬라이드는 "무엇/얼마나"를 시각화
- 나레이션이 감정/스토리 → 슬라이드는 데이터/구조를 보여줌
- 나레이션이 비유/수사적 표현 → 슬라이드는 **비유가 가리키는 실체**(구체적 상황, 예시, 데이터)를 보여줌

### 나레이션 앵무새 규칙 (Anti-Parrot Rule — 균형 있는 적용)

**금지** — 비유/수사 표현을 대형 텍스트로 직접 표시:
| ❌ 나레이션 앵무새 | ✅ 시각적 보충 |
|-------------------|---------------|
| 나레이터: "함정" → 화면: "함정" 대형 텍스트 + WARNING | 나레이터: "함정" → 화면: 잘못된 설정 화면/사용 패턴 예시 |
| 나레이터: "히든 활용법" → 화면: "HIDDEN" 배지 | 나레이터: "히든 활용법" → 화면: 실제 비교 화면 / 확장 용도 다이어그램 |
| 나레이터: "게임 체인저" → 화면: "GAME CHANGER" 텍스트 | 나레이터: "게임 체인저" → 화면: 변화의 구체적 수치/결과 비교 |

**허용** — 사실적 키워드(개념명, 단계명, 도구명)는 라벨에 사용 OK:
| ✅ 허용 | 설명 |
|---------|------|
| 나레이터: "만들고, 돌려보고, 확인하고" → 화면: "만들기 → 실행 → 확인" 플로우 노드 | 사실적 단계명을 라벨로 구조화 |
| 나레이터: "3가지를 다루겠습니다" → 화면: 3개 번호 카드 + 각 주제 키워드 | 구조 미니맵에 키워드 라벨 |
| 나레이터: "기존 방식 vs 새 방식" → 화면: "기존 방식" / "Skills 2.0" 비교 카드 | 비교 대상의 명칭 라벨 |

**⚠️ 과잉 제거 금지 (CRITICAL):**
- 텍스트를 모두 빼고 아이콘만 남기면 **정보 전달 불가** → 이것이 앵무새보다 더 나쁜 결과
- **모든 아이콘/노드/카드에는 반드시 한글 라벨**이 있어야 함
- 판단 기준: "음소거로 봤을 때 무슨 내용인지 알 수 있는가?" — NO면 라벨 추가

### 비유/수사 표현 처리 (Metaphor → Substance)

대본에서 비유적/수사적으로 쓰인 단어는 **절대 화면 텍스트로 직접 표시하지 않는다**.
비유는 감정을 전달하는 도구이므로 나레이터의 목소리에 맡기고, 화면은 **비유가 가리키는 실체**를 보여준다.

- "함정에 빠집니다" → 잘못된 사용 패턴의 실제 예시 (UI 목업, 잘못된 프롬프트 등)
- "무기가 됩니다" → 성과 비교 (before/after 차트, 개선 수치)
- "숨겨진 활용법" → 일반 용도 → 확장 용도로 분기하는 다이어그램
- "게임 체인저" → 변화 전후의 구체적 데이터/상황 비교

### 자기 검증 (음소거 테스트)

슬라이드를 만든 후 자문: **"이 화면을 음소거로 봐도 독립적으로 정보가 전달되는가?"**
- YES → 좋은 슬라이드 (시각 자체로 정보 전달)
- NO, 나레이션 키워드가 크게 써있을 뿐 → 재설계 필요

**실행 기준:**
- 대본 문장을 그대로 슬라이드에 복사 → FAIL
- 대본의 비유/수사 표현을 대형 텍스트로 표시 → FAIL (사실적 키워드 라벨은 OK)
- 아이콘만 있고 라벨이 없는 슬라이드 → FAIL (정보 전달 불가)
- 영어 텍스트가 화면에 표시됨 → FAIL (모든 라벨은 한글)
- 슬라이드 텍스트는 **개조식 키워드** (최대 6~8 단어/줄)
- 숫자/데이터가 대본에 언급되면 → 반드시 시각화 (bar chart, big number, icon grid)

## 점진적 공개 (Progressive Disclosure)
정보를 한 번에 보여주지 말고 **단계별로 드러내세요** — VOX 인포그래픽의 핵심 기법.
- 요소를 순차 등장시킴: 제목 → 0.3초 후 아이콘/다이어그램 → 0.5초 후 상세 텍스트
- `cascadeUp(frame, fps, itemIndex)` 또는 `stagger delay`로 시간차 진입
- 단순 → 복잡 순서로 쌓아가면 시청자가 각 요소를 읽을 시간이 생김
- **안티패턴**: 모든 요소가 동시에 fadeIn — "AI 슬라이드"의 가장 흔한 특징
- **비례 타이밍 필수**: `getAnimationZone(durationInFrames)` + `staggerDelays()` / `zoneDelay()` 사용. 하드코딩된 프레임 딜레이 금지. (see `slide-patterns.md` → Duration-Proportional Timing)

**실행 기준:**
- 모든 요소가 frame 0에서 동시 출현 → FAIL
- 최소 3단계 시차: 제목(zone start) → 주요 비주얼(+0.3s×fps) → 상세(+0.6s×fps)
- 아이템 리스트: `staggerDelays(itemCount)` 사용, 수동 delay 계산 금지
- Remotion 참고: `remotion-best-practices/rules/animations.md` (useCurrentFrame 기반 애니메이션)

## 비례 = 중요도 (Hitchcock's Proportion Rule)
화면에서 가장 큰 시각적 공간을 차지하는 요소가 가장 중요한 정보여야 합니다.
- 한 슬라이드에 강조점은 **1개만** — 모든 것을 강조하면 아무것도 강조되지 않음
- 주요 요소(숫자, 인용문, 핵심 다이어그램)가 화면의 50% 이상을 차지
- 보조 요소(라벨, 부연, 출처)는 항상 작고, 흐리고, 주변부에 배치

**실행 기준:**
- 주요 요소: `fontSize: 72~140px`, `fontWeight: 900`
- 보조 요소: `fontSize: 24~32px`, `opacity: 0.5~0.7`, `color: COLORS.MUTED`
- 한 슬라이드에 `fontSize >= 48px` 요소가 2개 이상 → 위반 (강조점 분산)
- 주요 요소의 컨테이너 면적 > 화면의 50% (예: 1920×1080에서 960×540 이상)

## 데이터-잉크 비율 (Tufte's Data-Ink Ratio)
슬라이드의 **모든 시각 요소는 정보를 전달**해야 합니다.
- 장식적 SVG, 의미 없는 글로우, 불필요한 구분선 → 제거 (chartjunk)
- SVG 아이콘은 내용과 **직접 관련된 것만** 사용 (예: 돈 이야기에 코드 아이콘 금지)
- "예쁘지만 의미 없는" 요소보다 "단순하지만 정보를 전달하는" 요소를 우선

**실행 기준:**
- 순수 장식 요소 (의미 없는 원, 별, 파티클) → 삭제
- SVG 아이콘: 대본 키워드와 1:1 매칭되는 것만 허용
- `boxShadow` 레이어 2개 초과 → 과잉 장식, 1개로 축소
- `background: linear-gradient(...)` 장식용 오버레이 → `AnimatedBackground`에 위임

## 근접 = 관계 (Gestalt Proximity)
**가까이 있는 요소는 관련 있는 것**으로 인식됩니다.
- 관련 요소 간격 좁게(8-16px), 무관한 그룹 간격 넓게(40-60px)
- 제목↔본문 간격 < 섹션↔섹션 간격 — 시각적 그룹이 의미적 그룹과 일치해야 함
- 카드/패널로 그룹핑하면 근접+폐쇄 원리가 동시에 작동

**실행 기준:**
- 제목↔본문: `gap: 8~16px` 또는 `marginTop: 8~16px`
- 섹션↔섹션: `gap: 40~60px` 또는 `marginTop: 40~60px`
- 같은 그룹 내 아이템: `gap: 12~20px`
- 그룹 간 간격 < 그룹 내 간격 → 위반 (시각 계층 파괴)

## 여백 = 임팩트 (Whitespace as Intentional Tool)
빈 공간은 실수가 아니라 **의도적 도구**입니다.
- 요소가 적을수록 남은 요소의 시각적 무게가 증가
- 화면의 **30% 이상**은 의도적으로 비워둘 것
- 정보를 더 넣고 싶으면 욱여넣지 말고 **다음 슬라이드에 배치**

**실행 기준:**
- 콘텐츠 영역 `maxWidth: 700px` (1920px 기준 → 양쪽 여백 각 610px = 63%)
- 상단 패딩: `paddingTop: 60~80px`
- 하단 자막 예약: 360px (콘텐츠는 상위 720px 영역에 집중)
- 요소 5개 초과 → "다음 슬라이드로 분할" 검토 필요

## 색상 의미론 (Color Semantics)
색상을 **일관되게** 사용하면 시청자가 무의식적으로 의미를 파악합니다.
- **ACCENT**(보라) = 핵심 개념, 주제 키워드, 강조 텍스트
- **TEAL**(청록) = 긍정적 결과, 성과, 해결책
- **ACCENT_BRIGHT**(밝은 보라) = 데이터, 수치, 통계
- **MUTED**(회색) = 보조 정보, 라벨, 부연 설명
- 한 슬라이드에서 강조 색상은 **최대 2개**

**실행 기준:**
- `COLORS.ACCENT` (`#7C7FD9`): 제목 accentWord, 핵심 키워드 배경
- `COLORS.TEAL` (`#3CB4B4`): 성과 수치, 긍정 결과 강조
- `COLORS.ACCENT_BRIGHT` (`#9B9EFF`): 데이터 바, 차트, 통계 수치
- `COLORS.MUTED` (`#9394A1`): 출처, 라벨, 보조 설명 텍스트
- 한 슬라이드에서 ACCENT + TEAL + ACCENT_BRIGHT 중 3개 동시 사용 → 위반

## 의도적 불완전함 (Anti-Polish)
과도하게 매끄러운 모션은 "AI/광고" 느낌을 줍니다.
- 모든 요소가 완벽한 대칭·정렬일 필요 없음 — 약간의 비대칭이 편집감을 줌
- spring 설정을 다양하게: `SPRING_BOUNCY`(역동), `SPRING_GENTLE`(차분), `SPRING_STIFF`(정보 전달)
- 같은 spring config로 모든 요소를 움직이면 기계적으로 보임

**실행 기준:**
- 인접 슬라이드가 동일 spring config 사용 → 변경 필요
- 한 슬라이드 내 spring 종류: 최소 2개 (예: 제목=SNAPPY, 아이템=BOUNCY)
- 모든 요소가 정확히 같은 delay 간격 → 약간의 변주 추가 (예: 0.15s, 0.2s, 0.15s)
- Remotion 참고: `remotion-best-practices/rules/timing.md` (spring, interpolate, easing)

---

## Remotion Best Practices 참조

이 프로젝트의 슬라이드 시스템은 자체 디자인 시스템(`remotion/src/design/`, `remotion/src/motifs/`)을 사용하지만,
Remotion 일반 패턴이 필요할 때 아래 rule 파일을 참조하세요:

| 주제 | 참조 파일 | 사용 시점 |
|------|----------|----------|
| 애니메이션 기초 | `remotion-best-practices/rules/animations.md` | useCurrentFrame, interpolate 패턴 |
| 차트/시각화 | `remotion-best-practices/rules/charts.md` | bar chart, pie chart, line chart, SVG path animation |
| 타이밍/이징 | `remotion-best-practices/rules/timing.md` | spring config, easing curves, interpolate |
| 전환 효과 | `remotion-best-practices/rules/transitions.md` | 씬 간 전환 패턴 |
| 폰트 로딩 | `remotion-best-practices/rules/fonts.md` | Google Fonts, 로컬 폰트 (@remotion/fonts) |
| 텍스트 애니메이션 | `remotion-best-practices/rules/text-animations.md` | typewriter, word highlight 패턴 |
| 시퀀싱 | `remotion-best-practices/rules/sequencing.md` | delay, trim, 순서 제어 |

> **주의**: 이 프로젝트는 `CSS transitions` / `Tailwind animation` 금지 — Remotion 렌더링 시 동작하지 않음.
> 반드시 `useCurrentFrame()` + `interpolate()` 또는 `spring()` 기반 애니메이션만 사용.
