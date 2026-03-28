# TTS 백엔드와 선택 로직

> 소스: `features/generate_tts/lib.py`, `features/generate_tts/backends/`

## 백엔드 자동 선택

`create_tts_backend()` 선택 순서:

```
1. config.force_backend 지정 → 해당 백엔드 사용
2. CUDA 감지 → QwenCudaBackend (bfloat16, flash_attention_2)
3. MPS 감지 → QwenMpsBackend (float32, sdpa)
4. Fallback → ElevenLabsBackend
```

## 4개 백엔드

| 백엔드 | 파일 | 요구사항 | 특징 |
|--------|------|----------|------|
| Qwen CUDA | `backends/qwen_cuda.py` | NVIDIA GPU | bfloat16, flash_attention_2 |
| Qwen MPS | `backends/qwen_mps.py` | Apple Silicon | float32, sdpa |
| ElevenLabs | `backends/elevenlabs_api.py` | API 키 | 클라우드 API |
| Custom Voice | `backends/custom_voice.py` | Fine-tuned 모델 | 사용자 정의 음성 |

## 주요 함수

### `generate_tts_for_paragraphs(paragraphs, audio_dir, config, backend=None)`
- 문단 리스트 → `audio/001.wav`, `002.wav`, ... 생성
- 기존 파일 존재 시 자동 skip (재사용)
- `AudioClip` 리스트 반환

### `generate_tts_for_text(text, output_path, config, backend=None, tts_text="")`
- 단일 텍스트 → 단일 오디오 파일
- `tts_text` 지정 시 해당 텍스트로 TTS (교정용)

## TTS 검증

`features/validate_tts/` -- TTS 출력 품질 검증 (선택):
- `config.tts.validation.enabled` -- 검증 on/off
- `min_match_rate` -- 최소 매칭률
- `max_retries` -- 재시도 횟수

## Config

```yaml
tts:
  model: "..."
  speaker: "..."
  language: "ko"
  force_backend: null  # null | cuda | mps | elevenlabs | custom_voice

pipeline:
  tts:
    backend: elevenlabs  # local | elevenlabs
```

## CLI

```bash
uv run video-automation tts generate --input paragraph.txt
```
