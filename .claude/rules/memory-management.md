# Memory Management Rules

## 저장소 구조

```
memory/
  MEMORY.md              # 인덱스 전용 (내용 X, 링크만)
  feedback_*.md          # 사용자 피드백/교정 — "이렇게 하지 마" 또는 "이게 맞아"
  project_*.md           # 프로젝트 맥락/의사결정 — 코드/git에서 알 수 없는 배경
  reference_*.md         # 외부 시스템 참조 포인터
  learnings/             # 실수에서 배운 교훈, 엣지케이스, gotcha
  daily/                 # 일일 작업 로그 (세션 간 맥락 연결)
```

## 분류 판단 (Decision Tree)

새 정보 발생 시 순서대로 판단:

1. **"어떻게 행동해야 하는가"** → CLAUDE.md 수정 제안 (자의적 수정 금지)
2. **"도메인별 작업 규칙"** → `.claude/rules/`
3. **"검증된 반복 절차"** → `.claude/commands/` (스킬, /skill-creator로만 관리)
4. **"실수/예외에서 배운 것"** → `memory/learnings/`
5. **"사용자가 교정/확인한 것"** → `memory/feedback_*.md`
6. **"프로젝트 맥락/의사결정"** → `memory/project_*.md`
7. **"외부 시스템 참조"** → `memory/reference_*.md`
8. **위 어디에도 해당 안 됨** → `memory/daily/YYYY-MM-DD.md`

## 수명 관리

| 저장소 | 수명 | 정리 기준 |
|--------|------|-----------|
| feedback_* | 영구 | 관련 기능이 제거되면 삭제 |
| learnings/ | 영구 | 분기별 점검 — 코드에 반영 완료된 것은 삭제 |
| project_* | 가변 | 프로젝트 방향 변경 시 업데이트 or 삭제 |
| reference_* | 가변 | 링크 깨지면 삭제 |
| daily/ | **7일** | 7일 후: 중요한 것 → 적합한 카테고리로 승격, 나머지 삭제 |

## 금지 규칙

1. **중복 저장 금지** — 동일 정보를 2곳에 넣지 않음
2. **MEMORY.md에 내용 직접 작성 금지** — 인덱스(링크)만 기록
3. **CLAUDE.md 자의적 수정 금지** — 수정 필요 시 제안만
4. **메모리 자의적 삭제 금지** — 정리 필요 시 먼저 보고
5. **코드에서 알 수 있는 것 저장 금지** — 파일 경로, 함수명, git 히스토리 등

## 메타데이터 (모든 항목에 필수)

```
<!-- added: YYYY-MM-DD | source: {user-instruction|self-learned|error-correction} | related: {관련 경로} -->
```

## Daily Log 형식

```markdown
# YYYY-MM-DD

## 수행 작업
- [프로젝트/기능] 작업 내용 요약

## 미완료/이슈
- 내일 이어서 할 것

## 승격 후보
- daily에서 상위 카테고리로 옮길 만한 내용
```
