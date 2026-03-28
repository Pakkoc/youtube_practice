"""전역 설정 로딩 (프로필 기반 + 환경변수 오버라이드)."""

from __future__ import annotations

import os
import threading
from pathlib import Path

from shared.config import AppConfig, load_config
from shared.lib.logger import get_logger

logger = get_logger()

_config: AppConfig | None = None
_config_lock = threading.Lock()

# Config 프로필
PROFILES = ["base", "api", "asmr", "shorts"]
DEFAULT_PROFILE = "api"
CONFIG_DIR = Path(__file__).parent.parent / "config"


def _load_profile_config(profile: str) -> AppConfig:
    """프로필 기반 설정 로드.

    Args:
        profile: 프로필 이름 ("base", "api", "asmr").

    Returns:
        로드된 AppConfig.

    Raises:
        ValueError: 프로필이 없으면 발생.
    """
    if profile not in PROFILES:
        logger.warning("❌ 알 수 없는 프로필: %s (기본값: %s)", profile, DEFAULT_PROFILE)
        profile = DEFAULT_PROFILE

    profile_path = CONFIG_DIR / f"config.{profile}.yaml"

    if not profile_path.exists():
        logger.warning("⚠️  프로필 파일 없음: %s (기본값으로 돌아감)", profile_path)
        profile_path = CONFIG_DIR / f"config.{DEFAULT_PROFILE}.yaml"

    logger.info("✅ 설정 프로필 로드: %s", profile_path.name)
    return load_config(profile_path)


def _apply_env_overrides(config: AppConfig) -> AppConfig:
    """환경변수로 설정 오버라이드.

    지원하는 환경변수:
    - ENABLE_AVATAR: true/false
    - ENABLE_BROLL: true/false
    - IMAGE_GEN_BACKEND: local/nanobanana
    - CONFIG_PROFILE: base/api/asmr (이미 로드되어 사용 안함)

    Args:
        config: 원본 AppConfig.

    Returns:
        환경변수 오버라이드가 적용된 AppConfig.
    """

    def _str_to_bool(value: str) -> bool:
        """문자열을 불린으로 변환."""
        return value.lower() in ("true", "1", "yes", "on")

    # 아바타
    if env_val := os.getenv("ENABLE_AVATAR"):
        config.avatar.enabled = _str_to_bool(env_val)
        logger.info("[env] avatar.enabled = %s", config.avatar.enabled)

    # B-roll 활성화
    if env_val := os.getenv("ENABLE_BROLL"):
        config.pipeline.broll.enabled = _str_to_bool(env_val)
        logger.info("[env] pipeline.broll.enabled = %s", config.pipeline.broll.enabled)

    # 이미지 생성 백엔드
    if env_val := os.getenv("IMAGE_GEN_BACKEND"):
        if env_val in ("local", "nanobanana"):
            config.pipeline.broll.image_gen_backend = env_val
            logger.info("[env] image_gen_backend = %s", env_val)
        else:
            logger.warning("Unknown IMAGE_GEN_BACKEND: %s", env_val)

    return config


def _validate_config(config: AppConfig) -> list[str]:
    """설정 검증 및 경고 반환.

    Args:
        config: 검증할 AppConfig.

    Returns:
        경고 메시지 리스트.
    """
    warnings = []

    # 경고 1: B-roll 비활성화
    if not config.pipeline.broll.enabled:
        warnings.append(
            "B-roll disabled. Enable for dynamic slide backgrounds."
        )

    # 경고 2: NanoBanana 백엔드인데 Google API Key 없음
    if config.pipeline.broll.image_gen_backend == "nanobanana":
        if not os.getenv("GOOGLE_API_KEY"):
            warnings.append(
                "NanoBanana backend selected but GOOGLE_API_KEY is not set."
            )

    return warnings


def apply_pipeline_overrides(config: AppConfig) -> AppConfig:
    """pipeline 섹션의 설정을 기존 세부 config에 반영.

    pipeline 통합 Control Panel의 값을 기존 세부 설정 필드에 동기화하여
    기존 코드가 변경 없이 동작하도록 합니다.

    Args:
        config: 원본 AppConfig.

    Returns:
        pipeline 오버라이드가 적용된 AppConfig.
    """
    p = config.pipeline

    # Slides backend (항상 remotion)
    config.slides.backend = "remotion"

    # B-roll
    config.broll.image_search.enabled = p.broll.image_search
    if p.broll.image_gen_backend == "nanobanana":
        config.broll.force_backend = "nanobanana"
        config.broll.nanobanana.save_captions = p.broll.save_captions
    # local → 기존 force_backend 유지 (flux2_klein 등)

    # Avatar (env var override 우선)
    if not os.getenv("ENABLE_AVATAR"):
        config.avatar.enabled = p.avatar.enabled

    return config


def get_config(config_path: Path | None = None) -> AppConfig:
    """전역 설정 싱글턴을 반환.

    프로필 로드 → 환경변수 오버라이드 → 파이프라인 오버라이드 순서로 적용.

    Args:
        config_path: 설정 파일 경로. 지정되지 않으면 프로필 사용.

    Returns:
        AppConfig 인스턴스.
    """
    global _config
    if _config is not None:
        return _config

    with _config_lock:
        # Double-checked locking
        if _config is not None:
            return _config

        # 1. 프로필 기반 로드
        profile = os.getenv("CONFIG_PROFILE", DEFAULT_PROFILE)
        if config_path:
            cfg = load_config(config_path)
        else:
            cfg = _load_profile_config(profile)

        # 2. 환경변수 오버라이드
        cfg = _apply_env_overrides(cfg)

        # 3. 파이프라인 Control Panel 오버라이드
        cfg = apply_pipeline_overrides(cfg)

        # 4. 설정 검증 및 경고
        warnings = _validate_config(cfg)
        for warning in warnings:
            logger.warning(warning)

        _config = cfg

    return _config


def reload_config(config_path: Path | None = None) -> AppConfig:
    """설정을 다시 로드 (thread-safe)."""
    global _config
    with _config_lock:
        _config = None
    return get_config(config_path)
