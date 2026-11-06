"""Adversarial tests for the AUREX Evidence Integrity Kernel and signed finding history."""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from aurex import dispater_store
from aurex.dispater_intelligence import RevenueLeakageEngine
from aurex.evidence_kernel import (
    ActorKind,
    Capability,
    ClaimState,
    EvidenceGraph,
    EvidenceRecord,
    Freshness,
    Outcome,
    QualificationError,
    RecoveryClaim,
    authorize,
    challenge_finding,
    digest,
    freshness_of,
    qualify,
)

NOW = datetime(2026, 11, 6, tzinfo=UTC)
T = "tenant-a"


def rec(eid: str, system: str, src: str, parents: tuple[str, ...] = (), **kw: Any) -> EvidenceRecord:
    kw.setdefault("event_time", NOW - timedelta(days=1))
    return EvidenceRecord(eid, T, system, src, digest(eid), NOW, parents=parents, **kw)


def graph() -> EvidenceGraph:
    return EvidenceGraph(
        T,
        [
            rec("pdf", "invoice-pdf", "INV-1"),
            rec("ocr", "ocr", "ocr-1", parents=("pdf",), transformations=("ocr:v1",)),
            rec("row", "db", "row-1", parents=("ocr",)),
            rec("bank", "bank-feed", "DEP-9"),
            rec("gps", "gps", "TRK-3"),
        ],
    )


def test_derived_copies_are_one_root() -> None:
    g = graph()
    assert g.independent_root_count(["pdf", "ocr", "row"]) == 1
    assert g.independent_root_count(["row", "bank"]) == 2


def test_duplicate_evidence_cannot_corroborate() -> None:
    with pytest.raises(QualificationError, match="independent"):
        qualify(ClaimState.SUSPECTED, ClaimState.CORROBORATED, actor=ActorKind.SYSTEM,
                graph=graph(), evidence_ids=["pdf", "ocr", "row"], now=NOW)
    assert qualify(ClaimState.SUSPECTED, ClaimState.CORROBORATED, actor=ActorKind.SYSTEM,
                   graph=graph(), evidence_ids=["row", "bank"], now=NOW) is ClaimState.CORROBORATED


def test_missing_parent_and_cycle_fail_closed() -> None:
    g = EvidenceGraph(T, [rec("a", "x", "1", parents=("ghost",)), rec("b", "x", "2", parents=("ghost",))])
    with pytest.raises(ValueError, match="unresolved evidence parent"):
        g.independent_root_count(["a", "b"])
    g = EvidenceGraph(T, [rec("a", "x", "1", parents=("b",)), rec("b", "x", "2", parents=("a",))])
    with pytest.raises(ValueError, match="cycle"):
        g.roots("a")


def test_model_can_never_corroborate_or_verify() -> None:
    for target, cur in ((ClaimState.CORROBORATED, ClaimState.SUSPECTED), (ClaimState.VERIFIED, ClaimState.CORROBORATED)):
        with pytest.raises(QualificationError, match="model"):
            qualify(cur, target, actor=ActorKind.MODEL, graph=graph(), evidence_ids=["row", "bank"],
                    now=NOW, reviewer="x")


def test_verification_requires_human_reviewer_and_no_skipping() -> None:
    kw: dict[str, Any] = {"graph": graph(), "evidence_ids": ["row", "bank"], "now": NOW}
    with pytest.raises(QualificationError):
        qualify(ClaimState.CORROBORATED, ClaimState.VERIFIED, actor=ActorKind.SYSTEM, reviewer="r", **kw)
    with pytest.raises(QualificationError):
        qualify(ClaimState.CORROBORATED, ClaimState.VERIFIED, actor=ActorKind.HUMAN, **kw)
    with pytest.raises(QualificationError):
        qualify(ClaimState.DETECTED, ClaimState.VERIFIED, actor=ActorKind.HUMAN, reviewer="r", **kw)
    with pytest.raises(QualificationError):
        qualify(ClaimState.REJECTED, ClaimState.SUSPECTED, actor=ActorKind.HUMAN, reviewer="r", **kw)
    assert qualify(ClaimState.CORROBORATED, ClaimState.VERIFIED, actor=ActorKind.HUMAN, reviewer="r", **kw) is ClaimState.VERIFIED


