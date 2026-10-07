from aurex.protocol import ChallengeResult, ChallengeStatus


def test_result_never_grants_authority_by_default() -> None:
    result = ChallengeResult(
        request_id="r-1",
        status=ChallengeStatus.SUPPORTED,
        rationale="fixture",
    )
    assert result.authority_granted is False
