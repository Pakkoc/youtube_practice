# Carousel Patterns — Extended Layout Patterns (J-W)

> 14 additional layout patterns for data visualization, code/tech, comparison, emphasis, mixed, and intro categories.
> Part of the carousel patterns suite — see `carousel-patterns-layouts.md` for base patterns A-I.

---

## Layout Patterns (Extended)

### J. Stat Dashboard
3-4 KPI cards in a grid layout. Each card shows a big number + label.

```tsx
const stats = [
  { value: "2.4M", label: "월간 사용자", trend: "+23%" },
  { value: "99.9%", label: "가동률", trend: "" },
  { value: "4.8", label: "평균 평점", trend: "+0.3" },
  { value: "150+", label: "글로벌 고객사", trend: "+12" },
];

{/* Title */}
<div style={{
  position: "absolute",
  top: 80,
  left: 72,
  right: 72,
}}>
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
  }}>
    핵심 지표 한눈에
  </div>
</div>

{/* KPI Grid */}
<div style={{
  position: "absolute",
  top: 200,
  left: 72,
  right: 72,
  display: "flex",
  flexWrap: "wrap" as const,
  gap: 24,
}}>
  {stats.map((s, i) => (
    <div key={i} style={{
      width: 430,
      padding: "40px 32px",
      background: "rgba(255,255,255,0.04)",
      borderRadius: 20,
      border: "1px solid rgba(255,255,255,0.08)",
      display: "flex",
      flexDirection: "column",
      gap: 8,
    }}>
      <div style={{
        fontSize: 48,
        fontWeight: 800,
        fontFamily: FONT.family,
        color: colors.accent,
        letterSpacing: "-0.02em",
      }}>
        {s.value}
      </div>
      <div style={{
        fontSize: 20,
        fontWeight: 500,
        fontFamily: FONT.family,
        color: `${colors.text}88`,
      }}>
        {s.label}
      </div>
      {s.trend && (
        <div style={{
          fontSize: 16,
          fontWeight: 600,
          fontFamily: FONT.family,
          color: COLORS.TEAL,
        }}>
          {s.trend}
        </div>
      )}
    </div>
  ))}
</div>
```

### K. Progress Tracker
Goal-vs-progress bars with labels. Good for roadmap, completion status.

```tsx
const goals = [
  { label: "데이터 수집", progress: 100, color: COLORS.TEAL },
  { label: "모델 학습", progress: 75, color: colors.accent },
  { label: "테스트 검증", progress: 40, color: COLORS.ACCENT_BRIGHT },
  { label: "배포 준비", progress: 10, color: `${colors.text}66` },
];

<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 24,
}}>
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    marginBottom: 16,
  }}>
    프로젝트 진행 현황
  </div>

  {goals.map((g, i) => (
    <div key={i} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        fontSize: 22,
        fontFamily: FONT.family,
      }}>
        <span style={{ color: colors.text, fontWeight: 600 }}>{g.label}</span>
        <span style={{ color: g.color, fontWeight: 700 }}>{g.progress}%</span>
      </div>
      <div style={{
        width: "100%",
        height: 16,
        background: "rgba(255,255,255,0.05)",
        borderRadius: 8,
        overflow: "hidden",
      }}>
        <div style={{
          width: `${g.progress}%`,
          height: "100%",
          background: g.color,
          borderRadius: 8,
        }} />
      </div>
    </div>
  ))}
</div>
```

### L. Ranking List
Ranked items with bar visualization. Good for top-N lists.

```tsx
const rankings = [
  { rank: 1, label: "Python", value: 28.5, suffix: "%" },
  { rank: 2, label: "JavaScript", value: 21.3, suffix: "%" },
  { rank: 3, label: "TypeScript", value: 12.7, suffix: "%" },
  { rank: 4, label: "Java", value: 10.1, suffix: "%" },
  { rank: 5, label: "Go", value: 8.4, suffix: "%" },
];
const maxVal = Math.max(...rankings.map(r => r.value));

<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 24,
}}>
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    marginBottom: 16,
  }}>
    2026 프로그래밍 언어 순위
  </div>

  {rankings.map((r, i) => (
    <div key={i} style={{
      display: "flex",
      alignItems: "center",
      gap: 20,
    }}>
      <div style={{
        minWidth: 44,
        height: 44,
        borderRadius: 12,
        background: i === 0 ? colors.accent : "rgba(255,255,255,0.06)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 20,
        fontWeight: 800,
        fontFamily: FONT.family,
        color: i === 0 ? "#FFFFFF" : colors.text,
      }}>
        {r.rank}
      </div>
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 6 }}>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 22,
          fontFamily: FONT.family,
        }}>
          <span style={{ color: colors.text, fontWeight: 600 }}>{r.label}</span>
          <span style={{ color: `${colors.text}99`, fontWeight: 500 }}>
            {r.value}{r.suffix}
          </span>
        </div>
        <div style={{
          width: "100%",
          height: 10,
          background: "rgba(255,255,255,0.05)",
          borderRadius: 5,
          overflow: "hidden",
        }}>
          <div style={{
            width: `${(r.value / maxVal) * 100}%`,
            height: "100%",
            background: i === 0 ? colors.accent : `${colors.accent}88`,
            borderRadius: 5,
          }} />
        </div>
      </div>
    </div>
  ))}
</div>
```

