# YouTube 업로드 기능 -- 아키텍처 설계

## 1. FSD 레이어 배치

기존 아키텍처 규칙(`app -> pipelines -> features -> entities -> shared`)에 따라
각 레이어에 배치할 모듈을 정의한다.

```
shared/
  api/
    youtube.py              [신규] YouTube Data API v3 클라이언트 래퍼
  config/
    schema.py               [수정] YoutubeUploadConfig 추가

entities/
  video/
    model.py                [수정] UploadResult 모델 추가, VideoMetadata 보강

features/
  upload_youtube/           [신규] YouTube 업로드 feature 슬라이스
    __init__.py             Public API export
    model.py                업로드 요청/응답 모델
    api.py                  YouTube API 호출 (인증, 업로드, 상태변경)
    lib.py                  메타데이터 생성, 썸네일 검증, 업로드 오케스트레이션

pipelines/
  script_to_video/
    lib.py                  [수정] --auto-upload 옵션 시 업로드 스텝 추가

app/
  cli.py                    [수정] youtube 커맨드 그룹 추가
```

## 2. 모듈 상세 설계

### 2.1 `shared/api/youtube.py` -- YouTube API 클라이언트

**역할**: YouTube Data API v3에 대한 저수준 래퍼. 인증, HTTP 호출만 담당.

```python
# 주요 함수 시그니처 (의사코드)

def get_youtube_service(credentials_dir: Path) -> Resource:
    """OAuth 2.0 인증을 수행하고 YouTube API 서비스 객체를 반환.

    1. token.json 존재 -> 토큰 로드 -> 만료 시 자동 갱신
    2. token.json 없음 -> client_secrets.json으로 브라우저 인증
    3. 갱신된 토큰을 token.json에 저장

    Args:
        credentials_dir: client_secrets.json과 token.json이 위치한 디렉토리.

    Returns:
        googleapiclient.discovery.Resource (youtube v3 서비스).
    """

def upload_video_resumable(
    service: Resource,
    video_path: Path,
    metadata: dict,
    *,
    chunk_size: int = 5 * 1024 * 1024,  # 5 MB
    on_progress: Callable[[int, int], None] | None = None,
) -> str:
    """Resumable upload로 영상을 업로드하고 video_id를 반환.

    Args:
        service: YouTube API 서비스.
        video_path: 업로드할 영상 파일 경로.
        metadata: snippet + status 딕셔너리.
        chunk_size: 청크 크기 (256KB 배수).
        on_progress: (bytes_sent, total_bytes) 콜백.

    Returns:
        업로드된 영상의 video_id.

    Raises:
        YouTubeUploadError: 업로드 실패 시.
    """

def set_thumbnail(service: Resource, video_id: str, thumbnail_path: Path) -> None:
    """영상 썸네일을 설정."""

def update_video_status(
    service: Resource,
    video_id: str,
    privacy_status: str,
    publish_at: str | None = None,
) -> None:
    """영상 공개 상태를 변경 (private -> public / unlisted / scheduled)."""
```

### 2.2 `features/upload_youtube/` -- 업로드 Feature 슬라이스

#### `model.py`

```python
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime

class UploadRequest(BaseModel):
    """YouTube 업로드 요청."""
    video_path: Path
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    category_id: str = "28"  # Science & Technology
    privacy_status: str = "private"  # private | unlisted | public
    thumbnail_path: Path | None = None
    publish_at: datetime | None = None  # 예약 공개 시각 (KST)

class UploadResult(BaseModel):
    """YouTube 업로드 결과."""
    video_id: str
    url: str  # https://youtu.be/{video_id}
    title: str
    privacy_status: str
    thumbnail_set: bool = False

class MetadataGenerationResult(BaseModel):
    """GPT로 생성한 메타데이터."""
    title: str
    description: str
    tags: list[str]
```

#### `api.py`

```python
def authenticate(credentials_dir: Path) -> Resource:
    """YouTube API 인증. shared/api/youtube.py 위임."""

def upload(request: UploadRequest, credentials_dir: Path) -> UploadResult:
    """영상 업로드 + 썸네일 설정 + 결과 반환."""

def publish(video_id: str, credentials_dir: Path, publish_at: datetime | None = None) -> None:
    """비공개 영상을 공개로 전환 (또는 예약 공개)."""
```

#### `lib.py`

```python
def generate_metadata(
    script_text: str,
    project_name: str,
    *,
    category_id: str = "28",
) -> MetadataGenerationResult:
    """대본 기반으로 GPT-5.4-mini를 사용하여 제목/설명/태그 자동 생성.

    프롬프트 전략:
    - 대본 전체를 컨텍스트로 제공
    - YouTube SEO 최적화 지시 (키워드 밀도, 태그 다양성)
    - 한국어 최적화 (제목 40자 이내 권장)
    - JSON 구조화 출력
    """

def validate_thumbnail(thumbnail_path: Path) -> Path:
    """썸네일 파일 검증 및 필요 시 리사이즈.

    - 최대 2MB 확인 (YouTube 제한)
    - 1280x720 권장 해상도 확인
    - JPEG/PNG 포맷 확인
    - 초과 시 Pillow로 리사이즈/압축
    """

def find_thumbnail(project: Project) -> Path | None:
    """프로젝트 디렉토리에서 썸네일 파일 자동 탐색.

    탐색 순서:
    1. output/thumbnail.png
    2. output/thumbnail.jpg
    3. slides/001.png (첫 슬라이드를 fallback으로)
    """

def save_upload_result(project: Project, result: UploadResult) -> Path:
    """업로드 결과를 프로젝트 디렉토리에 JSON으로 저장.

    저장 경로: projects/{name}/output/youtube_upload.json
    """

def load_upload_result(project: Project) -> UploadResult | None:
    """저장된 업로드 결과를 로드. 없으면 None."""
```

