# Remotion 레이아웃 패턴 레퍼런스

> 이 문서는 참고 자료입니다. 실제 템플릿 TSX 파일은 삭제되었으며, Freeform TSX가 유일한 슬라이드 생성 방식입니다.

## 개요

아래 11개 레이아웃 패턴은 과거 템플릿 모드에서 사용되었던 구조입니다.
Freeform TSX 작성 시 **구조적 영감**으로 활용할 수 있지만, 해당 TSX 컴포넌트는 더 이상 존재하지 않습니다.
패턴을 참고하되, 콘텐츠에 맞게 자유롭게 변형하여 사용합니다.

## 레이아웃 패턴 카탈로그

### 타이틀/인트로 패턴
| 패턴 | 활용 장면 | 핵심 구조 |
|------|----------|----------|
| **TitleSubtitle** | 섹션 시작, 주제 전환 | 중앙 정렬 제목 + 부제목, `accentWord` 강조 |

### 목록/설명 패턴
| 패턴 | 활용 장면 | 핵심 구조 |
|------|----------|----------|
| **BulletList** | 개념 나열 | 제목 + 2-4개 항목, 교대 진입 애니메이션 |
| **TypewriterGrid** | 다중 키워드 표시 | 아이콘+텍스트 그리드 (2-6개), 타이핑 효과 |

### 숫자/통계 패턴
| 패턴 | 활용 장면 | 핵심 구조 |
|------|----------|----------|
| **BigNumber** | 핵심 수치 강조 | 대형 숫자 (카운터 애니메이션) + 설명 텍스트 |
| **StatsDashboard** | 복수 지표 비교 | 2-4개 통계 카드, 각각 숫자+라벨 |

### 비교 패턴
| 패턴 | 활용 장면 | 핵심 구조 |
|------|----------|----------|
| **CompareTwo** | 좌우 대립 비교 | 좌/우 패널 + 항목 목록, `accentSide` 강조 |
| **BeforeAfter** | 전후 변화 | 상/하 또는 좌/우 전후 비교 항목 |

### 흐름/프로세스 패턴
| 패턴 | 활용 장면 | 핵심 구조 |
|------|----------|----------|
| **ProcessFlow** | 단계별 절차 | 제목 + 2-5개 단계 (화살표 연결) |
| **VerticalTimeline** | 시간순 정리 | 수직 타임라인 + 이벤트 노드 |

### 인용/메시지 패턴
| 패턴 | 활용 장면 | 핵심 구조 |
|------|----------|----------|
| **QuoteHighlight** | 핵심 메시지 1줄 | 큰 텍스트 + 형광펜 애니메이션, `accentWord` |
| **DramaticQuote** | 극적 인용 | 큰 인용문 + 키워드 배지 + 화자 표시 |

## Freeform TSX에서의 활용법

위 패턴은 **구조적 참고**입니다. Freeform TSX 작성 시:

1. **패턴 조합**: 하나의 슬라이드에 여러 패턴 요소를 혼합 가능
2. **시각 요소 추가**: SVG 아이콘, 다이어그램, 차트 등 자유롭게 추가
3. **레이아웃 변형**: 패턴의 배치/비율을 콘텐츠에 맞게 조정
4. **애니메이션 맞춤**: `interpolate()`, `spring()` 등 자유롭게 적용

### 예시: BulletList 패턴을 Freeform으로 확장

```tsx
// 단순 BulletList (X) → SVG 아이콘 그리드 + 설명 (O)
export const FreeformSlide: React.FC<FreeformCardProps> = ({ durationInFrames }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.BG_PRIMARY }}>
      <h2>핵심 개념</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40 }}>
        {items.map((item, i) => (
          <div key={i} style={{ opacity: interpolate(frame, [i*15, i*15+20], [0,1]) }}>
            <svg>...</svg>
            <span>{item.label}</span>
            <p>{item.desc}</p>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
```

## 시각 강화 컴포넌트 (재사용 가능)

`remotion/src/design/`, `remotion/src/motifs/` 에서 import 가능:
- SceneFade (입/퇴장 페이드)
- 형광펜 하이라이트
- 그라디언트 accentWord
- 프로그레스 바
- 적응형 폰트 사이징
- SVG 인용부호

## TSX 파일 위치

- Freeform 슬라이드: `remotion/src/slides/Freeform.tsx`, `FreeformSlot1-4.tsx`
- 디자인 토큰: `remotion/src/design/{theme,animations,fonts}.ts`
- 모티프 라이브러리: `remotion/src/motifs/{entries,emphasis,decorations}/`
