"""Deterministic baseline challenger for protocol validation."""

from aurex.challengers.base import Challenger
from aurex.protocol import ChallengeRequest, ChallengeResult, ChallengeStatus


class EvidencePresenceChallenger(Challenger):
    """A deliberately conservative baseline.

    Presence of evidence is not proof. This challenger exists to establish
    safe defaults before model-backed challengers are admitted.
    """

    def challenge(self, request: ChallengeRequest) -> ChallengeResult:
        if not request.evidence:
            return ChallengeResult(
                request_id=request.request_id,
                status=ChallengeStatus.INSUFFICIENT,
                rationale="No admissible evidence references were supplied.",
            )
        return ChallengeResult(
            request_id=request.request_id,
            status=ChallengeStatus.HOLD,
            rationale="Evidence exists, but no independent semantic verifier has established support.",
            evidence_used=[item.evidence_id for item in request.evidence],
        )
