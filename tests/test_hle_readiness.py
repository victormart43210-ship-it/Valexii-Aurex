"""Adversarial regression tests for AUREX admission and evaluation."""

import json

import pytest

from aurex.challengers.base import Challenger
from aurex.engine import AurexEngine
from aurex.evals.hle_gate import BenchmarkHold, assess_pair
from aurex.protocol import ChallengeRequest, ChallengeResult, ChallengeStatus


class ForgedChallenger(Challenger):
    def __init__(self, *, forged_id=False, authority=False, unknown_evidence=False):
        self.forged_id = forged_id
        self.authority = authority
        self.unknown_evidence = unknown_evidence

    def challenge(self, request):
        result = ChallengeResult(
            request_id="other" if self.forged_id else request.request_id,
            status=ChallengeStatus.SUPPORTED,
            rationale="Claimed support",
            evidence_used=["invented"] if self.unknown_evidence else [],
        )
        result.authority_granted = self.authority
        return result


@pytest.mark.parametrize(
    "kwargs",
    [
        {"forged_id": True},
        {"authority": True},
        {"unknown_evidence": True},
        {},
    ],
)
def test_untrusted_challenger_fails_closed(kwargs):
    result = AurexEngine([ForgedChallenger(**kwargs)]).evaluate(
        ChallengeRequest(request_id="test", claim="claim")
    )[0]
    assert result.status == ChallengeStatus.HOLD
    assert result.authority_granted is False


def test_hle_gate_requires_complete_independent_pairs(tmp_path):
    manifest = tmp_path / "manifest.json"
    results = tmp_path / "outcomes.jsonl"
    manifest.write_text(
        json.dumps(
            {
                "dataset_sha256": "a" * 64,
                "dataset_revision": "frozen",
                "item_ids": ["a", "b"],
                "baseline_model": "base",
                "aurex_model": "governed",
                "judge_id": "independent-reviewer",
                "evaluation_protocol_sha256": "b" * 64,
                "judge_independent": True,
                "contamination_checked": True,
                "dataset_authorized": True,
            }
        )
    )
    results.write_text(
        json.dumps({"item_id": "a", "base_correct": False, "governed_correct": True}) + "\n"
    )
    with pytest.raises(BenchmarkHold):
        assess_pair(manifest, results)
    with results.open("a") as stream:
        stream.write(
            json.dumps({"item_id": "b", "base_correct": True, "governed_correct": True}) + "\n"
        )
    report = assess_pair(manifest, results)
    assert report["n"] == 2
    assert report["improved_pairs"] == 1
    assert report["status"] == "PAIRED_COUNTS_VALIDATED_NOT_HLE_CERTIFIED"
