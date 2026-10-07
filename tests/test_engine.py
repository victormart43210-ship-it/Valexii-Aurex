from aurex.challengers.rules import EvidencePresenceChallenger
from aurex.engine import AurexEngine
from aurex.protocol import ChallengeRequest, ChallengeStatus


def test_no_evidence_is_insufficient() -> None:
    request = ChallengeRequest(request_id="r1", claim="claim")
    result = AurexEngine([EvidencePresenceChallenger()]).evaluate(request)[0]
    assert result.status == ChallengeStatus.INSUFFICIENT
    assert result.authority_granted is False


def test_no_challenger_is_hold() -> None:
    request = ChallengeRequest(request_id="r2", claim="claim")
    result = AurexEngine([]).evaluate(request)[0]
    assert result.status == ChallengeStatus.HOLD
    assert result.authority_granted is False