### M. Code Snippet
Code block with syntax-like styling + description. For dev tutorials.

```tsx
{/* Centered wrapper */}
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 28,
}}>
  {/* Title */}
  <div style={{
    fontSize: 32,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
  }}>
    API 호출 예시
  </div>

  {/* Code block */}
  <div style={{
    padding: "32px 28px",
    background: "rgba(0,0,0,0.4)",
    borderRadius: 16,
    border: "1px solid rgba(255,255,255,0.1)",
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    fontSize: 20,
    lineHeight: 1.8,
    color: "#E0E0E0",
    whiteSpace: "pre" as const,
    overflow: "hidden",
  }}>
    <span style={{ color: "#C792EA" }}>const</span>
    {" result = "}
    <span style={{ color: "#82AAFF" }}>await</span>
    {" fetch("}
    <span style={{ color: "#C3E88D" }}>'/api/generate'</span>
    {", {\n"}
    {"  method: "}
    <span style={{ color: "#C3E88D" }}>'POST'</span>
    {",\n"}
    {"  body: JSON.stringify({ prompt })\n"}{"}"}
    {");"}
  </div>

  {/* Explanation */}
  <div style={{
    fontSize: 22,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}AA`,
    lineHeight: 1.6,
  }}>
    POST 요청으로 프롬프트를 전송하면 AI가 자동으로 결과를 생성합니다.
  </div>
</div>
```

### N. Terminal Output
CLI command + result display. For tool demos, setup guides.

```tsx
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 28,
}}>
  <div style={{
    fontSize: 32,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
  }}>
    설치 한 줄이면 끝
  </div>

  {/* Terminal window */}
  <div style={{
    borderRadius: 16,
    overflow: "hidden",
    border: "1px solid rgba(255,255,255,0.1)",
  }}>
    {/* Title bar */}
    <div style={{
      padding: "12px 20px",
      background: "rgba(255,255,255,0.06)",
      display: "flex",
      gap: 8,
    }}>
      <div style={{ width: 12, height: 12, borderRadius: 6, background: "#FF5F56" }} />
      <div style={{ width: 12, height: 12, borderRadius: 6, background: "#FFBD2E" }} />
      <div style={{ width: 12, height: 12, borderRadius: 6, background: "#27C93F" }} />
    </div>

    {/* Terminal body */}
    <div style={{
      padding: "28px 24px",
      background: "rgba(0,0,0,0.5)",
      fontFamily: "'JetBrains Mono', monospace",
      fontSize: 20,
      lineHeight: 2,
      color: "#E0E0E0",
    }}>
      <div>
        <span style={{ color: COLORS.TEAL }}>$</span>
        {" npx create-my-app@latest"}
      </div>
      <div style={{ color: `${colors.text}66` }}>
        Creating project...
      </div>
      <div>
        <span style={{ color: COLORS.TEAL }}>✓</span>
        {" 프로젝트 생성 완료 (2.3s)"}
      </div>
    </div>
  </div>
</div>
```

### O. Feature Matrix
Checkmark comparison table. For product comparisons, plan tiers.

```tsx
const features = [
  { name: "기본 기능", free: true, pro: true, ent: true },
  { name: "API 접근", free: false, pro: true, ent: true },
  { name: "팀 협업", free: false, pro: true, ent: true },
  { name: "전용 서버", free: false, pro: false, ent: true },
  { name: "SLA 보장", free: false, pro: false, ent: true },
];
const plans = ["Free", "Pro", "Enterprise"];

