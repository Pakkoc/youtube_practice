"""전역 상수 정의."""

from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 설정 파일 경로
CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"

# 프로젝트 데이터 디렉토리
PROJECTS_DIR = PROJECT_ROOT / "projects"

# 템플릿/프롬프트 디렉토리
TEMPLATES_DIR = PROJECT_ROOT / "templates"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# TTS 기본값
DEFAULT_TTS_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
DEFAULT_TTS_TOKENIZER = "Qwen/Qwen3-TTS-Tokenizer-12Hz"
DEFAULT_TTS_SPEAKER = "Sohee"
DEFAULT_TTS_LANGUAGE = "Korean"

# 영상 기본값
DEFAULT_VIDEO_WIDTH = 1920
DEFAULT_VIDEO_HEIGHT = 1080
DEFAULT_VIDEO_FPS = 30

# 썸네일 기본값
DEFAULT_THUMBNAIL_WIDTH = 1280
DEFAULT_THUMBNAIL_HEIGHT = 720
