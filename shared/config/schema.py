"""설정 스키마 정의 (Pydantic)."""

from pydantic import BaseModel, Field


class CudaConfig(BaseModel):
    """CUDA TTS 백엔드 설정."""

    dtype: str = "bfloat16"
    attn_implementation: str = "flash_attention_2"
    device: str = "cuda:0"


class MpsConfig(BaseModel):
    """MPS (Apple Silicon) TTS 백엔드 설정."""

    dtype: str = "float32"
    attn_implementation: str = "sdpa"
    device: str = "mps"


class ElevenLabsConfig(BaseModel):
    """ElevenLabs TTS API 백엔드 설정."""

    voice_id: str = "60gzQ1UbhCSBg4mgozcQ"
    model_id: str = "eleven_multilingual_v2"
    stability: float = 0.85
    similarity_boost: float = 0.58
    style_exaggeration: float = 0.0  # 0.0~1.0 (API: style)
    use_speaker_boost: bool = True  # 스피커 부스트 활성화
    speed: float = 1.0
    output_format: str = "mp3_44100_192"  # Creator+: mp3_44100_192, Pro+: wav_44100
    language_code: str = "ko"
    api_key_env: str = "ELEVENLABS_API_KEY"  # 사용할 환경변수 이름
    fallback_api_key_env: str = ""  # 실패 시 재시도할 환경변수 (빈 문자열이면 비활성)


class CustomVoiceConfig(BaseModel):
    """커스텀 보이스 TTS 백엔드 설정.

    voice-fine-tuning의 speaker embedding + ICL 참조 오디오를 조합하여
    x-vec + ICL voice cloning 방식으로 음성을 생성합니다.

    필요 파일 (speakers/<name>/<version>/ 아래):
      - speaker_embedding_final.pt  (전체 오디오에서 추출한 x-vector)
      - ref_audio.wav               (ICL 참조 오디오, 5~15초)
      - ref_text.txt                (ref_audio의 전사 텍스트)
    """

    model_path: str = "voice-fine-tuning/models/Qwen3-TTS-12Hz-1.7B-Base"
    speaker_name: str = "hoyoung"
    speaker_version: str = "v1"
    instruction: str = "youtube"  # 프리셋: youtube, calm, steady, flat 등
    dtype: str = "bfloat16"
    attn_implementation: str = "sdpa"
    device: str = "cuda:0"
    max_tokens: int = 4096


class TTSConfig(BaseModel):
    """TTS 설정."""

    model: str = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
    tokenizer: str = "Qwen/Qwen3-TTS-Tokenizer-12Hz"
    speaker: str = "Sohee"
    language: str = "Korean"
    force_backend: str | None = None

    cuda: CudaConfig = Field(default_factory=CudaConfig)
    mps: MpsConfig = Field(default_factory=MpsConfig)
    elevenlabs: ElevenLabsConfig = Field(default_factory=ElevenLabsConfig)
    custom_voice: CustomVoiceConfig = Field(default_factory=CustomVoiceConfig)


class ValidationConfig(BaseModel):
    """TTS 검증 설정."""

    enabled: bool = True
    min_match_rate: float = 0.8
    max_retries: int = 3


class RemotionSlidesConfig(BaseModel):
    """Remotion 슬라이드 백엔드 설정."""

    remotion_project_path: str = "remotion"
    fps: int = 30
    width: int = 1920
    height: int = 1080
    render_parallel_slots: int = 4  # Freeform 병렬 렌더링 슬롯 수 (1=순차)


class ManimSlidesConfig(BaseModel):
    """Manim CE 슬라이드 백엔드 설정.

    수학 수식, 좌표계, 알고리즘 시각화 등 Remotion 템플릿으로
    표현 불가능한 문단을 Manim CE로 렌더링합니다.
    """

    model: str = "gpt-5-mini"
    max_retries: int = 2
    render_timeout: int = 120  # 렌더링 타임아웃 (초)
    quality: str = "high_quality"  # manim quality preset


class SlidesConfig(BaseModel):
    """슬라이드 설정."""

    backend: str = "remotion"
    width: int = 1920
    height: int = 1080
    font_path: str = "assets/fonts"  # 로컬 폰트 경로
    context_stride: int = 4  # 슬라이드 생성 시 참조할 앞뒤 문단 수 (4=±4개 총 9개 문단)
    remotion: RemotionSlidesConfig = Field(default_factory=RemotionSlidesConfig)
    manim: ManimSlidesConfig = Field(default_factory=ManimSlidesConfig)


