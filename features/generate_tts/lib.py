"""TTS 생성 핵심 로직 (백엔드 선택 및 실행)."""

from __future__ import annotations

from pathlib import Path

from entities.audio.model import AudioClip
from entities.script.model import Paragraph
from shared.config.schema import TTSConfig
from shared.lib.file_io import ensure_dir
from shared.lib.logger import get_logger
from shared.lib.platform import PlatformInfo, detect_platform

from .model import TTSBackend, TTSRequest, TTSResult
from .preprocess import preprocess_for_tts

logger = get_logger()


def create_tts_backend(config: TTSConfig, platform: PlatformInfo | None = None) -> TTSBackend:
    """플랫폼에 맞는 TTS 백엔드를 생성.

    Args:
        config: TTS 설정.
        platform: 플랫폼 정보. None이면 자동 감지.

    Returns:
        TTSBackend 인스턴스.
    """
    if config.force_backend:
        return _load_backend(config.force_backend, config)

    if platform is None:
        platform = detect_platform()

    if platform.has_cuda:
        return _load_backend("cuda", config)
    elif platform.has_mps:
        return _load_backend("mps", config)
    else:
        return _load_backend("elevenlabs", config)


def _load_backend(backend_name: str, config: TTSConfig) -> TTSBackend:
    """이름으로 특정 백엔드를 로딩."""
    if backend_name == "cuda":
        from .backends.qwen_cuda import QwenCudaBackend

        return QwenCudaBackend(
            model_name=config.model,
            speaker=config.speaker,
            language=config.language,
            dtype=config.cuda.dtype,
            attn_impl=config.cuda.attn_implementation,
            device=config.cuda.device,
        )
    elif backend_name == "mps":
        from .backends.qwen_mps import QwenMpsBackend

        return QwenMpsBackend(
            model_name=config.model,
            speaker=config.speaker,
            language=config.language,
            dtype=config.mps.dtype,
            attn_impl=config.mps.attn_implementation,
            device=config.mps.device,
        )
    elif backend_name == "elevenlabs":
        from .backends.elevenlabs_api import ElevenLabsBackend

        el = config.elevenlabs
        return ElevenLabsBackend(
            voice_id=el.voice_id,
            model_id=el.model_id,
            stability=el.stability,
            similarity_boost=el.similarity_boost,
            style_exaggeration=el.style_exaggeration,
            use_speaker_boost=el.use_speaker_boost,
            speed=el.speed,
            output_format=el.output_format,
            language_code=el.language_code,
            api_key_env=el.api_key_env,
            fallback_api_key_env=el.fallback_api_key_env,
        )
    elif backend_name == "custom_voice":
        from pathlib import Path

        from .backends.custom_voice import CustomVoiceBackend

        # voice-fine-tuning 경로 계산 (프로젝트 루트 기준)
        project_root = Path(__file__).resolve().parents[2]
        cv_config = config.custom_voice

        speaker_dir = (
            project_root
            / "voice-fine-tuning"
            / "speakers"
            / cv_config.speaker_name
            / cv_config.speaker_version
        )

        return CustomVoiceBackend(
            model_path=project_root / cv_config.model_path,
            embedding_path=speaker_dir / "speaker_embedding_final.pt",
            ref_audio_path=speaker_dir / "ref_audio.wav",
            ref_text_path=speaker_dir / "ref_text.txt",
            speaker_name=cv_config.speaker_name,
            language=config.language,
            dtype=cv_config.dtype,
            attn_impl=cv_config.attn_implementation,
            device=cv_config.device,
            max_tokens=cv_config.max_tokens,
        )
    else:
        raise ValueError(f"알 수 없는 TTS 백엔드: {backend_name}")


