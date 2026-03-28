---
name: detect-releases
description: "Claude Code GitHub 릴리즈 감지 → 필터링 → Auto-Update 카드 생성. anthropics/claude-code 릴리즈 노트를 분석하여 비개발자 쇼츠 콘텐츠 후보를 자동 선별."
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: "[--dry-run] [--since <tag>]"
---

# /detect-releases — CC 릴리즈 감지 + Auto-Update 카드 생성

`anthropics/claude-code` GitHub 릴리즈를 감지하고, 비개발자 쇼츠 콘텐츠로 적합한 항목을 필터링하여 Auto-Update 카드를 생성한다.

**Arguments**:
- (없음): 새 릴리즈 감지 + 카드 생성
- `--dry-run`: 파일 수정 없이 결과만 출력
- `--since <tag>`: 특정 태그 이후 릴리즈만 처리 (e.g., `--since v2.1.70`)

---

## Step 1: 릴리즈 가져오기

### 1-1. GitHub API로 릴리즈 목록 조회

```bash
gh api repos/anthropics/claude-code/releases --jq '[.[] | {tag_name, published_at, body, html_url}]'
```

### 1-2. 처리 대상 결정

- `cc-content/releases_state.json`을 읽는다 (없으면 첫 실행)
- **`--since <tag>` 지정 시**: 해당 태그 이후 릴리즈만 처리
- **state 파일 있을 때**: `last_checked_tag` 이후 릴리즈만 처리
- **첫 실행 (state 파일 없음)**: 최근 5개만 처리

처리 대상이 없으면 "No new releases since {tag}" 출력하고 종료.

---

## Step 2: 릴리즈 노트 파싱

각 릴리즈의 `body` (Markdown)를 파싱한다:

1. 섹션별 분리: Highlights, Features, Fixes, Other 등 (`##` 또는 `###` 헤더 기준)
2. 각 bullet point(`-` 또는 `*`)를 개별 아이템으로 추출
3. 아이템별 메타데이터 구성:

```
- release_tag: "v2.1.76"
- release_date: "2026-03-15"
- section: "Features"
- title: 아이템 첫 줄 요약
- description: 전체 텍스트
- source_url: 릴리즈 html_url
```

---

## Step 3: 필터링 + 점수 매기기

### Hard Rules (점수 계산 전에 적용)

| Rule | Action |
|------|--------|
| 순수 버그픽스 (기능 변화 없음) | **Hard skip** → 0점 |
| 의존성 업데이트 (bump, upgrade) | **Hard skip** → 0점 |
| CI/CD, 테스트, 리팩토링 | **Hard skip** → 0점 |
| 새 슬래시 명령 | **Hard pass** → 20점 |
| 새 모드/인터페이스 | **Hard pass** → 20점 |
| 새 통합 (MCP, IDE 등) | **Hard pass** → 20점 |

### 점수 기준 (Hard rule에 해당하지 않는 항목)

너(Claude)가 각 아이템을 읽고 4가지 기준으로 0~10점을 매긴다:

| 기준 | 가중치 | 높은 점수 (8~10) | 낮은 점수 (0~3) |
|------|--------|-----------------|----------------|
| 비개발자 관심도 | 3x | 새 명령어, UI 변화, 직관적 기능 | 내부 최적화, API 변경 |
| 설명 가능성 | 2x | 60초 데모 가능, 시각적 결과 | 추상적 구조 변경 |
| 신규성 | 2x | 완전히 새로운 기능 | 기존 기능 미세 조정 |
| 와우 팩터 | 1x | "이런 것도 돼?" 반응 | 예상 가능한 변화 |

**총점** = (비개발자 관심도 x 3) + (설명 가능성 x 2) + (신규성 x 2) + (와우 팩터 x 1)
→ 만점 80점, 정규화하여 0~20 스케일로 변환: `final_score = total / 4`

### 결과 분류

| 점수 | 분류 | 처리 |
|------|------|------|
| 14점 이상 | **PASS** | 카드 생성 대상 |
| 8~13점 | **BORDERLINE** | 사용자 확인용 출력 |
| 8점 미만 | **SKIP** | 무시 |

### 점수표 출력

모든 아이템의 점수표를 테이블로 출력한다:

```
| Item | Section | 관심도 | 설명성 | 신규성 | 와우 | Score | Result |
|------|---------|--------|--------|--------|------|-------|--------|
| Tab completion hints | Features | 5 | 6 | 4 | 3 | 11 | BORDERLINE |
| New /memory command | Highlights | 9 | 8 | 10 | 9 | 18 | PASS |
| Fix typo in help | Fixes | - | - | - | - | 0 | HARD SKIP |
```

