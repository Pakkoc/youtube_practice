"""Flux Kontext + LoRA 기반 B-roll 이미지 생성 백엔드.

Flux Kontext dev 모델에 커스텀 LoRA를 적용하여
일관된 캐릭터 스타일의 이미지를 생성합니다.
- img2img 전용 (참조 이미지 필수)
- 20 스텝, guidance_scale=4.0
- LoRA로 캐릭터 일관성 유지
"""

from __future__ import annotations

from pathlib import Path

from shared.lib.logger import get_logger

logger = get_logger()


class FluxKontextBackend:
    """Flux Kontext + LoRA 모델로 이미지 생성 (img2img 전용)."""

    def __init__(
        self,
        base_model_path: str,
        lora_path: str,
        num_inference_steps: int = 20,
        height: int = 768,
        width: int = 1344,
        guidance_scale: float = 4.0,
        lora_scale: float = 1.0,
        device: str = "cuda",
    ) -> None:
        self._base_model_path = base_model_path
        self._lora_path = lora_path
        self._num_inference_steps = num_inference_steps
        # 64의 배수로 조정
        self._height = (height // 64) * 64
        self._width = (width // 64) * 64
        self._guidance_scale = guidance_scale
        self._lora_scale = lora_scale
        self._device = device
        self._pipe = None

    @property
    def name(self) -> str:
        return "flux_kontext"

    def _load_pipeline(self) -> None:
        """파이프라인을 lazy 로딩."""
        if self._pipe is not None:
            return

        import torch
        from diffusers import FluxKontextPipeline

        logger.info("Flux Kontext: 파이프라인 로딩 중...")
        logger.info("  - Model: %s", self._base_model_path)
        logger.info("  - LoRA: %s", Path(self._lora_path).name)

        self._pipe = FluxKontextPipeline.from_pretrained(
            self._base_model_path,
            torch_dtype=torch.bfloat16,
        )
        self._pipe.enable_model_cpu_offload()

        # LoRA 로딩
        self._pipe.load_lora_weights(self._lora_path)
        logger.info(
            "Flux Kontext: 파이프라인 로딩 완료 (LoRA scale=%.1f)",
            self._lora_scale,
        )

    def generate(
        self,
        prompt: str,
        output_path: Path,
        reference_image: Path | None = None,
        seed: int | None = None,
    ) -> Path | None:
        """참조 이미지 기반으로 이미지 생성 (img2img).

        Args:
            prompt: 생성 프롬프트.
            output_path: 출력 이미지 경로.
            reference_image: 참조 이미지 경로 (필수).
            seed: 랜덤 시드.

        Returns:
            생성된 이미지 경로, 실패 시 None.
        """
        if reference_image is None or not Path(reference_image).exists():
            logger.warning(
                "Flux Kontext: 참조 이미지가 없습니다 (img2img 전용). "
                "reference_dir에 이미지를 추가하세요."
            )
            return None

        try:
            self._load_pipeline()

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            return self._generate_img2img(
                prompt, Path(reference_image), output_path, seed
            )

        except Exception as e:
            logger.error("Flux Kontext: 이미지 생성 실패 - %s", e)
            import traceback

            traceback.print_exc()
            return None

    def _generate_img2img(
        self,
        prompt: str,
        reference_image: Path,
        output_path: Path,
        seed: int | None = None,
    ) -> Path | None:
        """참조 이미지를 기반으로 img2img 생성."""
        import torch
        from PIL import Image as PILImage

        assert self._pipe is not None

        logger.info(
            "Flux Kontext: img2img 생성 - ref='%s', prompt='%s'",
            reference_image.name,
            prompt[:80],
        )

        # 참조 이미지 로드 및 리사이즈
        ref_img = PILImage.open(str(reference_image)).convert("RGB")
        orig_w, orig_h = ref_img.size
        ref_img_resized = ref_img.resize((self._width, self._height))

        logger.info(
            "  - Reference: %dx%d -> %dx%d",
            orig_w,
            orig_h,
            self._width,
            self._height,
        )

        generator = None
        if seed is not None:
            generator = torch.Generator(device="cpu").manual_seed(seed)

        image = self._pipe(
            image=ref_img_resized,
            prompt=prompt,
            height=self._height,
            width=self._width,
            num_inference_steps=self._num_inference_steps,
            guidance_scale=self._guidance_scale,
            generator=generator,
            joint_attention_kwargs={"scale": self._lora_scale},
        ).images[0]

        image.save(str(output_path))
        logger.info("Flux Kontext: 저장 완료 - %s", output_path.name)
        return output_path

    def cleanup(self) -> None:
        """파이프라인 리소스 정리."""
        if self._pipe is not None:
            import torch

            del self._pipe
            self._pipe = None
            torch.cuda.empty_cache()
            logger.info("Flux Kontext: 리소스 정리 완료")
