# YouTube 자동 업로드 전략

> 영상 완성 후 비공개/일부공개로 YouTube에 자동 업로드하기

> 난이도: 심화 | 소요: 읽기 20분 + 설정 30분

---

## Part 1: 왜 자동 업로드인가?

영상이 `final_video.mp4`로 완성된 후에도 할 일이 남아 있습니다:

```
final_video.mp4 완성
    ↓
[수동으로 하면]
YouTube Studio 접속 → 파일 선택 → 제목 입력 → 설명 작성
→ 태그 입력 → 카테고리 선택 → 공개 범위 설정 → 업로드
→ (매번 10~15분)

[자동화하면]
스크립트 한 줄 실행 → 비공개로 업로드 완료 → 나중에 공개로 전환
→ (1분)
```

자동 업로드의 핵심 전략은 **비공개(private) 또는 일부공개(unlisted)**로 먼저 올린 뒤, 확인 후 공개로 전환하는 것입니다. 실수로 미완성 영상이 구독자에게 노출되는 사고를 방지합니다.

### 업로드 공개 범위

| 상태 | 영어 | 설명 | 추천 용도 |
|------|------|------|----------|
| **비공개** | `private` | 나만 볼 수 있음 | 자동 업로드 기본값 (가장 안전) |
| **일부공개** | `unlisted` | 링크 아는 사람만 시청 | 팀 리뷰, 외부 피드백용 |
| **공개** | `public` | 모든 사람 시청 가능 | 최종 확인 후 수동 전환 |

> **핵심:** 자동 업로드는 항상 `private`로. 확인 후 YouTube Studio에서 `public`으로 전환하세요.

---

## Part 2: Google Cloud 프로젝트 & API 키 발급

### Step 1: Google Cloud 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속 + Google 계정 로그인
2. 상단 프로젝트 드롭다운 → **"새 프로젝트"** 클릭
3. 프로젝트 이름 입력 (예: `youtube-auto-upload`) → **"만들기"**

### Step 2: YouTube Data API v3 활성화

1. 왼쪽 메뉴 → **"API 및 서비스"** → **"라이브러리"**
2. 검색창에 `YouTube Data API v3` 입력
3. 클릭 → **"사용"** 버튼 클릭

### Step 3: OAuth 동의 화면 설정

1. **"API 및 서비스"** → **"OAuth 동의 화면"**
2. 사용자 유형: **외부** 선택 → "만들기"
3. 앱 정보 입력:
   - 앱 이름: `My YouTube Uploader` (아무거나)
   - 사용자 지원 이메일: 내 이메일
   - 개발자 연락처: 내 이메일
4. **범위 추가**: `youtube.upload`, `youtube` 검색 후 추가
5. **테스트 사용자 추가**: 내 Google 계정 이메일 입력
6. 저장

> **중요: Testing vs Production 모드**
>
> | 모드 | 토큰 유효기간 | 사용 가능 사용자 | 인증 필요 |
> |------|:----------:|:-----------:|:--------:|
> | **Testing** (기본) | **7일** | 테스트 사용자만 | X |
> | **Production** | **무기한** | 모든 Google 사용자 | O (Google 심사) |
>
> 개인 채널용이라면 Testing 모드로 충분합니다. 단, **7일마다 재인증**이 필요합니다.
> 주간 루틴에 포함시키면 불편하지 않습니다.
>
> 재인증 없이 장기 운영하려면 Production 모드로 전환해야 합니다 (Google 심사 2~4주 소요).

### Step 4: OAuth 클라이언트 ID 생성

1. **"API 및 서비스"** → **"사용자 인증 정보"**
2. **"+ 사용자 인증 정보 만들기"** → **"OAuth 클라이언트 ID"**
3. 애플리케이션 유형: **데스크톱 앱** 선택
4. 이름: `youtube-uploader` → "만들기"
5. **JSON 다운로드** 클릭 → `client_secret.json`으로 이름 변경

### Step 5: 프로젝트에 배치

```bash
# 프로젝트 루트에 credentials 폴더 생성
mkdir -p credentials

# 다운받은 파일을 이동
# (파일명은 client_secret_XXXX.json 형태 → client_secret.json으로 변경)
mv ~/Downloads/client_secret_*.json credentials/client_secret.json
```

```
프로젝트 루트/
├── credentials/
│   ├── client_secret.json     ← OAuth 클라이언트 (Git에 올리지 말 것!)
│   └── youtube_token.json     ← 인증 후 자동 생성됨
├── .gitignore                 ← credentials/ 추가 필수
└── ...
```

