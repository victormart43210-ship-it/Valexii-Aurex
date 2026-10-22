"""Repository CI version of offline AUREX research regression tests."""
from __future__ import annotations

import hashlib
import importlib
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

# The backend directory is a deployable isolated subproject, not an aurex package.
_BACKEND_ROOT = Path(__file__).resolve().parents[1] / "integrations" / "kusanagi-xvi"
sys.path.insert(0, str(_BACKEND_ROOT))
ev = importlib.import_module("backend.evidence_science")
evals = importlib.import_module("backend.evaluation_science")
nim = importlib.import_module("backend.nvidia_research")
router = importlib.import_module("backend.research_api").router

NOW = datetime(2026, 10, 22, 19, 0, tzinfo=UTC)


def record(sid, family, stance="SUPPORT", when=NOW, content=None):
    if content is None:
        content = sid
    return {
        "sourceId": sid,
        "family": family,
        "stance": stance,
        "capturedAt": when.isoformat(),
        "sha256": hashlib.sha256(content.encode()).hexdigest(),
    }


def claim(*items):
    return {"claimId": "fictional.1", "evidence": list(items)}


def test_solo_witness_stays_hold():
    r = ev.assess_claim(claim(record("a", "same_org")), now=NOW)
    assert r["status"] == "HOLD" and r["authority"] == "NONE"
    assert r["summary"]["sourceFamilyCount"] == 1
    assert not r["modelWasCalled"]


def test_conflicting_distinct_families_trigger_review_candidate_only():
    r = ev.assess_claim(claim(record("a", "bank", "SUPPORT"), record("b", "ledger", "CONTRADICT")), now=NOW)
    assert r["status"] == "REVIEW_CANDIDATE"
    assert r["summary"]["conflictDetected"]
    assert r["release"] == "HOLD" and r["independentVerification"] == "NOT_VERIFIED"


def test_copies_across_families_do_not_corroborate():
    r = ev.assess_claim(claim(record("a", "bank", content="same"), record("b", "ledger", content="same")), now=NOW)
    assert r["summary"]["sourceFamilyCount"] == 1
    assert r["summary"]["excluded"]["duplicateDigest"] == 1
    assert r["status"] == "HOLD"


def test_multiple_records_from_same_family_not_independent():
    r = ev.assess_claim(claim(record("a", "bank"), record("b", "bank")), now=NOW)
    assert r["summary"]["sourceFamilyCount"] == 1
    assert r["status"] == "HOLD"


def test_same_family_self_conflict_detected():
    r = ev.assess_claim(claim(record("a", "bank", "SUPPORT"), record("b", "bank", "CONTRADICT")), now=NOW)
    assert r["summary"]["conflictingFamilies"] == 1
    assert r["status"] == "REVIEW_CANDIDATE"


def test_stale_future_and_clock_skew_fail_closed():
    r = ev.assess_claim(claim(record("old", "bank", when=NOW - timedelta(days=31)), record("future", "cash", when=NOW + timedelta(minutes=1))), now=NOW)
    assert r["summary"]["sourceFamilyCount"] == 0
    assert r["summary"]["excluded"]["stale"] == 1
    assert r["summary"]["excluded"]["future"] == 1


@pytest.mark.parametrize("bad", [
    {"claimId": "!", "evidence": []},
    {"claimId": "a", "evidence": {}, "unexpected": True},
    {"claimId": "a", "evidence": [record("a", "org", when=NOW)] * 17},
    {"claimId": "a", "evidence": [record("a", "org"), record("a", "org2")]},
    {"claimId": "a", "evidence": [dict(record("a", "org"), sha256="NOT_DIGEST")]},
    {"claimId": "a", "evidence": [dict(record("a", "org"), capturedAt="2026-10-22T15:00:00")]},
    {"claimId": "a", "evidence": [dict(record("a", "org"), stance="CLEAN")]},
])
def test_invalid_evidence_fails_closed(bad):
    with pytest.raises(ValueError):
        ev.assess_claim(bad, now=NOW)


def test_assessment_hash_stable_and_strips_raw_ids():
    c = claim(record("a", "first"), record("b", "second"))
    a = ev.assess_claim(c, now=NOW)
    b = ev.assess_claim(c, now=NOW)
    assert a == b
    assert "first" not in str(a)
    assert "second" not in str(a)


def test_bayes_math_only():
    assert ev.bayesian_example(0.5, [3.0]) == pytest.approx(0.75)
    assert ev.bayesian_example(0.5, [2.0, 0.5]) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        ev.bayesian_example(1, [1])
    with pytest.raises(ValueError):
        ev.bayesian_example(0.5, [float('nan')])


def test_wilson_zero_trials_and_zero_error_not_zero_risk():
    assert evals.wilson_interval(0, 0) is None
    low, high = evals.wilson_interval(0, 10)
    assert low == 0 and high > 0.2
    with pytest.raises(ValueError):
        evals.wilson_interval(2, 1)


def test_selective_risk_coverage_brier_and_wilson():
    truth = [{"id": "a", "expected": "REVIEW"}, {"id": "b", "expected": "CLEAR"}, {"id": "c", "expected": "REVIEW"}, {"id": "d", "expected": "CLEAR"}]
    pred = [{"id": "a", "prediction": "REVIEW", "pReview": 0.8}, {"id": "b", "prediction": "CLEAR", "pReview": 0.2}, {"id": "c", "prediction": "HOLD"}, {"id": "d", "prediction": "REVIEW", "pReview": 0.6}]
    q = evals.evaluate_rows(truth, pred)
    assert q["coverage"] == 0.75
    assert q["selectiveRisk"] == pytest.approx(1/3, abs=1e-6)
    assert q["brierScore"] == pytest.approx((0.04 + 0.04 + 0.36)/3, abs=1e-6)
    assert q["falseReviewAgainstClear"] == 1
    assert q["unsafeClearAgainstReview"] == 0
    assert q["release"] == "HOLD" and q["modelImprovement"] == "NOT_VERIFIED"


