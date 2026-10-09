"""Provider-neutral adapter contract."""

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class ModelAnswer(BaseModel):
    provider: str
    model: str
    text: str
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)


class ModelAdapter(ABC):
    @abstractmethod
    def answer(self, prompt: str) -> ModelAnswer:
        """Return a model answer. Implementations must not embed credentials."""
        raise NotImplementedError


class GenerationSettings(BaseModel):
    """Portable subset; unsupported options must not be silently discarded."""

    model_config = {"extra": "forbid", "frozen": True}
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1, le=32768)
    seed: int = Field(default=42, ge=0)
