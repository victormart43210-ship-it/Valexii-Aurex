"""DISPATER synthetic-only, deterministic revenue-audit prototype.

No I/O, no API routes, no model calls, no customer data authorization. This is
an illustrative control-plane contract, NOT tax advice, DOT compliance, or an
independent audit. Treat findings as candidates for human review.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

SCHEMA = "dispater.synthetic.revenue.v1"


class InvalidSnapshot(ValueError):
    """Reject a malformed or non-synthetic audit snapshot."""


def digest(value: object) -> str:
    """Hash a canonical JSON representation; NOT an independent signature."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _rows(snapshot: dict[str, Any], key: str, required: set[str]) -> list[dict[str, Any]]:
    value = snapshot.get(key)
    if not isinstance(value, list):
        raise InvalidSnapshot(f"{key}: expected list")
    if len(value) > 1000:
        raise InvalidSnapshot(f"{key}: demo bound exceeded")
    for row in value:
        if not isinstance(row, dict) or set(row) != required:
            raise InvalidSnapshot(f"{key}: exact mandatory fields required")
        if not all(isinstance(row[field], str) and row[field] for field in required):
            raise InvalidSnapshot(f"{key}: mandatory fields must be nonempty strings")
    return value


def _unique(rows: list[dict[str, Any]], id_key: str) -> None:
    ids = [row[id_key] for row in rows]
    if len(ids) != len(set(ids)):
        raise InvalidSnapshot(f"duplicate {id_key}")


def _money(value: str) -> Decimal:
    if not re.fullmatch(r"[0-9]{1,9}(?:\.[0-9]{1,2})?", value):
        raise InvalidSnapshot("invalid nonnegative USD amount")
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise InvalidSnapshot("invalid amount") from exc
    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal("0.01")):
        raise InvalidSnapshot("amount must be nonnegative and have at most two decimal places")
    return amount


def _date(value: str) -> date:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise InvalidSnapshot("date must use ISO YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidSnapshot("invalid date") from exc


def audit_synthetic(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compare synthetic jobs, invoices, rate cards, and payments without writes.

    Rate gaps/ambiguity are UNKNOWN, never interpreted as an approved rate.
    Money amounts are per-job fixed rates for this first contract, not hourly.
    """
    if snapshot.get("dataset_type") != "SYNTHETIC_ONLY":
        raise InvalidSnapshot("only explicitly labeled synthetic examples are supported")
    jobs = _rows(snapshot, "jobs", {"job_id", "customer_id", "service_code", "date"})
    invoices = _rows(snapshot, "invoices", {"invoice_id", "job_id", "amount", "status"})
    payments = _rows(snapshot, "payments", {"payment_id", "invoice_id", "amount"})
    rates = _rows(snapshot, "rates", {"rate_id", "customer_id", "service_code", "start", "end", "amount"})
    for rows, key in ((jobs, "job_id"), (invoices, "invoice_id"), (payments, "payment_id"), (rates, "rate_id")):
        _unique(rows, key)
    if any(row["status"] not in ("open", "paid") for row in invoices):
        raise InvalidSnapshot("invalid invoice status")
    for row in jobs:
        _date(row["date"])
    for row in rates:
        if _date(row["end"]) < _date(row["start"]):
            raise InvalidSnapshot("rate end precedes rate start")
        _money(row["amount"])
    for row in invoices + payments:
        _money(row["amount"])

    by_job: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for invoice in invoices:
        by_job[invoice["job_id"]].append(invoice)
    by_invoice: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for payment in payments:
        by_invoice[payment["invoice_id"]].append(payment)

    findings: list[dict[str, Any]] = []

    def add(code: str, subject: str, source: list[tuple[str, dict[str, Any]]], detail: str, delta: Decimal | None = None) -> None:
        row_proof = [{"kind": kind, "sha256": digest(row)} for kind, row in source]
        finding: dict[str, Any] = {
            "code": code,
            "subject": subject,
            "detail": detail,
            "evidence": row_proof,
            "authority": "HUMAN_REVIEW_REQUIRED",
        }
        if delta is not None:
            finding["difference_usd"] = str(delta)
        findings.append(finding)

    job_ids = {row["job_id"] for row in jobs}
    invoice_ids = {row["invoice_id"] for row in invoices}
    for job in jobs:
        relevant = by_job[job["job_id"]]
        if not relevant:
            add("UNBILLED_JOB", job["job_id"], [("job", job)], "Completed job has no invoice in supplied snapshot")
        if len(relevant) > 1:
            add("MULTIPLE_INVOICES", job["job_id"], [("job", job)] + [("invoice", inv) for inv in relevant], "Multiple invoices reference this job; review before treating as duplicate")
        active = [
            rate for rate in rates
            if rate["customer_id"] == job["customer_id"]
            and rate["service_code"] == job["service_code"]
            and _date(rate["start"]) <= _date(job["date"]) <= _date(rate["end"])
        ]
        if len(active) != 1:
            add("RATE_UNVERIFIED", job["job_id"], [("job", job)] + [("rate", rate) for rate in active], "Exactly one effective rate was not established")
        elif len(relevant) == 1:
            rate = active[0]
            invoice = relevant[0]
            billed = _money(invoice["amount"])
            expected = _money(rate["amount"])
            if billed != expected:
                add("RATE_MISMATCH", invoice["invoice_id"], [("job", job), ("invoice", invoice), ("rate", rate)], "Invoice amount differs from uniquely applicable synthetic rate", billed - expected)

    for invoice in invoices:
        if invoice["job_id"] not in job_ids:
            add("ORPHAN_INVOICE", invoice["invoice_id"], [("invoice", invoice)], "Referenced job is missing from supplied snapshot")
        if invoice["status"] == "paid":
            total = sum((_money(p["amount"]) for p in by_invoice[invoice["invoice_id"]]), Decimal("0.00"))
            amount = _money(invoice["amount"])
            if total != amount:
                add("PAID_STATUS_UNRECONCILED", invoice["invoice_id"], [("invoice", invoice)] + [("payment", p) for p in by_invoice[invoice["invoice_id"]]], "Paid-marked invoice does not reconcile to supplied payment allocations", total - amount)
    for payment in payments:
        if payment["invoice_id"] not in invoice_ids:
            add("ORPHAN_PAYMENT", payment["payment_id"], [("payment", payment)], "Payment references an absent invoice")

    findings.sort(key=lambda row: (row["code"], row["subject"]))
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "dataset_sha256": digest(snapshot),
        "status": "HOLD",
        "independent_verification": "NOT VERIFIED",
        "scope": "FICTIONAL DATA ONLY; SOURCE-SNAPSHOT MATCHING ONLY",
        "counts": {"jobs": len(jobs), "invoices": len(invoices), "payments": len(payments), "findings": len(findings)},
        "findings": findings,
        "limits": "Missing records are unknown, not proof of a violation. No tax/DOT decisions, writeback, recovery estimates or customer-data admission.",
    }
    report["self_issued_receipt_sha256"] = digest(report)
    return report


def verify_self_issued_report(snapshot: dict[str, Any], report: dict[str, Any]) -> bool:
    """Byte-equivalent consistency check; cannot attest to independent truth."""
    return audit_synthetic(snapshot) == report
