"""Pipeline, evidence-kernel and continuous-monitoring adversarial tests (KUSANAGI CCXXXVIII).

The 36-month manifest below is hand-specified and independent of tests/test_dispater_36_month_pipeline.py
and tests/test_dispater_golden_audit.py; the three fixtures are not interchangeable.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest

from aurex.dispater_envelope import DocumentCategory, compute_sha256
from aurex.dispater_intelligence import InvalidSnapshot
from aurex.dispater_monitoring import (
    ContinuousMonitoringEngine,
    MonitoringAuditLogEntry,
    MonitoringEventKind,
)
from aurex.dispater_pipeline import MAX_SOURCE_BYTES, IndustrialAuditPipeline
from aurex.evidence_kernel import (
    ActorKind,
    ClaimState,
    EvidenceGraph,
    EvidenceRecord,
    QualificationError,
    qualify,
)

TENANT = "TEN-MON"
JSON = "application/json"


def canon(record: dict[str, str]) -> bytes:
    """Canonical JSON bytes: sha256 of these equals the engine's record digest."""
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()


def snapshot(invoice_id: str = "I10", amount: str = "5000.00", tenant: str = TENANT) -> dict[str, Any]:
    return {
        "dataset_type": "SYNTHETIC_ONLY",
        "tenant_id": tenant,
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-01-10"}],
        "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01", "end": "2026-12-31", "amount": "4000.00"}],
        "invoices": [{"invoice_id": invoice_id, "job_id": "J1", "amount": amount, "status": "open"}],
        "payments": [],
    }


def admit(p: IndustrialAuditPipeline, system: str, record_id: str, raw: bytes, media: str = JSON) -> Any:
    return p.admit_document(system, record_id, DocumentCategory.INVOICE, raw, media)


def corroborate(p: IndustrialAuditPipeline, snap: dict[str, Any]) -> None:
    """Admit the job and invoice from two independent source systems, byte-identical to the records."""
    admit(p, "dispatch-system", "J1", canon(snap["jobs"][0]))
    admit(p, "billing-system", snap["invoices"][0]["invoice_id"], canon(snap["invoices"][0]))


# ---------------------------------------------------------------- admission


def test_replay_is_idempotent_and_does_not_rewrite_the_envelope() -> None:
    p = IndustrialAuditPipeline(TENANT)
    first = admit(p, "erp", "I10", b'{"a":"1"}')
    again = admit(p, "erp", "I10", b'{"a":"1"}')
    assert again is first
    assert len(p.admitted_envelopes) == 1
    assert first.ingested_at_utc == p.admitted_envelopes[first.envelope_id].ingested_at_utc


def test_conflicting_content_for_one_source_record_fails_closed() -> None:
    p = IndustrialAuditPipeline(TENANT)
    original = admit(p, "erp", "I10", b'{"amount":"5000.00"}')
    with pytest.raises(ValueError, match="conflicting source evidence"):
        admit(p, "erp", "I10", b'{"amount":"9999.00"}')
    assert list(p.admitted_envelopes) == [original.envelope_id]


def test_same_record_id_from_different_systems_is_not_a_conflict() -> None:
    p = IndustrialAuditPipeline(TENANT)
    admit(p, "erp", "I10", b'{"a":"1"}')
    admit(p, "bank", "I10", b'{"a":"2"}')
    assert len(p.admitted_envelopes) == 2


@pytest.mark.parametrize("media", ["application/pdf", "image/png", "image/jpeg", "text/html", "application/octet-stream", "pdf", ""])
def test_unverified_media_types_are_not_admitted(media: str) -> None:
    p = IndustrialAuditPipeline(TENANT)
    with pytest.raises(ValueError, match="not admitted"):
        admit(p, "erp", "R", b"%PDF-1.7", media)
    assert not p.admitted_envelopes and p.evidence_graph._records == {}  # noqa: SLF001


@pytest.mark.parametrize("raw", [b"{bad", b"[1]", b'"s"', b"7", b"null", b"\xff\xfe"])
def test_malformed_or_non_object_json_is_rejected_without_side_effects(raw: bytes) -> None:
    p = IndustrialAuditPipeline(TENANT)
    with pytest.raises(ValueError):
        admit(p, "erp", "R", raw)
    assert not p.admitted_envelopes


