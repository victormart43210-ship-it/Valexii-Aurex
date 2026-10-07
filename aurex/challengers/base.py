"""Challenger contract. Challengers produce evidence judgments, never authority."""

from abc import ABC, abstractmethod

from aurex.protocol import ChallengeRequest, ChallengeResult


class Challenger(ABC):
    @abstractmethod
    def challenge(self, request: ChallengeRequest) -> ChallengeResult:
        """Evaluate a claim and return a non-authoritative result."""
        raise NotImplementedError