> **.gitignore에 반드시 추가:**
> ```
> credentials/
> ```
> `client_secret.json`과 `youtube_token.json`은 절대 Git에 올리지 마세요. 계정 탈취 위험이 있습니다.
>
> **참고:** 이 프로젝트의 `.gitignore`에는 `config/credentials/`가 이미 등록되어 있지만, 프로젝트 루트의 `credentials/`는 별도입니다. 위처럼 루트에 `credentials/` 폴더를 사용하는 경우 `.gitignore`에 직접 추가해야 합니다.

---

## Part 3: 첫 인증 (1회만)

### Python 패키지 설치

```bash
uv pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
# google-auth-httplib2는 프로젝트 의존성에 포함되지 않을 수 있으므로 별도 설치가 필요합니다.
```

### 인증 스크립트 실행

첫 인증 시 **브라우저가 열리고 Google 로그인 화면**이 표시됩니다. 로그인하면 토큰이 자동 저장됩니다.

```python
# scripts/youtube_auth.py
"""YouTube API 첫 인증 — 브라우저에서 로그인 후 토큰이 저장됩니다."""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
CLIENT_SECRET = "credentials/client_secret.json"
TOKEN_FILE = "credentials/youtube_token.json"

def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("토큰 갱신 중...")
            creds.refresh(Request())
        else:
            print("브라우저에서 Google 로그인을 진행해주세요...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"토큰 저장 완료: {TOKEN_FILE}")

    print("인증 성공!")
    return creds

if __name__ == "__main__":
    authenticate()
```

```bash
uv run python scripts/youtube_auth.py
```

> 1. 브라우저가 열림 → Google 로그인
> 2. "이 앱은 확인되지 않았습니다" → **"고급"** → **"(앱 이름)(으)로 이동"**
> 3. 권한 허용 → 터미널에 "인증 성공!" 출력
> 4. `credentials/youtube_token.json` 파일이 생성됨
>
> 이후에는 토큰이 자동 갱신되므로 브라우저 로그인이 필요 없습니다.
> (Testing 모드: 7일 후 재인증 필요)

---

## Part 4: 업로드 스크립트

### 기본 업로드

```python
# scripts/youtube_upload.py
"""YouTube 비공개 업로드 스크립트"""
import argparse
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
TOKEN_FILE = "credentials/youtube_token.json"


def get_youtube_service():
    """인증된 YouTube API 서비스를 반환합니다."""
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload_video(file_path, title, description, tags=None,
                 category_id="28", privacy="private"):
    """영상을 YouTube에 업로드합니다."""
    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or [],
            "categoryId": category_id,
            "defaultLanguage": "ko",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,   # AI 생성 콘텐츠 고지 (필수)
        },
    }

    media = MediaFileUpload(
        file_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB 청크
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
        notifySubscribers=False,  # 비공개이므로 구독자 알림 X
    )

    print(f"업로드 시작: {file_path}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  진행률: {int(status.progress() * 100)}%")

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"업로드 완료! ({privacy})")
    print(f"  URL: {video_url}")
    print(f"  Studio: https://studio.youtube.com/video/{video_id}/edit")
    return video_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube 비공개 업로드")
    parser.add_argument("file", help="업로드할 영상 파일 경로")
    parser.add_argument("--title", required=True, help="영상 제목")
    parser.add_argument("--description", default="", help="영상 설명")
    parser.add_argument("--tags", nargs="*", default=[], help="태그 목록")
    parser.add_argument("--category", default="28", help="카테고리 ID (기본: 28=과학기술)")
    parser.add_argument("--privacy", default="private",
                        choices=["private", "unlisted", "public"],
                        help="공개 범위 (기본: private)")
    args = parser.parse_args()

    upload_video(
        args.file, args.title, args.description,
        tags=args.tags, category_id=args.category, privacy=args.privacy,
    )
```

### 실행 예시

```bash
# 비공개로 업로드 (기본)
uv run python scripts/youtube_upload.py \
    projects/my-project/output/final_video.mp4 \
    --title "AI로 유튜브 영상을 자동으로 만드는 법" \
    --description "AI 자동화 시스템으로 대본 하나만 넣으면 영상이 완성됩니다." \
    --tags "AI" "자동화" "유튜브" "영상제작"

# 일부공개로 업로드 (링크 공유용)
uv run python scripts/youtube_upload.py \
    projects/my-project/output/final_video.mp4 \
    --title "AI 영상 자동화 데모" \
    --privacy unlisted \
    --tags "AI" "데모"
```

### Claude Code에서 업로드 요청

```
projects/my-project/output/final_video.mp4를 YouTube에 비공개로 업로드해줘.
제목: "AI로 유튜브 영상 자동 생성하기"
설명: "대본 하나로 AI가 음성, 슬라이드, 자막까지 자동으로 만들어줍니다."
태그: AI, 자동화, 유튜브, 영상제작, Claude Code
```

---

## Part 5: 롱폼 vs 쇼츠 -- 업로드 전략이 다릅니다

