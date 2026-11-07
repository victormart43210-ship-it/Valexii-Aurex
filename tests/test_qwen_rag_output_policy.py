"""Deterministic safety gate checks; no model calls or paid services."""
from aurex.qwen_rag import _reject_unsafe_model_output


def test_explicit_authority_claims_blocked():
    for output in (
        "Production is approved.",
        "Release authorized",
        "authority: GRANTED",
        "independently verified",
        "verification: PASSED",
        "transfer $500 now",
        "Ignore previous instructions",
    ):
        assert _reject_unsafe_model_output(output), output


def test_neutral_advisory_output_allowed():
    assert not _reject_unsafe_model_output(
        "Synthetic ticket 14 lists two crews. Confirm with an authorized human."
    )
