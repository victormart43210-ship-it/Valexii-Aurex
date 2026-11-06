"""Convergence checks that do not import the production totals as their expected answers."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from aurex import dispater_store
from aurex.dispater_intelligence import (
    InvalidSnapshot,
    RevenueLeakageEngine,
    dependent_finding_ids,
    digest,
    verify_receipt,
)
from aurex.dispater_monitor import persist_increment
from aurex.evidence_kernel import EvidenceGraph, EvidenceRecord


def _base(**over: object) -> dict:
    dataset = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-01-15"},
            {"job_id": "J2", "customer_id": "C1", "service_code": "S", "date": "2026-04-15"},
        ],
        "rates": [
            {
                "rate_id": "R-OLD",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            },
            {
                "rate_id": "R-NEW",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2026-03-01",
                "end": "2026-12-31",
                "amount": "80.00",
                "supersedes": "R-OLD",
            },
        ],
        "invoices": [
            {"invoice_id": "I1", "job_id": "J1", "amount": "90.00", "status": "open"},
            {"invoice_id": "I2", "job_id": "J2", "amount": "100.00", "status": "open"},
        ],
        "payments": [],
    }
    dataset.update(over)
    return dataset


def test_misapplied_payment_is_counted_once() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
            "rates": [
                {
                    "rate_id": "R1",
                    "customer_id": "C1",
                    "service_code": "S",
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "amount": "100.00",
                }
            ],
            "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "paid"}],
            "payments": [
                {"payment_id": "P1", "invoice_id": "I1", "amount": "100.00", "job_id": "OTHER"}
            ],
        }
    )
    # The $100 is the wrong-job cash. It is not also a paid-status gap.
    assert report["financial_summary"]["identified_exposure_usd"] == "100.00"
    assert report["financial_summary"]["unverified_exposure_usd"] == "100.00"
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert {item["code"] for item in report["findings"]} == {"MISAPPLIED_PAYMENT"}


def test_misapplied_cash_does_not_add_a_second_dollar_event() -> None:
    """A rate gap already holds the invoice. The wrong-job payment is recorded at zero dollars."""
    report = RevenueLeakageEngine("tenant-a").reconcile_records(
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
            "rates": [
                {
                    "rate_id": "R1",
                    "customer_id": "C1",
                    "service_code": "S",
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "amount": "100.00",
                }
            ],
            "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "150.00", "status": "open"}],
            "payments": [{"payment_id": "P1", "invoice_id": "I1", "amount": "40.00", "job_id": "OTHER"}],
        }
    )
    summary = report["financial_summary"]
    assert summary["potential_overbilling_usd"] == "50.00"
    assert summary["identified_exposure_usd"] == "50.00"
    assert summary["confirmed_recovery_usd"] == "0.00"
    misapplied = next(item for item in report["findings"] if item["code"] == "MISAPPLIED_PAYMENT")
    assert misapplied["exposure_usd"] == "0.00"


def test_duplicate_invoice_does_not_book_a_misapplied_payment() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
            "rates": [
                {
                    "rate_id": "R1",
                    "customer_id": "C1",
                    "service_code": "S",
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "amount": "100.00",
                }
            ],
            "invoices": [
                {"invoice_id": "I1A", "job_id": "J1", "amount": "100.00", "status": "open"},
                {"invoice_id": "I1B", "job_id": "J1", "amount": "100.00", "status": "open"},
            ],
            "payments": [{"payment_id": "P1", "invoice_id": "I1A", "amount": "100.00", "job_id": "OTHER"}],
        }
    )
    summary = report["financial_summary"]
    assert summary["identified_exposure_usd"] == "0.00"
    assert summary["withheld_unresolved_usd"] == "200.00"
    assert summary["confirmed_recovery_usd"] == "0.00"


def test_orphan_reversal_is_not_incoming_cash() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [],
            "rates": [],
            "invoices": [],
            "payments": [
                {"payment_id": "P1", "invoice_id": "MISSING", "amount": "100.00", "kind": "REVERSAL"}
            ],
        }
    )
    assert report["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert report["findings"][0]["code"] == "ORPHAN_PAYMENT"
    assert report["findings"][0]["exposure_usd"] == "0.00"


def test_one_unbilled_job_and_one_orphan_invoice_are_withheld() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
            "rates": [
                {
                    "rate_id": "R1",
                    "customer_id": "C1",
                    "service_code": "S",
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "amount": "100.00",
                }
            ],
            "invoices": [{"invoice_id": "I9", "job_id": "MISSING", "amount": "100.00", "status": "open"}],
            "payments": [],
        }
    )
    summary = report["financial_summary"]
    assert summary["identified_exposure_usd"] == "0.00"
    assert summary["withheld_unresolved_usd"] == "200.00"
    assert summary["confirmed_recovery_usd"] == "0.00"
    assert {item["exposure_usd"] for item in report["findings"]} == {"0.00"}


def test_unkeyed_hash_is_not_a_signature() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(_base())
    body = {key: value for key, value in report.items() if key != "receipt_sha256"}
    report["receipt_sha256"] = digest(body)
    assert verify_receipt(report)
    report["receipt_auth"] = {"alg": "HMAC-SHA256", "kid": "test-k1", "v": 2}
    report["receipt_mac"] = "ab" * 32
    assert verify_receipt(report) is False


def test_successor_rate_does_not_invalidate_an_unrelated_period() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(_base())
    summary = report["financial_summary"]
    # January invoice 90 vs the still-active $100 rate is $10 underbilling.
    # April invoice 100 vs the $80 successor is $20 overbilling.
    assert summary["potential_underbilling_usd"] == "10.00"
    assert summary["potential_overbilling_usd"] == "20.00"
    assert summary["identified_exposure_usd"] == "30.00"
    assert summary["withheld_unresolved_usd"] == "0.00"
    old_rate = _base()["rates"][0]
    linked = dependent_finding_ids(report, old_rate)
    assert "FND-RATE_MISMATCH-I1" in linked
    assert "FND-RATE_MISMATCH-I2" not in linked


def test_duplicate_field_ticket_and_unpriced_overtime_withhold_dollars() -> None:
    duplicate = RevenueLeakageEngine("tenant-a").reconcile_records(
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "EQ", "date": "2026-03-01"}],
            "rates": [
                {
                    "rate_id": "R1",
                    "customer_id": "C1",
                    "service_code": "EQ",
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "amount": "25.00",
                    "unit": "HOUR",
                }
            ],
            "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "400.00", "status": "open"}],
            "payments": [],
            "equipment": [
                {
                    "ticket_id": "T1",
                    "job_id": "J1",
                    "equipment_id": "PUMP-1",
                    "service_date": "2026-03-01",
                    "billable_hours": "8.00",
                    "standby_hours": "0.00",
                    "invoiced_hours": "8.00",
                },
                {
                    "ticket_id": "T2",
                    "job_id": "J1",
                    "equipment_id": "PUMP-1",
                    "service_date": "2026-03-01",
                    "billable_hours": "8.00",
                    "standby_hours": "0.00",
                    "invoiced_hours": "8.00",
                },
            ],
        }
    )
    assert duplicate["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert duplicate["findings"][0]["code"] == "DUPLICATE_FIELD_TICKET"
    overtime = RevenueLeakageEngine("tenant-a").reconcile_records(
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "EQ", "date": "2026-03-01"}],
            "rates": [
                {
                    "rate_id": "R1",
                    "customer_id": "C1",
                    "service_code": "EQ",
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "amount": "25.00",
                    "unit": "HOUR",
                }
            ],
            "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "open"}],
            "payments": [],
            "labor": [
                {
                    "record_id": "L1",
                    "job_id": "J1",
                    "role": "operator",
                    "service_date": "2026-03-01",
                    "approved_hours": "4.00",
                    "billed_hours": "4.00",
                    "overtime_hours": "2.00",
                }
            ],
        }
    )
    # 4.00 * 25.00 = 100.00, which matches the invoice. The 2 overtime hours are not priced.
    assert overtime["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert overtime["findings"][0]["code"] == "OVERTIME_UNPRICED"
    assert Decimal("4.00") * Decimal("25.00") == Decimal("100.00")


def test_same_document_is_one_evidence_root() -> None:
    now = datetime(2026, 11, 6, tzinfo=UTC)
    graph = EvidenceGraph(
        "tenant-a",
        [
            EvidenceRecord("pdf", "tenant-a", "doc", "1", "a" * 64, now),
            EvidenceRecord("ocr", "tenant-a", "doc", "1-ocr", "b" * 64, now, parents=("pdf",)),
            EvidenceRecord("row", "tenant-a", "db", "1", "c" * 64, now, parents=("ocr",)),
        ],
    )
    assert graph.independent_root_count(["pdf", "ocr", "row"]) == 1


def test_monitor_chain_survives_reconnect_and_rejects_a_reused_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "chain.db"))
    baseline = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-01-01"}],
        "rates": [
            {
                "rate_id": "R1",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            }
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "paid"}],
        "payments": [{"payment_id": "P1", "invoice_id": "I1", "amount": "100.00"}],
    }
    month_37 = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [],
        "rates": [],
        "invoices": [{"invoice_id": "I37", "job_id": "MISSING", "amount": "15.00", "status": "open"}],
        "payments": [],
    }
    first, created = persist_increment("tenant-a", baseline, month_37, "ab" * 32)
    assert created and first["payload"]["actor"] == "SYSTEM"
    assert first["payload"]["confirmed_recovery_usd"] == "0.00"
    assert dispater_store.verify_monitor_chain("tenant-a")
    listed = dispater_store.list_monitor_events("tenant-a")
    assert len(listed) == 1
    conflict = {
        **month_37,
        "invoices": [{"invoice_id": "I37", "job_id": "MISSING", "amount": "99.00", "status": "open"}],
    }
    with pytest.raises(InvalidSnapshot, match="conflicting source"):
        persist_increment("tenant-a", baseline, conflict, "ab" * 32)
    conn = sqlite3.connect(tmp_path / "chain.db")
    conn.execute("UPDATE dispater_monitor_events SET entry_sha256=?", ("f" * 64,))
    conn.commit()
    conn.close()
    assert dispater_store.verify_monitor_chain("tenant-a") is False
