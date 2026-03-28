# TTS 발음 사전 강화 워크플로

Claude Code가 직접 대본을 분석하여 `config/tts_dictionary.yaml`에 미등록 영어/숫자 표현의 한글 발음을 추가합니다.

## 왜 이 워크플로가 필요한가

파이프라인 Step 1.5의 `enhance_tts_dictionary()`는 GPT-5.1 API를 호출하여 발음을 생성합니다.
하지만 이 함수는 미등록 단어가 0개면 API를 호출하지 않습니다:

```python
if not new_words:
    logger.info("사전 강화: 미등록 영어 토큰 없음")
    return dictionary  # ← API 호출 없이 즉시 반환
```

Claude Code가 이 워크플로로 사전을 미리 보강하면 → 파이프라인에서 new_words=0 → GPT-5.1 호출 없음.
B-roll의 `prompts.json`과 동일한 "사전 생성 → 파이프라인 skip" 패턴입니다.

---

## 전체 흐름

```
script.txt
  → Step 1: 프로젝트 확인
  → Step 2: 기존 사전 로드
  → Step 3: 대본 스캔 (영어/숫자 추출)
  → Step 4: 한글 발음 생성 (Claude Code 직접)
  → Step 5: 사전 파일 업데이트
  → Step 6: 검증
```

---

## Step 1: 프로젝트 확인

1. `projects/$PROJECT/` 디렉토리 존재 확인
2. `script.txt` 읽기 (또는 `paragraphs/*.txt`가 있으면 그쪽 사용)
3. 전체 텍스트 합산

## Step 2: 기존 사전 로드

`config/tts_dictionary.yaml` 읽기:
- `tts_pronunciation:` 하위의 모든 key-value 파악
- 현재 항목 수 확인 (참고용)

## Step 3: 대본 스캔

### 영어 단어 추출 규칙

**추출 대상** (정규식 `[A-Za-z]{2,}`):
- 2글자 이상의 영어 단어/약어
- 복합어도 개별 토큰으로 분리됨 (예: "Machine Learning" → "Machine", "Learning")

**복합 용어 주의**:
- 개별 토큰 외에 복합 표현도 찾기 (예: "Fine Tuning", "Machine Learning")
- 사전에는 복합 키와 개별 키 모두 등록 (긴 키가 먼저 매칭됨)
- 예: `Machine Learning: 머신러닝` + `Machine: 머신` (필요시)

### 제외 대상 1: TTS가 잘 처리하는 일반 단어

다음 단어는 ElevenLabs TTS가 올바르게 발음하므로 사전 등록 불필요:

```
is, the, of, and, or, in, to, for, by, at, on, it, as, an, be, do, if,
so, no, up, my, we, he, me, us, am, not, but, all, can, had, has, was,
are, you, his, her, its, our, who, how, new, now, may, one, two, get,
got, let, say, see, use, way, day, too, any, few, old, own, set, run,
try, ask, put, end, why, big, top, also, just, than, then, them, they,
this, that, with, from, been, have, will, what, when, your, more, make,
like, over, such, take, each, only, very, into, some, well, back, much, good
```

### 제외 대상 2: 기존 사전에 이미 등록된 단어

대소문자 무시 비교 (`"openai"` == `"OpenAI"`).

### 출력

- 미등록 토큰 리스트를 사용자에게 보고
- **0개면 "사전 강화 불필요" → 종료** (Step 4-6 skip)

## Step 4: 한글 발음 생성

Claude Code가 직접 한글 발음을 결정합니다. API 호출 없음.

### 발음 규칙

| 유형 | 규칙 | 예시 |
|------|------|------|
| 브랜드명 | 한국에서 통용되는 한국어 | OpenAI = 오픈에이아이 |
| 약어 | 각 글자를 한국어로 읽기 | API = 에이피아이, GPU = 지피유 |
| 기술 용어 | 자연스러운 음차 | Embedding = 임베딩, Container = 컨테이너 |
| 혼합 영숫자 | 자연스럽게 읽기 | H100 = 에이치백, RTX 5090 = 알티엑스 오천구십 |
| 버전 번호 | 한국어 읽기 | v2.1 = 버전 이쩜일, 3.0 = 삼쩜영 |
| 복합어 | 하나의 단위로 음차 | Machine Learning = 머신러닝, Fine Tuning = 파인튜닝 |

### 판단 기준
- 한국 IT 커뮤니티에서 통용되는 발음을 우선
- 확신 없으면 소리 그대로 음차
- 기존 사전 항목의 패턴 참고 (일관성 유지)

### 결과 출력 (확인 대기 없이 즉시 진행)

생성된 발음 목록을 간략히 출력 후 **바로 Step 5로 진행**:

```
✅ 3개 등록: Kubernetes=쿠버네티스, Terraform=테라폼, ...
```

> 사용자 확인을 기다리지 않는다. 발음이 명백히 틀린 경우만 사후에 수정.

## Step 5: 사전 파일 업데이트

`config/tts_dictionary.yaml` 파일 끝에 새 항목을 append합니다.
기존 구조를 절대 건드리지 않고, 파일 끝에만 추가합니다.

### YAML 쓰기 규칙 (반드시 준수)

**형식**: 2-space 들여쓰기 + key: value (빈 줄 하나 후 시작)

```yaml

  NewTerm: 뉴텀
  "2.0": 이쩜영
```

**따옴표가 필요한 키** (쌍따옴표로 감싸기):

1. 숫자/소수점으로 파싱되는 값: `"2.0"`, `"100"`, `"3.5"`
2. YAML 예약어: `"true"`, `"false"`, `"null"`, `"yes"`, `"no"`, `"on"`, `"off"`
3. 특수문자로 시작하는 경우: `#`, `-`, `[`, `{`, `&`, `*`, `!`, `|`, `>`, `'`, `"`, `%`, `@`, `` ` ``, `?`
4. 콜론+공백(`: `)을 포함하거나, 콜론으로 끝나는 경우

**그 외 키는 따옴표 없이 그대로:**
```yaml
  Kubernetes: 쿠버네티스
  Fine Tuning: 파인튜닝
```

### Edit 도구 사용

Read로 파일 끝 부분을 읽고, Edit 도구로 파일 끝에 새 항목을 append합니다.
전체 파일을 다시 쓰지 말 것 (기존 항목 순서와 주석 보존).

## Step 6: 검증

```bash
cd /c/Users/hoyoung/Desktop/Youtube-Automation
uv run python3 -c "
from features.normalize_text import load_tts_dictionary
from features.normalize_text.enhance import enhance_tts_dictionary
from features.split_paragraphs.lib import split_script
text = open('projects/$PROJECT/script.txt', encoding='utf-8').read()
script = split_script(text)
d = load_tts_dictionary()
enhance_tts_dictionary(script.paragraphs, d)
"
```

**성공 기준**: `"사전 강화: 미등록 영어 토큰 없음"` 로그 출력.
이 로그가 나오면 파이프라인에서 GPT-5.1 API 호출이 발생하지 않습니다.

만약 아직 미등록 토큰이 남아있다면 → Step 3부터 다시 반복.

---

## 주의사항

- YAML 파일 전체를 다시 쓰지 말 것 (append만)
- 기존 항목과 중복 추가 주의 (대소문자 무시 비교)
- 숫자 키는 반드시 따옴표 처리 (YAML이 float로 파싱)
- 복합 키 순서 고려: 긴 키가 먼저 매칭됨 (Claude Code > Claude) — 관련 복합어도 함께 등록