class SubtitlesConfig(BaseModel):
    """자막 설정."""

    font: str = "Pretendard"
    font_size: int = 28
    color: str = "white"
    background: str = "rgba(0,0,0,0.6)"
    position: str = "bottom"
    margin_v: int = 50  # 하단 여백 (픽셀)
    max_chars_per_line: int = 25  # 한 줄 최대 글자 수
    min_chars_per_line: int = 5  # 최소 글자 수 (이하면 다음 구와 병합)



class Flux2KleinConfig(BaseModel):
    """FLUX.2 Klein 4B B-roll 이미지 생성 설정.

    Black Forest Labs의 FLUX.2 Klein 4B 모델을 사용합니다.
    - 4 스텝으로 1초 미만 생성
    - ~13GB VRAM
    - Apache 2.0 라이선스
    """

    model_id: str = "black-forest-labs/FLUX.2-klein-4B"
    num_inference_steps: int = 4  # Klein은 4스텝 권장
    height: int = 720  # 16:9 비율 (1280x720)
    width: int = 1280
    guidance_scale: float = 1.0  # Klein은 1.0 권장
    device: str = "cuda"
    use_reference: bool = True  # 레퍼런스 이미지 스타일 참조


class FluxKontextConfig(BaseModel):
    """Flux Kontext + LoRA B-roll 이미지 생성 설정 (img2img 전용).

    Flux Kontext dev 모델에 LoRA를 적용하여 일관된 캐릭터 이미지를 생성합니다.
    참조 이미지가 필수이며, 20 스텝으로 고품질 이미지를 생성합니다.
    """

    base_model_path: str = r"C:\Users\hoyoung\Desktop\ai-toolkit\models\FLUX.1-Kontext-dev"
    lora_path: str = (  # noqa: E501
        r"C:\Users\hoyoung\Desktop\ai-toolkit\output\flux_kontext_lora_v1\flux_kontext_lora_v1.safetensors"
    )
    num_inference_steps: int = 20
    height: int = 768  # 16:9 (1344x768), 64배수
    width: int = 1344
    guidance_scale: float = 4.0
    lora_scale: float = 1.0
    device: str = "cuda"
    use_reference: bool = True  # 항상 True (Kontext는 img2img 전용)


class ImageSearchConfig(BaseModel):
    """이미지 검색 설정 (SerperDev + OpenAI Vision).

    B-roll 이미지를 생성 대신 검색으로 가져올 때 사용합니다.
    AI가 컨텍스트를 분석하여 검색이 적합한 경우에만 사용됩니다.
    """

    enabled: bool = True  # 이미지 검색 기능 활성화
    validation_enabled: bool = True  # Vision 검증 활성화
    validation_model: str = "gpt-5.4-mini"  # 검증에 사용할 모델
    source_decision_model: str = "gpt-5-nano"  # source 판단에 사용할 모델
    max_candidates: int = 10  # 검색 결과 최대 개수 (다양한 이미지 확보)
    validation_threshold: float = 0.6  # 검증 통과 신뢰도 임계값


class NanoBananaConfig(BaseModel):
    """Gemini NanoBanana 이미지 생성/편집 백엔드 설정.

    google-genai 패키지를 사용하여 Gemini 이미지 생성 모델로
    텍스트→이미지 또는 레퍼런스 기반 이미지 편집을 수행합니다.
    """

    model: str = "gemini-2.5-flash-image"  # gemini-2.5-flash-image | gemini-3-pro-image-preview
    height: int = 720  # 16:9 비율 (1280x720)
    width: int = 1280
    aspect_ratio: str = "16:9"  # Gemini 지원: 1:1, 3:4, 4:3, 9:16, 16:9
    use_reference: bool = True  # 레퍼런스 이미지로 편집 (일관성 유지)
    save_captions: bool = True  # 프롬프트/캡션을 이미지 옆에 .txt 저장


