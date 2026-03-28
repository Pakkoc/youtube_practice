"""플랫폼 감지 모듈.

실행 환경(WSL2, Mac, Linux)과 GPU(CUDA, MPS) 가용 여부를 감지한다.
"""

from __future__ import annotations

import platform as _platform
from dataclasses import dataclass


@dataclass
class PlatformInfo:
    """현재 실행 환경 정보."""

    os: str = ""  # "linux", "darwin", "windows"
    is_wsl: bool = False
    has_cuda: bool = False
    has_mps: bool = False
    gpu_name: str | None = None
    vram_gb: float | None = None

    @property
    def summary(self) -> str:
        """사람이 읽을 수 있는 환경 요약."""
        parts: list[str] = []
        if self.is_wsl:
            parts.append("WSL2")
        else:
            parts.append(self.os)

        if self.has_cuda:
            gpu = f" ({self.gpu_name})" if self.gpu_name else ""
            vram = f" {self.vram_gb:.1f}GB" if self.vram_gb else ""
            parts.append(f"CUDA{gpu}{vram}")
        elif self.has_mps:
            parts.append("MPS (Apple Silicon)")
        else:
            parts.append("CPU only")

        return " / ".join(parts)


def _detect_wsl() -> bool:
    """WSL2 환경 여부를 감지."""
    try:
        with open("/proc/version", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except (FileNotFoundError, PermissionError):
        return False


def _detect_cuda() -> tuple[bool, str | None, float | None]:
    """CUDA GPU 가용 여부를 감지. (has_cuda, gpu_name, vram_gb)"""
    try:
        import torch

        if not torch.cuda.is_available():
            return False, None, None

        gpu_name = torch.cuda.get_device_name(0)
        vram_bytes = torch.cuda.get_device_properties(0).total_memory
        vram_gb = vram_bytes / (1024**3)
        return True, gpu_name, vram_gb
    except (ImportError, RuntimeError):
        return False, None, None


def _detect_mps() -> bool:
    """Apple MPS 가용 여부를 감지."""
    try:
        import torch

        return hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    except (ImportError, RuntimeError):
        return False


def detect_platform() -> PlatformInfo:
    """현재 실행 환경을 감지하여 PlatformInfo 반환."""
    os_name = _platform.system().lower()  # "linux", "darwin", "windows"
    is_wsl = os_name == "linux" and _detect_wsl()

    has_cuda, gpu_name, vram_gb = _detect_cuda()
    has_mps = not has_cuda and os_name == "darwin" and _detect_mps()

    return PlatformInfo(
        os=os_name,
        is_wsl=is_wsl,
        has_cuda=has_cuda,
        has_mps=has_mps,
        gpu_name=gpu_name,
        vram_gb=vram_gb,
    )