<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 24,
}}>
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    marginBottom: 8,
  }}>
    플랜 비교
  </div>

  {/* Header row */}
  <div style={{ display: "flex", gap: 0 }}>
    <div style={{ flex: 2 }} />
    {plans.map((p, i) => (
      <div key={i} style={{
        flex: 1,
        textAlign: "center" as const,
        fontSize: 20,
        fontWeight: 700,
        fontFamily: FONT.family,
        color: i === 1 ? colors.accent : `${colors.text}88`,
        padding: "12px 0",
      }}>
        {p}
      </div>
    ))}
  </div>

  {/* Feature rows */}
  {features.map((f, i) => (
    <div key={i} style={{
      display: "flex",
      alignItems: "center",
      padding: "16px 0",
      borderTop: "1px solid rgba(255,255,255,0.06)",
    }}>
      <div style={{
        flex: 2,
        fontSize: 22,
        fontWeight: 500,
        fontFamily: FONT.family,
        color: colors.text,
      }}>
        {f.name}
      </div>
      {[f.free, f.pro, f.ent].map((val, j) => (
        <div key={j} style={{
          flex: 1,
          textAlign: "center" as const,
          fontSize: 24,
        }}>
          {val ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="12" fill={`${COLORS.TEAL}20`} />
              <path d="M8 12l3 3 5-5" stroke={COLORS.TEAL}
                strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="12" fill="rgba(255,255,255,0.04)" />
              <path d="M8 12h8" stroke={`${colors.text}33`}
                strokeWidth="2" strokeLinecap="round" />
            </svg>
          )}
        </div>
      ))}
    </div>
  ))}
</div>
```

### P. Pros & Cons
Left-right split with green (pros) and red (cons) icons.

```tsx
const pros = ["설치 쉬움", "무료 사용", "활발한 커뮤니티"];
const cons = ["학습 곡선", "제한된 플러그인", "느린 빌드"];

<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 28,
}}>
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    textAlign: "center" as const,
  }}>
    장단점 비교
  </div>

  <div style={{ display: "flex", gap: 24 }}>
    {/* Pros */}
    <div style={{
      width: "48%",
      padding: "32px 28px",
      background: `${COLORS.TEAL}08`,
      borderRadius: 20,
      border: `1px solid ${COLORS.TEAL}20`,
    }}>
      <div style={{
        fontSize: 20,
        fontWeight: 700,
        fontFamily: FONT.family,
        color: COLORS.TEAL,
        marginBottom: 24,
        letterSpacing: "0.06em",
      }}>
        PROS
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {pros.map((p, i) => (
          <div key={i} style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            fontSize: 22,
            fontWeight: 500,
            fontFamily: FONT.family,
            color: colors.text,
          }}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M6 10l3 3 5-5" stroke={COLORS.TEAL}
                strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            {p}
          </div>
        ))}
      </div>
    </div>

    {/* Cons */}
    <div style={{
      width: "48%",
      padding: "32px 28px",
      background: "rgba(255,80,80,0.06)",
      borderRadius: 20,
      border: "1px solid rgba(255,80,80,0.15)",
    }}>
      <div style={{
        fontSize: 20,
        fontWeight: 700,
        fontFamily: FONT.family,
        color: "#FF6B6B",
        marginBottom: 24,
        letterSpacing: "0.06em",
      }}>
        CONS
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {cons.map((c, i) => (
          <div key={i} style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            fontSize: 22,
            fontWeight: 500,
            fontFamily: FONT.family,
            color: colors.text,
          }}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M6 6l8 8M14 6l-8 8" stroke="#FF6B6B"
                strokeWidth="2" strokeLinecap="round" />
            </svg>
            {c}
          </div>
        ))}
      </div>
    </div>
  </div>