롱폼(16:9 본편)과 쇼츠(9:16)는 YouTube 내부에서 완전히 다른 알고리즘으로 노출됩니다. 메타데이터 작성 전략도 달라야 합니다.

### 롱폼 vs 쇼츠 비교표

| 항목 | 롱폼 (16:9 본편) | 쇼츠 (9:16) |
|------|:---------------:|:-----------:|
| 출력 파일 | `output/final_video.mp4` | `shorts_slides/output/final_shorts.mp4` |
| 자막 파일 | `output/corrected_subtitles.srt` | 영상 내 워드 하이라이트 자막 |
| 챕터 타임스탬프 | **필수** (SRT에서 추출) | **불필요** (60초 이하라 의미 없음) |
| 제목 길이 | 40~60자 (SEO 키워드 앞배치) | 30~40자 (#Shorts 포함) |
| 설명 길이 | 500~2,000자 (챕터 + 상세) | 100~300자 (짧고 임팩트) |
| 태그 전략 | 검색 SEO 중심 (8~12개) | 발견 알고리즘 중심 (5~8개) |
| 해시태그 | 설명 하단 3개 | `#Shorts` 필수 + 2개 |
| 썸네일 | 커스텀 썸네일 설정 가능 | API로 설정 불가 (자동 추출) |
| 공개 시간 | 오전 9~11시 | 오후 6~8시 |
| `notifySubscribers` | `True` (공개 시) | `False` (피드 노출 별도 경로) |

---

### 5-1. 롱폼 업로드 전략 (16:9 본편)

롱폼은 **검색 SEO**가 핵심입니다. 제목/설명/태그에 키워드를 정확히 배치해야 합니다.

#### 제목 (Title) -- 가장 중요한 SEO 신호

| 규칙 | 설명 | 예시 |
|------|------|------|
| 40~60자 | 검색 결과에서 잘리지 않음 (API 최대 100자) | O |
| 핵심 키워드를 앞에 | 처음 3~5단어가 SEO 가중치 가장 높음 | `AI 영상 자동화: 대본 하나로 끝내는 법` |
| 숫자 포함 | CTR(클릭률) +8% 향상 | `3분 만에 영상 만드는 AI 자동화 5단계` |
| 파워 워드 | 관심 유도 | "완벽한", "필수", "실전" |

**Claude Code 프롬프트:**
```
이 대본에 맞는 YouTube 롱폼 제목 5개를 추천해줘.
SEO 키워드를 앞에 배치하고, 60자 이내로, 숫자 포함.
projects/my-project/script.txt 참조.
```

#### 설명 (Description) -- 챕터 타임스탬프가 핵심

롱폼 설명의 가장 큰 차별점은 **챕터 타임스탬프**입니다. 타임스탬프가 있으면 평균 시청 시간이 약 11% 증가하고, 검색 결과에서 챕터별로 노출됩니다.

```
[ 롱폼 설명 구조 템플릿 ]

첫 2줄 (가장 중요 — "더보기" 클릭 전에 보이는 영역):
핵심 키워드 포함 요약. 시청자가 클릭할 이유.

---

본문:
영상 내용 상세 설명 (키워드 2~3개 자연스럽게 삽입)

챕터 (SRT 자막 파일에서 자동 추출):
00:00 인트로
00:30 첫 번째 포인트
01:15 두 번째 포인트
02:00 세 번째 포인트
02:45 정리

---

링크:
관련 영상: [URL]
채널 구독: [URL]

해시태그:
#AI자동화 #유튜브영상 #영상제작
```

> 00:00으로 시작해야 YouTube가 챕터로 인식합니다.

#### 타임스탬프 자동 생성 -- SRT 자막 파일 활용

파이프라인이 완료되면 `output/` 폴더에 SRT 자막 파일이 생성됩니다. 이 파일에는 각 문단의 시작 시간이 정확히 기록되어 있으므로, **챕터 타임스탬프의 정확한 소스**로 활용할 수 있습니다.

```
projects/my-project/output/
├── final_video.mp4
├── corrected_subtitles.srt   ← 이 파일이 타임스탬프 소스
└── ...
```

**SRT 파일 예시:**
```srt
1
00:00:00,000 --> 00:00:08,500
오늘은 AI가 유튜브 영상을 자동으로 만드는 방법을 알아보겠습니다.

2
00:00:08,500 --> 00:00:18,200
첫 번째로, 대본을 작성합니다.

3
00:00:18,200 --> 00:00:30,100
두 번째로, 명령어 하나면 됩니다.
```

**→ 변환된 YouTube 챕터:**
```
00:00 인트로 — AI 영상 자동화란?
00:08 대본 작성하기
00:18 명령어 한 줄로 영상 생성
```

1 문단 = 1 슬라이드 = 1 SRT 블록이므로, SRT의 시작 시간이 곧 각 문단(챕터)의 시작 시간입니다.

**Claude Code로 SRT → 타임스탬프 변환:**
```
projects/my-project/output/corrected_subtitles.srt 파일을 읽고
YouTube 챕터 타임스탬프를 생성해줘.
각 자막 블록의 시작 시간을 MM:SS 형식으로 변환하고,
대본 내용을 요약해서 챕터 제목으로 만들어줘.
첫 번째는 반드시 00:00으로 시작.
```

**롱폼 설명문 전체 생성 프롬프트:**
```
projects/my-project의 대본(script.txt)과 자막(output/corrected_subtitles.srt)을 읽고
YouTube 롱폼 설명문을 작성해줘.

구조:
1. 첫 2줄: 핵심 키워드 포함 요약
2. 상세 설명: 키워드 자연스럽게 삽입
3. 챕터 타임스탬프: SRT 파일의 시작 시간 기반, 문단별 제목 요약
4. 해시태그 3개

SEO 키워드 "AI 영상 자동화", "유튜브 자동화" 포함.
```

> **핵심:** 타임스탬프를 직접 계산할 필요 없습니다. SRT 파일에 이미 정확한 시간이 있으므로, Claude Code에게 변환만 요청하면 됩니다.

#### 태그 (Tags) -- 8~12개

| 순서 | 태그 유형 | 개수 | 예시 |
|------|----------|:----:|------|
| 1번 | 정확한 타겟 키워드 | 1개 | `AI 영상 자동화` |
| 2~3번 | 핵심 키워드 변형 | 2개 | `유튜브 자동화`, `AI 영상 제작` |
| 4~8번 | 롱테일 키워드 | 4~5개 | `대본으로 영상 만들기`, `AI 유튜브 편집` |
| 9~12번 | 채널 브랜딩 | 2~3개 | `채널명`, `시리즈명` |

> 15개 이상의 태그는 오히려 관련성 신호가 약해집니다. 8~12개가 최적.

---

### 5-2. 쇼츠 업로드 전략 (9:16)

쇼츠는 검색 SEO가 아닌 **숏폼 피드 알고리즘**으로 노출됩니다. 전략이 근본적으로 다릅니다.

#### 쇼츠 업로드 필수 조건

| 조건 | 설명 |
|------|------|
| 비율 | 9:16 세로 (1080x1920) |
| 길이 | **60초 이하** |
| `#Shorts` | 제목 또는 설명에 반드시 포함 |
| 썸네일 | API로 커스텀 설정 **불가** (YouTube가 자동 추출) |
| 타임스탬프 | **불필요** (60초 이하라 챕터 의미 없음) |

#### 제목 -- 짧고 강렬하게

| 규칙 | 롱폼과 차이 | 예시 |
|------|-----------|------|
| **30~40자** | 롱폼보다 짧게 | `AI가 3분 만에 영상을 만든다고?` |
| `#Shorts` 포함 | 필수 | `AI 영상 자동화 #Shorts` |
| 훅 문장 그대로 | 대본 첫 문장 활용 | `코딩 없이 유튜브 영상 만드는 법 #Shorts` |
| 키워드보다 호기심 | SEO보다 클릭 유도 | `이게 된다고요? #Shorts` |

**Claude Code 프롬프트:**
```
이 대본에 맞는 YouTube 쇼츠 제목 5개를 추천해줘.
30~40자, #Shorts 포함, 훅(호기심/충격) 중심으로.
projects/my-project/script.txt 참조.
```

#### 설명 -- 짧게, 해시태그 중심

쇼츠 설명은 길게 쓸 필요 없습니다. 피드에서 설명이 거의 보이지 않기 때문입니다.

```
[ 쇼츠 설명 구조 ]

한 줄 요약 (1~2문장)

#Shorts #AI자동화 #유튜브

본편 영상: https://youtu.be/xxxxx  ← 롱폼으로 유도하는 핵심 CTA
```

> **챕터 타임스탬프**: 쇼츠에는 넣지 않습니다. 60초 이하 영상에서는 YouTube가 챕터를 인식하지 않으며, 오히려 설명이 지저분해 보입니다.

**쇼츠 설명문 생성 프롬프트:**
```
projects/my-project/script.txt 대본을 읽고 YouTube 쇼츠 설명문을 작성해줘.
구조: 한 줄 요약 + 해시태그 3개(#Shorts 필수) + 본편 링크 자리.
100자 이내로 짧게.
```

#### 태그 -- 5~8개, 발견 중심

쇼츠 태그는 검색보다 **"이 영상도 보세요" 추천**에 영향을 줍니다.

| 순서 | 태그 유형 | 개수 | 예시 |
|------|----------|:----:|------|
| 1번 | `Shorts` | 1개 | `Shorts` |
| 2~3번 | 주제 키워드 | 2개 | `AI 자동화`, `유튜브` |
| 4~6번 | 감정/상황 | 2~3개 | `꿀팁`, `충격`, `신기한` |
| 7~8번 | 채널 브랜딩 | 1~2개 | `채널명` |

#### 쇼츠 업로드 실행 예시

```bash
uv run python scripts/youtube_upload.py \
    projects/my-project/shorts_slides/output/final_shorts.mp4 \
    --title "AI가 3분 만에 유튜브 영상을 만든다 #Shorts" \
    --description "대본 하나로 영상 자동 생성. 본편: https://youtu.be/xxxxx #Shorts #AI자동화 #유튜브" \
    --tags "Shorts" "AI 자동화" "유튜브" "꿀팁" "영상제작" \
    --privacy private
```

---

### 5-3. 포맷별 메타데이터 비교 요약

| 항목 | 롱폼 | 쇼츠 |
|------|------|------|
| **제목** | `AI 영상 자동화: 대본 하나로 끝내는 5단계 가이드` | `AI가 영상을 만든다고? #Shorts` |
| **설명** | 500~2,000자 (챕터 타임스탬프 포함) | 50~100자 (해시태그 + 본편 링크) |
| **타임스탬프** | SRT 기반으로 자동 생성 | 없음 |
| **태그** | 검색 SEO 중심 8~12개 | 발견 알고리즘 중심 5~8개 |
| **해시태그** | 설명 하단 `#키워드` 3개 | `#Shorts` 필수 + 2개 |
| **CTA** | 설명에 "구독" + 관련 영상 링크 | 설명에 "본편 보기" 링크 |

**Claude Code로 롱폼+쇼츠 메타데이터 동시 생성:**
```
projects/my-project의 대본(script.txt)과 자막(output/corrected_subtitles.srt)을 읽고
롱폼과 쇼츠 각각의 YouTube 메타데이터를 생성해줘.

롱폼:
- 제목 3개 (60자 이내, SEO 키워드 앞배치)
- 설명 (2줄 요약 + 상세 + SRT 기반 챕터 타임스탬프 + 해시태그 3개)
- 태그 10개

쇼츠:
- 제목 3개 (40자 이내, #Shorts 포함, 훅 중심)
- 설명 (한 줄 요약 + #Shorts 포함 해시태그 3개 + 본편 링크 자리)
- 태그 6개

각각 upload_metadata_video.json, upload_metadata_shorts.json으로 저장.
```

---

### 카테고리 ID

| ID | 카테고리 | 추천 도메인 |
|----|----------|-----------|
| **22** | 사람 & 블로그 | 라이프스타일, 일상 |
| **26** | 노하우 & 스타일 | 요리, 뷰티, DIY |
| **27** | 교육 | 강의, 튜토리얼 |
| **28** | 과학 & 기술 | IT, AI, 테크 뉴스 |
| **24** | 엔터테인먼트 | 예능, 리뷰 |
| **25** | 뉴스 & 정치 | 시사, 뉴스 |
| **19** | 여행 & 이벤트 | 여행, 축제 |
| **17** | 스포츠 | 운동, 피트니스 |

### AI 생성 콘텐츠 고지 (필수)

2024년 10월부터 YouTube는 AI 생성 콘텐츠에 대해 **`containsSyntheticMedia: true`** 설정을 요구합니다. 이 시스템으로 만든 영상은 AI가 음성, 슬라이드, 이미지를 생성하므로 **반드시 `true`로 설정**해야 합니다.

업로드 스크립트에 이미 포함되어 있습니다:
```python
"status": {
    "containsSyntheticMedia": True,  # AI 생성 콘텐츠 고지
}
```

---

## Part 6: SEO 메타데이터 자동 생성 워크플로우

대본에서 제목/설명/태그를 자동으로 생성하는 전체 흐름입니다. 롱폼과 쇼츠를 동시에 만들었다면 메타데이터도 각각 생성합니다.

### 롱폼 워크플로우

```
[1] final_video.mp4 + corrected_subtitles.srt 완성
    ↓
[2] Claude Code에게 롱폼 메타데이터 생성 요청
    (대본 + SRT → 제목/설명/챕터 타임스탬프/태그)
    ↓
[3] 메타데이터 확인 + 수정
    ↓
[4] 비공개로 YouTube 업로드
    ↓
[5] YouTube Studio에서 확인 → 공개 전환
```

### 쇼츠 워크플로우

```
[1] final_shorts.mp4 완성
    ↓
[2] Claude Code에게 쇼츠 메타데이터 생성 요청
    (대본 → 훅 제목/#Shorts/짧은 설명/태그)
    ↓  ※ SRT 기반 타임스탬프 불필요 (60초 이하)
[3] 메타데이터 확인
    ↓
[4] 비공개로 YouTube 업로드
    ↓
[5] YouTube Studio에서 확인 → 공개 전환
```

### 메타데이터 일괄 생성 프롬프트

**롱폼 전용:**

```
projects/my-project/script.txt 대본과
projects/my-project/output/corrected_subtitles.srt 자막 파일을 읽고
YouTube 롱폼 업로드용 메타데이터를 생성해줘.

- 제목 후보 3개 (60자 이내, SEO 키워드 앞배치)
- 설명문:
  - 첫 2줄 요약
  - 상세 설명
  - 챕터 타임스탬프 (SRT 시작 시간 기반, MM:SS + 문단 요약 제목)
  - 해시태그 3개
- 태그 10개
- 카테고리 ID 추천

projects/my-project/upload_metadata_video.json으로 저장해줘.
```

**쇼츠 전용:**

```
projects/my-project/script.txt 대본을 읽고
YouTube 쇼츠 업로드용 메타데이터를 생성해줘.

- 제목 후보 3개 (40자 이내, #Shorts 포함, 훅 중심)
- 설명문 (한 줄 요약 + #Shorts 포함 해시태그 3개 + 본편 링크 자리)
- 태그 6개 (Shorts + 주제 키워드 + 감정 키워드)
- 카테고리 ID

projects/my-project/upload_metadata_shorts.json으로 저장해줘.
```

**롱폼 + 쇼츠 동시 생성:**

```
projects/my-project의 대본(script.txt)과 자막(output/corrected_subtitles.srt)을 읽고
롱폼과 쇼츠 각각의 YouTube 메타데이터를 한번에 생성해줘.

롱폼: 제목 3개(SEO) + 설명(챕터 타임스탬프 포함) + 태그 10개
쇼츠: 제목 3개(#Shorts/훅) + 설명(100자 이내) + 태그 6개

각각 upload_metadata_video.json, upload_metadata_shorts.json으로 저장.
```

### 저장 형식 (upload_metadata.json)

```json
{
  "title": "AI로 유튜브 영상을 자동으로 만드는 법 | 3분 완성",
  "description": "대본 하나만 넣으면 AI가 음성, 슬라이드, 자막까지 자동으로 만들어줍니다.\n\n...",
  "tags": ["AI 영상 자동화", "유튜브 자동화", "AI 영상 제작", "..."],
  "categoryId": "28",
  "privacy": "private"
}
```

### Step 4: 메타데이터 파일로 업로드

```bash
# metadata.json 기반 업로드 (Claude Code에게 요청)
projects/my-project/upload_metadata.json 파일의 메타데이터로
projects/my-project/output/final_video.mp4를 YouTube에 비공개 업로드해줘.
```

---

## Part 7: API 할당량 (Quota) 관리

### 일일 할당량

YouTube Data API v3는 프로젝트당 **일일 10,000 유닛**이 기본 할당됩니다. 자정(태평양 시간, 한국 시간 오후 5시) 기준 리셋됩니다.

### 작업별 비용

| 작업 | 유닛 비용 | 하루 최대 횟수 |
|------|:--------:|:------------:|
| **영상 업로드** (`videos.insert`) | ~100 | ~100회 |
| 메타데이터 수정 (`videos.update`) | 50 | 200회 |
| 썸네일 설정 (`thumbnails.set`) | 50 | 200회 |
| 영상 목록 조회 (`videos.list`) | 1 | 10,000회 |

### 1회 업로드 전체 비용

```
영상 업로드:  ~100 유닛
썸네일 설정:    50 유닛 (선택)
메타데이터 수정: 50 유닛 (선택)
────────────────────────
합계:        ~200 유닛/회

하루 10,000 유닛 ÷ 200 = 약 50회 업로드 가능
```

> 일반적인 채널 운영(주 3~5편)에서는 할당량 걱정이 전혀 없습니다. 10,000 유닛이면 하루 50편까지 가능합니다.

### 할당량 확인

```
YouTube API 할당량 사용량을 확인하는 방법 알려줘.
```

Google Cloud Console → **API 및 서비스** → **대시보드** → YouTube Data API v3 → **할당량** 탭에서 실시간 확인 가능합니다.

---

## Part 8: 업로드 후 워크플로우

### 비공개 → 공개 전환 체크리스트

비공개로 업로드한 후, 아래를 확인하고 공개로 전환합니다:

- [ ] 영상 재생해서 처음부터 끝까지 확인
- [ ] 제목에 오타 없는지 확인
- [ ] 설명문 링크가 작동하는지 확인
- [ ] 태그가 적절한지 확인
- [ ] 썸네일이 잘 보이는지 확인
- [ ] AI 생성 콘텐츠 고지가 설정되었는지 확인

### YouTube Studio에서 공개 전환

```
업로드 완료 후 출력되는 Studio 링크:
https://studio.youtube.com/video/{VIDEO_ID}/edit

→ "공개 범위" → "공개" 또는 "예약" 선택
```

### 예약 공개 (Scheduled Publishing)

특정 날짜/시간에 자동으로 공개되도록 예약할 수 있습니다:

```python
"status": {
    "privacyStatus": "private",
    "publishAt": "2026-04-01T09:00:00+09:00",  # 한국시간 4월 1일 오전 9시
}
```

**Claude Code로 예약 업로드:**
```
projects/my-project/output/final_video.mp4를 YouTube에 업로드해줘.
비공개로 올리되, 다음 주 월요일 오전 9시에 자동 공개되도록 예약 설정해줘.
```

### 최적 업로드 시간 (한국 기준)

| 콘텐츠 유형 | 추천 공개 시간 | 이유 |
|-----------|:----------:|------|
| 본편 영상 | 오전 9~11시 | 출퇴근/점심 시간 시청 |
| 쇼츠 | 오후 6~8시 | 퇴근 후 모바일 스크롤 |
| 주말 영상 | 토요일 오전 10시 | 주말 여유 시간 |

---

## Part 9: 보안 주의사항

### 절대 하면 안 되는 것

| 행동 | 위험 | 대신 할 것 |
|------|------|-----------|
| `client_secret.json`을 Git에 커밋 | 계정 탈취 | `.gitignore`에 `credentials/` 추가 |
| `youtube_token.json`을 공유 | 내 채널로 아무나 업로드 가능 | 토큰 파일은 로컬에만 보관 |
| API 키를 코드에 하드코딩 | 키 노출 | 환경변수 또는 파일로 관리 |
| 처음부터 `public`으로 업로드 | 미완성 영상 노출 | 항상 `private` → 확인 → `public` |

### .gitignore 필수 추가

```
# YouTube API 인증 파일
credentials/
client_secret*.json
youtube_token*.json
```

### 토큰 갱신 실패 시

Testing 모드에서 7일 후 토큰이 만료되면:

```bash
# 토큰 파일 삭제 후 재인증
rm credentials/youtube_token.json
uv run python scripts/youtube_auth.py
```

---

## Part 10: 실습 -- 첫 자동 업로드

### 사전 준비

1. Google Cloud 프로젝트 생성 + YouTube Data API v3 활성화 (Part 2)
2. OAuth 클라이언트 생성 + `client_secret.json` 다운로드 (Part 2)
3. 첫 인증 완료 (Part 3)
4. 업로드할 영상 (`final_video.mp4`) 준비

### 실습 순서

**Step 1: 메타데이터 생성**

```
projects/workshop-001/script.txt 대본을 읽고 YouTube 업로드용 메타데이터를 생성해줘.
제목 후보 3개 + 설명문 + 태그 10개 + 카테고리 추천.
```

**Step 2: 비공개 업로드**

```bash
uv run python scripts/youtube_upload.py \
    projects/workshop-001/output/final_video.mp4 \
    --title "AI로 유튜브 영상 자동 생성하기 | 입문 가이드" \
    --description "대본 하나로 AI가 영상을 만들어줍니다. 코딩 불필요." \
    --tags "AI 영상 자동화" "유튜브 자동화" "영상 제작" "AI" "자동화" \
    --privacy private
```

**Step 3: YouTube Studio에서 확인**

터미널에 출력된 Studio URL을 클릭하여 확인합니다.

**Step 4: 공개 전환**

문제가 없으면 YouTube Studio에서 "공개 범위"를 `private` → `public`으로 변경합니다.

### 도메인별 메타데이터 생성 프롬프트 (복사해서 사용)

**IT/테크 채널:**
```
이 대본 기반으로 YouTube 메타데이터를 생성해줘.
제목: SEO 키워드 "AI 자동화" 앞배치, 60자 이내, 숫자 포함
설명: 2줄 요약 + 상세 + 타임스탬프 + #AI자동화 #유튜브
태그: 기술 키워드 중심 10개
카테고리: 28 (과학기술)
```

**재테크 채널:**
```
이 대본 기반으로 YouTube 메타데이터를 생성해줘.
제목: SEO 키워드 "ETF 투자" 앞배치, 구체적 수익률/금액 포함
설명: 면책 조항("투자 판단은 개인의 몫") 포함 필수
태그: 투자/재테크 키워드 10개
카테고리: 27 (교육)
```

**건강/운동 채널:**
```
이 대본 기반으로 YouTube 메타데이터를 생성해줘.
제목: "하루 N분" 패턴, 동작 수 포함
설명: 운동 순서 타임스탬프 포함, 주의사항 고지
태그: 운동/건강 키워드 + 부위별 키워드 10개
카테고리: 17 (스포츠)
```

**교육 채널:**
```
이 대본 기반으로 YouTube 메타데이터를 생성해줘.
제목: "초보도 따라하는" 또는 "N단계로 배우는" 패턴
설명: 학습 목표 + 단계별 타임스탬프 + 관련 자료 링크 자리
태그: 학습 주제 + 난이도 키워드 10개
카테고리: 27 (교육)
```

**요리 채널:**
```
이 대본 기반으로 YouTube 메타데이터를 생성해줘.
제목: 요리명 + 소요시간 + "간단 레시피" 패턴
설명: 재료 목록 + 조리 타임스탬프 + 꿀팁
태그: 요리명 + 재료 키워드 + 상황(자취, 다이어트) 10개
카테고리: 26 (노하우)
```

---

## Part 11: 전체 파이프라인 연동 구상

### 롱폼 E2E 흐름

```
[1] 대본 작성 (script.txt)
    ↓
[2] /generate-video → 슬라이드 + B-roll + TTS
    ↓
[3] 파이프라인 실행 → final_video.mp4 + corrected_subtitles.srt
    ↓
[4] 메타데이터 생성 (대본 + SRT → 제목/설명/챕터/태그)
    ↓
[5] youtube_upload.py로 비공개 업로드
    ↓
[6] YouTube Studio 확인 → 오전 9~11시에 공개 전환
```

### 쇼츠 E2E 흐름

```
[1] 대본 작성 (script.txt) — 롱폼과 같은 대본 재활용
    ↓
[2] /generate-shorts → 쇼츠 슬라이드 + 훅 타이틀
    ↓
[3] 파이프라인 실행 → final_shorts.mp4
    ↓
[4] 메타데이터 생성 (대본 → 훅 제목/#Shorts/짧은 설명)
    ↓  ※ SRT 기반 타임스탬프 불필요
[5] youtube_upload.py로 비공개 업로드
    ↓
[6] YouTube Studio 확인 → 오후 6~8시에 공개 전환
```

### 멀티포맷 업로드 일정

같은 대본으로 만든 롱폼과 쇼츠를 **다른 날, 다른 시간**에 공개합니다:

```
Day 1 (월) 오전 9시: 롱폼 공개
    ├── 검색 인덱싱 시간 확보
    └── SRT 기반 챕터 타임스탬프가 검색 노출에 도움

Day 2 (화) 오후 6시: 쇼츠 공개
    ├── 퇴근 후 모바일 스크롤 시간대
    ├── 설명에 "본편 보기" 링크 → 롱폼으로 유도
    └── #Shorts 해시태그 필수

Day 3 (수): 캐러셀은 인스타그램에 수동 업로드 (API 별도)
```

**업로드 명령어:**

```bash
# Day 1: 롱폼 비공개 업로드
uv run python scripts/youtube_upload.py \
    projects/my-project/output/final_video.mp4 \
    --title "AI 영상 자동화: 대본 하나로 끝내는 5단계 가이드" \
    --description "$(cat projects/my-project/upload_metadata_video_description.txt)" \
    --tags "AI 영상 자동화" "유튜브 자동화" "AI 영상 제작" "대본" "자동화" \
    --privacy private

# Day 2: 쇼츠 비공개 업로드
uv run python scripts/youtube_upload.py \
    projects/my-project/shorts_slides/output/final_shorts.mp4 \
    --title "AI가 3분 만에 영상을 만든다 #Shorts" \
    --description "대본 하나로 영상 자동 생성 #Shorts #AI자동화 #유튜브" \
    --tags "Shorts" "AI 자동화" "유튜브" "꿀팁" "영상제작" \
    --privacy private
```

### Claude Code에 전체 워크플로우 요청

```
projects/my-project의 대본(script.txt)과 자막(output/corrected_subtitles.srt)을 읽고
롱폼과 쇼츠 각각의 YouTube 메타데이터를 생성해줘.

롱폼:
- 제목 (SEO 키워드 앞배치, 60자)
- 설명 (SRT 기반 챕터 타임스탬프 포함, 해시태그 3개)
- 태그 10개

쇼츠:
- 제목 (#Shorts 포함, 훅 중심, 40자)
- 설명 (100자 이내, #Shorts + 본편 링크 자리)
- 태그 6개

각각 upload_metadata_video.json, upload_metadata_shorts.json으로 저장.
```

---

## 더 알아보기

| 주제 | 참고 |
|------|------|
| 멀티포맷 동시 제작 | **07-multi-format-strategy.md** |
| 업로드 일정 전략 | **07-multi-format-strategy.md** Part 5 |
| 채널 유형별 운영 루틴 | **14-real-world-scenarios.md** |
| API 비용 관리 | **16-faq-troubleshooting.md** |
| YouTube Data API 공식 문서 | [developers.google.com/youtube/v3](https://developers.google.com/youtube/v3) |
