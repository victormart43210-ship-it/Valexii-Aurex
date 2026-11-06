"""Independent financial oracle for DISPATER reconciliation (Operation KUSANAGI CCXXXVIII).

Every expected value below is specified by hand from the scenario, never computed with
production helpers. The engine is exercised only through ``reconcile_records``.
Identified exposure, withheld exposure and confirmed recovery must stay separate.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest

from aurex.dispater_intelligence import InvalidSnapshot, RevenueLeakageEngine
from aurex.evidence_kernel import (
    ActorKind,
    EvidenceGraph,
    EvidenceRecord,
    Outcome,
    QualificationError,
    RecoveryClaim,
)


def job(job_id: str = "J1") -> dict[str, str]:
    return {"job_id": job_id, "customer_id": "C1", "service_code": "SVC", "date": "2026-03-01"}


def rate(rate_id: str = "R1", amount: str = "4000.00", start: str = "2026-01-01", end: str = "2026-12-31") -> dict[str, str]:
    return {"rate_id": rate_id, "customer_id": "C1", "service_code": "SVC", "start": start, "end": end, "amount": amount}


def inv(invoice_id: str, amount: str, status: str = "open", job_id: str = "J1") -> dict[str, str]:
    return {"invoice_id": invoice_id, "job_id": job_id, "amount": amount, "status": status}


def pay(payment_id: str, invoice_id: str, amount: str) -> dict[str, str]:
    return {"payment_id": payment_id, "invoice_id": invoice_id, "amount": amount}


def run(tenant: str = "T-A", **tables: list[dict[str, str]]) -> dict[str, Any]:
    dataset: dict[str, Any] = {"dataset_type": "SYNTHETIC_ONLY", "tenant_id": tenant}
    for name in ("jobs", "invoices", "rates", "payments"):
        dataset[name] = tables.get(name, [])
    return RevenueLeakageEngine(tenant).reconcile_records(dataset)


def money(report: dict[str, Any]) -> dict[str, str]:
    return report["financial_summary"]


def codes(report: dict[str, Any]) -> list[str]:
    return sorted(f["code"] for f in report["findings"])


def test_same_invoice_rate_and_cash_findings_count_the_dollars_once() -> None:
    # Billed 5000 vs rate 4000 (+1000), "paid" with only 4000 cash (-1000 cash gap on the same invoice).
    r = run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "5000.00", "paid")], payments=[pay("P1", "I1", "4000.00")])
    assert codes(r) == ["PAID_STATUS_UNRECONCILED", "RATE_MISMATCH"]
    s = money(r)
    assert s["identified_exposure_usd"] == "1000.00"
    assert s["potential_overbilling_usd"] == "1000.00"
    assert s["unverified_exposure_usd"] == "0.00"
    assert s["confirmed_recovery_usd"] == "0.00"
    exposures = {f["code"]: f["exposure_usd"] for f in r["findings"]}
    assert exposures == {"RATE_MISMATCH": "1000.00", "PAID_STATUS_UNRECONCILED": "0.00"}


def test_two_invoices_one_ticket_are_withheld_not_exposure() -> None:
    r = run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "4000.00"), inv("I2", "4000.00")])
    s = money(r)
    assert s["withheld_unresolved_usd"] == "8000.00"
    assert s["identified_exposure_usd"] == "0.00"
    assert codes(r) == ["DUPLICATE_INVOICE_UNRESOLVED"]


def test_duplicate_invoices_that_disagree_on_amount_pick_no_winner() -> None:
    r = run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "4000.00"), inv("I2", "4500.00")])
    s = money(r)
    assert s["withheld_unresolved_usd"] == "8500.00"
    assert s["identified_exposure_usd"] == "0.00"
    assert s["potential_overbilling_usd"] == "0.00"


def test_duplicate_invoice_order_does_not_change_totals() -> None:
    a = run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "4000.00"), inv("I2", "4500.00")])
    b = run(jobs=[job()], rates=[rate()], invoices=[inv("I2", "4500.00"), inv("I1", "4000.00")])
    assert money(a) == money(b)


def test_one_invoice_with_split_payments_that_sum_to_bill_creates_no_cash_exposure() -> None:
    r = run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "4000.00", "paid")], payments=[pay("P1", "I1", "2500.00"), pay("P2", "I1", "1500.00")])
    assert codes(r) == ["SPLIT_OR_DUPLICATE_PAYMENT_UNRESOLVED"]
    assert money(r)["identified_exposure_usd"] == "0.00"


def test_duplicate_looking_payment_counts_only_the_net_overpayment_once() -> None:
    # Bill 4000, two payments of 2200 = 4400: the 400 overage is booked once, not 2200 or 4400.
    r = run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "4000.00", "paid")], payments=[pay("P1", "I1", "2200.00"), pay("P2", "I1", "2200.00")])
    assert codes(r) == ["PAID_STATUS_UNRECONCILED", "SPLIT_OR_DUPLICATE_PAYMENT_UNRESOLVED"]
    assert money(r)["unverified_exposure_usd"] == "400.00"
    assert money(r)["identified_exposure_usd"] == "400.00"


def test_partial_payment_and_overpayment_are_distinct_unverified_findings() -> None:
    r = run(
        jobs=[job("J1"), job("J2")],
        rates=[rate(amount="1000.00")],
        invoices=[inv("I1", "1000.00", job_id="J1"), inv("I2", "1000.00", job_id="J2")],
        payments=[pay("P1", "I1", "400.00"), pay("P2", "I2", "1250.00")],
    )
    by_subject = {f["subject"]: (f["code"], f["exposure_usd"]) for f in r["findings"]}
    assert by_subject == {"I1": ("PARTIAL_PAYMENT", "600.00"), "I2": ("OVERPAYMENT", "250.00")}
    assert money(r)["identified_exposure_usd"] == "850.00"
    assert money(r)["potential_overbilling_usd"] == "0.00"


def test_payment_applied_to_wrong_invoice_is_flagged_on_both_invoices() -> None:
    # I1 got 500 too much and I2 is 500 short. The engine cannot prove it is one misapplication,
    # so both are reported UNVERIFIED (1000.00 total). LIMITATION: not netted across invoices.
    r = run(
        jobs=[job("J1"), job("J2")],
        rates=[rate(amount="1000.00")],
        invoices=[inv("I1", "1000.00", job_id="J1"), inv("I2", "1000.00", job_id="J2")],
        payments=[pay("P1", "I1", "1500.00"), pay("P2", "I2", "500.00")],
    )
    assert codes(r) == ["OVERPAYMENT", "PARTIAL_PAYMENT"]
    assert money(r)["unverified_exposure_usd"] == "1000.00"
    assert money(r)["potential_overbilling_usd"] == "0.00"
    assert money(r)["potential_underbilling_usd"] == "0.00"


def test_unapplied_cash_is_unverified_exposure_not_recovery() -> None:
    r = run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "4000.00", "paid")], payments=[pay("P1", "I1", "4000.00"), pay("P9", "NOPE", "700.00")])
    assert [f["code"] for f in r["findings"] if f["subject"] == "P9"] == ["ORPHAN_PAYMENT"]
    assert money(r)["unverified_exposure_usd"] == "700.00"
    assert money(r)["confirmed_recovery_usd"] == "0.00"


def test_overlapping_contract_revisions_are_ambiguous_and_book_nothing() -> None:
    r = run(
        jobs=[job()],
        rates=[rate("R1", "4000.00"), rate("R2", "4200.00", start="2026-02-01")],
        invoices=[inv("I1", "5000.00")],
    )
    assert codes(r) == ["AMBIGUOUS_RATE"]
    assert money(r)["identified_exposure_usd"] == "0.00"


def test_missing_contract_never_invents_an_expected_amount() -> None:
    r = run(jobs=[job()], invoices=[inv("I1", "5000.00")])
    assert codes(r) == ["RATE_UNVERIFIED"]
    assert money(r)["identified_exposure_usd"] == "0.00"


def test_unbilled_job_without_a_unique_rate_is_not_valued() -> None:
    assert money(run(jobs=[job()]))["potential_underbilling_usd"] == "0.00"
    two = run(jobs=[job()], rates=[rate("R1"), rate("R2", "4100.00")])
    assert money(two)["potential_underbilling_usd"] == "0.00"
    one = run(jobs=[job()], rates=[rate()])
    assert money(one)["potential_underbilling_usd"] == "4000.00"


def test_orphan_invoice_that_is_also_paid_wrong_is_not_double_counted() -> None:
    r = run(invoices=[inv("I1", "900.00", "paid", job_id="GHOST")], payments=[pay("P1", "I1", "100.00")])
    assert money(r)["identified_exposure_usd"] == "900.00"


@pytest.mark.parametrize("bad", ["-5.00", "NaN", "Infinity", "-Infinity", "1e5", "5.001", "", "1,000.00", "$5.00", " "])
def test_invalid_amounts_are_rejected_not_coerced(bad: str) -> None:
    with pytest.raises(InvalidSnapshot):
        run(jobs=[job()], rates=[rate()], invoices=[inv("I1", bad)])
    with pytest.raises(InvalidSnapshot):
        run(jobs=[job()], rates=[rate(amount=bad)], invoices=[inv("I1", "1.00")])
    with pytest.raises(InvalidSnapshot):
        run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "1.00")], payments=[pay("P1", "I1", bad)])


def test_reversals_cannot_be_expressed_as_negative_payments() -> None:
    # Reversals are NOT_VERIFIED as a feature: a negative payment fails closed.
    with pytest.raises(InvalidSnapshot):
        run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "100.00")], payments=[pay("P1", "I1", "-100.00")])


def test_non_string_numbers_are_rejected() -> None:
    bad = inv("I1", "1.00")
    bad["amount"] = 5000  # type: ignore[assignment]
    with pytest.raises(InvalidSnapshot):
        run(jobs=[job()], rates=[rate()], invoices=[bad])


def test_identical_amounts_across_tenants_are_isolated() -> None:
    tables = {"jobs": [job()], "rates": [rate()], "invoices": [inv("I1", "5000.00")]}
    a, b = run("T-A", **tables), run("T-B", **tables)
    assert money(a)["identified_exposure_usd"] == money(b)["identified_exposure_usd"] == "1000.00"
    assert a["tenant_id"] == "T-A" and b["tenant_id"] == "T-B"
    assert a["receipt_sha256"] != b["receipt_sha256"]
    with pytest.raises(InvalidSnapshot):
        RevenueLeakageEngine("T-B").reconcile_records({"dataset_type": "SYNTHETIC_ONLY", "tenant_id": "T-A", **{k: [] for k in ("jobs", "rates", "invoices", "payments")}})


def test_confirmed_recovery_is_never_produced_by_reconciliation() -> None:
    r = run(jobs=[job()], rates=[rate()], invoices=[inv("I1", "5000.00", "paid")], payments=[pay("P1", "I1", "5000.00")])
    assert money(r)["confirmed_recovery_usd"] == "0.00"
    assert money(r)["human_confirmed_discrepancy_usd"] == "0.00"
    assert r["authority_state"] == "HOLD"


def _graph(tenant: str = "T-A") -> EvidenceGraph:
    now = datetime.now(UTC)
    mk = lambda eid, system: EvidenceRecord(eid, tenant, system, eid, "a" * 64, now)  # noqa: E731
    return EvidenceGraph(tenant, [mk("claim-src", "erp"), mk("bank-1", "bank"), mk("erp-copy", "erp")])


def _claim_at_approved(graph: EvidenceGraph) -> RecoveryClaim:
    claim = RecoveryClaim("T-A", "OB-1", Decimal("1000.00"))
    claim.advance(Outcome.VERIFIED_DISCREPANCY, actor=ActorKind.SYSTEM, evidence_ids=("claim-src", "bank-1"), graph=graph)
    claim.advance(Outcome.SUBMITTED_CLAIM, actor=ActorKind.HUMAN, evidence_ids=("claim-src",), graph=graph, reviewer="r.chen")
    claim.advance(Outcome.APPROVED_CLAIM, actor=ActorKind.HUMAN, evidence_ids=("claim-src",), graph=graph, reviewer="r.chen")
    return claim


def test_unsupported_recovery_confirmation_is_refused() -> None:
    g = _graph()
    claim = _claim_at_approved(g)
    confirm = dict(target=Outcome.CONFIRMED_RECOVERED, graph=g)
    # Payment evidence shares the claim's own root.
    with pytest.raises(QualificationError):
        claim.advance(evidence_ids=("erp-copy",), actor=ActorKind.HUMAN, reviewer="r.chen", received_amount=Decimal("1000.00"), claim_source_ids=("erp-copy",), **confirm)  # type: ignore[arg-type]
    # Over-receipt, zero, non-finite, model actor, and anonymous reviewer.
    for amount in (Decimal("1000.01"), Decimal("0"), Decimal("NaN"), Decimal("-1")):
        with pytest.raises(QualificationError):
            claim.advance(evidence_ids=("bank-1",), actor=ActorKind.HUMAN, reviewer="r.chen", received_amount=amount, claim_source_ids=("claim-src",), **confirm)  # type: ignore[arg-type]
    with pytest.raises(QualificationError):
        claim.advance(evidence_ids=("bank-1",), actor=ActorKind.MODEL, reviewer="r.chen", received_amount=Decimal("1.00"), claim_source_ids=("claim-src",), **confirm)  # type: ignore[arg-type]
    with pytest.raises(QualificationError):
        claim.advance(evidence_ids=("bank-1",), actor=ActorKind.HUMAN, reviewer="  ", received_amount=Decimal("1.00"), claim_source_ids=("claim-src",), **confirm)  # type: ignore[arg-type]
    assert claim.recovered_amount == Decimal("0")
    assert claim.state is Outcome.APPROVED_CLAIM


def test_confirmed_recovery_needs_independent_payment_evidence_and_stays_bounded() -> None:
    g = _graph()
    claim = _claim_at_approved(g)
    claim.advance(Outcome.CONFIRMED_RECOVERED, actor=ActorKind.HUMAN, evidence_ids=("bank-1",), graph=g, reviewer="r.chen", received_amount=Decimal("400.00"), claim_source_ids=("claim-src",))
    assert claim.recovered_amount == Decimal("400.00")
    assert claim.recovered_amount <= claim.amount


def test_cross_tenant_graph_cannot_advance_a_claim() -> None:
    claim = RecoveryClaim("T-A", "OB-1", Decimal("10.00"))
    with pytest.raises(QualificationError):
        claim.advance(Outcome.VERIFIED_DISCREPANCY, actor=ActorKind.SYSTEM, evidence_ids=("x",), graph=_graph("T-B"))


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("Infinity")])
def test_claims_reject_non_positive_or_non_finite_amounts(amount: Decimal) -> None:
    with pytest.raises(QualificationError):
        RecoveryClaim("T-A", "OB-1", amount)
