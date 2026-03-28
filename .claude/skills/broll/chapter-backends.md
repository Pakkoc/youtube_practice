# B-roll 이미지 백엔드

> 소스: `features/fetch_broll/lib.py`, `features/fetch_broll/backends/`

## 백엔드 라우팅

`fetch_broll_image()` 에서 `backend` 파라미터로 라우팅:

| 백엔드 | 값 | 소스 | 특징 |
|--------|-----|------|------|
| FLUX.2 Klein | `flux2_klein` | 로컬 GPU | 4-step, ~12초/이미지, 1280x720 |
| Flux Kontext | `flux_kontext` | 로컬 GPU | img2img, LoRA, 20 steps, ~35초, 1344x768 |
| NanoBanana | `nanobanana` | Gemini API | 레퍼런스 기반 편집, 클라우드 |
| Search | `search` | SerperDev | 실제 이미지 검색 + Vision 검증 |

## FLUX.2 Klein

- `features/fetch_broll/backends/flux2_klein.py`
- `Flux2KleinPipeline` (diffusers dev 버전 필수)
- `enable_cpu_offload: true` → VRAM 절약
- Config: `broll.flux2_klein` (Flux2KleinConfig)

## Flux Kontext + LoRA

- `features/fetch_broll/backends/flux_kontext.py`
- **img2img 전용** -- 참조 이미지 필수 (없으면 None 반환)
- `FluxKontextPipeline` + `enable_model_cpu_offload()` + LoRA
- `guidance_scale=4.0`, `lora_scale=1.0`
- Config: `broll.flux_kontext` (FluxKontextConfig)

## NanoBanana (Gemini)

- Gemini 이미지 생성/편집 API
- `use_reference: true` -- 스타일 일관성
- `save_captions: true` -- 프롬프트 저장
- Config: `broll.nanobanana` (NanoBananaConfig)

## 이미지 검색 (SerperDev)

- SerperDev API로 이미지 검색
- Vision 검증 (검색 결과 품질 확인)
- Fallback: 검색 실패 → generate, generate 실패 → Pexels

## Config 설정

```yaml
pipeline:
  broll:
    enabled: true
    image_search: true          # AI가 search/generate 자동 결정
    image_gen_backend: local    # local | nanobanana

broll:
  force_backend: flux2_klein    # 개별 백엔드 강제 지정
  character_description: "..."  # 캐릭터 프롬프트
```

### 주의: image_gen_backend과 force_backend 관계
- `image_gen_backend: "nanobanana"` → `force_backend`를 `"nanobanana"`로 덮어씀
- `image_gen_backend: "local"` → 기존 `force_backend` 유지 (flux2_klein, flux_kontext 등)