def test_freshness_states_never_silently_current() -> None:
    day = timedelta(days=30)
    ok = rec("e", "s", "1")
    assert freshness_of(ok, NOW, day) is Freshness.CURRENT
    assert freshness_of(rec("e", "s", "1", event_time=NOW - timedelta(days=90)), NOW, day) is Freshness.STALE
    assert freshness_of(rec("e", "s", "1", event_time=NOW + timedelta(days=2)), NOW, day) is Freshness.UNKNOWN
    naive = EvidenceRecord("e", T, "s", "1", "h", datetime(2026, 11, 5))
    assert freshness_of(naive, NOW, day) is Freshness.UNKNOWN
    assert freshness_of(rec("e", "s", "1", available=False), NOW, day) is Freshness.UNAVAILABLE
    assert freshness_of(rec("e", "s", "1", integrity_failed=True), NOW, day) is Freshness.DEGRADED
    assert freshness_of(ok, NOW, day, conflicting_hashes=["other"]) is Freshness.CONFLICTED


def test_stale_evidence_blocks_corroboration() -> None:
    g = EvidenceGraph(T, [rec("a", "s1", "1"), rec("b", "s2", "2", event_time=NOW - timedelta(days=400))])
    with pytest.raises(QualificationError, match="CURRENT"):
        qualify(ClaimState.SUSPECTED, ClaimState.CORROBORATED, actor=ActorKind.SYSTEM,
                graph=g, evidence_ids=["a", "b"], now=NOW)


def test_cross_tenant_evidence_rejected() -> None:
    g = EvidenceGraph(T)
    with pytest.raises(ValueError, match="tenant"):
        g.add(EvidenceRecord("x", "tenant-b", "s", "1", "h", NOW))


def test_financial_execution_is_never_authorized() -> None:
    everything = list(Capability)
    for actor in ActorKind:
        assert not authorize(actor, everything, Capability.EXECUTE_FINANCIAL)
    assert not authorize(ActorKind.MODEL, everything, Capability.EXPORT_REPORT)
    assert not authorize(ActorKind.MODEL, everything, Capability.PROPOSE_ADJUSTMENT)
    assert not authorize(ActorKind.SYSTEM, [], Capability.READ_EVIDENCE)
    assert authorize(ActorKind.SYSTEM, [Capability.READ_EVIDENCE], Capability.READ_EVIDENCE)


def _claim() -> RecoveryClaim:
    return RecoveryClaim(T, "OBL-1", Decimal("150.00"))


def test_outcome_chain_needs_independent_payment_evidence() -> None:
    g = graph()
    c = _claim()
    with pytest.raises(QualificationError, match="skipped"):
        c.advance(Outcome.APPROVED_CLAIM, actor=ActorKind.HUMAN, evidence_ids=("bank",), graph=g, reviewer="r")
    with pytest.raises(QualificationError, match="two independent"):
        c.advance(Outcome.VERIFIED_DISCREPANCY, actor=ActorKind.SYSTEM, evidence_ids=("pdf", "ocr"), graph=g)
    c.advance(Outcome.VERIFIED_DISCREPANCY, actor=ActorKind.SYSTEM, evidence_ids=("row", "gps"), graph=g)
    c.advance(Outcome.SUBMITTED_CLAIM, actor=ActorKind.HUMAN, evidence_ids=("row",), graph=g, reviewer="r")
    c.advance(Outcome.APPROVED_CLAIM, actor=ActorKind.HUMAN, evidence_ids=("row",), graph=g, reviewer="r")
    assert c.recovered_amount == 0  # projected money is never recovered money
    with pytest.raises(QualificationError, match="independent of the claim"):
        c.advance(Outcome.CONFIRMED_RECOVERED, actor=ActorKind.HUMAN, evidence_ids=("ocr",), graph=g,
                  reviewer="r", received_amount=Decimal("150.00"), claim_source_ids=("row", "gps"))
    with pytest.raises(QualificationError, match="exceed"):
        c.advance(Outcome.CONFIRMED_RECOVERED, actor=ActorKind.HUMAN, evidence_ids=("bank",), graph=g,
                  reviewer="r", received_amount=Decimal("150.01"), claim_source_ids=("row", "gps"))
    c.advance(Outcome.CONFIRMED_RECOVERED, actor=ActorKind.HUMAN, evidence_ids=("bank",), graph=g,
              reviewer="r", received_amount=Decimal("100.00"), claim_source_ids=("row", "gps"))
    assert c.recovered_amount == Decimal("100.00") and len(c.history) == 4
    with pytest.raises(QualificationError):
        c.advance(Outcome.CONFIRMED_RECOVERED, actor=ActorKind.HUMAN, evidence_ids=("bank",), graph=g,
                  reviewer="r", received_amount=Decimal("1"))


