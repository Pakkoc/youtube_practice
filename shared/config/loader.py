"""설정 파일 로더."""

from pathlib import Path

import yaml
from dotenv import load_dotenv

from shared.config.schema import AppConfig
from shared.constants import DEFAULT_CONFIG_PATH, PROJECT_ROOT

# .env 파일에서 환경 변수 로드
load_dotenv(PROJECT_ROOT / ".env")


def load_config(config_path: Path | None = None) -> AppConfig:
    """YAML 설정 파일을 로드하여 AppConfig 반환.

    Args:
        config_path: 설정 파일 경로. None이면 기본 경로 사용.

    Returns:
        검증된 AppConfig 인스턴스.
    """
    path = config_path or DEFAULT_CONFIG_PATH

    if not path.exists():
        return AppConfig()

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if raw is None:
        return AppConfig()

    return AppConfig.model_validate(raw)
