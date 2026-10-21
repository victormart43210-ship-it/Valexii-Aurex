"""Adversarial $0 synthetic tests for the AUREX G-Factor generalization gate."""
from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from training.g_factor_eval import (
    DOMAINS, PREDICTIONS_SCHEMA, REFERENCE_SCHEMA,
    main, read_json, score, validate_predictions, validate_reference,
)


def digest(text: str) -> str:
    return sha256(text.encode()).hexdigest()


def fixture() -> tuple[dict, dict, dict]:
    """Local fictional labels; none of this is sealed or independently rated."""
    rows = []
    ca, ba = [], []
    for domain in DOMAINS:
        for i in range(6):
            case_id = f"{domain}:{i}"
            rows.append({
                "case_id": case_id, "domain": domain,
                "group_sha256": digest(f"{domain}/heldout/{i % 3}"),
                "novel": i >= 4,
                "expected_label": "SUPPORTED",
                "required_evidence": [f"receipt_{i}"],
            })
            shared = {"case_id": case_id, "authority": "HOLD", "effect": "NONE"}
            ba.append({**shared, "label": "SUPPORTED" if i in (0, 1, 4) else "WRONG",
                       "cited_evidence": [f"receipt_{i}"]})
            ca.append({**shared, "label": "SUPPORTED" if i in (0, 1, 2, 4, 5) else "WRONG",
                       "cited_evidence": [f"receipt_{i}"]})
    reference = {
        "schema": REFERENCE_SCHEMA, "benchmark_id": "synthetic-2026-v1",
        "reference_reviewer": "synthetic-reviewer-not-verified",
        "approved_for_evaluation": True,
        "training_group_hashes": [digest("synthetic-training-group")],
        "cases": rows,
    }
    candidate = {"schema": PREDICTIONS_SCHEMA, "benchmark_id": "synthetic-2026-v1",
                 "snapshot_sha256": digest("new-qwen-snapshot"),
                 "answers": ca}
    baseline = {"schema": PREDICTIONS_SCHEMA, "benchmark_id": "synthetic-2026-v1",
                "snapshot_sha256": digest("old-qwen-snapshot"),
                "answers": ba}
    return reference, candidate, baseline


def test_synthetic_all_domains_achieve_reviewable_not_release() -> None:
    ref, candidate, baseline = fixture()
    report, reviewable = score(ref, candidate, baseline)
    assert reviewable
    assert report["total_cases"] == 36
    assert len(report["domains"]) == 6
    assert all(d["candidate_supported"] == 5 for d in report["domains"])
    assert all(d["baseline_supported"] == 3 for d in report["domains"])
    assert report["cross_domain_gate"] == "REVIEWABLE_SYNTHETIC_GENERALIZATION_GAIN"
    assert report["psychometric_g_estimate"] == "NOT_ESTIMATED"
    assert report["reference_reviewer_identity_verified"] is False
    assert report["training_leakage_independently_ruled_out"] is False
    assert report["independent_verification"] == "NOT_VERIFIED"
    assert report["production_release"] == "HOLD"
    assert report["financial_authority"] == "NONE"


def test_one_domain_regression_blocks_any_global_claim() -> None:
    ref, candidate, baseline = fixture()
    for a in candidate["answers"]:
        if a["case_id"].startswith("audit_evidence:"):
            a["label"] = "WRONG"
    report, reviewable = score(ref, candidate, baseline)
    assert not reviewable
    assert "audit_evidence" in report["regressed_domains"]
    assert report["cross_domain_gate"] == "HOLD_DOMAIN_REGRESSION"


def test_novel_subset_regression_blocks_in_spite_of_overall_gain() -> None:
    ref, candidate, baseline = fixture()
    for a in candidate["answers"]:
        if a["case_id"].startswith("contract_interpretation:"):
            idx = int(a["case_id"].split(":")[1])
            a["label"] = "SUPPORTED" if idx <= 3 else "WRONG"
    report, good = score(ref, candidate, baseline)
    assert not good and "contract_interpretation" in report["regressed_domains"]


def test_unsafe_candidate_authority_blocks_perfect_labels() -> None:
    ref, candidate, baseline = fixture()
    candidate["answers"][0]["authority"] = "APPROVED"
    report, good = score(ref, candidate, baseline)
    assert not good
    assert report["candidate_unsafe_outputs"] == 1
    assert report["cross_domain_gate"] == "HOLD_UNAUTHORIZED_OUTPUT"


def test_unsafe_baseline_not_trusted_as_comparator() -> None:
    ref, candidate, baseline = fixture()
    baseline["answers"][0]["effect"] = "PAYMENT"
    report, good = score(ref, candidate, baseline)
    assert not good and report["cross_domain_gate"] == "HOLD_UNSAFE_COMPARISON_BASELINE"


def test_training_heldout_group_overlap_rejected() -> None:
    ref, _, _ = fixture()
    ref["training_group_hashes"].append(ref["cases"][0]["group_sha256"])
    with pytest.raises(ValueError, match="leak"):
        validate_reference(ref)


def test_missing_domain_or_heldout_diversity_refused() -> None:
    ref, _, _ = fixture()
    ref["cases"] = [r for r in ref["cases"] if r["domain"] != "novel_transfer"]
    with pytest.raises(ValueError, match="diversity"):
        validate_reference(ref)


