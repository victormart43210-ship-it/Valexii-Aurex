"""DISPATER Industrial Revenue Intelligence & Audit Reconciliation Engine.

Implements deterministic, decimal-safe operational revenue reconciliation,
equipment ticket matching, approved rate schedule verification, SHA-256 evidence
digest generation, CSV formula-injection defenses, and canonical 5-step XAELI findings
(NOW -> CHANGED -> NEXT -> WHY -> PROOF).

NON-DELEGABLE CONSTRAINTS:
- No automatic billing, payment execution, invoice modification, or customer account changes.
- All detected discrepancies are candidates for human review (HUMAN_REVIEW_REQUIRED).
- Potential exposure is NOT confirmed recovery or realized savings.
- The system may never be its own sole witness.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

SCHEMA = "dispater.synthetic.revenue_intelligence.v1"
MAX_FIELD_LEN = 256
SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
# Exposure classes: potential_* and unverified are candidates only; none is recovered revenue.
UNDERBILLING = "POTENTIAL_UNDERBILLING"
OVERBILLING = "POTENTIAL_OVERBILLING"
UNVERIFIED = "UNVERIFIED_EXPOSURE"


class InvalidSnapshot(ValueError):
    """Reject a malformed, invalid, or non-synthetic audit payload."""


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
            if len(v) > MAX_FIELD_LEN:
                raise InvalidSnapshot(f"'{key}[{idx}].{k}' exceeds {MAX_FIELD_LEN} characters")
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


class RevenueLeakageEngine:
    """Deterministic Revenue Leakage and Billing Exception Audit Engine."""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id

    def reconcile_records(self, dataset: dict[str, Any]) -> dict[str, Any]:
        """Reconcile jobs, invoices, approved rates, and payments deterministically."""
        if not isinstance(dataset, dict):
            raise InvalidSnapshot("Dataset must be a JSON object")

        if dataset.get("dataset_type") != "SYNTHETIC_ONLY":
            raise InvalidSnapshot("Only explicitly labeled SYNTHETIC_ONLY datasets are admitted")

        dataset_tenant = dataset.get("tenant_id", "default")
        if dataset_tenant != self.tenant_id:
            raise InvalidSnapshot(
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
        totals = {UNDERBILLING: Decimal("0.00"), OVERBILLING: Decimal("0.00"), UNVERIFIED: Decimal("0.00")}

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
                totals[UNDERBILLING] += potential_val
                findings.append(
                    self._create_finding(
                        exposure_class=UNDERBILLING,
                        code="UNBILLED_JOB",
                        subject=j_id,
                        severity="HIGH",
                        records=[("job", job)],
                        exposure=potential_val,
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
                totals[OVERBILLING] += dup_exposure
                evidence_records = [("job", job)] + [("invoice", inv) for inv in relevant_invoices]
                findings.append(
                    self._create_finding(
                        exposure_class=OVERBILLING,
                        code="MULTIPLE_INVOICES",
                        subject=j_id,
                        severity="CRITICAL",
                        records=evidence_records,
                        exposure=dup_exposure,
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
                        exposure_class=UNVERIFIED,
                        code="RATE_UNVERIFIED",
                        subject=j_id,
                        severity="MEDIUM",
                        records=[("job", job)],
                        exposure=Decimal("0.00"),
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
                        exposure_class=UNVERIFIED,
                        code="AMBIGUOUS_RATE",
                        subject=j_id,
                        severity="MEDIUM",
                        records=evidence_records,
                        exposure=Decimal("0.00"),
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
                    exposure_class = UNDERBILLING if diff < 0 else OVERBILLING
                    totals[exposure_class] += abs_diff
                    findings.append(
                        self._create_finding(
                            exposure_class=exposure_class,
                            code="RATE_MISMATCH",
                            subject=target_inv["invoice_id"],
                            severity="HIGH" if abs_diff > Decimal("100.00") else "MEDIUM",
                            records=[("job", job), ("invoice", target_inv), ("rate", target_rate)],
                            exposure=abs_diff,
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
                totals[UNVERIFIED] += parse_money(inv["amount"])
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code="ORPHAN_INVOICE",
                        subject=inv_id,
                        severity="HIGH",
                        records=[("invoice", inv)],
                        exposure=parse_money(inv["amount"]),
                        now=f"Invoice {inv_id} references non-existent job ID '{inv['job_id']}'.",
                        changed="Invoice billed without field operational equipment ticket backing.",
                        next_action="Locate valid job ticket or void orphan billing entry.",
                        why="Unbacked invoices fail external financial audits and revenue recognition standards.",
                        proof=f"Invoice payload digest: {digest(inv)}",
                    )
                )

            payments_for_inv = by_invoice_payments[inv_id]
            total_paid = sum((parse_money(p["amount"]) for p in payments_for_inv), Decimal("0.00"))
            billed = parse_money(inv["amount"])
            delta = total_paid - billed
            code = None
            if inv["status"] == "paid" and delta != 0:
                code = "PAID_STATUS_UNRECONCILED"
            elif inv["status"] != "paid" and delta > 0:
                code = "OVERPAYMENT"
            elif inv["status"] != "paid" and total_paid > 0 and delta < 0:
                code = "PARTIAL_PAYMENT"
            if code:
                abs_delta = abs(delta)
                # Payment shortfalls and surpluses are cash-application questions, never confirmed.
                totals[UNVERIFIED] += abs_delta
                evidence_records = [("invoice", inv)] + [("payment", p) for p in payments_for_inv]
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code=code,
                        subject=inv_id,
                        severity="HIGH" if code == "PAID_STATUS_UNRECONCILED" else "MEDIUM",
                        records=evidence_records,
                        exposure=abs_delta,
                        now=f"Invoice {inv_id} ({inv['status']}) payments total ${total_paid} vs billed ${billed} (delta ${delta:+}).",
                        changed="General ledger status out of balance with cash application records.",
                        next_action="Review remittance advice and post missing payment, refund, or short-pay adjustment.",
                        why="Unreconciled payment status misstates accounts receivable and cash flow.",
                        proof=f"Invoice SHA:{digest(inv)[:12]}, Payments: {len(payments_for_inv)} records",
                    )
                )

        # 3. Payment-level evaluation (orphan payments)
        for payment in payments:
            p_id = payment["payment_id"]
            if payment["invoice_id"] not in invoice_ids:
                p_amt = parse_money(payment["amount"])
                totals[UNVERIFIED] += p_amt
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code="ORPHAN_PAYMENT",
                        subject=p_id,
                        severity="MEDIUM",
                        records=[("payment", payment)],
                        exposure=p_amt,
                        now=f"Payment {p_id} references non-existent invoice ID '{payment['invoice_id']}'.",
                        changed="Cash receipt deposited without matched invoice account.",
                        next_action="Research customer remittance to match unapplied cash to open invoice.",
                        why="Unapplied cash creates suspense balances and obscures collection performance.",
                        proof=f"Payment payload digest: {digest(payment)}",
                    )
                )

        findings.sort(key=lambda x: (SEVERITY_RANK[x["severity"]], x["code"], x["subject"]))
        identified_exposure = sum(totals.values(), Decimal("0.00"))

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
                "identified_exposure_usd": str(identified_exposure),
                "potential_underbilling_usd": str(totals[UNDERBILLING]),
                "potential_overbilling_usd": str(totals[OVERBILLING]),
                "unverified_exposure_usd": str(totals[UNVERIFIED]),
                "human_confirmed_discrepancy_usd": "0.00",
                "confirmed_recovery_usd": "0.00",
                "recovery_rate_disclaimer": "Identified exposure is a candidate for human review, not confirmed recovery.",
            },
            "findings": findings,
            "limits": (
                "Deterministic synthetic revenue reconciliation only. Not tax, accounting, or legal advice. "
                "No autonomous changes to ERP/billing software authorized. Human audit signature required."
            ),
        }
        audit_summary["receipt_sha256"] = digest(audit_summary)
        return audit_summary

    def _create_finding(
        self,
        exposure_class: str,
        code: str,
        subject: str,
        severity: str,
        records: list[tuple[str, dict[str, Any]]],
        exposure: Decimal,
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
            "exposure_class": exposure_class,
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


def verify_receipt(report: dict[str, Any]) -> bool:
    """Return True when the report's receipt hash matches its content (tamper check)."""
    body = {k: v for k, v in report.items() if k != "receipt_sha256"}
    try:
        return hmac_equal(digest(body), str(report.get("receipt_sha256", "")))
    except (TypeError, ValueError):
        return False


def hmac_equal(a: str, b: str) -> bool:
    import hmac

    return hmac.compare_digest(a.encode(), b.encode())


def report_to_csv(report: dict[str, Any]) -> str:
    """Export findings as CSV with formula-injection neutralization on every cell."""
    import csv
    import io

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["finding_id", "code", "subject", "severity", "exposure_class", "exposure_usd", "authority"])
    for f in report.get("findings", []):
        writer.writerow(
            [
                sanitize_formula_field(str(f.get(k, "")))
                for k in ("finding_id", "code", "subject", "severity", "exposure_class", "exposure_usd", "authority")
            ]
        )
    return buf.getvalue()
