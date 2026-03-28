# Video-to-Shorts 워크플로

외부 영상에서 쇼츠/릴스를 생성. Whisper SRT + corrections.txt 교정 + Claude 바이럴 구간 선정 + 캡션 생성.

## 전체 흐름

```
MP4 영상
  → Step 1: 프로젝트 확인 + 소스 영상 탐색
  → Step 2: Word Timestamps 추출 (Whisper)
  → Step 3: SRT 자동 생성
  → Step 4: SRT 품질 확인 → 사용자 결정
  → Step 5: corrections.txt 생성 (선택)
  → Step 6: 바이럴 구간 선정 (Claude 직접 분석)
  → Step 7: 파이프라인 실행
  → Step 8: 결과 확인
  → Step 9: 캡션 생성
```

## Step 1: 프로젝트 확인 + 소스 영상

1. `projects/$PROJECT/` 확인
2. MP4 탐색: 1개면 바로 사용, 여러 개면 사용자 선택
3. 캐시 확인:
   - `shorts/word_timestamps.json` → Whisper skip
   - `output/corrected_subtitles.srt` → SRT skip
   - `shorts/viral_plan.json` → 바이럴 선정 skip

## Step 2: Word Timestamps (Whisper)

`shorts/word_timestamps.json` 없을 때만:

```bash
uv run python -c "
from pathlib import Path
from pipelines.video_to_shorts.lib import _step_word_timestamps
project_dir = Path('projects/$PROJECT')
video_path = Path('<영상 경로>')
shorts_dir = project_dir / 'shorts'
shorts_dir.mkdir(parents=True, exist_ok=True)
words = _step_word_timestamps(video_path, shorts_dir / 'word_timestamps.json')
print(f'완료: {len(words)}개 단어')
"
```

## Step 3: SRT 생성

`output/corrected_subtitles.srt` 없을 때만:

```bash
uv run python -c "
import json
from pathlib import Path
from entities.subtitle.model import WordTimestamp
from pipelines.video_to_shorts.lib import _apply_text_corrections, _generate_srt_from_words
project_dir = Path('projects/$PROJECT')
word_ts_path = project_dir / 'shorts' / 'word_timestamps.json'
data = json.loads(word_ts_path.read_text(encoding='utf-8'))
words = [WordTimestamp.model_validate(w) for w in data]
corrections_path = project_dir / 'corrections.txt'
if corrections_path.exists():
    words = _apply_text_corrections(words, corrections_path)
srt_path = project_dir / 'output' / 'corrected_subtitles.srt'
srt_path.parent.mkdir(parents=True, exist_ok=True)
_generate_srt_from_words(words, srt_path)
"
```

## Step 4: SRT 품질 확인

1. 처음 20~30줄 표시
2. 오타/오인식 패턴 테이블 제시
3. 사용자 결정: "교정 없이 진행" / "corrections.txt 작성" / "직접 수정"

## Step 5: corrections.txt (선택)

```
# 교정 매핑 파일
NaN → n8n
지밀 → Gmail
```

기존 SRT 삭제 → Step 3 재실행 (corrections 적용) → 확인

## Step 6: 바이럴 구간 선정 (Claude 직접)

### 데이터 수집
- corrected_subtitles.srt 전문
- script.txt (있으면)
- ShortsConfig 기본값: max_shorts=3, min_duration=15, max_duration=60

### 바이럴 판단 기준
1. **3초 훅 임팩트** (최우선): 스크롤 멈추게 하는 문장
2. **자기완결성**: 구간만으로 맥락 완전 이해
3. **바이럴 요소**: 실용 팁, 감정 포인트, 논쟁 유발

### hook_title 규칙
- 한 줄 메인 타이틀 (최대 16자)
- 영상 내용 특화 (범용 클릭베이트 금지)

### 사용자 승인
테이블로 제시 → "이대로 진행" / "구간 수정" / "구간 삭제" / "대안 요청"

### viral_plan.json

```json
{
  "segments": [
    {
      "index": 1,
      "start_time": 59.64,
      "end_time": 86.20,
      "hook_title": "20분 영상을\n2분 PPT로",
      "viral_reason": "3초 훅 + 구체적 변환 팁"
    }
  ]
}
```

검증: overlap 없음, duration 범위 내, index 순차, hook_title 16자

## Step 7: 파이프라인 실행

```bash
uv run video-automation pipeline video-to-shorts \
  --project "$PROJECT" --input "<영상 경로>"
```

캐시 재사용: word_timestamps, SRT, viral_plan.json

## Step 8: 결과 확인

생성된 쇼츠 목록 테이블 + 선정 이유 표시

## Step 9: 캡션 생성

### 가이드라인
`docs/shorts/caption-guideline.md` 로드

### 작성 규칙
- 브랜드 톤 (경험 기반, 솔직, 구체적 숫자)
- 3~6줄, 빈 줄로 호흡
- 클릭베이트 금지, 해시태그 금지
- 쇼츠 유형 자동 판단 (데모형/팁형/비교형)

### 저장
`projects/$PROJECT/shorts/short_001_caption.txt` 등 개별 파일

## 재실행 가이드

| 상황 | 방법 |
|------|------|
| corrections.txt 수정 후 SRT 재생성 | `rm output/corrected_subtitles.srt shorts/viral_plan.json` |
| 바이럴 구간만 재선정 | `rm shorts/viral_plan.json` |
| 전체 재생성 | `rm -rf shorts/ output/` |

## 주의사항
- word_timestamps.json 보존 (Whisper API 비용)
- corrections.txt 대소문자 구분
- script.txt 없는 외부 영상도 정상 동작
- viral_plan.json은 ViralSegmentPlan 모델 호환 (features/select_viral_segments/model.py)
