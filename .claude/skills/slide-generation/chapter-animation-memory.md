# Animation Memory (시각 연속성 시스템)

독립 렌더링되는 Remotion TSX 슬라이드 간 시각적 연속성을 구현한다.
각 슬라이드는 여전히 독립 MP4로 렌더링되지만, 이전 슬라이드의 핵심 비주얼을 **정확히 재현한 뒤 변형**함으로써 시청자에게 "이어지는 느낌"을 준다.

파이프라인/Remotion 아키텍처 변경 없음 — TSX 작성 워크플로만 확장.

---

## 작동 원리

```
Art Direction 단계
  → 대본 전체 읽기 → 시각 연속성 기회 자동 감지
  → animation-memory.json 초기화 (recall_links 사전 계획)

Slide Table 단계
  → Memory 컬럼에 SAVE/RECALL 표기

TSX 작성 단계
  → SAVE 슬라이드: 작성 후 key element 좌표 추출 → JSON append
  → RECALL 슬라이드: JSON 읽기 → 소스 비주얼 재현 → recall_type 적용
```

---

## animation-memory.json 스키마

위치: `projects/$PROJECT/animation-memory.json`

```json
{
  "version": 1,
  "entries": [
    {
      "entry_id": "mcp-arch",
      "source_slide": 3,
      "concept": "MCP 아키텍처 다이어그램",
      "keywords": ["MCP", "서버", "클라이언트"],
      "visual_snapshot": {
        "layout": "diagram-flow",
        "elements": [
          {"id": "node-server", "label": "MCP 서버", "x": 300, "y": 480, "w": 260, "h": 90, "color": "#7C7FD9"},
          {"id": "node-client", "label": "클라이언트", "x": 900, "y": 480, "w": 260, "h": 90, "color": "#3CB4B4"},
          {"id": "arrow-1", "type": "arrow", "from": "node-server", "to": "node-client"}
        ]
      },
      "end_state_description": "2개 노드가 수평 배치, 화살표 연결, 모두 fully visible"
    }
  ],
  "recall_links": [
    {
      "target_slide": 15,
      "source_entry_id": "mcp-arch",
      "recall_type": "expand",
      "transformation": "기존 2노드에 3개 노드 추가, 서버 노드 TEAL로 전환"
    }
  ]
}
```

### entries 필드 규칙

- **entry_id**: 짧고 읽기 쉬운 kebab-case (e.g., `pricing-chart`, `step-flow-v1`)
- **visual_snapshot.elements**: 핵심 구조 요소만 (노드, 화살표, 바, 배지). 장식(glow, particle) 제외
- **end_state_description**: 자연어 요약 — 구조화 데이터가 부족할 때 fallback으로 사용

### recall_links 필드 규칙

- Slide Table 작성 시 사전 계획 (TSX 작성 전)
- `recall_type`: 아래 5종 중 선택
- `transformation`: 어떤 변화를 적용할지 한 줄 요약

---

## recall_type 5종

### expand — 기존 비주얼에 새 요소 추가

소스 비주얼을 그대로 재현(frame 0, 애니메이션 없이 즉시 표시)한 뒤, 새 요소가 입장 애니메이션으로 등장.

```tsx
// 소스 노드: frame 0에 즉시 표시 (interpolate 없음)
const sourceNodes = [
  { label: "MCP 서버", x: 300, y: 480, color: COLORS.ACCENT },
  { label: "클라이언트", x: 900, y: 480, color: COLORS.TEAL },
];
// 새 노드: 0.3s 후 cascadeUp 입장
const newNodeOpacity = spring({ frame: frame - 9, fps, config: SPRING_SNAPPY });
```

### transform — 기존 요소의 상태 변경

소스 비주얼을 재현한 뒤, 특정 요소의 색상/크기/위치를 spring 애니메이션으로 전환.

```tsx
// 바 색상을 ACCENT → TEAL로 전환
const barColor = interpolateColors(
  spring({ frame: frame - delay, fps, config: SPRING_SNAPPY }),
  [0, 1], [COLORS.ACCENT, COLORS.TEAL]
);
```

### compare — 소스와 새 비주얼 병렬 배치

소스 비주얼을 좌측(또는 상단)에 축소 재현, 새 비주얼을 우측(또는 하단)에 입장.

