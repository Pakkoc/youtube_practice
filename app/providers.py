"""환경 감지 및 의존성 주입.

플랫폼에 따라 적절한 TTS 백엔드를 선택한다.
"""

from __future__ import annotations

from shared.config.schema import TTSConfig
from shared.lib.logger import get_logger
from shared.lib.platform import PlatformInfo, detect_platform

logger = get_logger()


def get_tts_backend_name(tts_config: TTSConfig, platform: PlatformInfo | None = None) -> str:
    """플랫폼에 맞는 TTS 백엔드 이름을 반환.

    Args:
        tts_config: TTS 설정.
        platform: 플랫폼 정보. None이면 자동 감지.

    Returns:
        백엔드 이름: "cuda", "mps", "elevenlabs"
    """
    if tts_config.force_backend:
        logger.info("TTS 백엔드 강제 지정: %s", tts_config.force_backend)
        return tts_config.force_backend

    if platform is None:
        platform = detect_platform()

    logger.info("플랫폼 감지: %s", platform.summary)

    if platform.has_cuda:
        logger.info("TTS 백엔드 선택: CUDA (bfloat16, flash_attention_2)")
        return "cuda"
    elif platform.has_mps:
        logger.info("TTS 백엔드 선택: MPS (float32, sdpa)")
        return "mps"
    else:
        logger.info("TTS 백엔드 선택: ElevenLabs API (GPU 미감지)")
        return "elevenlabs"