---

## Step 4: 에버그린 카드와 중복 제거

`cc-content/cards.json`의 기존 카드 목록을 읽고, PASS된 각 아이템과 의미적으로 비교한다.

### 비교 기준

- 기존 카드의 `feature_name`, `dev_term`, `one_line`, `flow_steps`를 참조
- 같은 기능의 개선/확장인지, 완전히 새로운 기능인지 판단

### 결과 분류

| 분류 | 설명 | 처리 |
|------|------|------|
| **NEW** | 기존 카드에 없는 새 기능 | Step 5에서 카드 생성 |
| **ENHANCEMENT** | 기존 카드 기능의 개선 | 업데이트 제안만 출력 (카드 생성 안 함) |
| **DUPLICATE** | 기존 카드와 동일 | 스킵 |

ENHANCEMENT의 경우 출력 예시:
```
ENHANCEMENT: "Improved /compact with auto-trigger" → 기존 cc-004 (/compact) 업데이트 제안
  제안: one_line에 자동 트리거 기능 추가 언급
```

---

## Step 5: Auto-Update 카드 생성

`--dry-run`이면 이 Step을 건너뛰고 Step 6으로 이동한다.

### 5-1. 카드 ID 부여

- 형식: `cc-au-{NNN}` (zero-padded 3자리)
- `cc-content/cards.json`에서 기존 `cc-au-*` 카드의 최대 번호 + 1부터 시작
- 없으면 `cc-au-001`부터

### 5-2. content_format 자동 배정

| 릴리즈 아이템 유형 | content_format |
|------------------|---------------|
| 새 명령어, 새 플래그, 새 옵션 | `situation` |
| 새 개념, 새 모델 기능 | `translator` |
| 새 워크플로우, 새 통합, 새 파이프라인 | `flow` |

### 5-3. 카드 필드 구성

너(Claude)가 릴리즈 노트 내용을 바탕으로 각 필드를 **직접** 작성한다:

```json
{
  "feature_id": "cc-au-001",
  "feature_name": "릴리즈 아이템 제목",
  "category": "slash_command | workflow | concept | config_file",
  "difficulty": 1~3,
  "dev_term": "개발자 용어",
  "plain_term": "비개발자가 이해할 수 있는 한마디",
  "one_line": "한 줄 설명 (비개발자 대상)",
  "use_case": "이럴 때 쓰세요",
  "flow_steps": ["단계1", "단계2", "단계3", "단계4"],
  "content_format": "situation | translator | flow",
  "source": "auto-update",
  "status": "pending",
  "created_at": "ISO 8601 timestamp",
  "publish_date": null,
  "source_url": "릴리즈 html_url",
  "filter_score": 점수 (정수)
}
```

### 5-4. 저장

1. `cc-content/cards.json`의 `cards` 배열에 새 카드를 append
2. `last_updated` 타임스탬프 갱신
3. `cc-content/releases_state.json` 업데이트:

```json
{
  "last_checked_tag": "가장 최신 처리한 태그",
  "last_checked_at": "ISO 8601 timestamp",
  "processed_releases": [
    {
      "tag": "v2.1.76",
      "processed_at": "ISO 8601 timestamp",
      "cards_created": ["cc-au-001", "cc-au-002"]
    }
  ]
}
```

state 파일이 이미 있으면 `processed_releases` 배열에 append하고, `last_checked_tag`와 `last_checked_at`을 갱신한다.

---

## Step 6: 요약 출력

```
=== Release Detection Complete ===
Releases checked: v2.1.76, v2.1.75, v2.1.74
Items found: 12 / Passed: 3 / Borderline: 2 / Skipped: 7
Deduped: 1 (ENHANCEMENT for cc-004)

New cards created:
  cc-au-001 (flow, 18점) - "Agent Teams with Custom Roles"
  cc-au-002 (situation, 16점) - "New /memory Command"

Borderline (manual review):
  "Improved tab completion" (11점)
  "Better error messages in Plan Mode" (9점)

Enhancements suggested:
  cc-004 (/compact): 자동 트리거 기능 추가

Next steps:
  /generate-cc-script cc-au-001
  /generate-cc-script cc-au-002
```

`--dry-run`이면 "New cards created" 대신 "Cards that WOULD be created (dry-run)" 으로 표시하고, 파일 수정이 없었음을 명시한다.
