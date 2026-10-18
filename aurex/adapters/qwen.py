"""Qwen Local Model Upgrade Adapter Architecture for AUREX (Project Qwen Ascension)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from aurex.adapters.base import GenerationSettings
from aurex.adapters.llama_cpp import LlamaCppAdapter


class QwenModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    family: Literal["Qwen2.5", "Qwen3.5"] = "Qwen3.5"
    parameter_size: str = "2B"
    quantization: str = "Q4_K_M"
    estimated_ram_mb: int = Field(default=2048, ge=256)
    recommended_context_tokens: int = Field(default=4096, ge=512)


QWEN_MODEL_CATALOG: dict[str, QwenModelSpec] = {
    "Qwen2.5-0.5B": QwenModelSpec(
        name="Qwen2.5-0.5B-Instruct",
        family="Qwen2.5",
        parameter_size="0.5B",
        quantization="Q4_K_M",
        estimated_ram_mb=600,
        recommended_context_tokens=2048,
    ),
    "Qwen3.5-0.8B": QwenModelSpec(
        name="Qwen3.5-0.8B-Instruct",
        family="Qwen3.5",
        parameter_size="0.8B",
        quantization="Q4_K_M",
        estimated_ram_mb=900,
        recommended_context_tokens=4096,
    ),
    "Qwen3.5-2B": QwenModelSpec(
        name="Qwen3.5-2B-Instruct",
        family="Qwen3.5",
        parameter_size="2B",
        quantization="Q4_K_M",
        estimated_ram_mb=1800,
        recommended_context_tokens=4096,
    ),
    "Qwen3.5-4B": QwenModelSpec(
        name="Qwen3.5-4B-Instruct",
        family="Qwen3.5",
        parameter_size="4B",
        quantization="Q4_K_M",
        estimated_ram_mb=3200,
        recommended_context_tokens=4096,
    ),
    "Qwen3.5-9B": QwenModelSpec(
        name="Qwen3.5-9B-Instruct",
        family="Qwen3.5",
        parameter_size="9B",
        quantization="Q4_K_M",
        estimated_ram_mb=6500,
        recommended_context_tokens=8192,
    ),
}


def select_optimal_qwen_model(available_ram_mb: int) -> QwenModelSpec:
    if available_ram_mb >= 8000:
        return QWEN_MODEL_CATALOG["Qwen3.5-4B"]
    if available_ram_mb >= 4000:
        return QWEN_MODEL_CATALOG["Qwen3.5-2B"]
    if available_ram_mb >= 2000:
        return QWEN_MODEL_CATALOG["Qwen3.5-0.8B"]
    return QWEN_MODEL_CATALOG["Qwen2.5-0.5B"]


class QwenLlamaCppAdapter(LlamaCppAdapter):
    def __init__(
        self,
        spec: QwenModelSpec = QWEN_MODEL_CATALOG["Qwen3.5-2B"],
        base_url: str = "http://127.0.0.1:8080/v1",
        generation: GenerationSettings | None = None,
    ) -> None:
        super().__init__(
            model=spec.name,
            base_url=base_url,
            generation=generation or GenerationSettings(max_tokens=512, temperature=0.2),
        )
        self.spec = spec
