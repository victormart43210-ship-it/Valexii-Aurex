"""KUSANAGI XCV: deterministic no-network corpus and plan validation tests."""
from __future__ import annotations

import json

import pytest

from aurex.research_alignment import (
    filter_parallel_pairs,
    synthetic_baseline,
    synthetic_corpus,
    validate_synthetic_plan,
)


def test_synthetic_corpus_receipt_is_bounded_and_deterministic():
    kept, r = filter_parallel_pairs(synthetic_corpus())
    other, again = filter_parallel_pairs(synthetic_corpus())
    assert kept == other and r == again
    assert len(kept) == 2
    assert (r.input_pairs, r.accepted_pairs, r.rejected_pairs) == (5, 2, 3)
    assert r.reason_counts["empty"] == 1
    assert r.reason_counts["ratio"] == 1
    assert r.reason_counts["duplicate"] == 1
    assert r.authority == "NONE" and r.independent_verification == "NOT_VERIFIED"
    assert len(r.source_sha256) == len(r.filtered_sha256) == 64
    assert "Inspect a sample record" not in json.dumps(r.__dict__)


def test_filter_rejects_control_characters_without_leaking_original():
    kept, receipt = filter_parallel_pairs((("secret\x00data", "ok"),))
    assert kept == ()
    assert receipt.status == "HOLD_EMPTY_FILTER"
    assert receipt.reason_counts["control"] == 1
    assert "secret" not in json.dumps(receipt.__dict__)


@pytest.mark.parametrize("corpus", [
    [], [("ok",)], ["single"], [("left", 123)], [("left", "right")] * 101,
    [("a" * 70000, "b")],
])
def test_bad_corpus_inputs_fail_closed(corpus):
    with pytest.raises(ValueError):
        filter_parallel_pairs(corpus)


@pytest.mark.parametrize("config", [
    {"min_words": 0}, {"max_words": 101}, {"min_words": 9, "max_words": 8},
    {"ratio_threshold": 1.0}, {"ratio_threshold": 11.0},
])
def test_invalid_filter_policy_fails_closed(config):
    with pytest.raises(ValueError):
        filter_parallel_pairs((("hello", "hello"),), **config)


def test_ratio_exactly_equal_threshold_rejected():
    kept, receipt = filter_parallel_pairs((("one", "one two three"),))
    assert kept == () and receipt.reason_counts["ratio"] == 1


def test_plan_validates_only_exact_synthetic_sequence():
    r = validate_synthetic_plan('{"steps":["inspect","test","review"]}')
    assert r.status == "STRUCTURE_MATCH_ONLY"
    assert r.reason == "SYNTHETIC_SEQUENCE_MATCH"
    assert r.authority == "NONE" and r.independent_verification == "NOT_VERIFIED"
    assert len(r.response_sha256) == 64


@pytest.mark.parametrize("raw,reason", [
    ('{"steps":["test","inspect","review"]}', "ORDER_OR_ACTION_MISMATCH"),
    ('{"steps":["inspect","deploy","review"]}', "ORDER_OR_ACTION_MISMATCH"),
    ('{"steps":["inspect","test","review"],"execute":true}', "INVALID_SCHEMA"),
    ('{"steps":["inspect","review"]}', "INVALID_STEPS"),
    ('{"steps":"inspect,test,review"}', "INVALID_STEPS"),
    ('["inspect","test","review"]', "INVALID_SCHEMA"),
    ('not-json', "INVALID_JSON"),
    ('```json\n{"steps":["inspect","test","review"]}\n```', "INVALID_JSON"),
    ("", "EMPTY_OR_OVERSIZED"),
    ('x' * 9000, "EMPTY_OR_OVERSIZED"),
])
def test_invalid_plan_is_hold_not_authority(raw, reason):
    r = validate_synthetic_plan(raw)
    assert r.status == "HOLD"
    assert r.reason == reason
    assert r.authority == "NONE"


def test_default_baseline_never_claims_real_qwen_or_validation():
    data = synthetic_baseline()
    assert data["kind"] == "SYNTHETIC_ONLY_NOT_MODEL_INFERENCE"
    assert data["production_authority"] == "HOLD"
    assert data["external_spend_usd"] == 0
    assert data["plan"]["status"] == "STRUCTURE_MATCH_ONLY"
    assert data["corpus"]["accepted_pairs"] == 2