</div>
```

### Q. Big Number
Single impactful number with context. High visual weight.

```tsx
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  textAlign: "center" as const,
}}>
  {/* Small label */}
  <div style={{
    fontSize: 20,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: colors.accent,
    letterSpacing: "0.1em",
    marginBottom: 24,
  }}>
    MONTHLY REVENUE
  </div>

  {/* Big number */}
  <div style={{
    fontSize: 120,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    letterSpacing: "-0.04em",
    lineHeight: 1,
  }}>
    $4.2M
  </div>

  {/* Accent line */}
  <div style={{
    width: 80,
    height: 3,
    background: colors.accent,
    borderRadius: 2,
    marginTop: 32,
    marginBottom: 32,
  }} />

  {/* Context description */}
  <div style={{
    fontSize: 26,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}88`,
    lineHeight: 1.5,
    maxWidth: 600,
  }}>
    전년 대비 340% 성장, 업계 평균의 2.5배
  </div>
</div>
```

### R. Highlight Box
Single key message in a prominent box. For takeaways, warnings, tips.

```tsx
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 28,
}}>
  {/* Section label */}
  <div style={{
    display: "inline-flex",
    padding: "6px 16px",
    background: `${colors.accent}15`,
    border: `1px solid ${colors.accent}30`,
    borderRadius: 20,
    fontSize: 16,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: colors.accent,
    letterSpacing: "0.06em",
    alignSelf: "flex-start",
  }}>
    KEY TAKEAWAY
  </div>

  {/* Highlight box */}
  <div style={{
    padding: "48px 40px",
    background: `${colors.accent}08`,
    borderRadius: 24,
    borderLeft: `4px solid ${colors.accent}`,
  }}>
    <div style={{
      fontSize: 36,
      fontWeight: 700,
      fontFamily: FONT.family,
      color: colors.text,
      lineHeight: 1.5,
    }}>
      핵심 메시지가 여기에 들어갑니다. 한 문장으로 독자의 시선을 사로잡아야 합니다.
    </div>
  </div>

  {/* Supporting text */}
  <div style={{
    fontSize: 22,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}88`,
    lineHeight: 1.6,
  }}>
    보충 설명이 필요한 경우 아래에 간결하게 추가합니다.
  </div>
</div>
```

### S. Testimonial
User review with avatar circle + quote. Social proof card.

```tsx
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  gap: 32,
}}>
  {/* Avatar circle */}
  <div style={{
    width: 100,
    height: 100,
    borderRadius: 50,
    background: `linear-gradient(135deg, ${colors.accent}40, ${COLORS.TEAL}40)`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 40,
    fontWeight: 700,
    fontFamily: FONT.family,
    color: colors.text,
  }}>
    JK
  </div>

  {/* Stars */}
  <div style={{ display: "flex", gap: 8 }}>
    {[1,2,3,4,5].map(i => (
      <svg key={i} width="28" height="28" viewBox="0 0 24 24"
        fill={i <= 5 ? "#FFD700" : `${colors.text}33`}>
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18
          6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
      </svg>
    ))}
  </div>

  {/* Quote */}
  <div style={{
    fontSize: 30,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: colors.text,
    lineHeight: 1.6,
    textAlign: "center" as const,
    maxWidth: 780,
  }}>
    "도입 후 작업 시간이 절반으로 줄었습니다. 팀 전체가 만족하고 있어요."
  </div>

  {/* Attribution */}
  <div style={{
    fontSize: 20,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}88`,
  }}>
    김지현 · 스타트업 CTO
  </div>
</div>
```

### T. Timeline
Vertical timeline with 3-5 events. For history, roadmap, process.

```tsx
const events = [
  { date: "2024.03", title: "프로토타입 출시", desc: "MVP 버전 공개" },
  { date: "2024.09", title: "시리즈 A 투자", desc: "50억원 유치" },
  { date: "2025.03", title: "글로벌 확장", desc: "일본·동남아 진출" },
  { date: "2025.12", title: "100만 사용자", desc: "MAU 100만 달성" },
];

<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
}}>
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    marginBottom: 40,
  }}>
    성장 타임라인
  </div>

  <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
    {events.map((e, i) => (
      <div key={i} style={{
        display: "flex",
        alignItems: "flex-start",
        gap: 24,
        paddingBottom: i < events.length - 1 ? 40 : 0,
      }}>
        {/* Timeline dot + line */}
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          minWidth: 24,
        }}>
          <div style={{
            width: 16,
            height: 16,
            borderRadius: 8,
            background: i === 0 ? colors.accent : `${colors.accent}44`,
            boxShadow: i === 0 ? `0 0 12px ${colors.accent}60` : "none",
          }} />
          {i < events.length - 1 && (
            <div style={{
              width: 2,
              height: 48,
              background: `${colors.text}15`,
              marginTop: 4,
            }} />
          )}
        </div>

        {/* Content */}
        <div style={{ paddingTop: -2 }}>
          <div style={{
            fontSize: 16,
            fontWeight: 600,
            fontFamily: FONT.family,
            color: colors.accent,
            marginBottom: 4,
          }}>
            {e.date}
          </div>
          <div style={{
            fontSize: 26,
            fontWeight: 700,
            fontFamily: FONT.family,
            color: colors.text,
            marginBottom: 4,
          }}>
            {e.title}
          </div>
          <div style={{
            fontSize: 20,
            fontWeight: 500,
            fontFamily: FONT.family,
            color: `${colors.text}88`,
          }}>
            {e.desc}
          </div>
        </div>
      </div>
    ))}
  </div>
</div>
```

### U. Split Image-Text
50/50 image + text split. For product showcases, visual stories.

```tsx
{/* Left half — Image area (placeholder with gradient) */}
<div style={{
  position: "absolute",
  top: 0,
  left: 0,
  width: "50%",
  height: "100%",
  background: `linear-gradient(135deg, ${colors.accent}15, ${COLORS.TEAL}10)`,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}}>
  {/* SVG placeholder icon or use Img component */}
  <svg width="120" height="120" viewBox="0 0 24 24" fill={`${colors.accent}30`}>
    <rect x="3" y="3" width="18" height="18" rx="2" stroke={colors.accent}
      strokeWidth="1.5" fill="none" />
    <circle cx="8.5" cy="8.5" r="1.5" fill={colors.accent} />
    <path d="M21 15l-5-5L5 21" stroke={colors.accent}
      strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
</div>

{/* Right half — Text content */}
<div style={{
  position: "absolute",
  top: 0,
  left: "50%",
  width: "50%",
  height: "100%",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  padding: "60px 48px 60px 40px",
  gap: 20,
}}>
  <div style={{
    display: "inline-flex",
    padding: "4px 12px",
    background: `${colors.accent}15`,
    borderRadius: 12,
    fontSize: 14,
    fontWeight: 600,
    fontFamily: FONT.family,
    color: colors.accent,
    alignSelf: "flex-start",
  }}>
    FEATURE
  </div>
  <div style={{
    fontSize: 34,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    lineHeight: 1.3,
  }}>
    직관적인 인터페이스
  </div>
  <div style={{
    fontSize: 22,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}AA`,
    lineHeight: 1.6,
  }}>
    복잡한 설정 없이 드래그 앤 드롭으로 워크플로우를 구성하세요.
    초보자도 5분 만에 시작할 수 있습니다.
  </div>
