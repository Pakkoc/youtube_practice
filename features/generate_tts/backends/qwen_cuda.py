"""Qwen3-TTS CUDA 백엔드 (bfloat16, flash_attention_2)."""

from __future__ import annotations

from shared.lib.logger import get_logger

from ..model import TTSBackend, TTSRequest, TTSResult

logger = get_logger()


class QwenCudaBackend(TTSBackend):
    """CUDA GPU 환경 Qwen3-TTS 백엔드."""

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        speaker: str = "Sohee",
        language: str = "Korean",
        dtype: str = "bfloat16",
        attn_impl: str = "flash_attention_2",
        device: str = "cuda:0",
    ) -> None:
        self._model_name = model_name
        self._speaker = speaker
        self._language = language
        self._dtype = dtype
        self._attn_impl = attn_impl
        self._device = device
        self._model = None

    @property
    def name(self) -> str:
        return "qwen_cuda"

    def is_available(self) -> bool:
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False

    def _load_model(self):
        """모델을 lazy 로딩."""
        if self._model is not None:
            return

        import torch
        from qwen_tts import Qwen3TTSModel

        dtype_map = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32,
        }
        torch_dtype = dtype_map.get(self._dtype, torch.bfloat16)

        logger.info(
            "Qwen3-TTS CUDA 모델 로딩: %s (dtype=%s, attn=%s)",
            self._model_name,
            self._dtype,
            self._attn_impl,
        )

        self._model = Qwen3TTSModel.from_pretrained(
            self._model_name,
            device_map=self._device,
            dtype=torch_dtype,
            attn_implementation=self._attn_impl,
        )

        logger.info("Qwen3-TTS CUDA 모델 로딩 완료")

    def generate(self, request: TTSRequest) -> TTSResult:
        try:
            import soundfile as sf
            import torch

            # 시드 고정 — 구간별 생성 시 음성 일관성 유지
            torch.manual_seed(42)
            torch.cuda.manual_seed(42)

            self._load_model()

            speaker = request.speaker or self._speaker
            language = request.language or self._language
            speak_text = request.tts_text or request.text

            logger.info(
                "TTS 생성 중 (CUDA): speaker=%s, language=%s, text=%s...",
                speaker,
                language,
                speak_text[:50],
            )

            wavs, sr = self._model.generate_custom_voice(
                text=speak_text,
                language=language,
                speaker=speaker,
                instruct=request.instruct or "",
            )

            request.output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(str(request.output_path), wavs[0], sr)

            duration = len(wavs[0]) / sr

            logger.info(
                "TTS 생성 완료 (CUDA): %s (%.1f초)",
                request.output_path.name,
                duration,
            )

            return TTSResult(
                output_path=request.output_path,
                duration=duration,
                sample_rate=sr,
            )

        except Exception as e:
            logger.error("TTS 생성 실패 (CUDA): %s", e)
            return TTSResult(
                output_path=request.output_path,
                success=False,
                error=str(e),
            )