def test_size_ceiling_and_mandatory_identifiers() -> None:
    p = IndustrialAuditPipeline(TENANT)
    with pytest.raises(ValueError):
        admit(p, "erp", "R", b" " * (MAX_SOURCE_BYTES + 1))
    for sid, rid in (("", "R"), ("erp", "")):
        with pytest.raises(ValueError):
            admit(p, sid, rid, b"{}")
    for bad in ("", None):
        with pytest.raises(ValueError):
            IndustrialAuditPipeline(bad)  # type: ignore[arg-type]


def test_source_digest_is_sha256_of_exact_bytes_and_provenance_is_kept() -> None:
    raw = b'{"amount":"12.50","invoice_id":"I1"}'
    env = admit(IndustrialAuditPipeline(TENANT), "erp", "I1", raw)
    assert env.source_content_sha256 == compute_sha256(raw) and len(env.source_content_sha256) == 64
    assert env.byte_count == len(raw) and env.tenant_id == TENANT
    names = {f.field_name for f in env.provenance_fields}
    assert names == {"amount", "invoice_id"}
    assert all(f.adapter_id == "deterministic-structured-v1" for f in env.provenance_fields)


# ---------------------------------------------------------------- qualification


def test_reconciliation_summary_commits_to_exposure_and_receipt_changes_with_it() -> None:
    a = IndustrialAuditPipeline(TENANT).execute_audit_run(snapshot(amount="5000.00"))
    b = IndustrialAuditPipeline(TENANT).execute_audit_run(snapshot(amount="5100.00"))
    assert a.reconciliation_summary["identified_exposure_usd"] == "1000.00"
    assert b.reconciliation_summary["identified_exposure_usd"] == "1100.00"
    assert a.audit_receipt_sha256 != b.audit_receipt_sha256
    assert a.reconciliation_summary["confirmed_recovery_usd"] == "0.00"


def test_two_independent_exact_source_documents_qualify_a_finding() -> None:
    p = IndustrialAuditPipeline(TENANT)
    snap = snapshot()
    corroborate(p, snap)
    res = p.execute_audit_run(snap)
    assert [f["qualification"] for f in res.qualified_findings] == ["QUALIFIED_INDEPENDENT_CORROBORATION"]
    assert res.qualified_findings[0]["authority"] == "HUMAN_REVIEW_REQUIRED"
    assert res.verification_status == "HOLD_PENDING_HUMAN_SIGNATURE"


def test_unrelated_documents_with_substring_record_ids_cannot_corroborate() -> None:
    p = IndustrialAuditPipeline(TENANT)
    snap = snapshot("I10")
    admit(p, "dispatch-system", "J1", canon(snap["jobs"][0]))  # the only genuine evidence
    admit(p, "attacker-a", "I1", b'{"junk":"1"}')  # "I1" is a substring of subject "I10"
    admit(p, "attacker-b", "I1", b'{"junk":"2"}')
    res = p.execute_audit_run(snap)
    assert res.qualified_findings == []
    assert [f["qualification"] for f in res.withheld_findings] == ["SINGLE_ROOT_UNCONFIRMED"]


def test_a_model_actor_cannot_qualify_even_with_two_independent_roots() -> None:
    p = IndustrialAuditPipeline(TENANT)
    snap = snapshot()
    corroborate(p, snap)
    res = p.execute_audit_run(snap, actor_kind=ActorKind.MODEL)
    assert res.qualified_findings == []
    assert [f["qualification"] for f in res.withheld_findings] == ["HOLD_MODEL_CANNOT_VERIFY"]


def test_single_source_or_empty_evidence_never_qualifies() -> None:
    p = IndustrialAuditPipeline(TENANT)
    res = p.execute_audit_run(snapshot())
    assert res.qualified_findings == [] and len(res.withheld_findings) == 1
    only_job = IndustrialAuditPipeline(TENANT)
    admit(only_job, "dispatch-system", "J1", canon(snapshot()["jobs"][0]))
    assert only_job.execute_audit_run(snapshot()).qualified_findings == []