### 2.3 `entities/video/model.py` 변경

기존 `VideoMetadata` 모델에 `privacy_status` 필드 추가:

```python
class VideoMetadata(BaseModel):
    """유튜브 업로드용 메타데이터."""
    title: str
    description: str = ""
    tags: list[str] = []
    category_id: str = "28"
    thumbnail_path: Path | None = None
    privacy_status: str = "private"  # [추가] 초기 업로드 상태
```

### 2.4 `shared/config/schema.py` 변경

기존 `YoutubeConfig`를 확장:

```python
class YoutubeUploadConfig(BaseModel):
    """YouTube 업로드 설정."""
    credentials_dir: str = "config/credentials"  # OAuth 인증 파일 위치
    default_privacy: str = "private"  # 기본 업로드 상태
    default_category: str = "28"  # Science & Technology
    chunk_size_mb: int = 5  # resumable upload 청크 크기
    metadata_model: str = "gpt-5.4-mini"  # 메타데이터 생성 LLM

class YoutubeConfig(BaseModel):
    """유튜브 설정."""
    schedule: YoutubeScheduleConfig = Field(default_factory=YoutubeScheduleConfig)
    default_category: str = "28"
    upload: YoutubeUploadConfig = Field(default_factory=YoutubeUploadConfig)  # [추가]
```

### 2.5 `app/cli.py` 변경 -- YouTube CLI 커맨드 그룹

```python
@cli.group()
def youtube() -> None:
    """YouTube 업로드 및 관리 명령어."""
    pass

@youtube.command("upload")
@click.option("--project", required=True)
@click.option("--video", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--generate-metadata/--no-generate-metadata", default=True)
def youtube_upload(project_name, video, generate_metadata): ...

@youtube.command("publish")
@click.option("--project", required=True)
@click.option("--schedule", default=None, help="예약 공개 시각 (ISO 8601)")
def youtube_publish(project_name, schedule): ...

@youtube.command("generate-metadata")
@click.option("--project", required=True)
def youtube_generate_metadata(project_name): ...

@youtube.command("status")
@click.option("--project", required=True)
def youtube_status(project_name): ...
```


## 3. 데이터 흐름

```
[영상 생성 완료]
       |
       v
  find_thumbnail()           -- 프로젝트에서 썸네일 탐색
       |
       v
  generate_metadata()         -- GPT-5.4-mini로 제목/설명/태그 생성
       |                        (script.txt 전체를 컨텍스트로)
       v
  validate_thumbnail()        -- 2MB 이하, 1280x720 확인/리사이즈
       |
       v
  UploadRequest 구성           -- privacy_status="private"
       |
       v
  upload_video_resumable()    -- Resumable Upload (5MB 청크)
       |                        Rich progress bar로 진행률 표시
       v
  set_thumbnail()             -- 썸네일 설정 (별도 API 호출)
       |
       v
  save_upload_result()        -- youtube_upload.json에 결과 저장
       |
       v
  [사용자 확인]               -- YouTube Studio에서 영상 검토
       |
       v
  publish()                   -- private -> public 전환
                                (또는 schedule 지정 시 예약 공개)
```


## 4. OAuth 2.0 인증 흐름

### 4.1 사전 준비 (1회)

1. Google Cloud Console에서 프로젝트 생성
2. YouTube Data API v3 활성화
3. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)
4. `client_secrets.json` 다운로드 -> `config/credentials/` 에 저장

### 4.2 런타임 인증 흐름

```
[최초 실행]
  client_secrets.json 존재 확인
       |
       v
  InstalledAppFlow.from_client_secrets_file()
       |
       v
  flow.run_local_server(port=0)  -- 브라우저에서 Google 로그인
       |
       v
  credentials 저장 -> config/credentials/token.json
       |
       v
  [이후 실행]
  token.json 로드 -> 만료 확인 -> 자동 갱신
```

### 4.3 필요한 OAuth Scope

```python
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",      # 영상 업로드
    "https://www.googleapis.com/auth/youtube",             # 영상 관리 (상태 변경)
    "https://www.googleapis.com/auth/youtube.force-ssl",   # 썸네일 설정
]
```

### 4.4 보안 고려사항

- `client_secrets.json`과 `token.json`은 `.gitignore`에 이미 포함되어야 함
- `config/credentials/` 디렉토리는 빈 디렉토리로 유지 (현재 이미 존재)
- `.env`에 YouTube 관련 키를 저장하지 않음 (OAuth 토큰 파일 방식)


## 5. Import 규칙 준수 확인

```
app/cli.py
  -> features/upload_youtube        (app -> features: OK)
  -> entities/project/model         (app -> entities: OK)

features/upload_youtube/api.py
  -> shared/api/youtube             (features -> shared: OK)

features/upload_youtube/lib.py
  -> shared/api/claude (ask())      (features -> shared: OK)
  -> entities/project/model         (features -> entities: OK)
  -> entities/video/model           (features -> entities: OK)

shared/api/youtube.py
  -> (외부 패키지만 import)         (shared: OK)

pipelines/script_to_video/lib.py
  -> features/upload_youtube        (pipelines -> features: OK)
```

모든 import 경로가 FSD 레이어 규칙을 준수한다.