def test_model_cannot_advance_claim() -> None:
    with pytest.raises(QualificationError, match="model"):
        _claim().advance(Outcome.VERIFIED_DISCREPANCY, actor=ActorKind.MODEL, evidence_ids=("row", "gps"), graph=graph())


def test_challenger_flags_known_weaknesses() -> None:
    assert challenge_finding({"evidence": [{"k": 1}], "exposure_usd": "5.00"}, T, set()) == []
    bad = {"tenant_id": "other", "obligation_id": "O1", "exposure_usd": "-1", "recovered_usd": "5",
           "evidence_timestamp": "2026-01-01T00:00:00"}
    out = challenge_finding(bad, T, {"O1"})
    for expected in ("missing evidence", "tenant attribution mismatch", "duplicate obligation",
                     "negative exposure", "recovery exceeds exposure", "timestamp without timezone"):
        assert expected in out
    assert "invalid amount" in challenge_finding({"evidence": [1], "exposure_usd": "NaNx"}, T, set())


def test_canonical_digest_is_order_independent() -> None:
    assert digest({"a": 1, "b": [1, 2]}) == digest({"b": [1, 2], "a": 1})
    with pytest.raises(ValueError):
        digest({"a": float("nan")})


# ---- signed finding history ------------------------------------------------


def _saved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str, Path]:
    db = tmp_path / "h.db"
    monkeypatch.setenv("AUREX_DISPATER_DB", str(db))
    data: dict[str, Any] = {
        "tenant_id": T,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01",
                   "end": "2026-12-31", "amount": "100.00"}],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "150.00", "status": "open"}],
        "payments": [],
    }
    report, _ = dispater_store.save_run(T, RevenueLeakageEngine(T).reconcile_records(data))
    return report["run_id"], report["findings"][0]["finding_id"], db


def test_history_returns_only_verified_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run_id, fid, _ = _saved(tmp_path, monkeypatch)
    hist = dispater_store.finding_history(T, fid)
    assert hist[0]["run_id"] == run_id and hist[0]["verified"] is True


