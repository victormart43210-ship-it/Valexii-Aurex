"""DISPATER Industrial Revenue Intelligence & Audit Reconciliation Engine.

Implements deterministic, decimal-safe operational revenue reconciliation,
equipment ticket matching, approved rate schedule verification, SHA-256 evidence
digest generation, CSV formula-injection defenses, canonical 5-step XAELI findings
(NOW -> CHANGED -> NEXT -> WHY -> PROOF), and durable SQLite storage for multi-tenant
audit isolation.

NON-DELEGABLE CONSTRAINTS:
- No automatic billing, payment execution, invoice modification, or customer account changes.
- All detected discrepancies are candidates for human review (HUMAN_REVIEW_REQUIRED).
- Potential exposure is strictly categorized (underbilling, overbilling, unverified exposure).
- Confirmed recovery remains permanently 0.00 without external financial evidence.
- The system may never be its own sole witness.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from collections import defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

SCHEMA = "dispater.synthetic.revenue_intelligence.v2"
DEFAULT_DISPATER_DB = os.environ.get("DISPATER_DB_PATH", "/tmp/dispater_audit.db")


class InvalidSnapshot(ValueError):
    """Reject a malformed, invalid, or non-synthetic audit payload."""


class TenantAuthorizationError(PermissionError):
    """Reject an unauthorized cross-tenant audit access attempt."""


def digest(value: object) -> str:
    """Compute deterministic SHA-256 hash of a JSON-serializable object."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def sanitize_formula_field(val: str) -> str:
    """Neutralize spreadsheet formula injection characters (=, +, -, @, tab, CR)."""
    if not val:
        return val
    if val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + val
    return val


def parse_money(value: str) -> Decimal:
    """Parse nonnegative 2-decimal USD currency amount securely."""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,9}(?:\.[0-9]{1,2})?", value):
        raise InvalidSnapshot(f"invalid nonnegative USD amount: {value!r}")
    try:
        amt = Decimal(value)
        return amt.quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError) as exc:
        raise InvalidSnapshot(f"invalid decimal amount: {value!r}") from exc


def parse_date(value: str) -> date:
    """Parse ISO YYYY-MM-DD date."""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise InvalidSnapshot(f"date must be ISO YYYY-MM-DD: {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidSnapshot(f"invalid date value: {value!r}") from exc


def _validate_rows(
    payload: dict[str, Any], key: str, required_fields: set[str], max_rows: int = 2000
) -> list[dict[str, Any]]:
    rows = payload.get(key)
    if not isinstance(rows, list):
        raise InvalidSnapshot(f"'{key}' must be a list of records")
    if len(rows) > max_rows:
        raise InvalidSnapshot(f"'{key}' exceeds record limit of {max_rows}")
    cleaned_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise InvalidSnapshot(f"'{key}[{idx}]' must be an object")
        missing = required_fields - set(row.keys())
        if missing:
            raise InvalidSnapshot(f"'{key}[{idx}]' missing required fields: {sorted(missing)}")
        cleaned: dict[str, Any] = {}
        for k, v in row.items():
            if not isinstance(v, str):
                raise InvalidSnapshot(f"'{key}[{idx}].{k}' must be a string")
            cleaned[k] = sanitize_formula_field(v.strip())
        cleaned_rows.append(cleaned)
    return cleaned_rows


def _ensure_unique_ids(rows: list[dict[str, Any]], id_key: str, context: str) -> None:
    seen: set[str] = set()
    for row in rows:
        val = row.get(id_key, "")
        if not val:
            raise InvalidSnapshot(f"{context}: '{id_key}' must not be empty")
        if val in seen:
            raise InvalidSnapshot(f"{context}: duplicate identifier '{val}' detected")
        seen.add(val)


# ---------------------------------------------------------------------------
# Durable SQLite Audit Storage
# ---------------------------------------------------------------------------


def get_dispater_db(db_path: str = DEFAULT_DISPATER_DB) -> sqlite3.Connection:
    """Initialize and return a SQLite connection for durable audit records."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dispater_audit_runs (
                run_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                dataset_sha256 TEXT NOT NULL,
                receipt_sha256 TEXT NOT NULL,
                status TEXT NOT NULL,
                report_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_dispater_tenant_time
            ON dispater_audit_runs(tenant_id, created_at DESC)
            """
        )
    return conn


