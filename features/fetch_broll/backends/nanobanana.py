"""Gemini NanoBanana 이미지 생성/편집 백엔드.

Google Gemini의 이미지 생성 모델을 사용하여 B-roll 이미지를 생성합니다.
- 텍스트→이미지: 프롬프트만으로 이미지 생성
- 레퍼런스 편집: 프롬프트 + 레퍼런스 이미지 → 일관된 스타일의 이미지 편집

Requirements:
- google-genai 패키지: pip install google-genai
- GOOGLE_API_KEY 환경변수 설정
"""

from __future__ import annotations

from pathlib import Path

from shared.lib.logger import get_logger

logger = get_logger()


class NanoBananaBackend:
    """Gemini NanoBanana (gemini-2.5-flash-image) 이미지 생성/편집 백엔드."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash-image",
        height: int = 720,
        width: int = 1280,
        aspect_ratio: str = "16:9",
        use_reference: bool = True,
        save_captions: bool = True,
    ) -> None:
        """NanoBananaBackend 초기화.

        Args:
            model: Gemini 이미지 모델 ID.
            height: 출력 이미지 높이 (16:9 비율, 기본: 720).
            width: 출력 이미지 너비 (16:9 비율, 기본: 1280).
            aspect_ratio: 이미지 비율 (1:1, 3:4, 4:3, 9:16, 16:9).
            use_reference: 레퍼런스 이미지 편집 모드 사용 여부.
            save_captions: 프롬프트/캡션을 sidecar .txt로 저장할지 여부.
        """
        self._model = model
        self._height = height
        self._width = width
        self._aspect_ratio = aspect_ratio
        self._use_reference = use_reference
        self._save_captions = save_captions
        self._client = None

    @property
    def name(self) -> str:
        return "nanobanana"

    def _get_client(self):
        """google-genai 클라이언트 lazy 초기화."""
        if self._client is None:
            from google import genai

            self._client = genai.Client()  # GOOGLE_API_KEY 환경변수 사용
            logger.info("NanoBanana: Gemini 클라이언트 초기화 (model=%s)", self._model)
        return self._client

    def generate(
        self,
        prompt: str,
        output_path: Path,
        reference_image: Path | None = None,
    ) -> Path | None:
        """이미지 생성 또는 편집.

        reference_image가 있고 use_reference=True이면 편집 모드 (일관성 유지),
        없으면 텍스트→이미지 생성.

        Args:
            prompt: 생성/편집 프롬프트.
            output_path: 출력 이미지 경로.
            reference_image: 레퍼런스 이미지 경로 (선택).

        Returns:
            생성된 이미지 경로, 실패 시 None.
        """
        try:
            from google.genai import types

            client = self._get_client()

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            enhanced_prompt = (
                f"{prompt} Do not include any text, letters, words, or typography in the image."
            )

            contents = [enhanced_prompt]
            has_reference = (
                self._use_reference
                and reference_image is not None
                and Path(reference_image).exists()
            )

            if has_reference:
                from PIL import Image

                ref_img = Image.open(str(reference_image))
                contents = [enhanced_prompt, ref_img]
                logger.info(
                    "NanoBanana: 레퍼런스 편집 - ref='%s', prompt='%s'",
                    Path(reference_image).name,
                    prompt[:80],
                )
            else:
                logger.info("NanoBanana: 텍스트->이미지 생성 - '%s'", prompt[:80])

            response = client.models.generate_content(
                model=self._model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    image_config=types.ImageConfig(
                        aspect_ratio=self._aspect_ratio,
                    ),
                ),
            )

            # 응답에서 이미지 추출
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type or "image/png"

                        # MIME 타입에 따라 확장자 결정
                        if "jpeg" in mime_type or "jpg" in mime_type:
                            actual_ext = ".jpg"
                        else:
                            actual_ext = ".png"

                        # 확장자가 다르면 경로 조정
                        if output_path.suffix.lower() != actual_ext:
                            output_path = output_path.with_suffix(actual_ext)

                        output_path.write_bytes(image_data)
                        logger.info("NanoBanana: 저장 완료 - %s", output_path.name)

                        # 캡션 저장
                        if self._save_captions:
                            self._save_caption(output_path, prompt, reference_image)

                        return output_path

            logger.warning("NanoBanana: 응답에서 이미지를 찾을 수 없음")
            return None

        except Exception as e:
            logger.error("NanoBanana: 이미지 생성 실패 - %s", e)
            import traceback

            traceback.print_exc()
            return None

    def _save_caption(
        self,
        image_path: Path,
        prompt: str,
        reference_image: Path | None = None,
    ) -> None:
        """프롬프트/캡션을 이미지 옆에 저장 (파인튜닝 데이터용).

        저장 형식: broll_001_caption.txt
        내용: prompt + reference 경로 + 모델명

        Args:
            image_path: 이미지 파일 경로.
            prompt: 사용된 프롬프트.
            reference_image: 사용된 레퍼런스 이미지 경로.
        """
        caption_path = image_path.with_name(image_path.stem + "_caption.txt")
        lines = [prompt]
        if reference_image is not None:
            lines.append(f"[reference] {reference_image}")
        lines.append(f"[model] {self._model}")
        caption_path.write_text("\n".join(lines), encoding="utf-8")
        logger.debug("NanoBanana: 캡션 저장 - %s", caption_path.name)

    def cleanup(self) -> None:
        """클라이언트 리소스 정리."""
        self._client = None
        logger.info("NanoBanana: 리소스 정리 완료")
