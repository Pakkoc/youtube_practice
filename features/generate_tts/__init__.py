"""TTS 음성 생성 feature."""

from .lib import (
    create_tts_backend as create_tts_backend,
)
from .lib import (
    generate_tts_for_paragraphs as generate_tts_for_paragraphs,
)
from .lib import (
    generate_tts_for_text as generate_tts_for_text,
)
from .model import TTSBackend as TTSBackend
from .model import TTSRequest as TTSRequest
from .model import TTSResult as TTSResult
from .preprocess import (
    detect_language_code as detect_language_code,
)
from .preprocess import (
    preprocess_for_tts as preprocess_for_tts,
)