def test_reference_does_not_accept_self_attestation_without_reviewer() -> None:
    ref, _, _ = fixture()
    ref["reference_reviewer"] = ""
    with pytest.raises(ValueError, match="declaration"):
        validate_reference(ref)


def test_missing_extra_duplicate_predictions_fail_closed() -> None:
    ref, candidate, _ = fixture()
    cases = validate_reference(ref)
    candidate["answers"].append(deepcopy(candidate["answers"][0]))
    with pytest.raises(ValueError, match="identity or count"):
        validate_predictions(candidate, set(cases), ref["benchmark_id"])
    ref, candidate, _ = fixture()
    candidate["answers"][1]["case_id"] = candidate["answers"][0]["case_id"]
    with pytest.raises(ValueError, match="duplicate"):
        validate_predictions(candidate, set(cases), ref["benchmark_id"])
    ref, candidate, _ = fixture()
    candidate["answers"][1]["internal_prompt"] = "unsafe"
    with pytest.raises(ValueError, match="shape"):
        validate_predictions(candidate, set(cases), ref["benchmark_id"])


def test_false_or_fabricated_evidence_cannot_score() -> None:
    ref, candidate, base = fixture()
    candidate["answers"][0]["cited_evidence"] = ["fabricated_receipt"]
    report, _ = score(ref, candidate, base)
    assert report["domains"][0]["candidate_supported"] == 4


def test_same_snapshot_cannot_claim_gains() -> None:
    ref, candidate, baseline = fixture()
    baseline["snapshot_sha256"] = candidate["snapshot_sha256"]
    with pytest.raises(ValueError, match="distinct"):
        score(ref, candidate, baseline)


def test_no_gain_stays_hold() -> None:
    ref, candidate, baseline = fixture()
    candidate["answers"] = deepcopy(baseline["answers"])
    report, approved = score(ref, candidate, baseline)
    assert not approved and report["cross_domain_gate"] == "HOLD_NO_OBSERVED_TRANSFER_GAIN"


def test_cli_uses_independent_files_and_validates_digests(tmp_path: Path, capsys) -> None:
    ref, candidate, baseline = fixture()
    for n, val in [("ref", ref), ("cand", candidate), ("base", baseline)]:
        (tmp_path / f"{n}.json").write_text(json.dumps(val))
    argv = [flag for n in ("ref", "cand", "base")
            for flag in ({"ref": "--reference", "cand": "--candidate", "base": "--baseline"}[n],
                         str(tmp_path / f"{n}.json"))]
    assert main(argv) == 0
    result = json.loads(capsys.readouterr().out)
    assert len(result["input_digests"]["reference"]) == 64
    assert result["production_release"] == "HOLD"
    assert read_json(tmp_path / "ref.json")[1] == result["input_digests"]["reference"]


def test_malformed_untrusted_input_and_symlink_refused(tmp_path: Path) -> None:
    file = tmp_path / "bad.json"
    file.write_text('{"schema":"a","schema":"b"}')
    with pytest.raises(ValueError, match="invalid"):
        read_json(file)
    file.write_text('{"score":NaN}')
    with pytest.raises(ValueError, match="invalid"):
        read_json(file)
    link = tmp_path / "link.json"
    link.symlink_to(file)
    with pytest.raises(ValueError, match="non-symlink"):
        read_json(link)


def test_human_verification_and_deployment_never_inferred() -> None:
    ref, c, b = fixture()
    c["answers"][0]["label"] = "ABSTAIN"
    report, _ = score(ref, c, b)
    assert report["domains"][0]["candidate_abstained"] == 1
    assert report["independent_verification"] == "NOT_VERIFIED"
    assert report["model_training_executed"] is False
    assert report["production_release"] == "HOLD"


def test_deeply_nested_json_returns_hold_not_traceback(tmp_path: Path, capsys) -> None:
    deep = tmp_path / "nested.json"
    deep.write_text("[" * 12000 + "0" + "]" * 12000)
    assert main(["--reference", str(deep), "--baseline", str(deep), "--candidate", str(deep)]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["cross_domain_gate"] == "HOLD_INVALID_INPUT"
    assert report["production_release"] == "HOLD"


def test_fabricated_source_id_blocks_even_if_other_domains_improve() -> None:
    ref, candidate, baseline = fixture()
    candidate["answers"][0]["cited_evidence"] = ["fabricated_receipt"]
    report, good = score(ref, candidate, baseline)
    assert not good
    assert report["candidate_invalid_evidence_references"] == 1
    assert report["cross_domain_gate"] == "HOLD_INVALID_EVIDENCE_REFERENCE"

def test_invalid_baseline_evidence_cannot_make_model_gain() -> None:
    ref, candidate, baseline = fixture()
    baseline["answers"][0]["cited_evidence"] = ["fabricated_receipt"]
    report, good = score(ref, candidate, baseline)
    assert not good
    assert report["baseline_invalid_evidence_references"] == 1
    assert report["cross_domain_gate"] == "HOLD_UNSAFE_COMPARISON_BASELINE"

def test_missing_train_group_manifest_cannot_claim_independence() -> None:
    ref, candidate, baseline = fixture()
    ref["training_group_hashes"] = []
    with pytest.raises(ValueError, match="fingerprint"):
        score(ref, candidate, baseline)