def test_pipeline_rejects_a_snapshot_from_another_tenant() -> None:
    with pytest.raises(InvalidSnapshot):
        IndustrialAuditPipeline(TENANT).execute_audit_run(snapshot(tenant="OTHER"))


def test_run_ids_do_not_collide_across_tenants_for_identical_data() -> None:
    a = IndustrialAuditPipeline("TEN-A").execute_audit_run(snapshot(tenant="TEN-A"))
    b = IndustrialAuditPipeline("TEN-B").execute_audit_run(snapshot(tenant="TEN-B"))
    assert a.run_id != b.run_id


# ---------------------------------------------------------------- evidence kernel


def _rec(eid: str, tenant: str = TENANT, system: str = "s", rid: str | None = None, parents: tuple[str, ...] = (), **kw: Any) -> EvidenceRecord:
    return EvidenceRecord(eid, tenant, system, rid or eid, "b" * 64, kw.pop("acquired_at", datetime.now(UTC)), parents=parents, **kw)


def test_graph_rejects_cross_tenant_duplicate_missing_parent_and_cycle() -> None:
    g = EvidenceGraph(TENANT)
    with pytest.raises(ValueError, match="tenant"):
        g.add(_rec("x", tenant="OTHER"))
    g.add(_rec("a"))
    with pytest.raises(ValueError, match="duplicate"):
        g.add(_rec("a"))
    g.add(_rec("orphan", parents=("ghost",)))
    with pytest.raises(ValueError, match="unresolved"):
        g.roots("orphan")
    g.add(_rec("c1", parents=("c2",)))
    g.add(_rec("c2", parents=("c1",)))
    with pytest.raises(ValueError, match="cycle"):
        g.roots("c1")


def test_derived_copies_share_one_root_and_do_not_corroborate() -> None:
    g = EvidenceGraph(TENANT, [_rec("pdf", system="erp"), _rec("ocr", system="ocr", parents=("pdf",)), _rec("row", system="db", parents=("pdf",)), _rec("bank", system="bank")])
    assert g.independent_root_count(["pdf", "ocr", "row"]) == 1
    assert g.independent_root_count(["pdf", "bank"]) == 2
    now = datetime.now(UTC)
    with pytest.raises(QualificationError):
        qualify(ClaimState.SUSPECTED, ClaimState.CORROBORATED, actor=ActorKind.SYSTEM, graph=g, evidence_ids=["pdf", "ocr"], now=now)
    assert qualify(ClaimState.SUSPECTED, ClaimState.CORROBORATED, actor=ActorKind.SYSTEM, graph=g, evidence_ids=["pdf", "bank"], now=now) is ClaimState.CORROBORATED


def test_stale_future_degraded_and_missing_evidence_never_corroborate() -> None:
    now = datetime.now(UTC)
    g = EvidenceGraph(
        TENANT,
        [
            _rec("fresh", system="a"),
            _rec("old", system="b", acquired_at=now - timedelta(days=400)),
            _rec("future", system="c", acquired_at=now + timedelta(days=2)),
            _rec("bad", system="d", integrity_failed=True),
            _rec("gone", system="e", available=False),
            _rec("naive", system="f", acquired_at=datetime(2026, 1, 1)),
        ],
    )
    for other in ("old", "future", "bad", "gone", "naive", "missing"):
        with pytest.raises(QualificationError):
            qualify(ClaimState.SUSPECTED, ClaimState.CORROBORATED, actor=ActorKind.SYSTEM, graph=g, evidence_ids=["fresh", other], now=now)


