---
name: tts
description: "Reference manual for TTS audio generation — 4 backends (Qwen CUDA/MPS, ElevenLabs, Custom Voice), auto-selection logic, batch paragraph processing, and TTS pronunciation dictionary enhancement workflow. Load when working with features/generate_tts/, debugging audio generation, or enhancing the TTS pronunciation dictionary before pipeline execution."
user-invocable: false
---

# TTS Manual

## Activation Conditions
- **Keywords**: tts, 음성, 보이스, elevenlabs, qwen, speech, 오디오, 사전 강화, 발음 사전, pronunciation, dictionary
- **Intent Patterns**: "TTS 변경", "음성 백엔드 교체", "음성 생성", "발음 사전 보강", "사전에 발음 추가"
- **Working Files**: `features/generate_tts/`, `features/generate_tts/backends/`, `config/tts_dictionary.yaml`, `features/normalize_text/enhance.py`
- **Content Patterns**: `create_tts_backend`, `generate_tts_for_paragraphs`, `TTSBackend`, `enhance_tts_dictionary`, `tts_dictionary`

## Chapters
1. [백엔드와 선택 로직](chapter-backends-and-selection.md) -- 4개 백엔드, 자동 선택, 전처리
2. [발음 사전 강화 워크플로](chapter-dictionary-enhancement.md) -- 대본의 영어/숫자 → 한글 발음 사전 등록 (Claude Code 직접 수행, GPT-5.1 API 대체)
