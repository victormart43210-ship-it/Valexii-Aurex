"""
AUREX DISPATER Commercial Pilot Engine & Historical Revenue Audit Prototype.

Manages synthetic customer onboarding, read-only operational data ingestion,
multi-record reconciliation, equipment downtime tracking, XAELI 5-step explanations,
human review queues, and historical deterministic audit checks.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel

from aurex.dispater_intelligence import (
    MaintenanceRecord,
    RevenueLeakageEngine,
    Xaeli5StepFinding,
)

SCHEMA = "dispater.synthetic.revenue.v1"


class InvalidSnapshot(ValueError):
    """Reject a malformed or non-synthetic audit snapshot."""


def digest(value: object) -> str:
    """Hash a canonical JSON representation; NOT an independent signature."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _compute_sha256(payload: Any) -> str:
    """Compute deterministic SHA-256 digest of dict/list/model."""
    if isinstance(payload, BaseModel):
        data_str = payload.model_dump_json()
    elif isinstance(payload, (dict, list)):
        data_str = json.dumps(payload, sort_keys=True, default=str)
    else:
        data_str = str(payload)
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


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
    """Compare synthetic jobs, invoices, rate cards, and payments without writes."""
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


# --- Commercial Pilot Engine Models ---

def sanitize_csv_formula_injection(text: str) -> str:
    """Sanitizes text against CSV formula injection attacks (=, +, -, @, tab, CR)."""
    if not isinstance(text, str):
        return str(text)
    cleaned = text.strip()
    if cleaned and cleaned[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + cleaned
    return cleaned


class PilotDataRetentionPolicy(BaseModel):
    tenant_id: str
    retention_days: int = 90
    auto_delete_on_expiry: bool = True
    authorized_deletion_requested: bool = False
    data_deleted_at: str | None = None


class PilotTenantConfig(BaseModel):
    tenant_id: str
    company_name: str
    industry_sector: str  # Oilfield Operations or Towing & Recovery
    onboarded_at: str
    active: bool = True
    authorized_human_approver: str


class PilotIngestionBatch(BaseModel):
    batch_id: str
    tenant_id: str
    ingested_at: str
    field_tickets_count: int
    purchase_orders_count: int
    invoices_count: int
    rate_sheets_count: int
    equipment_records_count: int
    batch_digest: str


class HumanReviewDecision(BaseModel):
    decision_id: str
    tenant_id: str
    exception_id: str
    review_status: str  # PENDING_REVIEW, APPROVED_CORRECTION, DISPUTED, DISMISSED
    reviewer_identity: str
    reviewed_at: str
    notes: str
    approved_adjustment_usd: float = 0.0
    actual_recovered_usd: float = 0.0


class CommercialPilotSummary(BaseModel):
    tenant_id: str
    company_name: str
    batch_id: str
    evaluated_revenue_usd: float
    potential_exposure_usd: float
    confirmed_discrepancies_usd: float
    customer_approved_corrections_usd: float
    actual_recovered_revenue_usd: float
    exceptions_count: int
    xaeli_findings: list[Xaeli5StepFinding]
    fleet_records: list[MaintenanceRecord]
    pending_human_reviews_count: int
    audit_event_ref: str


class CommercialPilotEngine:
    def __init__(self, tenant_config: PilotTenantConfig) -> None:
        self.config = tenant_config
        self.review_decisions: dict[str, HumanReviewDecision] = {}

    def process_ingestion_batch(
        self,
        batch_id: str,
        ingested_at: str,
        field_tickets: list[dict[str, Any]],
        invoices: list[dict[str, Any]],
        purchase_orders: list[dict[str, Any]],
        rate_sheets: list[dict[str, Any]],
        fleet_data: list[dict[str, Any]],
    ) -> CommercialPilotSummary:
        """Executes read-only reconciliation and fleet maintenance analysis for a pilot batch."""
        batch_payload = {
            "batch_id": batch_id,
            "tenant_id": self.config.tenant_id,
            "ft_count": len(field_tickets),
            "po_count": len(purchase_orders),
            "inv_count": len(invoices),
        }
        _compute_sha256(batch_payload)

        # 1. Run Revenue Leakage Detection Engine
        exceptions = RevenueLeakageEngine.evaluate_records(
            tenant_id=self.config.tenant_id,
            field_tickets=field_tickets,
            invoices=invoices,
            purchase_orders=purchase_orders,
            rate_sheets=rate_sheets,
            is_demo=True,
        )

        # 2. Convert to XAELI 5-Step Findings
        xaeli_findings = RevenueLeakageEngine.convert_to_xaeli_findings(exceptions)

        # 3. Evaluate Fleet Maintenance
        from aurex.dispater_intelligence import FleetMaintenanceEngine
        fleet_records = FleetMaintenanceEngine.evaluate_fleet(
            tenant_id=self.config.tenant_id,
            fleet_data=fleet_data,
            is_demo=True,
        )

        evaluated_revenue = sum(float(ft.get("total_amount", 0.0)) for ft in field_tickets)
        potential_exposure = sum(e.financial_exposure for e in exceptions)

        confirmed_discrepancies = 0.0
        approved_corrections = 0.0
        actual_recovered = 0.0
        pending_count = 0

        for exc in exceptions:
            dec = self.review_decisions.get(exc.exception_id)
            if dec:
                if dec.review_status in ("APPROVED_CORRECTION", "DISPUTED"):
                    confirmed_discrepancies += exc.financial_exposure
                if dec.review_status == "APPROVED_CORRECTION":
                    approved_corrections += dec.approved_adjustment_usd
                    actual_recovered += dec.actual_recovered_usd
                if dec.review_status == "PENDING_REVIEW":
                    pending_count += 1
            else:
                pending_count += 1

        return CommercialPilotSummary(
            tenant_id=self.config.tenant_id,
            company_name=self.config.company_name,
            batch_id=batch_id,
            evaluated_revenue_usd=round(evaluated_revenue, 2),
            potential_exposure_usd=round(potential_exposure, 2),
            confirmed_discrepancies_usd=round(confirmed_discrepancies, 2),
            customer_approved_corrections_usd=round(approved_corrections, 2),
            actual_recovered_revenue_usd=round(actual_recovered, 2),
            exceptions_count=len(exceptions),
            xaeli_findings=xaeli_findings,
            fleet_records=fleet_records,
            pending_human_reviews_count=pending_count,
            audit_event_ref=f"PILOT-AUDIT-{batch_id}",
        )

    def purge_tenant_data(self, requested_by: str) -> dict[str, Any]:
        """Executes authorized data deletion for customer offboarding / retention policy."""
        if requested_by != self.config.authorized_human_approver:
            raise ValueError("Unauthorized data deletion request.")
        self.review_decisions.clear()
        return {
            "tenant_id": self.config.tenant_id,
            "status": "DATA_PURGED_SUCCESSFULLY",
            "purged_by": requested_by,
        }

    def record_human_decision(self, decision: HumanReviewDecision) -> None:
        """Records a human manager review decision in the pilot queue."""
        if decision.tenant_id != self.config.tenant_id:
            raise ValueError("Tenant isolation error: decision tenant mismatch.")
        self.review_decisions[decision.exception_id] = decision