class BrollConfig(BaseModel):
    """B-roll 설정."""

    image_sources: list[str] = Field(default_factory=lambda: ["pexels", "generate"])
    force_backend: str | None = (
        None  # null=기존방식, "flux2_klein"=FLUX.2, "nanobanana"=Gemini, "flux_kontext"=Kontext+LoRA  # noqa: E501
    )
    character_description: str = ""  # B-roll 캐릭터 설명 (FLUX.2 프롬프트 생성용)
    flux2_klein: Flux2KleinConfig = Field(default_factory=Flux2KleinConfig)
    flux_kontext: FluxKontextConfig = Field(default_factory=FluxKontextConfig)
    nanobanana: NanoBananaConfig = Field(default_factory=NanoBananaConfig)
    image_search: ImageSearchConfig = Field(default_factory=ImageSearchConfig)
    reference_base_dir: str = "assets/references"  # 레퍼런스 이미지 베이스 디렉토리
    reference_style: str = "chibi"  # 레퍼런스 이미지 스타일 (서브 디렉토리명)


class AvatarConfig(BaseModel):
    """아바타 오버레이 설정.

    Ditto를 사용하여 립싱크 아바타를 생성하고
    영상 우측 하단에 원형으로 오버레이합니다.
    """

    enabled: bool = False  # 아바타 오버레이 활성화 여부
    image_path: str = "assets/avatar_image/vtuber-avatar.png"  # 아바타 이미지 경로
    size: int = 180  # 원형 지름 (픽셀)
    margin_x: int = 30  # 우측 여백 (픽셀)
    margin_y: int = 120  # 하단 여백 (픽셀, 자막 피하기)
    border_width: int = 3  # 테두리 두께 (픽셀)
    border_color: str = "white"  # 테두리 색상
    ditto_project_path: str = "C:/Users/hoyoung/Desktop/ditto-talkinghead"  # Ditto 프로젝트 경로


class ThumbnailConfig(BaseModel):
    """썸네일 설정."""

    width: int = 1280
    height: int = 720
    main_copy_color: str = "white"
    sub_copy_color: str = "yellow"


class YoutubeScheduleConfig(BaseModel):
    """유튜브 스케줄 설정."""

    days: int = 5
    uploads_per_day: int = 2


class YoutubeConfig(BaseModel):
    """유튜브 설정."""

    schedule: YoutubeScheduleConfig = Field(default_factory=YoutubeScheduleConfig)
    default_category: str = "28"


class EnvironmentConfig(BaseModel):
    """환경 설정."""

    platform: str = "auto"


class PipelineTTSControl(BaseModel):
    """TTS 파이프라인 제어."""

    backend: str = "local"  # local


class PipelineSlidesControl(BaseModel):
    """슬라이드 파이프라인 제어."""

    backend: str = "remotion"  # remotion


class PipelineBrollControl(BaseModel):
    """B-roll 파이프라인 제어."""

    enabled: bool = True  # B-roll 전체 on/off
    image_search: bool = True  # false → 전부 이미지 생성
    image_gen_backend: str = "local"  # local | nanobanana
    save_captions: bool = True  # 프롬프트 저장 (파인튜닝용)
    scene_grouping: bool = True  # 연속 문단을 씬으로 그룹핑 (이미지 생성 수 절감)


class PipelineAvatarControl(BaseModel):
    """아바타 파이프라인 제어."""

    enabled: bool = True  # true | false


class PipelineScenesControl(BaseModel):
    """씬 분할 파이프라인 제어."""

    enabled: bool = True  # 기본 ON (문장 단위 씬 분할 표준)
    merge_threshold: int = 30  # 이 글자수 미만 문장은 인접 문장과 병합


class PipelineConfig(BaseModel):
    """파이프라인 통합 Control Panel.

    각 파이프라인 단계의 on/off, 백엔드 선택을 한 곳에서 관리합니다.
    여기서 설정한 값은 기존 세부 config에 자동 반영됩니다.
    """

    tts: PipelineTTSControl = Field(default_factory=PipelineTTSControl)
    slides: PipelineSlidesControl = Field(default_factory=PipelineSlidesControl)
    broll: PipelineBrollControl = Field(default_factory=PipelineBrollControl)
    avatar: PipelineAvatarControl = Field(default_factory=PipelineAvatarControl)
    scenes: PipelineScenesControl = Field(default_factory=PipelineScenesControl)


