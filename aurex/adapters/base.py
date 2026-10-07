"""Provider-neutral adapter contract."""

from abc import ABC, abstractmethod
from pydantic import BaseModel


class ModelAnswer(BaseModel):
    provider: str
    model: str
    text: str


class ModelAdapter(ABC):
    @abstractmethod
    def answer(self, prompt: str) -> ModelAnswer:
        """Return a model answer. Implementations must not embed credentials."""
        raise NotImplementedError
