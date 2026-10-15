"""CUSTOS: a manifest must never accept fabricated evaluation success."""

import copy

import pytest

from aurex.scientific_evidence import EvaluationCase, evaluate_exact, execution_manifest, verify_manifest


SOURCE = "a" * 40
ENV = "b" * 64


def manifest(evaluation):
    return execution_manifest(source_sha=SOURCE, environment_digest=ENV,
                              inputs={"request": "q"}, outputs={"answer": "a"},
                              evaluation=evaluation)


def test_real_scored_evaluation_is_admissible_but_unverified():
    evaluation = evaluate_exact([EvaluationCase("one", "q", "a")], {"one": "a"})
    record = manifest(evaluation)
    assert record["qualification"] == "UNVERIFIED"
    assert record["authority"] == "NONE"
    assert verify_manifest(record, source_sha=SOURCE, environment_digest=ENV,
                           inputs={"request": "q"}, outputs={"answer": "a"},
                           evaluation=evaluation)


@pytest.mark.parametrize("forgery", [
    {"passed": True},
    {"passed": True, "complete": True, "counts": {"PASS": 1, "FAIL": 0, "UNKNOWN": 0}},
    {"passed": True, "complete": True, "counts": {"PASS": True, "FAIL": 0, "UNKNOWN": 0}},
    {"passed": True, "complete": True, "counts": {"PASS": 0, "FAIL": 1, "UNKNOWN": 0}},
])
def test_incomplete_or_contradictory_evaluation_cannot_be_manifested(forgery):
    with pytest.raises(ValueError):
        manifest(forgery)


def test_modified_result_digest_or_denominator_rejected():
    evaluation = evaluate_exact([EvaluationCase("one", "q", "a")], {"one": "a"})
    for change in ("digest", "count", "result", "verdict"):
        forged = copy.deepcopy(evaluation)
        if change == "digest":
            forged["digest_sha256"] = "0" * 64
        elif change == "count":
            forged["counts"]["PASS"] = 2
        elif change == "result":
            forged["results"][0]["outcome"] = "FAIL"
        else:
            forged["passed"] = False
        with pytest.raises(ValueError):
            manifest(forged)


def test_unknown_evaluation_cannot_claim_pass():
    evaluation = evaluate_exact([EvaluationCase("one", "q", "a")], {})
    assert manifest(evaluation)["qualification"] == "UNVERIFIED"
    evaluation["passed"] = True
    with pytest.raises(ValueError):
        manifest(evaluation)
