"""AUREX orchestration boundary. Challenger outputs never grant authority."""

from collections.abc import Iterable

from aurex.challengers.base import Challenger
from aurex.protocol import ChallengeRequest, ChallengeResult, ChallengeStatus


class ChallengerFailure(RuntimeError):
    """Sanitized failure crossing the untrusted challenger boundary."""


class AurexEngine:
    def __init__(self, challengers: Iterable[Challenger]) -> None:
        self._challengers = tuple(challengers)

    def evaluate(self, request: ChallengeRequest) -> list[ChallengeResult]:
        if not self._challengers:
            return [self._hold(request, "No independent challenger is configured.")]

        allowed_ids = {item.evidence_id for item in request.evidence}
        results: list[ChallengeResult] = []
        for challenger in self._challengers:
            try:
                results.append(self._validated_challenge(challenger, request, allowed_ids))
            except ChallengerFailure:
                results.append(self._hold(request, "Challenger failed validation or execution."))
        return results

    @staticmethod
    def _validated_challenge(
        challenger: Challenger, request: ChallengeRequest, allowed_ids: set[str]
    ) -> ChallengeResult:
        try:
            untrusted = challenger.challenge(request)
            result = ChallengeResult.model_validate(untrusted.model_dump())
            if result.authority_granted:
                raise ValueError("Challenger attempted to grant authority.")
            if result.request_id != request.request_id:
                raise ValueError("Challenger returned a mismatched request ID.")
            if not set(result.evidence_used).issubset(allowed_ids):
                raise ValueError("Challenger cited evidence absent from the request.")
            if result.status == ChallengeStatus.SUPPORTED and not result.evidence_used:
                raise ValueError("Support requires an explicit evidence reference.")
            return result
        except Exception as exc:
            # Normalize arbitrary plugin failures without exposing provider messages.
            raise ChallengerFailure("Challenger failed validation or execution.") from exc

    @staticmethod
    def _hold(request: ChallengeRequest, rationale: str) -> ChallengeResult:
        return ChallengeResult(
            request_id=request.request_id,
            status=ChallengeStatus.HOLD,
            rationale=rationale,
        )