```tsx
// --- RECALL: manual-process:compare ---
// 좌: 소스 다이어그램 (0.55x 스케일, 즉시 표시)
<div style={{ position: "absolute", left: 80, top: 200, transform: "scale(0.55)", transformOrigin: "top left" }}>
  {/* 소스 비주얼 그대로 재현 */}
</div>
// 우: 새 다이어그램 (insetReveal 입장)
const revealProgress = spring({ frame: frame - 12, fps, config: SPRING_SNAPPY });
<div style={{ position: "absolute", right: 80, top: 200, transform: "scale(0.55)", transformOrigin: "top right",
  clipPath: `inset(${interpolate(revealProgress, [0, 1], [100, 0])}% 0 0 0)` }}>
  {/* 새로운 비주얼 */}
</div>
```

### echo — 모서리/배지에 축소 콜백

메인 콘텐츠는 독립적이지만, 소스 비주얼의 축소판(~120x80)이 모서리에 표시되어 서사적 연결을 암시.

### simplify — 전체 비주얼에서 하나만 확대

소스 비주얼 전체를 재현 → 대상 외 요소 fadeOut → 대상 요소를 center로 scale up.

---

## Chain Recall (연쇄 회상)

1개 SAVE → N개 연속 RECALL (n ≥ 2). 동일 persistent 요소가 여러 슬라이드에 걸쳐 **끊김 없이** 유지되면서 점진 변형.

### 대표 패턴

- **Step Indicator 진행**: 5단계 워크플로우에서 step bar가 유지되고, 각 단계마다 이전 step에 ✓ 표시
- **타임라인 확장**: 타임라인이 유지되면서 이벤트가 하나씩 추가
- **점진 구축**: 다이어그램에 노드가 하나씩 추가되는 3+ 슬라이드 연속

### Slide Table 표기

```
| 21 | Step 1 초기화 | step-indicator | ... | SAVE:workflow          |
| 22 | Step 2 논의   | step-indicator | ... | RECALL:workflow:transform |
| 23 | Step 3 계획   | step-indicator | ... | RECALL:workflow:transform |
| 24 | Step 4 실행   | step-indicator | ... | RECALL:workflow:transform |
| 25 | Step 5 검증   | step-indicator | ... | RECALL:workflow:transform |
```

### recall_links 누적 기술

각 link의 `transformation`에 **해당 슬라이드의 최종 상태**를 기술 (원본 SAVE 대비 변형):

```json
{"target_slide": 22, "source_entry_id": "workflow", "recall_type": "transform",
 "transformation": "step 1 ✓, step 2 활성화, 3-5 회색"},
{"target_slide": 23, "source_entry_id": "workflow", "recall_type": "transform",
 "transformation": "steps 1-2 ✓, step 3 활성화, 4-5 회색"}
```

### 자동 감지

"점진적 구축" 신호에서 **순번이 3개+ 연속**이면 Chain Recall 후보. 예: "1단계는...", "2단계에서는...", "3단계는..." 패턴.

---

## Seamless Handoff (무전환 핸드오프)

독립 MP4 경계에서 persistent 요소의 **깜빡임을 제거**하는 규칙. Chain Recall 시 필수.

### 3가지 규칙

1. **SAVE 슬라이드의 Exit = `cut`**: Chain Recall로 이어지는 SAVE(및 체인 내 RECALL) 슬라이드는 exit 애니메이션 없이 즉시 종료. blurOut/fadeSlideOut 등을 사용하면 persistent 요소가 사라졌다 다시 나타나며 **깜빡임 발생**.
2. **RECALL의 recalled 요소 = frame 0 즉시 표시** (기존 규칙 그대로). 입장 애니메이션 없음.
3. **Longform SceneFade 분리**: Recalled 요소는 SceneFade 래퍼 **밖에** 배치. 새 콘텐츠에만 SceneFade 적용.

> Shorts는 기본이 cut-first이므로 규칙 1, 3이 자연 적용. 별도 조치 불필요.

### Longform TSX 패턴

```tsx
// Chain Recall 패턴: SceneFade 분리
export const Freeform: React.FC<FreeformProps> = ({ ... }) => {
  return (
    <AbsoluteFill>
      <AnimatedBackground />
      {/* 1. Recalled 요소: SceneFade 밖 — frame 0 즉시, fade 없음 */}
      <div style={{ position: "absolute", top: 120, left: 0, width: "100%" }}>
        {/* step bar: transform만 적용 (이전 step → ✓, 현재 step 활성화) */}
      </div>
      {/* 2. 새 콘텐츠: SceneFade 안 — 정상 fade in/out */}
      <SceneFade>
        <div style={{ position: "absolute", top: 280, left: 60 }}>
          {/* 이 단계의 고유 콘텐츠 */}
        </div>
      </SceneFade>
      <ProgressBar />
    </AbsoluteFill>
  );
};
```