</div>
```

### V. Accordion (FAQ)
Question-answer pairs in expandable-looking cards.

```tsx
const faqs = [
  { q: "무료로 사용할 수 있나요?", a: "네, 기본 기능은 무료입니다. 고급 기능은 Pro 플랜에서 제공됩니다." },
  { q: "데이터는 안전한가요?", a: "모든 데이터는 AES-256으로 암호화되며 SOC 2 인증을 받았습니다." },
  { q: "팀 협업이 가능한가요?", a: "최대 50명까지 실시간 협업이 가능합니다." },
];

<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 24,
}}>
  <div style={{
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    marginBottom: 16,
  }}>
    자주 묻는 질문
  </div>

  {faqs.map((faq, i) => (
    <div key={i} style={{
      padding: "28px 32px",
      background: "rgba(255,255,255,0.04)",
      borderRadius: 16,
      border: "1px solid rgba(255,255,255,0.08)",
    }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 16,
      }}>
        <div style={{
          fontSize: 24,
          fontWeight: 700,
          fontFamily: FONT.family,
          color: colors.text,
        }}>
          {faq.q}
        </div>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M6 9l6 6 6-6" stroke={colors.accent}
            strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      <div style={{
        fontSize: 20,
        fontWeight: 400,
        fontFamily: FONT.family,
        color: `${colors.text}99`,
        lineHeight: 1.6,
      }}>
        {faq.a}
      </div>
    </div>
  ))}
</div>
```

### W. Chapter Divider
Section separator card with large number + title. Minimal content.

```tsx
<div style={{
  position: "absolute",
  top: 80, left: 72, right: 72, bottom: 80,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  textAlign: "center" as const,
}}>
  {/* Large chapter number */}
  <div style={{
    fontSize: 160,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: `${colors.accent}20`,
    lineHeight: 1,
    letterSpacing: "-0.04em",
  }}>
    02
  </div>

  {/* Chapter title */}
  <div style={{
    fontSize: 40,
    fontWeight: 800,
    fontFamily: FONT.family,
    color: colors.text,
    lineHeight: 1.3,
    marginTop: -20,
  }}>
    실전 적용 방법
  </div>

  {/* Accent line */}
  <div style={{
    width: 60,
    height: 3,
    background: colors.accent,
    borderRadius: 2,
    marginTop: 24,
  }} />

  {/* Optional subtitle */}
  <div style={{
    fontSize: 22,
    fontWeight: 500,
    fontFamily: FONT.family,
    color: `${colors.text}66`,
    marginTop: 20,
  }}>
    3가지 핵심 전략
  </div>
</div>
```
