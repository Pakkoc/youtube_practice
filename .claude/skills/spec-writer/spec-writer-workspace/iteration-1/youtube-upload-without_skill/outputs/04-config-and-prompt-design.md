# YouTube 업로드 기능 -- 설정 및 프롬프트 설계

## 1. YAML 설정 변경

### 1.1 `config/config.base.yaml` -- youtube 섹션 확장

```yaml
# 유튜브 설정
youtube:
  schedule:
    days: 5
    uploads_per_day: 2
  default_category: "28"  # Science & Technology

  # [추가] 업로드 설정
  upload:
    credentials_dir: "config/credentials"   # OAuth 인증 파일 위치
    default_privacy: "private"              # 기본 업로드 상태: private | unlisted | public
    chunk_size_mb: 5                        # Resumable Upload 청크 크기 (MB)
    metadata_model: "gpt-5.4-mini"          # 메타데이터 생성 LLM
```

### 1.2 `config/config.base.yaml` -- pipeline 섹션 확장

```yaml
pipeline:
  # ... (기존 tts, slides, broll, avatar, scenes)

  # [추가] 업로드 제어
  upload:
    auto_upload: false    # 파이프라인 완료 후 자동 업로드 (기본 OFF)
```


## 2. GPT 메타데이터 생성 프롬프트

### 2.1 시스템 프롬프트

```
당신은 YouTube 콘텐츠 전략가입니다.
주어진 대본을 분석하여 YouTube 영상의 메타데이터(제목, 설명, 태그)를 생성합니다.

## 규칙

### 제목 (title)
- 한국어 기준 40자 이내 권장 (최대 100자)
- 클릭을 유도하되 낚시성 제목 금지
- 핵심 키워드를 앞쪽에 배치
- 숫자, 구체적 정보 활용 (예: "5가지 방법", "2026년 최신")
- 불필요한 특수문자/이모지 지양

### 설명 (description)
- 첫 2줄에 핵심 내용 요약 (검색 미리보기에 노출)
- 3-5개의 챕터 타임스탬프 포함 (00:00 형식)
- 관련 키워드를 자연스럽게 포함
- 채널 구독 유도 문구 포함
- 총 300-1000자 범위

### 태그 (tags)
- 10-15개 태그
- 브로드 키워드 (예: "AI", "기술") + 롱테일 키워드 혼합
- 한국어 + 영어 태그 병행
- 총 길이 500자 이내

## 출력 형식
반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요.

{
  "title": "제목",
  "description": "설명",
  "tags": ["태그1", "태그2", ...]
}
```

### 2.2 사용자 프롬프트

```
아래 대본을 분석하여 YouTube 영상 메타데이터를 생성해주세요.

## 대본
{script_text}

## 추가 정보
- 채널명: {brand_name}
- 카테고리: {category_name}
- 타겟 시청자: {target_audience}
```

### 2.3 프롬프트 설계 고려사항

| 항목 | 설계 결정 | 이유 |
|------|----------|------|
| 모델 | `gpt-5.4-mini` | 비용 효율적 + 메타데이터 생성에 충분한 품질 |
| max_tokens | 2048 | JSON 응답이므로 충분 |
| JSON 파싱 | `json.loads()` + strip markdown fence | GPT가 ```json 블록으로 감싸는 경우 대응 |
| Fallback | 프로젝트명 기반 기본값 | API 실패 시에도 업로드 가능하도록 |
| 타임스탬프 | 더미 생성 (00:00 형식) | 실제 챕터 분할 정보가 없으므로 대략적 시간 |

### 2.4 JSON 파싱 후처리

```python
def _postprocess_metadata(raw: dict, max_title: int = 100) -> MetadataGenerationResult:
    """GPT 응답을 검증하고 제약 조건에 맞게 보정."""
    title = raw.get("title", "")[:max_title]
    description = raw.get("description", "")[:5000]

    tags = raw.get("tags", [])
    # 태그 총 길이 500자 제한
    validated_tags = []
    total_len = 0
    for tag in tags:
        tag = str(tag).strip()
        if total_len + len(tag) + 1 > 500:  # +1 for comma
            break
        validated_tags.append(tag)
        total_len += len(tag) + 1

    return MetadataGenerationResult(
        title=title,
        description=description,
        tags=validated_tags,
    )
```

### 2.5 Fallback 메타데이터

GPT 호출 실패 시 사용하는 기본값:

```python
def _fallback_metadata(project_name: str) -> MetadataGenerationResult:
    return MetadataGenerationResult(
        title=f"{project_name} - AI 자동화 영상",
        description=f"{project_name} 프로젝트에서 자동 생성된 영상입니다.",
        tags=["AI", "자동화", project_name],
    )
```


## 3. OAuth 설정 가이드 (사용자 대면)

`youtube upload` 명령 실행 시 `client_secrets.json`이 없으면 출력할 가이드:

```
YouTube 업로드를 위해 Google OAuth 인증이 필요합니다.

[설정 방법]
1. Google Cloud Console (https://console.cloud.google.com) 접속
2. 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" > "라이브러리" > "YouTube Data API v3" 활성화
4. "API 및 서비스" > "사용자 인증 정보" > "OAuth 클라이언트 ID" 생성
   - 애플리케이션 유형: "데스크톱 앱"
5. JSON 다운로드 후 아래 경로에 저장:
   config/credentials/client_secrets.json

[참고]
- 최초 실행 시 브라우저에서 Google 계정 로그인이 필요합니다
- 이후 실행에서는 저장된 토큰으로 자동 인증됩니다
- 토큰 경로: config/credentials/token.json
```


## 4. `.env.example` 변경

```bash
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_SECOND_API_KEY=your_elevenlabs_second_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
SERPER_API_KEY=your_serperdev_api_key_here

# YouTube Upload (OAuth 파일 기반 인증 -- 환경변수 불필요)
# 설정 방법: config/credentials/client_secrets.json 파일 배치
# 상세 가이드: uv run video-automation youtube upload --help
```


## 5. `.gitignore` 추가 항목

```gitignore
# YouTube OAuth credentials
config/credentials/client_secrets.json
config/credentials/token.json
```


## 6. 프로젝트 디렉토리 변경

### 6.1 `youtube_upload.json` 스키마

업로드 성공 시 `projects/{name}/output/youtube_upload.json`에 저장:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "url": "https://youtu.be/dQw4w9WgXcQ",
  "title": "자동 생성된 제목",
  "privacy_status": "private",
  "thumbnail_set": true,
  "uploaded_at": "2026-03-26T15:30:00+09:00",
  "metadata": {
    "description": "자동 생성된 설명...",
    "tags": ["AI", "자동화"],
    "category_id": "28"
  }
}
```

### 6.2 `entities/project/model.py` 확장 (선택)

```python
@property
def youtube_upload_path(self) -> Path:
    """YouTube 업로드 결과 JSON 경로."""
    return self.output_dir / "youtube_upload.json"
```