class ShortsConfig(BaseModel):
    """쇼츠/릴스 재가공 설정."""

    max_shorts: int = 3  # 영상당 최대 쇼츠 수
    min_duration: int = 15  # 최소 길이 (초)
    max_duration: int = 60  # 최대 길이 (초)
    model: str = "gpt-5.4-mini"  # 바이럴 구간 선정 LLM
    accent_color: str = "#A2FFEB"  # 메인 훅 타이틀 민트 컬러
    background_color: str = "#0f0f0f"  # 배경색
    hook_font_size: int = 200  # 훅 제목 폰트 크기 (Black 900, neon glow, 200px base)
    subtitle_font_size: int = 48  # 자막 폰트 크기
    video_corner_radius: int = 0  # 영상 모서리 라운드 (풀스크린이므로 0)


class ShortsSlideConfig(BaseModel):
    """쇼츠 슬라이드 (script-to-shorts) 설정.

    훅 타이틀은 /generate-shorts-title 스킬로 사전 생성 (API 미사용).
    """

    width: int = 1080
    height: int = 1920
    fps: int = 30
    render_parallel_slots: int = 4
    accent_color: str = "#A2FFEB"
    background_color: str = "#0f0f0f"
    hook_font_size: int = 200
    subtitle_font_size: int = 48
    whisper_language: str = "ko"


class BrandingConfig(BaseModel):
    """채널 브랜딩 설정 (카루셀/슬라이드 공용)."""

    brand_name: str = "@ai.sam_hottman"  # 채널명/핸들 (어트리뷰션)
    brand_voice: str = "친근하지만 전문적, 개조식, 핵심만"  # 글쓰기 톤
    target_audience: str = "AI/테크에 관심 있는 한국어 사용자"  # 타겟 독자


class CarouselBackgroundConfig(BaseModel):
    """캐러셀 AI 배경 이미지 생성 설정.

    NanoBanana (Gemini) 백엔드로 시네마틱 배경 이미지를 생성하여
    선택적 카드에 투명도 오버레이로 적용합니다.
    """

    enabled: bool = False  # opt-in: copy_deck.md에 image_prompt가 있어야 활성화
    backend: str = "nanobanana"  # 이미지 생성 백엔드
    opacity: float = 0.15  # 배경 이미지 투명도 (0.10~0.20 권장)
    prompt_suffix: str = (
        "cinematic lighting, dark moody atmosphere, professional quality, high detail, "
        "subject positioned in upper half of frame, "
        "leaving bottom 40% relatively clear for text overlay"
    )


class CarouselConfig(BaseModel):
    """카드뉴스(카루셀) 생성 설정 (Freeform TSX 전용)."""

    width: int = 1080  # 4:5 비율
    height: int = 1350
    theme: str = "dark"  # THEME_PRESETS key: dark | quiet-luxury
    background_color: str = "#0B0C0E"
    accent_color: str = "#7C7FD9"
    text_color: str = "#EDEDEF"
    branding: BrandingConfig = Field(default_factory=BrandingConfig)
    background: CarouselBackgroundConfig = Field(default_factory=CarouselBackgroundConfig)


class OutroConfig(BaseModel):
    """아웃트로 영상 합성 설정."""

    enabled: bool = True  # 아웃트로 합성 활성화
    video_path: str = "assets/outro_video/Outro Video.mp4"  # 아웃트로 영상 경로


class AppConfig(BaseModel):
    """전체 애플리케이션 설정."""

    outro: OutroConfig = Field(default_factory=OutroConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    slides: SlidesConfig = Field(default_factory=SlidesConfig)
    subtitles: SubtitlesConfig = Field(default_factory=SubtitlesConfig)
    broll: BrollConfig = Field(default_factory=BrollConfig)
    avatar: AvatarConfig = Field(default_factory=AvatarConfig)
    thumbnail: ThumbnailConfig = Field(default_factory=ThumbnailConfig)
    youtube: YoutubeConfig = Field(default_factory=YoutubeConfig)
    shorts: ShortsConfig = Field(default_factory=ShortsConfig)
    shorts_slide: ShortsSlideConfig = Field(default_factory=ShortsSlideConfig)
    carousel: CarouselConfig = Field(default_factory=CarouselConfig)
