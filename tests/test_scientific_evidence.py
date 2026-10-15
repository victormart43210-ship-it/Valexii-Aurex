"""CUSTOS adversarial tests for scientific evidence foundation."""
import copy

import pytest

from aurex.scientific_evidence import (
    EvaluationCase,
    evaluate_exact,
    execution_manifest,
    unsigned_statement,
    verify_manifest,
)

SOURCE = "a" * 40
ENV = "b" * 64


def test_independent_scoring_distinguishes_missing_and_wrong() -> None:
    cases = [EvaluationCase("a", "prompt a", "yes"), EvaluationCase("b", "prompt b", "no")]
    scored = evaluate_exact(cases, {"a": "yes"})
    assert scored["counts"] == {"PASS": 1, "FAIL": 0, "UNKNOWN": 1}
    assert scored["passed"] is False and scored["complete"] is False
    wrong = evaluate_exact(cases, {"a": "yes", "b": "wrong"})
    assert wrong["counts"]["FAIL"] == 1 and wrong["passed"] is False
    correct = evaluate_exact(cases, {"a": "yes", "b": "no"})
    assert correct["passed"] is True and correct["complete"] is True


def test_rejects_ambiguous_or_unbounded_cases() -> None:
    with pytest.raises(ValueError):
        evaluate_exact([], {})
    with pytest.raises(ValueError):
        evaluate_exact([EvaluationCase("same", "", ""), EvaluationCase("same", "", "")], {})
    with pytest.raises(ValueError):
        evaluate_exact([EvaluationCase("a", "", "")], {"unknown": "x"})


def test_reproducibility_detects_tampering() -> None:
    evaluation = evaluate_exact([EvaluationCase("a", "q", "x")], {"a": "x"})
    manifest = execution_manifest(source_sha=SOURCE, environment_digest=ENV,
                                  inputs={"prompt": "q"}, outputs={"answer": "x"},
                                  evaluation=evaluation)
    args = dict(source_sha=SOURCE, environment_digest=ENV, inputs={"prompt": "q"},
                outputs={"answer": "x"}, evaluation=evaluation)
    assert verify_manifest(manifest, **args)
    assert not verify_manifest(manifest, **{**args, "outputs": {"answer": "tampered"}})
    altered = copy.deepcopy(manifest)
    altered["authority"] = "APPROVED"
    assert not verify_manifest(altered, **args)


def test_unsigned_attestation_does_not_claim_signature() -> None:
    evaluation = evaluate_exact([EvaluationCase("a", "q", "x")], {"a": "x"})
    manifest = execution_manifest(source_sha=SOURCE, environment_digest=ENV,
                                  inputs={}, outputs={}, evaluation=evaluation)
    statement = unsigned_statement(manifest)
    assert statement["_type"] == "https://in-toto.io/Statement/v1"
    assert statement["predicate"]["authority"] == "NONE"
    assert "signatures" not in statement
    assert "verification" not in statement


def test_invalid_provenance_fails_closed() -> None:
    with pytest.raises(ValueError):
        execution_manifest(source_sha="short", environment_digest=ENV,
                           inputs={}, outputs={}, evaluation={"passed": True})
    with pytest.raises(ValueError):
        execution_manifest(source_sha=SOURCE, environment_digest=ENV,
                           inputs={}, outputs={}, evaluation={"passed": "yes"})