---

## 자동 감지 신호

Art Direction 단계에서 대본 전체를 읽을 때, 아래 신호를 탐지:

| 신호 | 대본 마커 | 감지 근거 |
|------|----------|----------|
| **명시적 콜백** | "앞서 살펴본", "위에서 설명한", "다시 돌아가서", "처음에 보여드린" | 직접적 참조 표현 |
| **개념 재등장** | 동일 기술 용어가 3+ 슬라이드 간격으로 재등장 | 용어 빈도 분석 |
| **점진적 구축** | "다음 단계", "4번째", "더 나아가서", 순번 나열 | 단계적 확장 패턴 |
| **대비 쌍** | "문제는"→"해결책은", "이전에는"→"이제는" | 대립 구조 |
| **반복 엔티티** | 고유명사(도구명, 프레임워크명) 3회+ 등장 | 명사 빈도 |

감지 결과가 0개면 → "Animation Memory: 해당 없음"으로 넘어감. 시스템은 완전히 선택적.

---

## 가드레일

이 시스템의 남용은 오히려 영상 품질을 떨어뜨린다. 회상은 **서사적 필연성**이 있을 때만 사용:

- **슬라이드 거리 < 3**: recall 금지 — 인접 장면은 연속 시청으로 이미 연결됨. **단, Chain Recall 체인 내 연속 슬라이드는 예외**
- **영상 당 최대**: longform 3-4회, shorts 1-2회 **(Chain Recall 그룹은 1회로 카운트)**
- **Chain Recall 상한**: 1그룹 최대 6 슬라이드. 초과 시 레이아웃 전환으로 시각 리셋
- **대본 뒷받침 필수**: 대본에서 개념이 실제로 재등장하거나 콜백하지 않으면 recall 금지
- **모드 불일치**: 소스가 Manim이고 타겟이 TSX면 recall 불가 (또는 반대)
- **강제 recall 금지**: 대본이 뒷받침하지 않는 시각적 연결을 억지로 만들지 않음
- **echo 남용 금지**: echo는 영상 전체에서 최대 1-2회
- **레이아웃 빈도 적용**: RECALL 슬라이드도 기존 "레이아웃 max 3회" 규칙에 포함됨. 만약 RECALL이 빈도를 초과하면 `compare`나 `echo`로 recall_type 변경 (다른 레이아웃 사용)
- **우선순위** (기회 > 상한 시): (1) 명시적 콜백 최우선, (2) 의미 있는 변환이 동반되는 개념 재등장, (3) 점진적 구축. 먼저 탈락: echo/compare 기회

---

## Slide Table Memory 컬럼

`Memory` 컬럼 추가. 표기: `SAVE:id` | `RECALL:id:type` | `-`

```
| 3  | MCP 아키텍처 설명  | TSX | diagram-flow | ... | SAVE:mcp-arch            |
| 15 | MCP 확장 기능      | TSX | diagram-flow | ... | RECALL:mcp-arch:expand   |
```

---

## SAVE/RECALL 작성법

**SAVE**: TSX 작성 후 구조적 요소(노드/바/카드)의 `(x, y, w, h, color, label)`을 `animation-memory.json` entries에 append. 장식(glow, particle) 제외.

**RECALL**:
1. JSON에서 `source_entry_id`의 `visual_snapshot` 찾기 (부족 시 소스 TSX 직접 읽기)
2. 소스 요소를 **frame 0에 즉시 표시** (입장 애니메이션 없이)
3. `recall_type`에 따라 변형 적용 (§ recall_type 5종 참조)
4. 소스 비주얼 좌표/색상이 원본과 정확히 일치하는지 검증

**Chain Recall 추가**: 직전 슬라이드의 **누적 변형 상태**를 재현. Seamless Handoff 3규칙 적용.

---

## 배치 디스패치 규칙

- SAVE→RECALL 쌍을 같은 배치에 우선 배정. 크로스 배치 시 SAVE 먼저 완료
- Fallback: entry 못 찾으면 `transformation` + `end_state_description` 참고, `echo`/`compare` 권장
- 동시 쓰기 방지: 복수 에이전트 시 `animation-memory-batch-N.json`에 별도 저장 → 메인 세션이 병합