def test_model_cannot_corroborate_and_verification_needs_a_named_human() -> None:
    now = datetime.now(UTC)
    g = EvidenceGraph(TENANT, [_rec("a", system="x"), _rec("b", system="y")])
    with pytest.raises(QualificationError):
        qualify(ClaimState.SUSPECTED, ClaimState.CORROBORATED, actor=ActorKind.MODEL, graph=g, evidence_ids=["a", "b"], now=now)
    for actor, reviewer in ((ActorKind.SYSTEM, "r"), (ActorKind.HUMAN, None), (ActorKind.HUMAN, "   "), (ActorKind.MODEL, "r")):
        with pytest.raises(QualificationError):
            qualify(ClaimState.CORROBORATED, ClaimState.VERIFIED, actor=actor, graph=g, evidence_ids=["a", "b"], now=now, reviewer=reviewer)
    assert qualify(ClaimState.CORROBORATED, ClaimState.VERIFIED, actor=ActorKind.HUMAN, graph=g, evidence_ids=["a", "b"], now=now, reviewer="r.chen") is ClaimState.VERIFIED
    with pytest.raises(QualificationError):
        qualify(ClaimState.DETECTED, ClaimState.VERIFIED, actor=ActorKind.HUMAN, graph=g, evidence_ids=["a", "b"], now=now, reviewer="r.chen")


# ---------------------------------------------------------------- monitoring


