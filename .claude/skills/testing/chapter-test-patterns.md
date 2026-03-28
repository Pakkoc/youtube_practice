# 테스트 패턴

> 소스: `tests/`

## 디렉토리 구조

```
tests/
├── features/          # 기능 테스트
├── entities/          # 엔티티 모델 테스트
├── shared/            # 공유 유틸리티 테스트
├── pipelines/         # 파이프라인 통합 테스트
└── conftest.py        # 공통 픽스처
```

소스 구조를 **미러링**: `features/generate_tts/lib.py` → `tests/features/test_generate_tts.py`

## 테스트 작성 패턴

### 클래스 기반 그룹핑
```python
class TestGenerateTTS:
    def test_basic_generation(self, tmp_path):
        ...
    def test_reuse_existing(self, tmp_path):
        ...
```

### tmp_path 사용 (임시 파일)
```python
def test_something(tmp_path):
    output = tmp_path / "output.wav"
    result = generate_tts(text, output)
    assert output.exists()
```

### API 모킹
```python
from unittest.mock import patch, MagicMock

@patch("features.generate_slides.lib.generate_remotion_props_for_paragraphs")
def test_generate_remotion_props(mock_gen):
    mock_gen.return_value = [{"index": 0, "mode": "freeform", "tsx_path": "slides/001.tsx"}]
    result = mock_gen(paragraphs=["test paragraph"], audio_clips=[], project_dir=".")
    assert result[0]["mode"] == "freeform"
```

### 슬라이드 렌더링 테스트
```python
from unittest.mock import patch

@patch("features.generate_slides.lib.render_remotion_slides")
def test_render_remotion_slides(mock_render):
    mock_render.return_value = ["slides/001.mp4"]
    result = mock_render(props=[{"index": 0}], project_dir=".")
    assert result[0].endswith(".mp4")
```

## 핵심 테스트 명령

```bash
# 전체 테스트
pytest

# 특정 파일
pytest tests/shared/test_config.py

# 특정 테스트
pytest tests/shared/test_config.py -k test_load

# 짧은 출력
pytest --tb=short -q

# API 스모크 테스트 (ask() 수정 시 필수)
pytest tests/shared/test_ask_api.py -v
```
