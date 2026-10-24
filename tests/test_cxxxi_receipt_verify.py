"""CXXXI mutation tests: the verifier must DETECT corrupted receipts.

Offline, synthetic. Source base: work/kusanagi-cxxix-staging-convergence@6adc1936d09534b134182e769f88fea9c5a0125a
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "cxxxi_receipt_verify",
    Path(__file__).resolve().parents[1] / "scripts" / "cxxxi_receipt_verify.py",
)
assert _SPEC and _SPEC.loader
mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mod)

JOB = "job-" + "a" * 24
EV = "ev-" + "b" * 24


def _good() -> dict:
    obs = {"probe": "sqlite_roundtrip_v1", "executed": True, "passed": True,
           "sha256": "c" * 64, "verification": "NOT VERIFIED"}
    return {"jobId": JOB, "state": "succeeded", "evidenceId": EV,
            "sha256": mod.canonical_digest(obs), "observation": obs,
            "integrity": "RECORDED", "verification": "NOT VERIFIED",
            "authority": "NONE", "release": "HOLD"}


def test_valid_receipt_passes_but_stays_unverified() -> None:
    out = mod.verify_receipt(_good(), expected_job_id=JOB, expected_evidence_id=EV)
    assert out["digest_consistency"] == "PASS"
    assert out["independent_verification"] == "NOT VERIFIED"
    assert out["authority"] == "NONE" and out["release"] == "HOLD"


def test_altered_observation_detected() -> None:
    r = _good()
    r["observation"]["passed"] = False
    with pytest.raises(mod.ReceiptError):
        mod.verify_receipt(r, expected_job_id=JOB)


def test_altered_digest_detected() -> None:
    r = _good()
    r["sha256"] = "0" * 64
    with pytest.raises(mod.ReceiptError):
        mod.verify_receipt(r, expected_job_id=JOB)


@pytest.mark.parametrize("field,value", [
    ("state", "failed"), ("state", "cancelled"), ("integrity", "VERIFIED"),
    ("verification", "VERIFIED"), ("authority", "GRANTED"), ("release", "OPEN"),
    ("evidenceId", None), ("evidenceId", "bad"), ("jobId", "job-" + "d" * 24),
])
def test_field_mutations_rejected(field: str, value: object) -> None:
    r = _good()
    r[field] = value
    with pytest.raises(mod.ReceiptError):
        mod.verify_receipt(r, expected_job_id=JOB)


def test_unsupported_and_missing_fields_rejected() -> None:
    extra = _good()
    extra["extra"] = 1
    with pytest.raises(mod.ReceiptError):
        mod.verify_receipt(extra, expected_job_id=JOB)
    missing = _good()
    del missing["evidenceId"]
    with pytest.raises(mod.ReceiptError):
        mod.verify_receipt(missing, expected_job_id=JOB)


def test_non_object_and_bad_expected_id_rejected() -> None:
    with pytest.raises(mod.ReceiptError):
        mod.verify_receipt([], expected_job_id=JOB)
    with pytest.raises(mod.ReceiptError):
        mod.verify_receipt(_good(), expected_job_id="nope")


def test_evidence_id_mismatch_rejected() -> None:
    with pytest.raises(mod.ReceiptError):
        mod.verify_receipt(_good(), expected_job_id=JOB, expected_evidence_id="ev-" + "e" * 24)


def test_input_not_mutated() -> None:
    r = _good()
    snap = copy.deepcopy(r)
    mod.verify_receipt(r, expected_job_id=JOB)
    assert r == snap
