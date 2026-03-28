"""FLUX.2 Klein 4B 기반 B-roll 이미지 생성 백엔드.

Black Forest Labs의 FLUX.2 Klein 4B 모델을 사용하여 빠른 이미지 생성을 지원합니다.
- 4 스텝으로 1초 미만 생성
- ~13GB VRAM
- Apache 2.0 라이선스

Requirements:
- diffusers >= 0.37.0.dev0 (GitHub main 브랜치)
  pip install git+https://github.com/huggingface/diffusers.git
- Flux2KleinPipeline 클래스 사용 필수
"""

from __future__ import annotations

from pathlib import Path

from shared.lib.logger import get_logger

logger = get_logger()


class Flux2KleinBackend:
    """FLUX.2 Klein 4B 모델로 이미지 생성.

    텍스트→이미지 및 img2img(reference image)를 지원합니다.
    """

    def __init__(
        self,
        model_id: str = "black-forest-labs/FLUX.2-klein-4B",
        num_inference_steps: int = 4,
        height: int = 720,
        width: int = 1280,
        guidance_scale: float = 3.5,
        device: str = "cuda",
    ) -> None:
        """Flux2KleinBackend 초기화.

        Args:
            model_id: HuggingFace 모델 ID.
            num_inference_steps: 추론 스텝 수 (Klein은 4 권장).
            height: 출력 이미지 높이 (64의 배수로 자동 조정).
            width: 출력 이미지 너비 (64의 배수로 자동 조정).
            guidance_scale: Guidance scale (distilled 모델에서는 무시됨).
            device: 디바이스 (cuda, cpu).
        """
        self._model_id = model_id
        self._num_inference_steps = num_inference_steps
        # 64의 배수로 조정
        self._height = (height // 64) * 64
        self._width = (width // 64) * 64
        self._guidance_scale = guidance_scale
        self._device = device
        self._pipe = None

    @property
    def name(self) -> str:
        return "flux2_klein"

    def is_available(self) -> bool:
        """백엔드 사용 가능 여부 확인."""
        try:
            import torch

            if not torch.cuda.is_available() and self._device == "cuda":
                return False

            # diffusers 0.37.0.dev0+ 확인 (Flux2KleinPipeline 필요)
            from diffusers import Flux2KleinPipeline  # noqa: F401

            return True
        except ImportError:
            logger.warning(
                "Flux2KleinPipeline not found. Install: "
                "pip install git+https://github.com/huggingface/diffusers.git"
            )
            return False

    def _load_pipeline(self) -> None:
        """파이프라인을 lazy 로딩."""
        if self._pipe is not None:
            return

        import torch
        from diffusers import Flux2KleinPipeline

        logger.info("FLUX.2 Klein: 파이프라인 로딩 중...")
        logger.info("  - Model: %s", self._model_id)
        logger.info("  - CUDA: %s", torch.cuda.is_available())
        if torch.cuda.is_available():
            logger.info("  - GPU: %s", torch.cuda.get_device_name(0))

        self._pipe = Flux2KleinPipeline.from_pretrained(
            self._model_id,
            torch_dtype=torch.bfloat16,
            device_map="balanced",  # 자동으로 GPU/CPU 분산
        )

        logger.info("FLUX.2 Klein: 파이프라인 로딩 완료 (device_map=balanced)")

    def generate(
        self,
        prompt: str,
        output_path: Path,
        reference_image: Path | None = None,
        negative_prompt: str = "",
        seed: int | None = None,
    ) -> Path | None:
        """이미지 생성.

        Args:
            prompt: 생성 프롬프트.
            output_path: 출력 이미지 경로.
            reference_image: 레퍼런스 이미지 경로 (선택, 스타일 참조용).
            negative_prompt: 네거티브 프롬프트 (FLUX.2에서는 미사용).
            seed: 랜덤 시드.

        Returns:
            생성된 이미지 경로, 실패 시 None.
        """
        try:
            self._load_pipeline()

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if reference_image and Path(reference_image).exists():
                return self._generate_with_reference(
                    prompt, Path(reference_image), output_path, seed
                )
            else:
                return self._generate_from_text(prompt, output_path, seed)

        except Exception as e:
            logger.error("FLUX.2 Klein: 이미지 생성 실패 - %s", e)
            import traceback
            traceback.print_exc()
            return None

    def _generate_from_text(
        self,
        prompt: str,
        output_path: Path,
        seed: int | None = None,
    ) -> Path | None:
        """텍스트에서 이미지 생성.

        Args:
            prompt: 생성 프롬프트.
            output_path: 출력 경로.
            seed: 랜덤 시드.

        Returns:
            생성된 이미지 경로.
        """
        import torch

        assert self._pipe is not None

        logger.info("FLUX.2 Klein: 텍스트→이미지 생성 - '%s'", prompt[:80])

        generator = None
        if seed is not None:
            generator = torch.Generator(device="cpu").manual_seed(seed)

        image = self._pipe(
            prompt=prompt,
            height=self._height,
            width=self._width,
            num_inference_steps=self._num_inference_steps,
            guidance_scale=self._guidance_scale,
            generator=generator,
        ).images[0]

        image.save(str(output_path))
        logger.info("FLUX.2 Klein: 저장 완료 - %s", output_path.name)
        return output_path

    def _generate_with_reference(
        self,
        prompt: str,
        reference_image: Path,
        output_path: Path,
        seed: int | None = None,
    ) -> Path | None:
        """레퍼런스 이미지를 참조하여 이미지 생성 (img2img 방식).

        FLUX.2 Klein은 image 파라미터로 reference image를 받아
        해당 스타일을 참조한 이미지를 생성합니다.

        Args:
            prompt: 생성 프롬프트.
            reference_image: 레퍼런스 이미지 경로.
            output_path: 출력 경로.
            seed: 랜덤 시드.

        Returns:
            생성된 이미지 경로.
        """
        import torch
        from PIL import Image as PILImage

        assert self._pipe is not None

        logger.info(
            "FLUX.2 Klein: 레퍼런스 참조 생성 - ref='%s', prompt='%s'",
            reference_image.name,
            prompt[:80],
        )

        # 레퍼런스 이미지 로드 및 64의 배수로 리사이즈
        ref_img = PILImage.open(str(reference_image)).convert("RGB")
        orig_w, orig_h = ref_img.size

        # 출력 크기에 맞추거나, 원본 비율 유지하며 64의 배수로 조정
        # 여기서는 설정된 출력 크기 사용
        target_w = self._width
        target_h = self._height
        ref_img_resized = ref_img.resize((target_w, target_h))

        logger.info(
            "  - Reference: %dx%d → %dx%d",
            orig_w, orig_h, target_w, target_h,
        )

        generator = None
        if seed is not None:
            generator = torch.Generator(device="cpu").manual_seed(seed)

        # img2img 방식으로 생성 (image 파라미터에 단일 이미지 전달)
        image = self._pipe(
            image=ref_img_resized,  # reference image (단일)
            prompt=prompt,
            height=target_h,
            width=target_w,
            num_inference_steps=self._num_inference_steps,
            guidance_scale=self._guidance_scale,
            generator=generator,
        ).images[0]

        image.save(str(output_path))
        logger.info("FLUX.2 Klein: 저장 완료 - %s", output_path.name)
        return output_path

    def cleanup(self) -> None:
        """파이프라인 리소스 정리."""
        if self._pipe is not None:
            import torch

            del self._pipe
            self._pipe = None
            torch.cuda.empty_cache()
            logger.info("FLUX.2 Klein: 리소스 정리 완료")
