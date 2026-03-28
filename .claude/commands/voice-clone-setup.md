---
name: voice-clone-setup
description: "Voice Clone Speaker Profile Setup"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, WebFetch
argument-hint: "<speaker-name> <source>"
---

# /voice-clone-setup -- Voice Clone Speaker Profile Setup

노이즈/멀티화자 음성에서 타겟 화자를 분리하고 Qwen TTS x-vec + ICL 스피커 프로필을 생성합니다.

**Argument**: `<speaker-name> <source>` (e.g., `elvin https://youtube.com/watch?v=...`)

---

## Pipeline Overview

```
1. acquire   — YouTube URL or 로컬 파일 → raw.wav
2. diarize   — STT + MFCC/pitch/energy 특성 → 화자 클러스터링
3. extract   — 타겟 화자 구간만 추출 + x-vector (사용자 확인 필수)
4. select-ref — 일관된 톤 구간을 ref_audio로 선정 (pitch 안정성 우선)
5. test      — x-vec + ICL 조합 인퍼런스 테스트
```

**핵심 원칙:**
- ref_audio는 **에너지 높은 구간이 아니라 톤이 일관된 구간** (pitch 분산 낮은 서술/설명체)
- 화자 분리는 STT 텍스트 맥락 + 오디오 특성을 **함께** 사용
- x-vector는 타겟 화자 **전용** clean audio에서 추출 (다른 화자 오염 방지)
- x-vector는 **청크 평균 임베딩** 방식: 10초 균등 분할 → per-chunk 추출 → L2 정규화 → 평균 → 스케일 복원 → `[1, 2048]` shape

---

## Step 1: Audio Acquisition

인자에서 speaker name과 source를 파싱합니다.

```bash
uv run python scripts/voice_clone_pipeline.py acquire <SPEAKER_NAME> --source "<SOURCE>"
```

- YouTube URL이면 yt-dlp로 다운로드
- 로컬 파일이면 복사
- 결과: `voice_clone/<name>/raw.wav`

---

## Step 2: Speaker Diarization

```bash
uv run python scripts/voice_clone_pipeline.py diarize <SPEAKER_NAME> --speakers <N> --language <LANG>
```

- `--speakers`: 예상 화자 수 (기본 2)
- `--language`: STT 언어 코드 (ko, ja, en 등)
- 결과: `voice_clone/<name>/diarization.json` + `speakers/SPEAKER_*.wav`

**실행 후 반드시:**
1. `diarization.json`을 읽어 화자별 대사 텍스트를 사용자에게 보여줌
2. `speakers/SPEAKER_*.wav` 파일 경로를 안내하여 청취 유도
3. **사용자에게 질문**: "어떤 화자가 타겟인가요? 제거할 세그먼트가 있나요?"

### 자동 클러스터링이 감정별로 분리될 수 있음

같은 화자가 차분한 톤/열혈 톤으로 분리되는 경우:
- STT 텍스트의 **대화 맥락** (질문↔응답 패턴)으로 실제 화자 경계 파악
- 사용자와 함께 세그먼트 단위로 검수하여 타겟/비타겟 구분

---

## Step 3: Target Speaker Extraction

사용자가 화자를 확인한 후 실행합니다.

```bash
uv run python scripts/voice_clone_pipeline.py extract <SPEAKER_NAME> \
  --keep <SPEAKER_IDS> \
  --remove <SEGMENT_INDICES>  # optional, 개별 세그먼트 제거
```

- `--keep`: 유지할 화자 번호 (e.g., `0` 또는 `0,1`)
- `--remove`: 제거할 세그먼트 인덱스 (e.g., `2,4,5,23,24,25`)
- **x-vector 추출 방식**: 청크 평균 임베딩
  - clean.wav를 10초 균등 분할 (마지막 3초 미만 잔여 버림)
  - per-chunk ECAPA-TDNN 임베딩 추출
  - L2 정규화 → 평균 → 원래 norm 스케일 복원
  - 짧은 오디오 (≤13초)는 통째로 1회 추출
- 결과:
  - `voice_clone/<name>/clean.wav` (타겟 화자만)
  - `voice-fine-tuning/speakers/<name>/v1/speaker_embedding_final.pt` (shape `[1, 2048]`)
  - `voice-fine-tuning/speakers/<name>/v1/metadata.yaml`

---

## Step 4: Ref Audio Selection

```bash
uv run python scripts/voice_clone_pipeline.py select-ref <SPEAKER_NAME> --language <LANG>
```

- clean.wav를 STT하고 5~15초 후보 구간을 점수화
- **점수 기준 (pitch 안정성이 최대 가중치)**:
  - pitch stability 25% (F0 분산 낮을수록 = 절규 아님)
  - energy consistency 20%
  - text substance 20%
  - speech density 15%
  - duration proximity 10%
  - speaking rate 10%
- 결과:
  - `voice-fine-tuning/speakers/<name>/v1/ref_audio.wav`
  - `voice-fine-tuning/speakers/<name>/v1/ref_text.txt`
  - `voice_clone/<name>/ref_candidates.json` (상위 10개 후보)

**실행 후:** 상위 5개 후보를 사용자에게 보여주고, 1위가 적합한지 확인.
부적합하면 `ref_candidates.json`에서 다른 후보를 수동 선택 가능.

---

## Step 5: Test Generation

```bash
uv run python scripts/voice_clone_pipeline.py test <SPEAKER_NAME> \
  -t "<TEST_TEXT>" -l <LANGUAGE>
```

- x-vec + ICL 조합으로 테스트 음성 생성
- 결과: `voice_clone/<name>/test_output.wav`
- 사용자에게 파일 경로 안내하여 청취 유도

**일관성 테스트**: 다양한 톤의 문장 3개 이상을 생성하여 음색 일관성 확인:
- 차분한 톤 (서술/설명)
- 강한 톤 (연설/감정)
- 나레이션 톤 (중립)

---

## File Structure

```
voice_clone/<name>/           # 작업 디렉토리 (임시)
  raw.wav                     # 원본 오디오
  diarization.json            # 화자 분리 결과
  speakers/SPEAKER_*.wav      # 화자별 오디오
  clean.wav                   # 타겟 화자 전용
  ref_candidates.json         # ref_audio 후보 목록
  test_output.wav             # 테스트 결과

voice-fine-tuning/speakers/<name>/v1/   # 최종 프로필
  speaker_embedding_final.pt  # x-vector [1, 2048] (청크 평균 임베딩)
  ref_audio.wav               # ICL 참조 오디오 (5~15s)
  ref_text.txt                # ref_audio 전사
  metadata.yaml               # 메타데이터
```

---

## Config Integration

스피커 프로필 생성 후 파이프라인에서 사용하려면:

```yaml
# config.base.yaml (또는 활성 프로필)
tts:
  force_backend: "custom_voice"
  custom_voice:
    speaker_name: "<name>"
    speaker_version: "v1"
    instruction: "youtube"
```

---

## Error Recovery

| 문제 | 해결 |
|------|------|
| 클러스터링이 감정별로 분리 | diarization.json + STT 텍스트로 수동 검수 |
| ref_audio가 절규 구간 | `ref_candidates.json`에서 pitch 점수 높은 후보 선택 |
| x-vector에 다른 화자 오염 | `--remove`로 세그먼트 제거 후 extract 재실행 |
| 테스트 음질 불량 | ref_audio 교체 (select-ref 재실행) |