def generate_tts_for_text(
    text: str,
    output_path: Path,
    config: TTSConfig,
    backend: TTSBackend | None = None,
    tts_text: str = "",
) -> TTSResult:
    """단일 텍스트에 대한 TTS 음성을 생성.

    Args:
        text: 원본 텍스트 (자막/메타데이터용).
        output_path: 출력 오디오 파일 경로.
        config: TTS 설정.
        backend: TTS 백엔드. None이면 자동 선택.
        tts_text: 전처리된 TTS용 텍스트. 비어있으면 text 사용.

    Returns:
        TTS 생성 결과.
    """
    if backend is None:
        backend = create_tts_backend(config)

    request = TTSRequest(
        text=text,
        tts_text=tts_text,
        speaker=config.speaker,
        language=config.language,
        output_path=output_path,
    )

    logger.info("TTS 생성: backend=%s, speaker=%s", backend.name, config.speaker)
    return backend.generate(request)


def generate_tts_for_paragraphs(
    paragraphs: list[Paragraph],
    audio_dir: Path,
    config: TTSConfig,
    backend: TTSBackend | None = None,
) -> list[AudioClip]:
    """여러 문단에 대한 TTS 음성을 일괄 생성.

    Args:
        paragraphs: 문단 목록.
        audio_dir: 오디오 파일 저장 디렉토리.
        config: TTS 설정.
        backend: TTS 백엔드. None이면 자동 선택.

    Returns:
        생성된 AudioClip 엔티티 목록.
    """
    if backend is None:
        backend = create_tts_backend(config)

    # TTS 발음 사전 로드
    from features.normalize_text import load_tts_dictionary

    tts_dictionary = load_tts_dictionary()

    ensure_dir(audio_dir)
    clips: list[AudioClip] = []

    from shared.lib.ffmpeg import get_duration

    from .sidecar import read_tts_sidecar, sync_tts_sidecar

    for paragraph in paragraphs:
        output_path = audio_dir / f"{paragraph.index:03d}.wav"

        # 기존 파일이 있으면 재사용 (0바이트/손상 파일 제외)
        if output_path.exists() and output_path.stat().st_size > 0:
            try:
                # sidecar에서 duration/tts_text 읽기 (ffprobe + preprocess 생략)
                sidecar = read_tts_sidecar(output_path)
                text_match = sidecar and sidecar.get("text") == paragraph.text
                if text_match and sidecar.get("duration", 0) > 0:
                    duration = sidecar["duration"]
                    logger.info("기존 TTS 재사용 (sidecar): %s", output_path.name)
                else:
                    duration = get_duration(output_path)
                    logger.info("기존 TTS 재사용: %s", output_path.name)
                    tts_text = preprocess_for_tts(paragraph.text, tts_dictionary=tts_dictionary)
                    sync_tts_sidecar(output_path, paragraph.text, tts_text, duration)

                clip = AudioClip(
                    index=paragraph.index,
                    file_path=output_path,
                    duration=duration,
                    sample_rate=sidecar.get("sample_rate", 24000) if sidecar else 24000,
                )
                clips.append(clip)
                continue
            except Exception:
                logger.warning(
                    "손상된 TTS 파일 삭제 후 재생성: %s",
                    output_path.name,
                )
                output_path.unlink(missing_ok=True)

        # 발음 사전 + 숫자 정규화 전처리
        tts_text = preprocess_for_tts(paragraph.text, tts_dictionary=tts_dictionary)

        logger.info("TTS 생성 중: 문단 %d/%d", paragraph.index, len(paragraphs))
        result = generate_tts_for_text(
            text=paragraph.text,
            output_path=output_path,
            config=config,
            backend=backend,
            tts_text=tts_text,
        )

        if not result.success:
            logger.error("TTS 생성 실패 (문단 %d): %s", paragraph.index, result.error)
            raise RuntimeError(f"문단 {paragraph.index} TTS 생성 실패: {result.error}")

        clip = AudioClip(
            index=paragraph.index,
            file_path=result.output_path,
            duration=result.duration,
            sample_rate=result.sample_rate,
        )
        clips.append(clip)

    logger.info("전체 %d개 TTS 음성 생성 완료", len(clips))
    return clips
