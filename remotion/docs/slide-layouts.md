# Layout Boilerplates

> Copy-paste ready layout patterns for Freeform slides.
> All layouts are shorts-safe (center-aligned, maxWidth constrained).
> **Read only the sub-file(s) you need** -- don't load all 4 at once.

---

## Sub-files

### [slide-layouts-diagrams.md](slide-layouts-diagrams.md) -- Diagrams & Charts

**When to read**: 대본이 수치 데이터, 순서/단계, 시간 흐름, 비교 수치를 설명할 때.

| Pattern | Use when the script says... |
|---------|-----------------------------|
| Circle + Line Flow | "A에서 B를 거쳐 C로", 아키텍처, 데이터 흐름, 파이프라인 |
| **Cycle Flow** | "반복", "순환", "계속 개선", "피드백 루프", PDCA, 이터레이션 |
| **Branch-Merge Flow** | "여러 경로", "분기", "동시에 진행", "결과가 합쳐져", 의사결정 트리 |
| Horizontal Bar Chart | "A는 85%, B는 62%", 순위, 점유율, 성능 비교 |
| Vertical Timeline | "2020년에 시작해서 2024년에", 연혁, 발전 과정, 로드맵 |
| Step Indicator | "첫 번째 단계는", "Step 2", 튜토리얼, 가이드, 설정 방법 |

---

### [slide-layouts-mockups.md](slide-layouts-mockups.md) -- UI Mockups

**When to read**: 대본이 앱/웹 UI, 제품 화면, 채팅 인터페이스, 서비스 화면을 묘사하거나 UX 문제를 논할 때.

| Pattern | Use when the script says... |
|---------|-----------------------------|
| Document Frame | 코드 에디터, 문서 뷰어, 터미널 화면을 보여줄 때 |
| App Window Chat Mockup | "채팅 UI", "AI한테 물어보면", 챗봇 대화 예시, 메시지 버블 |
| App Window Service Mockup | "버튼을 누르면", 서비스 메뉴, 액션 카드, 구조화된 UI |
| Side-by-Side App Compare | "채팅 UI vs 버튼 UI", "기존 방식 vs 새 방식", UX 패턴 비교 |
| Warning Callout | "주의할 점", "경고", "함정", 중요 메시지 강조 박스 |
| Badge / Pill | 섹션 번호, 카테고리 라벨, 좌상단 뱃지 (단독 사용보다 다른 레이아웃과 조합) |

---

### [slide-layouts-metaphors.md](slide-layouts-metaphors.md) -- Visual Metaphors

**When to read**: 대본이 추상적 개념, 비율/비중, 장단점, 프로세스 흐름을 은유적으로 전달할 때. 구체적 숫자보다 "느낌"이나 "구조"를 보여주는 슬라이드.

| Pattern | Use when the script says... |
|---------|-----------------------------|
| ★ **Numbered Card Row** | "A → B → C" 인과/순서, 단계별 진행 — **Arrow Flow 대신 우선 사용** |
| ★ **Vertical Descent** | 순차 프로세스, 원인→결과 체인 — 수직 배치로 순서 전달 |
| ★ **Staircase Progress** | 진행/발전/레벨업 — 계단식 위치로 순서 전달 |
| ★ **Annotated Hub** | 중심 개념 + 속성들, 팬아웃 관계 — **Branch Flow 대신 우선 사용** |
| People Row Pictograph | "10명 중 1명", "대부분의 사람들은", 비율/비중 시각화 |
| Balance Scale | "장점과 단점", "균형", "트레이드오프", 양쪽 비교 (저울 은유) |
| Labeled Arrow Flow | 개체 간 관계/개념 흐름 — ⚠ 빈도 제한 (영상 전체 수평 화살표 합산 2회) |
| Icon Grid (3x2) | "법률, 의료, 교육, 쇼핑...", 카테고리 나열, 서비스 종류 6개 |

---

### [slide-layouts-extras.md](slide-layouts-extras.md) -- Extras & Shorts-Safe

**When to read**: 보조 UI 요소가 필요하거나, 쇼츠 크롭 대응이 필요할 때. 다른 레이아웃과 조합하는 경우가 많음.

| Pattern | Use when the script says... |
|---------|-----------------------------|
| Animated Progress Bar | "난이도: 매우 높음", 게이지, 진행률, 로딩 표현 |
| Icon + Text Grid (1x4) | "품질, 속도, 확장성, 안정성" 같은 4개 키워드 나열 |
| SVG Stroke Draw | 도형이 그려지는 애니메이션, 원/삼각형/경로 드로잉 |
| Shorts-Safe Bar Chart | 바 차트인데 쇼츠(9:16) 크롭에서도 잘리지 않아야 할 때 |
| Shorts-Safe Split Compare | 2열 비교인데 쇼츠 크롭 안전이 필요할 때 |
| Shorts-Safe Timeline | 수직 타임라인의 쇼츠 대응 버전 |

---

## Decision Flowchart

```
대본 문단을 읽고 핵심 시각 요소를 판단:

⚠ 수평 화살표 빈도 체크 (FIRST):
  영상에서 이미 수평 화살표 2회 사용?  ──→ 비화살표 패턴 강제 (★ 표시)

반복/순환/피드백/PDCA/이터레이션?  ──→ diagrams (Cycle Flow) ★교육 핵심
여러 경로/분기/합류/동시 진행?    ──→ ★ metaphors (Annotated Hub) / diagrams (Branch-Merge)
선형 단계 흐름/파이프라인?        ──→ ★ metaphors (Numbered Card Row, Vertical Descent, Staircase)
                                       diagrams (Circle+Line Flow) — 빈도 여유 시에만
"A → B → C" 인과/순서?           ──→ ★ metaphors (Numbered Card Row) 우선
                                       metaphors (Vertical Descent, Staircase) 대안
숫자/퍼센트/순위가 있다?          ──→ diagrams (Bar Chart, Step)
시간 순서가 있다?                 ──→ diagrams (Timeline, Step)
앱 화면/UI를 묘사한다?            ──→ mockups (Chat, Service, Compare)
"주의", "경고", "함정"?           ──→ mockups (Warning Callout)
"~명 중 ~명" 비율이다?            ──→ metaphors (People Row)
장단점/트레이드오프?              ──→ metaphors (Balance Scale)
카테고리 나열(4~6개)?             ──→ metaphors (Icon Grid)
기술 아키텍처/데이터 파이프라인?  ──→ diagrams (Circle Flow / Cycle Flow)
개체/개념 간 관계 흐름?           ──→ ★ metaphors (Annotated Hub) 우선
                                       metaphors (Arrow Flow) — 빈도 여유 시에만
쇼츠용 크롭 안전이 필요?         ──→ extras (Shorts-Safe 변형)
위 어디에도 안 맞는다?            ──→ slide-patterns.md의 Common Patterns
```

> **복합 슬라이드**: 2개 이상 서브파일의 패턴을 조합해야 할 경우 (예: UI 목업 + 프로그레스 바), 해당 서브파일들을 모두 읽으세요.
