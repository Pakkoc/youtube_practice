"""ElevenLabs TTS API backend."""

from __future__ import annotations

import os

import requests

from shared.lib.ffmpeg import _ffmpeg, _run_ffmpeg
from shared.lib.logger import get_logger

from ..model import TTSBackend, TTSRequest, TTSResult
from ..preprocess import detect_language_code

logger = get_logger()

_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"


class ElevenLabsBackend(TTSBackend):
    """ElevenLabs TTS API backend.

    eleven_multilingual_v2 model. MP3 -> WAV ffmpeg conversion.
    Supports fallback API key for multi-account setups.
    """

    def __init__(
        self,
        voice_id: str = "60gzQ1UbhCSBg4mgozcQ",
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.85,
        similarity_boost: float = 0.58,
        style_exaggeration: float = 0.0,
        use_speaker_boost: bool = True,
        speed: float = 1.0,
        output_format: str = "mp3_44100_128",
        language_code: str = "ko",
        api_key_env: str = "ELEVENLABS_API_KEY",
        fallback_api_key_env: str = "",
    ) -> None:
        self._voice_id = voice_id
        self._model_id = model_id
        self._stability = stability
        self._similarity_boost = similarity_boost
        self._style_exaggeration = style_exaggeration
        self._use_speaker_boost = use_speaker_boost
        self._speed = speed
        self._output_format = output_format
        self._language_code = language_code
        self._api_key_env = api_key_env
        self._fallback_api_key_env = fallback_api_key_env

    @property
    def name(self) -> str:
        return "elevenlabs_api"

    def is_available(self) -> bool:
        return bool(os.environ.get(self._api_key_env))

    def generate(self, request: TTSRequest) -> TTSResult:
        result = self._call_api(request, self._api_key_env)
        if result.success:
            return result

        # Fallback: 1차 키 실패 시 2차 키로 재시도
        if self._fallback_api_key_env and os.environ.get(self._fallback_api_key_env):
            logger.warning(
                "1차 API 키(%s) 실패, fallback 키(%s)로 재시도...",
                self._api_key_env,
                self._fallback_api_key_env,
            )
            return self._call_api(request, self._fallback_api_key_env)

        return result

    def _call_api(self, request: TTSRequest, api_key_env: str) -> TTSResult:
        try:
            api_key = os.environ.get(api_key_env)
            if not api_key:
                raise RuntimeError(
                    f"{api_key_env} 환경 변수가 설정되지 않았습니다."
                )

            # tts_text가 있으면 전처리된 텍스트 사용, 없으면 원문
            speak_text = request.tts_text or request.text

            # 영어 단어 2개 이상(3글자+) -> language_code="en"
            lang_code = detect_language_code(speak_text, default=self._language_code)

            logger.info(
                "TTS 생성 중 (ElevenLabs API, key=%s): voice=%s, lang=%s, text=%s...",
                api_key_env,
                self._voice_id,
                lang_code,
                speak_text[:50],
            )

            url = f"{_API_URL}/{self._voice_id}"
            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json",
            }
            payload = {
                "text": speak_text,
                "model_id": self._model_id,
                "language_code": lang_code,
                "voice_settings": {
                    "stability": self._stability,
                    "similarity_boost": self._similarity_boost,
                    "style": self._style_exaggeration,
                    "use_speaker_boost": self._use_speaker_boost,
                    "speed": self._speed,
                },
            }
            params = {"output_format": self._output_format}

            response = requests.post(
                url, headers=headers, json=payload, params=params, timeout=120
            )
            response.raise_for_status()

            request.output_path.parent.mkdir(parents=True, exist_ok=True)

            # MP3 -> WAV lossless conversion via ffmpeg
            # -acodec pcm_s16le: 16-bit signed LE (standard WAV)
            # -ac 1: mono (TTS content)
            # -ar 생략: 소스 샘플레이트 유지 (리샘플링 없음, 품질 보존)
            mp3_path = request.output_path.with_suffix(".mp3")
            with open(mp3_path, "wb") as f:
                f.write(response.content)

            try:
                _run_ffmpeg(
                    [
                        _ffmpeg(),
                        "-y",
                        "-i",
                        str(mp3_path),
                        "-acodec",
                        "pcm_s16le",
                        "-ac",
                        "1",
                        str(request.output_path),
                    ],
                    timeout=60,
                )
            finally:
                mp3_path.unlink(missing_ok=True)

            duration = self._get_duration(request.output_path)

            # 메타데이터 JSON sidecar 저장
            from ..sidecar import sync_tts_sidecar

            sync_tts_sidecar(request.output_path, request.text, speak_text, duration, lang_code)

            logger.info(
                "TTS 생성 완료 (ElevenLabs API, key=%s): %s (%.1f초)",
                api_key_env,
                request.output_path.name,
                duration,
            )

            return TTSResult(
                output_path=request.output_path,
                duration=duration,
                sample_rate=44100,
            )

        except Exception as e:
            logger.error("TTS 생성 실패 (ElevenLabs API, key=%s): %s", api_key_env, e)
            return TTSResult(
                output_path=request.output_path,
                success=False,
                error=str(e),
            )

    @staticmethod
    def _get_duration(audio_path) -> float:
        try:
            from shared.lib.ffmpeg import get_duration

            return get_duration(audio_path)
        except Exception:
            return 0.0
