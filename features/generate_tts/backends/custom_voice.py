"""CustomVoice TTS 백엔드 — x-vec(full embedding) + ICL(ref audio) 조합."""

from __future__ import annotations

from pathlib import Path

from shared.lib.logger import get_logger

from ..model import TTSBackend, TTSRequest, TTSResult

logger = get_logger()


class CustomVoiceBackend(TTSBackend):
    """x-vec + ICL voice cloning 백엔드.

    Base 모델에 전체 오디오에서 추출한 speaker embedding(x-vector)과
    대표 참조 오디오(ICL)를 조합하여 음성을 생성합니다.

    필요 파일:
      - speaker_embedding_final.pt  (x-vector, 전체 오디오 기반)
      - ref_audio.wav               (ICL 참조 오디오, 5~15초)
      - ref_text.txt                (ref_audio 전사 텍스트)
    """

    def __init__(
        self,
        model_path: Path,
        embedding_path: Path,
        ref_audio_path: Path,
        ref_text_path: Path,
        speaker_name: str = "hoyoung",
        language: str = "Korean",
        dtype: str = "bfloat16",
        attn_impl: str = "sdpa",
        device: str = "cuda:0",
        max_tokens: int = 4096,
    ) -> None:
        self._model_path = Path(model_path)
        self._embedding_path = Path(embedding_path)
        self._ref_audio_path = Path(ref_audio_path)
        self._ref_text_path = Path(ref_text_path)
        self._speaker_name = speaker_name
        self._language = language
        self._dtype = dtype
        self._attn_impl = attn_impl
        self._device = device
        self._max_tokens = max_tokens
        self._model = None
        self._prompt = None

    @property
    def name(self) -> str:
        return "custom_voice"

    def is_available(self) -> bool:
        """백엔드 사용 가능 여부 확인."""
        try:
            import torch

            if not torch.cuda.is_available() and self._device.startswith("cuda"):
                return False

            if not self._model_path.exists():
                logger.warning("CustomVoice: 모델 경로 없음 - %s", self._model_path)
                return False

            if not self._embedding_path.exists():
                logger.warning("CustomVoice: 임베딩 파일 없음 - %s", self._embedding_path)
                return False

            if not self._ref_audio_path.exists():
                logger.warning("CustomVoice: ref_audio 없음 - %s", self._ref_audio_path)
                return False

            if not self._ref_text_path.exists():
                logger.warning("CustomVoice: ref_text 없음 - %s", self._ref_text_path)
                return False

            return True
        except ImportError:
            return False

    def _load_model(self) -> None:
        """모델, 임베딩, ICL 프롬프트를 lazy 로딩."""
        if self._model is not None:
            return

        import librosa
        import torch
        from qwen_tts import Qwen3TTSModel
        from qwen_tts.inference.qwen3_tts_model import VoiceClonePromptItem

        dtype_map = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32,
        }
        torch_dtype = dtype_map.get(self._dtype, torch.bfloat16)

        # Base 모델 로드
        logger.info(
            "CustomVoice: Base 모델 로딩 - %s (dtype=%s, attn=%s)",
            self._model_path.name,
            self._dtype,
            self._attn_impl,
        )

        self._model = Qwen3TTSModel.from_pretrained(
            str(self._model_path),
            device_map=self._device,
            dtype=torch_dtype,
            attn_implementation=self._attn_impl,
        )

        # x-vector: 전체 오디오에서 추출한 speaker embedding 로드
        logger.info("CustomVoice: x-vector 로딩 - %s", self._embedding_path.name)
        full_emb = torch.load(
            str(self._embedding_path), weights_only=True, map_location=self._device
        )
        if full_emb.dim() == 2:
            full_emb = full_emb[0]  # [1, 2048] -> [2048]

        # ICL: ref_audio 코드 추출
        logger.info("CustomVoice: ICL ref_audio 로딩 - %s", self._ref_audio_path.name)
        ref_wav, ref_sr = librosa.load(str(self._ref_audio_path), sr=None, mono=True)
        enc = self._model.model.speech_tokenizer.encode([ref_wav], sr=ref_sr)
        ref_code = enc.audio_codes[0]

        # ref_text 로드
        ref_text = self._ref_text_path.read_text(encoding="utf-8").strip()
        logger.info("CustomVoice: ref_text = %s...", ref_text[:50])

        # x-vec + ICL 프롬프트 조합
        self._prompt = VoiceClonePromptItem(
            ref_code=ref_code,
            ref_spk_embedding=full_emb,
            x_vector_only_mode=False,
            icl_mode=True,
            ref_text=ref_text,
        )

        logger.info(
            "CustomVoice: 모델 로딩 완료 (speaker=%s, x-vec+ICL)",
            self._speaker_name,
        )

    def generate(self, request: TTSRequest) -> TTSResult:
        """텍스트에서 음성을 생성."""
        try:
            import soundfile as sf
            import torch

            torch.manual_seed(42)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(42)

            self._load_model()

            assert self._model is not None
            assert self._prompt is not None

            language = request.language or self._language
            speak_text = request.tts_text or request.text

            logger.info(
                "CustomVoice: 생성 중 (x-vec+ICL) - speaker=%s, text=%s...",
                self._speaker_name,
                speak_text[:50],
            )

            wavs, sr = self._model.generate_voice_clone(
                text=speak_text,
                language=language,
                voice_clone_prompt=[self._prompt],
                max_new_tokens=self._max_tokens,
            )

            request.output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(str(request.output_path), wavs[0], sr)

            duration = len(wavs[0]) / sr

            logger.info(
                "CustomVoice: 생성 완료 - %s (%.1f초)",
                request.output_path.name,
                duration,
            )

            return TTSResult(
                output_path=request.output_path,
                duration=duration,
                sample_rate=sr,
            )

        except Exception as e:
            logger.error("CustomVoice: 생성 실패 - %s", e)
            return TTSResult(
                output_path=request.output_path,
                success=False,
                error=str(e),
            )

    def cleanup(self) -> None:
        """모델 리소스 정리."""
        if self._model is not None:
            import torch

            del self._model
            self._model = None
            self._prompt = None
            torch.cuda.empty_cache()
            logger.info("CustomVoice: 모델 리소스 정리 완료")