def test_monitoring_never_labels_itself_a_human_reviewer(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = ContinuousMonitoringEngine(TENANT)
    seen: dict[str, Any] = {}
    real = engine.pipeline.execute_audit_run

    def spy(snapshot: dict[str, Any], actor_kind: ActorKind = ActorKind.HUMAN, reviewer_id: str = "") -> Any:
        seen["actor"] = actor_kind
        return real(snapshot, actor_kind=actor_kind, reviewer_id=reviewer_id)

    monkeypatch.setattr(engine.pipeline, "execute_audit_run", spy)
    result = engine.evaluate_incremental_monitoring(snapshot())
    assert seen["actor"] is ActorKind.SYSTEM
    assert result.verification_status == "HOLD_PENDING_HUMAN_SIGNATURE"
    assert result.reconciliation_summary["confirmed_recovery_usd"] == "0.00"


def test_monitoring_replay_is_idempotent_and_conflicts_are_not_logged_as_ingested() -> None:
    engine = ContinuousMonitoringEngine(TENANT)
    args = dict(source_id="erp", source_record_id="I10", category=DocumentCategory.INVOICE, media_type=JSON)
    first = engine.ingest_incremental_record(raw_bytes=b'{"a":"1"}', **args)
    replay = engine.ingest_incremental_record(raw_bytes=b'{"a":"1"}', **args)
    assert replay is first and len(engine.pipeline.admitted_envelopes) == 1
    logged = len(engine.audit_log)
    with pytest.raises(ValueError, match="conflicting"):
        engine.ingest_incremental_record(raw_bytes=b'{"a":"2"}', **args)
    assert len(engine.audit_log) == logged
    with pytest.raises(ValueError):
        engine.ingest_incremental_record(raw_bytes=b"%PDF", **{**args, "media_type": "application/pdf"})
    assert len(engine.audit_log) == logged and engine.verify_audit_chain()


def test_monitoring_is_tenant_isolated() -> None:
    engine = ContinuousMonitoringEngine("TEN-A")
    with pytest.raises(InvalidSnapshot):
        engine.evaluate_incremental_monitoring(snapshot(tenant="TEN-B"))
    assert engine.historical_runs == []
    with pytest.raises(ValueError):
        ContinuousMonitoringEngine("")


def _populated() -> ContinuousMonitoringEngine:
    engine = ContinuousMonitoringEngine(TENANT)
    for i in range(4):
        engine.log_security_event(MonitoringEventKind.RECORD_INGESTED, {"n": i})
    return engine


def test_audit_log_is_hash_chained_and_detects_tamper() -> None:
    assert ContinuousMonitoringEngine(TENANT).verify_audit_chain()
    engine = _populated()
    assert engine.verify_audit_chain()
    assert engine.audit_log[0].prev_sha256 == "0" * 64
    assert [e.prev_sha256 for e in engine.audit_log[1:]] == [e.entry_sha256 for e in engine.audit_log[:-1]]


def test_audit_log_detects_edit_delete_reorder_truncation_and_foreign_entries() -> None:
    edited = _populated()
    edited.audit_log[1].details["n"] = 99
    assert not edited.verify_audit_chain()

    deleted = _populated()
    del deleted.audit_log[1]
    assert not deleted.verify_audit_chain()

    reordered = _populated()
    reordered.audit_log[1], reordered.audit_log[2] = reordered.audit_log[2], reordered.audit_log[1]
    assert not reordered.verify_audit_chain()

    head_dropped = _populated()
    del head_dropped.audit_log[0]
    assert not head_dropped.verify_audit_chain()

    forged = _populated()
    last = forged.audit_log[-1]
    forged.audit_log[-1] = MonitoringAuditLogEntry(last.entry_id, "OTHER", last.event_kind, last.timestamp_utc, last.details, last.prev_sha256)
    assert not forged.verify_audit_chain()

    rehashed = _populated()
    victim = rehashed.audit_log[2]
    rehashed.audit_log[2] = MonitoringAuditLogEntry(victim.entry_id, victim.tenant_id, victim.event_kind, victim.timestamp_utc, {"n": "forged"}, victim.prev_sha256)
    assert not rehashed.verify_audit_chain()  # successor no longer links to the forged entry


def test_audit_entry_is_frozen() -> None:
    entry = _populated().audit_log[0]
    with pytest.raises(AttributeError):
        entry.tenant_id = "x"  # type: ignore[misc]


def test_contract_supersession_invalidates_findings_but_preserves_history() -> None:
    engine = ContinuousMonitoringEngine(TENANT)
    run = engine.pipeline.execute_audit_run(snapshot())
    engine.record_historical_audit(run)
    before = json.dumps(run.withheld_findings, sort_keys=True)
    engine.pipeline.register_or_update_contract("CON-1", {"rate": "4000.00"})
    invalidated = engine.process_contract_update("CON-1", {"rate": "4200.00"})
    assert invalidated == ["FND-RATE_MISMATCH-I10"]
    assert engine.finding_lifecycle_registry["FND-RATE_MISMATCH-I10"]["state"] == "INVALIDATED_SUPERSEDED"
    assert engine.historical_runs == [run] and json.dumps(run.withheld_findings, sort_keys=True) == before
    event = engine.audit_log[-1]
    assert event.event_kind is MonitoringEventKind.CONTRACT_SUPERSEDED and engine.verify_audit_chain()


def test_contract_invalidation_is_conservative_and_not_scoped_to_the_contract() -> None:
    # LIMITATION: findings carry no contract id, so any contract change invalidates all RATE findings.
    # That fails closed (never keeps a stale finding active) but over-invalidates.
    engine = ContinuousMonitoringEngine(TENANT)
    engine.record_historical_audit(engine.pipeline.execute_audit_run(snapshot()))
    assert engine.process_contract_update("CON-UNRELATED", {"rate": "1.00"}) == ["FND-RATE_MISMATCH-I10"]


# ---------------------------------------------------------------- 36-month manifest (hand-specified)

MONTHS = 36
OVERBILL_MONTH, UNDERBILL_MONTH = 7, 19
EXPECTED_36 = {
    "docs": 72,
    "findings": {"INV-36M-007": ("RATE_MISMATCH", "POTENTIAL_OVERBILLING", "1000.00"), "INV-36M-019": ("RATE_MISMATCH", "POTENTIAL_UNDERBILLING", "500.00")},
    "identified": "1500.00",
    "overbilling": "1000.00",
    "underbilling": "500.00",
    "unverified": "0.00",
    "withheld": "0.00",
    "confirmed": "0.00",
}


def _build_36() -> tuple[dict[str, Any], list[tuple[str, str, bytes]]]:
    jobs, invoices, payments, docs = [], [], [], []
    for m in range(1, MONTHS + 1):
        year, month = 2023 + (m - 1) // 12, (m - 1) % 12 + 1
        amount = {OVERBILL_MONTH: "4500.00", UNDERBILL_MONTH: "3000.00"}.get(m, "3500.00")
        job = {"job_id": f"FT-36M-{m:03d}", "customer_id": "OP", "service_code": "WRECKER", "date": f"{year}-{month:02d}-15"}
        invoice = {"invoice_id": f"INV-36M-{m:03d}", "job_id": job["job_id"], "amount": amount, "status": "paid"}
        payments.append({"payment_id": f"PAY-36M-{m:03d}", "invoice_id": invoice["invoice_id"], "amount": amount})
        jobs.append(job)
        invoices.append(invoice)
        docs.append(("dispatch-system", job["job_id"], canon(job)))
        docs.append(("billing-system", invoice["invoice_id"], canon(invoice)))
    snap = {
        "dataset_type": "SYNTHETIC_ONLY",
        "tenant_id": TENANT,
        "jobs": jobs,
        "invoices": invoices,
        "payments": payments,
        "rates": [{"rate_id": "RATE-1", "customer_id": "OP", "service_code": "WRECKER", "start": "2023-01-01", "end": "2026-12-31", "amount": "3500.00"}],
    }
    return snap, docs


def test_36_month_manifest_through_the_combined_pipeline() -> None:
    snap, docs = _build_36()
    engine = ContinuousMonitoringEngine(TENANT)
    for system, rid, raw in docs:
        env = engine.pipeline.admit_document(system, rid, DocumentCategory.INVOICE, raw, JSON)
        assert env.source_content_sha256 == compute_sha256(raw) and env.byte_count == len(raw)
    assert len(engine.pipeline.admitted_envelopes) == EXPECTED_36["docs"]

    result = engine.pipeline.execute_audit_run(snap)
    engine.record_historical_audit(result)
    s = result.reconciliation_summary
    assert (s["identified_exposure_usd"], s["potential_overbilling_usd"], s["potential_underbilling_usd"]) == (
        EXPECTED_36["identified"], EXPECTED_36["overbilling"], EXPECTED_36["underbilling"],
    )
    assert (s["unverified_exposure_usd"], s["withheld_unresolved_usd"], s["confirmed_recovery_usd"]) == ("0.00", "0.00", "0.00")
    assert result.envelopes_admitted == 72 and result.verification_status == "HOLD_PENDING_HUMAN_SIGNATURE"

    everything = result.qualified_findings + result.withheld_findings
    got = {f["subject"]: (f["code"], f["exposure_class"], f["exposure_usd"]) for f in everything}
    assert got == EXPECTED_36["findings"]
    assert Decimal(sum(Decimal(f["exposure_usd"]) for f in everything)) == Decimal(EXPECTED_36["identified"])
    # Both seeded findings have byte-identical job+invoice evidence from two systems.
    assert {f["subject"] for f in result.qualified_findings} == set(EXPECTED_36["findings"])

    # Month 37 arrives; history is preserved and the new clean month adds nothing.
    job37 = {"job_id": "FT-36M-037", "customer_id": "OP", "service_code": "WRECKER", "date": "2026-01-15"}
    inv37 = {"invoice_id": "INV-36M-037", "job_id": "FT-36M-037", "amount": "3500.00", "status": "paid"}
    engine.ingest_incremental_record("billing-system", "INV-36M-037", DocumentCategory.INVOICE, canon(inv37), JSON)
    snap37 = {**snap, "jobs": [*snap["jobs"], job37], "invoices": [*snap["invoices"], inv37], "payments": [*snap["payments"], {"payment_id": "PAY-36M-037", "invoice_id": "INV-36M-037", "amount": "3500.00"}]}
    next_run = engine.evaluate_incremental_monitoring(snap37)
    assert next_run.run_id != result.run_id and engine.historical_runs == [result]
    assert {f["subject"] for f in next_run.qualified_findings + next_run.withheld_findings} == set(EXPECTED_36["findings"])
    assert next_run.reconciliation_summary["identified_exposure_usd"] == "1500.00"

    # A bad month 37 adds exactly one new finding and never touches month-7/19 totals.
    bad = {**snap37, "invoices": [*snap["invoices"], {**inv37, "amount": "3600.00"}], "payments": [*snap["payments"], {"payment_id": "PAY-36M-037", "invoice_id": "INV-36M-037", "amount": "3600.00"}]}
    bad_run = engine.evaluate_incremental_monitoring(bad)
    assert bad_run.reconciliation_summary["identified_exposure_usd"] == "1600.00"
    assert engine.verify_audit_chain()