def save_audit_run(report: dict[str, Any], db_path: str = DEFAULT_DISPATER_DB) -> None:
    """Atomically store an audit reconciliation report in durable SQLite."""
    run_id = report.get("run_id") or f"RUN-{digest(report)[:16]}"
    report["run_id"] = run_id
    tenant_id = report["tenant_id"]
    dataset_sha256 = report["dataset_sha256"]
    receipt_sha256 = report["receipt_sha256"]
    status = report["status"]
    report_json = json.dumps(report, sort_keys=True)
    created_at = datetime.now(UTC).isoformat()

    conn = get_dispater_db(db_path)
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO dispater_audit_runs (
                run_id, tenant_id, dataset_sha256, receipt_sha256, status, report_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, tenant_id, dataset_sha256, receipt_sha256, status, report_json, created_at),
        )
    conn.close()


def get_latest_audit_run(tenant_id: str, db_path: str = DEFAULT_DISPATER_DB) -> dict[str, Any] | None:
    """Retrieve the latest durable audit run for a specific tenant."""
    conn = get_dispater_db(db_path)
    cursor = conn.execute(
        """
        SELECT report_json FROM dispater_audit_runs
        WHERE tenant_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (tenant_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return json.loads(row["report_json"])  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Revenue Leakage Engine
# ---------------------------------------------------------------------------


class RevenueLeakageEngine:
    """Deterministic Revenue Leakage and Billing Exception Audit Engine."""

    def __init__(self, tenant_id: str = "default", db_path: str = DEFAULT_DISPATER_DB):
        self.tenant_id = tenant_id
        self.db_path = db_path

    def reconcile_records(self, dataset: dict[str, Any]) -> dict[str, Any]:
        """Reconcile jobs, invoices, approved rates, and payments deterministically."""
        if not isinstance(dataset, dict):
            raise InvalidSnapshot("Dataset must be a JSON object")

        if dataset.get("dataset_type") != "SYNTHETIC_ONLY":
            raise InvalidSnapshot("Only explicitly labeled SYNTHETIC_ONLY datasets are admitted")

        dataset_tenant = dataset.get("tenant_id", "default")
        if dataset_tenant != self.tenant_id:
            raise TenantAuthorizationError(
                f"Tenant isolation mismatch: dataset tenant '{dataset_tenant}' != engine tenant '{self.tenant_id}'"
            )

        jobs = _validate_rows(
            dataset,
            "jobs",
            {"job_id", "customer_id", "service_code", "date"},
        )
        invoices = _validate_rows(
            dataset,
            "invoices",
            {"invoice_id", "job_id", "amount", "status"},
        )
        rates = _validate_rows(
            dataset,
            "rates",
            {"rate_id", "customer_id", "service_code", "start", "end", "amount"},
        )
        payments = _validate_rows(
            dataset,
            "payments",
            {"payment_id", "invoice_id", "amount"},
        )

        _ensure_unique_ids(jobs, "job_id", "jobs")
        _ensure_unique_ids(invoices, "invoice_id", "invoices")
        _ensure_unique_ids(rates, "rate_id", "rates")
        _ensure_unique_ids(payments, "payment_id", "payments")

        for inv in invoices:
            if inv["status"] not in ("open", "paid", "disputed"):
                raise InvalidSnapshot(f"Invalid invoice status: {inv['status']!r}")
            parse_money(inv["amount"])

        for j in jobs:
            parse_date(j["date"])
            # Validate operating hours if present
            if "hours" in j:
                try:
                    hrs = float(j["hours"])
                    if hrs < 0.0 or hrs > 168.0:
                        raise InvalidSnapshot(f"Invalid equipment hours: {j['hours']}")
                except ValueError as err:
                    raise InvalidSnapshot(f"Non-numeric equipment hours: {j['hours']}") from err

        for r in rates:
            s_date = parse_date(r["start"])
            e_date = parse_date(r["end"])
            if e_date < s_date:
                raise InvalidSnapshot(f"Rate end date precedes start date in rate {r['rate_id']}")
            parse_money(r["amount"])

        for p in payments:
            parse_money(p["amount"])

        by_job_invoices: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for inv in invoices:
            by_job_invoices[inv["job_id"]].append(inv)

        by_invoice_payments: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for p in payments:
            by_invoice_payments[p["invoice_id"]].append(p)

        findings: list[dict[str, Any]] = []

        potential_underbilling = Decimal("0.00")
        potential_overbilling = Decimal("0.00")
        unverified_exposure = Decimal("0.00")

        job_ids = {j["job_id"] for j in jobs}
        invoice_ids = {inv["invoice_id"] for inv in invoices}

        # 1. Job-level evaluation
        for job in jobs:
            j_id = job["job_id"]
            cust_id = job["customer_id"]
            svc = job["service_code"]
            j_date = parse_date(job["date"])
            relevant_invoices = by_job_invoices[j_id]

            # Unbilled ticket / job
            if not relevant_invoices:
                applicable_rates = [
                    r
                    for r in rates
                    if r["customer_id"] == cust_id
                    and r["service_code"] == svc
                    and parse_date(r["start"]) <= j_date <= parse_date(r["end"])
                ]
                potential_val = parse_money(applicable_rates[0]["amount"]) if len(applicable_rates) == 1 else Decimal("0.00")
                potential_underbilling += potential_val
                findings.append(
                    self._create_finding(
                        code="UNBILLED_JOB",
                        subject=j_id,
                        severity="HIGH",
                        records=[("job", job)],
                        exposure=potential_val,
                        exposure_kind="POTENTIAL_UNDERBILLING",
                        now=f"Completed job {j_id} has no invoice record in the snapshot.",
                        changed=f"Job marked executed on {job['date']} without a generated billing reference.",
                        next_action="Review field completion log and draft invoice according to agreed schedule.",
                        why="Uninvoiced field work results in immediate unbilled revenue leakage.",
                        proof=f"Job payload digest: {digest(job)}",
                    )
                )

            # Duplicate / Multiple invoices
            if len(relevant_invoices) > 1:
                dup_exposure = sum((parse_money(inv["amount"]) for inv in relevant_invoices[1:]), Decimal("0.00"))
                potential_overbilling += dup_exposure
                evidence_records = [("job", job)] + [("invoice", inv) for inv in relevant_invoices]
                findings.append(
                    self._create_finding(
                        code="MULTIPLE_INVOICES",
                        subject=j_id,
                        severity="CRITICAL",
                        records=evidence_records,
                        exposure=dup_exposure,
                        exposure_kind="POTENTIAL_OVERBILLING",
                        now=f"Job {j_id} is referenced by {len(relevant_invoices)} distinct invoices.",
                        changed=f"Multiple billing references issued for single work completion {j_id}.",
                        next_action="Quarantine secondary invoices and verify single legitimate charge with billing clerk.",
                        why="Duplicate invoices lead to customer disputes, reputational harm, and audit restatements.",
                        proof=f"Referenced invoice digests: {', '.join(digest(inv)[:16] for inv in relevant_invoices)}",
                    )
                )

            # Rate matching & reconciliation
            active_rates = [
                r
                for r in rates
                if r["customer_id"] == cust_id
                and r["service_code"] == svc
                and parse_date(r["start"]) <= j_date <= parse_date(r["end"])
            ]
            if len(active_rates) == 0:
                findings.append(
                    self._create_finding(
                        code="RATE_UNVERIFIED",
                        subject=j_id,
                        severity="MEDIUM",
                        records=[("job", job)],
                        exposure=Decimal("0.00"),
                        exposure_kind="UNVERIFIED_EXPOSURE",
                        now=f"No approved rate schedule found for job {j_id} ({cust_id}/{svc}).",
                        changed="Work scheduled and billed without active contractual rate schedule in ledger.",
                        next_action="Obtain counter-signed rate schedule or master services agreement amendment.",
                        why="Unapproved rates cannot be defended in contract verification or tax review.",
                        proof=f"Job record digest: {digest(job)}",
                    )
                )
            elif len(active_rates) > 1:
                evidence_records = [("job", job)] + [("rate", r) for r in active_rates]
                findings.append(
                    self._create_finding(
                        code="AMBIGUOUS_RATE",
                        subject=j_id,
                        severity="MEDIUM",
                        records=evidence_records,
                        exposure=Decimal("0.00"),
                        exposure_kind="UNVERIFIED_EXPOSURE",
                        now=f"Multiple conflicting rate schedules active for job {j_id} on {job['date']}.",
                        changed=f"{len(active_rates)} overlapping rate definitions found for customer {cust_id}.",
                        next_action="Determine binding rate schedule precedence with account representative.",
                        why="Ambiguous pricing creates billing unpredictability and contract breach risk.",
                        proof=f"Overlapping rate digests: {', '.join(digest(r)[:16] for r in active_rates)}",
                    )
                )
            elif len(relevant_invoices) == 1:
                # Exactly 1 active rate and 1 invoice: test for rate discrepancy
                target_rate = active_rates[0]
                target_inv = relevant_invoices[0]
                billed_amt = parse_money(target_inv["amount"])
                expected_amt = parse_money(target_rate["amount"])
                diff = billed_amt - expected_amt
                if diff != Decimal("0.00"):
                    abs_diff = abs(diff)
                    if diff > Decimal("0.00"):
                        potential_overbilling += abs_diff
                        kind = "POTENTIAL_OVERBILLING"
                    else:
                        potential_underbilling += abs_diff
                        kind = "POTENTIAL_UNDERBILLING"

                    findings.append(
                        self._create_finding(
                            code="RATE_MISMATCH",
                            subject=target_inv["invoice_id"],
                            severity="HIGH" if abs_diff > Decimal("100.00") else "MEDIUM",
                            records=[("job", job), ("invoice", target_inv), ("rate", target_rate)],
                            exposure=abs_diff,
                            exposure_kind=kind,
                            now=f"Invoice {target_inv['invoice_id']} billed ${billed_amt} vs approved rate of ${expected_amt} (delta ${diff:+}).",
                            changed=f"Discrepancy of ${abs_diff} detected between field rate schedule and billing line.",
                            next_action="Issue corrected invoice or credit memo reflecting approved master rate schedule.",
                            why="Deviating from contractual agreed rates causes revenue leakage or overbilling penalties.",
                            proof=f"Job SHA:{digest(job)[:12]}, Inv SHA:{digest(target_inv)[:12]}, Rate SHA:{digest(target_rate)[:12]}",
                        )
                    )

        # 2. Invoice-level evaluation (orphans & unreconciled payments)
        for inv in invoices:
            inv_id = inv["invoice_id"]
            if inv["job_id"] not in job_ids:
                exposure_amt = parse_money(inv["amount"])
                unverified_exposure += exposure_amt
                findings.append(
                    self._create_finding(
                        code="ORPHAN_INVOICE",
                        subject=inv_id,
                        severity="HIGH",
                        records=[("invoice", inv)],
                        exposure=exposure_amt,
                        exposure_kind="UNVERIFIED_EXPOSURE",
                        now=f"Invoice {inv_id} references non-existent job ID '{inv['job_id']}'.",
                        changed="Invoice billed without field operational equipment ticket backing.",
                        next_action="Locate valid job ticket or void orphan billing entry.",
                        why="Unbacked invoices fail external financial audits and revenue recognition standards.",
                        proof=f"Invoice payload digest: {digest(inv)}",
                    )
                )

            if inv["status"] == "paid":
                payments_for_inv = by_invoice_payments[inv_id]
                total_paid = sum((parse_money(p["amount"]) for p in payments_for_inv), Decimal("0.00"))
                billed = parse_money(inv["amount"])
                if total_paid != billed:
                    delta = total_paid - billed
                    abs_delta = abs(delta)
                    if delta < Decimal("0.00"):
                        potential_underbilling += abs_delta
                        kind = "POTENTIAL_UNDERBILLING"
                    else:
                        potential_overbilling += abs_delta
                        kind = "POTENTIAL_OVERBILLING"

                    evidence_records = [("invoice", inv)] + [("payment", p) for p in payments_for_inv]
                    findings.append(
                        self._create_finding(
                            code="PAID_STATUS_UNRECONCILED",
                            subject=inv_id,
                            severity="HIGH",
                            records=evidence_records,
                            exposure=abs_delta,
                            exposure_kind=kind,
                            now=f"Invoice {inv_id} marked paid but payments total ${total_paid} vs billed ${billed} (delta ${delta:+}).",
                            changed="General ledger status out of balance with cash application records.",
                            next_action="Review remittance advice and post missing payment or short-pay adjustment.",
                            why="Unreconciled paid statuses misstate accounts receivable and cash flow.",
                            proof=f"Invoice SHA:{digest(inv)[:12]}, Payments: {len(payments_for_inv)} records",
                        )
                    )

        # 3. Payment-level evaluation (orphan payments)
        for payment in payments:
            p_id = payment["payment_id"]
            if payment["invoice_id"] not in invoice_ids:
                p_amt = parse_money(payment["amount"])
                unverified_exposure += p_amt
                findings.append(
                    self._create_finding(
                        code="ORPHAN_PAYMENT",
                        subject=p_id,
                        severity="MEDIUM",
                        records=[("payment", payment)],
                        exposure=p_amt,
                        exposure_kind="UNVERIFIED_EXPOSURE",
                        now=f"Payment {p_id} references non-existent invoice ID '{payment['invoice_id']}'.",
                        changed="Cash receipt deposited without matched invoice account.",
                        next_action="Research customer remittance to match unapplied cash to open invoice.",
                        why="Unapplied cash creates suspense balances and obscures collection performance.",
                        proof=f"Payment payload digest: {digest(payment)}",
                    )
                )

        findings.sort(key=lambda x: (x["severity"], x["code"], x["subject"]))

        total_exposure = potential_underbilling + potential_overbilling + unverified_exposure

        audit_summary = {
            "schema": SCHEMA,
            "tenant_id": self.tenant_id,
            "dataset_sha256": digest(dataset),
            "status": "AUDIT_COMPLETE",
            "authority_state": "HOLD",
            "human_review_required": True,
            "counts": {
                "jobs": len(jobs),
                "invoices": len(invoices),
                "rates": len(rates),
                "payments": len(payments),
                "findings": len(findings),
            },
            "financial_summary": {
                "identified_exposure_usd": str(total_exposure),
                "potential_underbilling_usd": str(potential_underbilling),
                "potential_overbilling_usd": str(potential_overbilling),
                "unverified_exposure_usd": str(unverified_exposure),
                "confirmed_recovery_usd": "0.00",
                "recovery_rate_disclaimer": (
                    "Identified exposure is a candidate for human review, not confirmed recovery. "
                    "Confirmed recovery remains 0.00 until independent settlement."
                ),
            },
            "findings": findings,
            "limits": (
                "Deterministic synthetic revenue reconciliation only. Not tax, accounting, or legal advice. "
                "No autonomous changes to ERP/billing software authorized. Human audit signature required."
            ),
        }
        audit_summary["receipt_sha256"] = digest(audit_summary)

        # Persist report to durable SQLite storage
        save_audit_run(audit_summary, db_path=self.db_path)

        return audit_summary

    def _create_finding(
        self,
        code: str,
        subject: str,
        severity: str,
        records: list[tuple[str, dict[str, Any]]],
        exposure: Decimal,
        exposure_kind: str,
        now: str,
        changed: str,
        next_action: str,
        why: str,
        proof: str,
    ) -> dict[str, Any]:
        evidence = [{"kind": kind, "record_sha256": digest(rec)} for kind, rec in records]
        finding_body = {
            "finding_id": f"FND-{code}-{subject}",
            "code": code,
            "subject": subject,
            "severity": severity,
            "exposure_usd": str(exposure),
            "exposure_kind": exposure_kind,
            "evidence": evidence,
            "authority": "HUMAN_REVIEW_REQUIRED",
            "xaeli_explanation": {
                "now": now,
                "changed": changed,
                "next": next_action,
                "why": why,
                "proof": proof,
            },
        }
        finding_body["finding_sha256"] = digest(finding_body)
        return finding_body
