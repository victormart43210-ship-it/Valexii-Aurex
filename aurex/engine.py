"""AUREX orchestration boundary."""

from collections.abc import Iterable

from aurex.challengers.base import Challenger
from aurex.protocol import ChallengeRequest, ChallengeResult, ChallengeStatus


class AurexEngine:
    def __init__(self, challengers: Iterable[Challenger]) -> None:
        self._challengers = tuple(challengers)

    def evaluate(self, request: ChallengeRequest) -> list[ChallengeResult]:
        if not self._challengers:
            return [
                ChallengeResult(
                    request_id=request.request_id,
                    status=ChallengeStatus.HOLD,
                    rationale="No independent challenger is configured.",
                )
            ]
        results = [challenger.challenge(request) for challenger in self._challengers]
        for result in results:
            if result.authority_granted:
                raise RuntimeError("AUREX invariant violation: challenger attempted to grant authority")
        return results
