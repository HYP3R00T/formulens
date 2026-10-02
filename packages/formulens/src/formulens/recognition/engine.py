"""Hugging Face inference for cropped equation images."""

from pathlib import Path
from typing import Any

from formulens.configuration.schema import Settings

# Keep model revisions stable so repeat downloads use the same artifacts.
MODELS = {
    "paddle": ("PaddlePaddle/PaddleOCR-VL", "7fa00a8c55b735ba51ba49a9058f3f9c57a99a11"),
    "got": ("stepfun-ai/GOT-OCR-2.0-hf", "d3017ef2c2c1395888c8d635c5e0508bcb0ac78d"),
}


def clean_latex(text: str) -> str:
    """Remove display wrappers without rewriting mathematical content."""
    text = text.strip()
    if "<smiles" in text.lower():
        raise RuntimeError("The model returned chemistry markup instead of LaTeX. Try model paddle or a clearer crop.")
    if text.startswith("```") and text.endswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    for opening, closing in (("$$", "$$"), (r"\[", r"\]"), (r"\(", r"\)"), ("$", "$")):
        if text.startswith(opening) and text.endswith(closing) and len(text) > len(opening) + len(closing):
            return text[len(opening) : -len(closing)].strip()
    return text


class EquationRecognizer:
    """Load one model lazily and reuse it for subsequent requests."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model: Any = None
        self.processor: Any = None
        self.device = "cuda"

    def load(self) -> None:
        if self.model is not None:
            return
        try:
            import torch
            from transformers import AutoConfig, AutoModelForImageTextToText, AutoProcessor
        except ImportError as error:
            raise RuntimeError("Install OCR support with: uv sync --package formulens --extra ocr") from error

        if not torch.version.cuda or getattr(torch.version, "hip", None):
            raise RuntimeError("Formulens requires NVIDIA CUDA-enabled PyTorch. Install the OCR dependencies.")
        if not torch.cuda.is_available():
            raise RuntimeError("NVIDIA CUDA is unavailable. Check your NVIDIA GPU and driver with nvidia-smi.")
        model_id, revision = MODELS[self.settings.model]
        cache = self.settings.get_model_directory()
        cache.mkdir(parents=True, exist_ok=True)
        self.processor = AutoProcessor.from_pretrained(model_id, revision=revision, cache_dir=cache)
        model_options = {}
        if self.settings.model == "paddle":
            config = AutoConfig.from_pretrained(model_id, revision=revision, cache_dir=cache)
            # Transformers' legacy flat-config conversion changes this checkpoint's
            # untied embeddings to tied defaults. Preserve its separate weights.
            config.tie_word_embeddings = False
            config.text_config.tie_word_embeddings = False
            model_options["config"] = config
        model: Any = AutoModelForImageTextToText.from_pretrained(
            model_id,
            revision=revision,
            cache_dir=cache,
            dtype=torch.float16,
            attn_implementation="sdpa" if self.settings.model == "paddle" else "eager",
            **model_options,
        )
        self.model = model.to(self.device).eval()

    def recognize(self, path: Path) -> str:
        """Return LaTeX from an existing image; never delete the caller's file."""
        try:
            from PIL import Image, ImageOps
        except ImportError as error:
            raise RuntimeError("Install OCR support with: uv sync --package formulens --extra ocr") from error

        with Image.open(path) as source:
            foreground = ImageOps.exif_transpose(source).convert("RGBA")
            image = Image.new("RGBA", foreground.size, "white")
            image.alpha_composite(foreground)
            image = image.convert("RGB")
        self.load()
        import torch

        if self.settings.model == "paddle":
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": "Formula Recognition:"},
                    ],
                }
            ]
            inputs = self.processor.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt"
            ).to(self.device)
        else:
            inputs = self.processor(image, format=True, return_tensors="pt").to(self.device)
        generation_options = {}
        if self.settings.model == "got":
            generation_options = {"stop_strings": "<|im_end|>", "tokenizer": self.processor.tokenizer}
        with torch.inference_mode():
            generated = self.model.generate(
                **inputs,
                do_sample=False,
                use_cache=True,
                max_new_tokens=self.settings.max_tokens,
                **generation_options,
            )
        tokens = generated[0, inputs["input_ids"].shape[1] :]
        if len(tokens) >= self.settings.max_tokens:
            raise RuntimeError("Output reached max_tokens and may be incomplete; increase max_tokens and retry.")
        text = clean_latex(self.processor.decode(tokens, skip_special_tokens=True))
        if not text:
            raise RuntimeError("The model returned no equation. Try a clearer crop.")
        return text
