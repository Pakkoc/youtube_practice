"""공용 유틸리티 모듈 Public API."""

from shared.lib.logger import get_logger, setup_logger
from shared.lib.platform import PlatformInfo, detect_platform

__all__ = ["PlatformInfo", "detect_platform", "get_logger", "setup_logger"]