def test_abstention_never_counts_as_correct():
    truth = [{"id": "a", "expected": "CLEAR"}, {"id": "b", "expected": "REVIEW"}]
    pred = [{"id": "a", "prediction": "HOLD"}, {"id": "b", "prediction": "HOLD"}]
    q = evals.evaluate_rows(truth, pred)
    assert q["coverage"] == 0 and q["selectiveRisk"] is None
    assert q["brierScore"] is None


def test_exact_id_join_and_bad_probability_rejected():
    with pytest.raises(ValueError):
        evals.evaluate_rows([{"id": "x", "expected": "CLEAR"}], [])
    with pytest.raises(ValueError):
        evals.evaluate_rows([{"id": "x", "expected": "CLEAR"}], [{"id": "x", "prediction": "REVIEW", "pReview": float("nan")}])


def test_group_fold_reproducibility_and_no_leak():
    rows = [{"id": f"{g}.{i}", "group": f"subject{g}"} for g in range(7) for i in range(g % 3 + 1)]
    folds = evals.deterministic_group_folds(rows, k=4)
    assert folds == evals.deterministic_group_folds(list(reversed(rows)), k=4)
    for g in range(7):
        assert len({folds[row["id"]] for row in rows if row["group"] == f"subject{g}"}) == 1


def test_cusum_shift_is_candidate_only():
    assert evals.cusum_shift([0.5] * 20, reference_mean=0.5, threshold=2) == []
    assert evals.cusum_shift([0.9] * 40, reference_mean=0.5, slack=0, threshold=2)
    with pytest.raises(ValueError):
        evals.cusum_shift([float('nan')], reference_mean=0.5)


def test_nvidia_off_by_default_does_not_reserve(monkeypatch):
    def cannot_reserve():
        raise AssertionError("quota should not be used")
    assert nim.optional_nvidia_explanation({}, reserve=cannot_reserve, answer=lambda _: {})["status"] == "HOLD"


def enable_nvidia(monkeypatch):
    env = {
        "RAILWAY_ENVIRONMENT_NAME": "aurex-staging",
        "AUREX_RESEARCH_LAB_ENABLED": "true",
        "AUREX_NVIDIA_SYNTHESIS_ENABLED": "true",
        "AUREX_NVIDIA_ALLOW_TEXT_EGRESS": "true",
        "AUREX_LLM_PROVIDER": "nvidia",
        "AUREX_LLM_ENABLED": "true",
        "AUREX_LLM_ALLOW_BILLING": "true",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)


def test_nvidia_aggregates_only_and_quota(monkeypatch):
    enable_nvidia(monkeypatch)
    summary = {"sourceFamilyCount": 2, "supportFamilies": 1, "contradictFamilies": 1, "conflictingFamilies": 0}
    called = []
    r = nim.optional_nvidia_explanation(summary, reserve=lambda: True, answer=lambda q: called.append(q) or {"reply": "Unverified explanation", "authority": "NONE", "verification": "NOT_VERIFIED"})
    assert r["status"] == "UNVERIFIED_NVIDIA_NARRATIVE"
    assert called and "sourceFamilyCount=2" in called[0]
    assert "bank" not in called[0] and "credential" not in called[0]
    assert r["authority"] == "NONE"
    assert nim.optional_nvidia_explanation(summary, reserve=lambda: False, answer=lambda _: {})["status"] == "HOLD"


def test_nvidia_rejects_sensitive_fields_and_fake_authority(monkeypatch):
    enable_nvidia(monkeypatch)
    summary = {"sourceFamilyCount": 2, "supportFamilies": 1, "contradictFamilies": 1, "conflictingFamilies": 0}
    with pytest.raises(ValueError):
        nim.optional_nvidia_explanation({**summary, "customerData": "private"}, reserve=lambda: True, answer=lambda _: {})
    r = nim.optional_nvidia_explanation(summary, reserve=lambda: True, answer=lambda _: {"reply": "All clear", "authority": "PASS", "verification": "VERIFIED"})
    assert r["status"] == "HOLD"


def test_research_http_requires_bearer_and_flag(monkeypatch):
    app = FastAPI()
    def auth(authorization: str = Header(default="")):
        if authorization != "Bearer TEST":
            raise HTTPException(401, "unauthorized")
    app.include_router(router, dependencies=[Depends(auth)])
    with TestClient(app) as c:
        q = claim(record("a", "bank", when=NOW), record("b", "ledger", "CONTRADICT", when=NOW))
        assert c.post("/v1/research/assess", json=q).status_code == 401
        assert c.post("/v1/research/assess", json=q, headers={"Authorization":"Bearer TEST"}).status_code == 503
        monkeypatch.setenv("AUREX_RESEARCH_LAB_ENABLED", "true")
        monkeypatch.setenv("RAILWAY_ENVIRONMENT_NAME", "aurex-staging")
        # The synthetic evidence at 2026-10-22 is real-time scoped when tests run;
        # a later clock may mark it stale, but never grant authority.
        v = c.post("/v1/research/assess", json=q, headers={"Authorization":"Bearer TEST"})
        assert v.status_code == 200
        assert v.json()["release"] == "HOLD"
        assert v.json()["authority"] == "NONE"
