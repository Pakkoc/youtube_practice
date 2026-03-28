# AI 영상 자동화 워크숍 교육 자료

> 원데이 클래스 (10:00 ~ 18:00)
> 대상: Claude Code 입문자 (코딩 경험 불필요)

### Padlet (자료 공유)

수업 중 사용하는 프롬프트, 수강생 아웃풋, 참고 자료는 모두 Padlet에서 공유합니다:

> **https://padlet.com/aisamhottman/asmr-250328-yb184f0wzhdk4x8r**

---

## 문서 목록

### 오전: 설치 & 첫 영상 (입문)

| # | 문서 | 내용 | 비고 |
|:-:|------|------|------|
| 00 | [timetable](00-timetable.md) | 타임테이블 + 시스템 개요 | 수업 시작 시 |
| 01 | [hands-on-setup](01-hands-on-setup.md) | 실습: 설치 + 첫 영상 | 오전 내내 |

### 설치 대기 중 읽기 (입문)

| # | 문서 | 내용 | 비고 |
|:-:|------|------|------|
| 02 | [architecture](02-architecture.md) | 아키텍처 (비유 중심) | npm install 동안 |
| 03 | [claude-code-basics](03-claude-code-basics.md) | Claude Code 기초 사용법 | .env 설정 후 |
| 04 | [skills-system](04-skills-system.md) | Skills & Commands 시스템 | 파이프라인 대기 중 |
| 05 | [slide-generation](05-slide-generation.md) | 슬라이드 + 리버스 프롬프팅 | 렌더링 대기 중 |

### 오후 전반: 멀티포맷 & 워크플로우 (중급)

| # | 문서 | 내용 | 비고 |
|:-:|------|------|------|
| 06 | [pipeline-reference](06-pipeline-reference.md) | 파이프라인 상세 (API 모드) | 쇼츠/캐러셀 실습 |
| 07 | [multi-format-strategy](07-multi-format-strategy.md) | 대본 1개 → 영상+쇼츠+캐러셀 | 멀티포맷 실습 |
| 08 | [advanced-workflows](08-advanced-workflows.md) | 부분 재실행, 배치 생산, 복구 | 워크플로우 심화 |

### 오후 후반: 브랜딩 & 스킬 (심화)

| # | 문서 | 내용 | 비고 |
|:-:|------|------|------|
| 09 | [config-customization](09-config-customization.md) | 설정 & 커스터마이징 | 설정 변경 |
| 10 | [visual-identity](10-visual-identity.md) | 나만의 채널 디자인 시스템 | 브랜딩 실습 |
| 11 | [quality-iteration](11-quality-iteration.md) | 품질 반복 개선 & 설정 튜닝 | 품질 루프 |
| 12 | [content-strategy](12-content-strategy.md) | 소재 선정 & 운영 노하우 | 콘텐츠 전략 |
| 13 | [custom-skills](13-custom-skills.md) | 나만의 스킬 만들기 실습 | 스킬 제작 |
| 14 | [real-world-scenarios](14-real-world-scenarios.md) | 채널 유형별 실전 워크스루 | 자유 실습 |

### 집에서 활용: 업로드 자동화 (심화)

| # | 문서 | 내용 | 비고 |
|:-:|------|------|------|
| 15 | [youtube-upload-strategy](15-youtube-upload-strategy.md) | YouTube 비공개 자동 업로드 + SEO | 집에서 셋업 |

### 심화 학습 (선택)

| # | 문서 | 내용 | 비고 |
|:-:|------|------|------|
| 18 | [dev-methodology](18-dev-methodology.md) | FSD·SDD·DDD + CLAUDE.md 개발 방법론 + 오픈소스 레버리지 | 시스템 커스터마이징 시 |
| 19 | [skills-deep-dive](19-skills-deep-dive.md) | Skills 완전 해부 — 계층 구조, 동작 원리, 콘텐츠별 Skill 흐름 | Skills 심층 이해 |

### 참조 (수시)

| # | 문서 | 내용 |
|:-:|------|------|
| 16 | [faq-troubleshooting](16-faq-troubleshooting.md) | FAQ & 에러 해결 |
| 17 | [quick-reference](17-quick-reference.md) | 치트시트 (명령어/환경변수) |

---

## 하루 흐름 요약

```
10:00  ┌─ 설치 & 환경 구축 (Fork, Clone, npm, uv, .env)
       │  └─ 대기 시간에 02~05 문서 읽기
11:10  ├─ 첫 영상 생성 (/generate-video + 파이프라인)
12:00  ├─ 점심
13:30  ├─ 쇼츠 + 캐러셀 (멀티포맷)
14:15  ├─ 고급 워크플로우 + 품질 개선
15:00  ├─ 비주얼 아이덴티티 + 스킬 만들기
16:30  ├─ 자유 실습 + Q&A
17:30  └─ 마무리
```

---

## 사전 준비

수업 전 `install-guideline.md` (프로젝트 루트)의 **숙제 1 + 숙제 2**를 완료해 주세요.

### 필수 체크리스트

- [ ] Node.js 22+, Git, Python 3.13+, VS Code 설치
- [ ] Claude Code CLI 설치 + 로그인
- [ ] FFmpeg, uv 설치
- [ ] GitHub, Anthropic, ElevenLabs, Google AI Studio, Serper, OpenAI 가입

---

## 강사 참고

### API 키 확인
- 참가자 전원 `.env` 파일에 4개 필수 키 (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, ELEVENLABS_API_KEY) + 3개 선택 키가 입력되었는지 확인
- ElevenLabs 크레딧 잔액 확인

### ElevenLabs Voice ID
- 강사의 Voice ID: `config/config.api.yaml`의 `tts.elevenlabs.voice_id` 참조
- 참가자에게 직접 공유하거나, Fork한 저장소에 이미 포함

### API 모드 실행
- 모든 파이프라인 명령어 앞에 `CONFIG_PROFILE=api` 추가
- 또는 `.env`에 `CONFIG_PROFILE=api` 추가