def test_history_rejects_tampered_unsigned_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, fid, db = _saved(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    conn.execute("UPDATE dispater_findings SET exposure_usd='0.01' WHERE finding_id=?", (fid,))
    conn.commit()
    conn.close()
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.finding_history(T, fid)


def test_history_rejects_tampered_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, fid, db = _saved(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    rpt = json.loads(conn.execute("SELECT report_json FROM dispater_runs").fetchone()[0])
    rpt["findings"][0]["severity"] = "LOW"
    conn.execute("UPDATE dispater_runs SET report_json=?", (json.dumps(rpt),))
    conn.execute("UPDATE dispater_findings SET severity='LOW'")
    conn.commit()
    conn.close()
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.finding_history(T, fid)


def test_history_denies_other_tenant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, fid, _ = _saved(tmp_path, monkeypatch)
    assert dispater_store.finding_history("tenant-b", fid) == []


def test_history_fails_closed_without_receipt_keys(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, fid, _ = _saved(tmp_path, monkeypatch)
    monkeypatch.delenv("AUREX_DISPATER_RECEIPT_KEYS")
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.finding_history(T, fid)


def test_signed_report_key_set_matches_frontend_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """website/src/lib/dispater-contract.ts must type every signed key, or exports lose it."""
    run_id, _, _ = _saved(tmp_path, monkeypatch)
    report = dispater_store.get_run(T, run_id)
    assert report is not None
    assert set(report) == {
        "authority_state", "counts", "created_at", "dataset_sha256", "financial_summary", "findings",
        "human_review_required", "limits", "receipt_auth", "receipt_binding", "receipt_mac",
        "receipt_sha256", "run_id", "schema", "status", "tenant_id",
    }
    assert report["receipt_binding"] == "BOUND_V2"
    assert set(report["findings"][0]) == {
        "authority", "code", "evidence", "exposure_class", "exposure_event_id", "exposure_usd",
        "finding_id", "finding_sha256", "qualification", "severity", "subject", "xaeli_explanation",
    }


def test_exported_report_still_verifies_independently(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from aurex.dispater_receipt import verify_mac

    run_id, _, _ = _saved(tmp_path, monkeypatch)
    report = dispater_store.get_run(T, run_id)
    assert report is not None
    exported = json.loads(json.dumps(report, indent=2))
    assert verify_mac(exported)
    for field in ("run_id", "created_at", "receipt_binding", "receipt_mac", "receipt_auth"):
        stripped = {k: v for k, v in report.items() if k != field}
        assert not verify_mac(stripped)
    altered = {**report, "status": "TAMPERED"}
    assert not verify_mac(altered)


def test_distinct_missing_parents_cannot_create_false_independence() -> None:
    g = EvidenceGraph(T, [
        rec("a", "source-a", "1", parents=("missing-a",)),
        rec("b", "source-b", "2", parents=("missing-b",)),
    ])
    with pytest.raises(QualificationError, match="unresolved provenance"):
        qualify(ClaimState.SUSPECTED, ClaimState.CORROBORATED,
                actor=ActorKind.SYSTEM, graph=g, evidence_ids=("a", "b"), now=NOW)


def test_confirmed_recovery_requires_original_claim_sources() -> None:
    c = _claim()
    c.state = Outcome.APPROVED_CLAIM
    with pytest.raises(QualificationError, match="claim source evidence is required"):
        c.advance(Outcome.CONFIRMED_RECOVERED, actor=ActorKind.HUMAN,
                  evidence_ids=("bank",), graph=graph(), reviewer="r",
                  received_amount=Decimal("50.00"), now=NOW)
    assert c.state is Outcome.APPROVED_CLAIM
    assert c.recovered_amount == 0


def test_recovery_rejects_stale_and_unresolved_evidence() -> None:
    g = EvidenceGraph(T, [
        rec("stale", "s", "1", event_time=NOW - timedelta(days=200)),
        rec("fresh", "s", "2"),
        rec("orphan", "s", "3", parents=("missing",)),
    ])
    c = _claim()
    with pytest.raises(QualificationError, match="CURRENT"):
        c.advance(Outcome.VERIFIED_DISCREPANCY, actor=ActorKind.SYSTEM,
                  evidence_ids=("stale", "fresh"), graph=g, now=NOW)
    with pytest.raises(QualificationError, match="unresolved provenance"):
        c.advance(Outcome.VERIFIED_DISCREPANCY, actor=ActorKind.SYSTEM,
                  evidence_ids=("orphan", "fresh"), graph=g, now=NOW)


def test_system_cannot_approve_or_confirm_recovery() -> None:
    c = _claim()
    c.state = Outcome.SUBMITTED_CLAIM
    with pytest.raises(QualificationError, match="human reviewer"):
        c.advance(Outcome.APPROVED_CLAIM, actor=ActorKind.SYSTEM,
                  evidence_ids=("bank",), graph=graph(), reviewer="r", now=NOW)


def test_blank_reviewer_cannot_verify_or_approve() -> None:
    kw: dict[str, Any] = {"graph": graph(), "evidence_ids": ["row", "bank"], "now": NOW}
    for reviewer in (" ", "\t", ""):
        with pytest.raises(QualificationError, match="reviewer"):
            qualify(
                ClaimState.CORROBORATED,
                ClaimState.VERIFIED,
                actor=ActorKind.HUMAN,
                reviewer=reviewer,
                **kw,
            )
    claim = _claim()
    claim.state = Outcome.SUBMITTED_CLAIM
    with pytest.raises(QualificationError, match="reviewer"):
        claim.advance(
            Outcome.APPROVED_CLAIM,
            actor=ActorKind.HUMAN,
            evidence_ids=("bank",),
            graph=graph(),
            reviewer=" ",
            now=NOW,
        )
    assert claim.state is Outcome.SUBMITTED_CLAIM
    assert claim.history == []


def test_nonpositive_or_nonfinite_claim_amount_is_rejected() -> None:
    for amount in (Decimal("0"), Decimal("-1.00"), Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")):
        with pytest.raises(QualificationError, match="claim amount"):
            RecoveryClaim(T, "OBL-1", amount)


def test_negative_recovery_is_challenged() -> None:
    issues = challenge_finding(
        {"evidence": [1], "exposure_usd": "10.00", "recovered_usd": "-0.01"}, T, set()
    )
    assert "negative recovery" in issues
    assert "recovery exceeds exposure" not in issues


def test_nonfinite_financial_values_are_rejected() -> None:
    for amount in ("NaN", "Infinity", "-Infinity"):
        issues = challenge_finding({"evidence": [1], "exposure_usd": amount}, T, set())
        assert "invalid amount" in issues
        issues = challenge_finding({"evidence": [1], "exposure_usd": "100", "recovered_usd": amount}, T, set())
        assert "invalid amount" in issues
    c = _claim()
    c.state = Outcome.APPROVED_CLAIM
    with pytest.raises(QualificationError, match="received amount"):
        c.advance(Outcome.CONFIRMED_RECOVERED, actor=ActorKind.HUMAN,
                  evidence_ids=("bank",), graph=graph(), reviewer="r",
                  received_amount=Decimal("NaN"), claim_source_ids=("pdf",), now=NOW)
