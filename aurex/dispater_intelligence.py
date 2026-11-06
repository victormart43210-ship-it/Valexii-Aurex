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
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

SCHEMA = "dispater.synthetic.revenue_intelligence.v1"
MAX_FIELD_LEN = 256
SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
# Exposure classes: potential_* and unverified are candidates only; none is recovered revenue.
UNDERBILLING = "POTENTIAL_UNDERBILLING"
OVERBILLING = "POTENTIAL_OVERBILLING"
UNVERIFIED = "UNVERIFIED_EXPOSURE"
QUALIFICATION = {
    "UNBILLED_JOB": "SUSPECTED_DISCREPANCY",
    "RATE_MISMATCH": "SUSPECTED_DISCREPANCY",
    "RATE_UNVERIFIED": "INSUFFICIENT_EVIDENCE",
    "AMBIGUOUS_RATE": "INSUFFICIENT_EVIDENCE",
    "DUPLICATE_INVOICE_UNRESOLVED": "INSUFFICIENT_EVIDENCE",
    "ORPHAN_INVOICE": "INSUFFICIENT_EVIDENCE",
    "ORPHAN_PAYMENT": "INSUFFICIENT_EVIDENCE",
    "PAID_STATUS_UNRECONCILED": "STATUS_INCONSISTENCY",
    "STATUS_UNRECONCILED": "STATUS_INCONSISTENCY",
    "OVERPAYMENT": "STATUS_INCONSISTENCY",
    "PARTIAL_PAYMENT": "STATUS_INCONSISTENCY",
    "SPLIT_OR_DUPLICATE_PAYMENT_UNRESOLVED": "INSUFFICIENT_EVIDENCE",
    "EQUIPMENT_HOURS_MISMATCH": "SUSPECTED_DISCREPANCY",
    "LABOR_HOURS_MISMATCH": "SUSPECTED_DISCREPANCY",
    "EQUIPMENT_HOURS_UNPRICED": "INSUFFICIENT_EVIDENCE",
    "HOURS_EVIDENCE_MISSING": "INSUFFICIENT_EVIDENCE",
    "HOURS_SOURCE_CONFLICT": "INSUFFICIENT_EVIDENCE",
    "UNBILLED_EQUIPMENT": "SUSPECTED_DISCREPANCY",
    "UNBILLED_LABOR": "SUSPECTED_DISCREPANCY",
    "MISAPPLIED_PAYMENT": "INSUFFICIENT_EVIDENCE",
    "DUPLICATE_FIELD_TICKET": "INSUFFICIENT_EVIDENCE",
    "OVERTIME_UNPRICED": "INSUFFICIENT_EVIDENCE",
}


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


def _optional_rows(payload: dict[str, Any], key: str, required_fields: set[str]) -> list[dict[str, Any]]:
    if key not in payload or payload[key] is None:
        return []
    return _validate_rows(payload, key, required_fields)


def _signed_payment(payment: dict[str, Any]) -> Decimal:
    kind = payment.get("kind", "PAYMENT")
    if kind not in ("PAYMENT", "REVERSAL"):
        raise InvalidSnapshot("payment kind must be PAYMENT or REVERSAL")
    amount = parse_money(payment["amount"])
    return -amount if kind == "REVERSAL" else amount


def _hours_amount(hours: Decimal, rate: Decimal) -> Decimal:
    return (hours * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _covering_rates(
    rates: list[dict[str, Any]], customer: str, service: str, job_date: date
) -> list[dict[str, Any]]:
    """Rates in force on the job date. A successor with ``supersedes`` retires only that prior rate."""
    covering = [
        rate
        for rate in rates
        if rate["customer_id"] == customer
        and rate["service_code"] == service
        and parse_date(rate["start"]) <= job_date <= parse_date(rate["end"])
    ]
    inactive: set[str] = set()
    for successor in covering:
        previous = successor.get("supersedes", "")
        if previous and parse_date(successor["start"]) <= job_date:
            inactive.add(str(previous))
    return [rate for rate in covering if rate["rate_id"] not in inactive]


def _duplicate_identity(rows: list[dict[str, Any]], id_field: str, date_field: str) -> bool:
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row[id_field], row[date_field])
        if key in seen:
            return True
        seen.add(key)
    return False


def dependent_finding_ids(report: dict[str, Any], superseded_record: dict[str, Any]) -> list[str]:
    """Findings whose evidence digest is exactly the superseded record. Unrelated findings stay."""
    target = digest(superseded_record)
    return [
        str(finding["finding_id"])
        for finding in report.get("findings", [])
        if any(item.get("record_sha256") == target for item in finding.get("evidence", []))
    ]


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
        equipment = _optional_rows(
            dataset,
            "equipment",
            {"ticket_id", "job_id", "equipment_id", "service_date", "billable_hours", "standby_hours", "invoiced_hours"},
        )
        labor = _optional_rows(
            dataset,
            "labor",
            {"record_id", "job_id", "role", "service_date", "approved_hours", "billed_hours"},
        )

        _ensure_unique_ids(jobs, "job_id", "jobs")
        _ensure_unique_ids(invoices, "invoice_id", "invoices")
        _ensure_unique_ids(rates, "rate_id", "rates")
        _ensure_unique_ids(payments, "payment_id", "payments")
        _ensure_unique_ids(equipment, "ticket_id", "equipment")
        _ensure_unique_ids(labor, "record_id", "labor")

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

        invoices_by_id = {inv["invoice_id"]: inv for inv in invoices}
        misapplied: list[dict[str, Any]] = []
        applicable_payments: list[dict[str, Any]] = []
        for payment in payments:
            declared_job = payment.get("job_id", "")
            invoice = invoices_by_id.get(payment["invoice_id"])
            if declared_job and invoice is not None and invoice["job_id"] != declared_job:
                misapplied.append(payment)
            else:
                applicable_payments.append(payment)
        by_invoice_payments: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for payment in applicable_payments:
            by_invoice_payments[payment["invoice_id"]].append(payment)
        equipment_by_job: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for ticket in equipment:
            equipment_by_job[ticket["job_id"]].append(ticket)
        labor_by_job: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in labor:
            labor_by_job[record["job_id"]].append(record)

        findings: list[dict[str, Any]] = []
        totals = {UNDERBILLING: Decimal("0.00"), OVERBILLING: Decimal("0.00"), UNVERIFIED: Decimal("0.00")}
        withheld = Decimal("0.00")
        rate_mismatch_ids: set[str] = set()

        job_ids = {j["job_id"] for j in jobs}
        invoice_ids = {inv["invoice_id"] for inv in invoices}
        orphan_ids = {inv["invoice_id"] for inv in invoices if inv["job_id"] not in job_ids}
        duplicate_ids = {
            inv["invoice_id"]
            for job_id, grouped in by_job_invoices.items()
            if job_id in job_ids and len(grouped) > 1
            for inv in grouped
        }

        # 1. Job-level evaluation
        for job in jobs:
            j_id = job["job_id"]
            cust_id = job["customer_id"]
            svc = job["service_code"]
            j_date = parse_date(job["date"])
            # Sorted so the withheld narrative does not depend on input row order.
            relevant_invoices = sorted(by_job_invoices[j_id], key=lambda i: str(i["invoice_id"]))

            # Unbilled ticket / job
            if not relevant_invoices:
                applicable_rates = _covering_rates(rates, cust_id, svc, j_date)
                hourly = len(applicable_rates) == 1 and applicable_rates[0].get("unit") == "HOUR"
                if hourly:
                    self._append_unbilled_hours(
                        findings, totals, job, applicable_rates[0], equipment_by_job[j_id], labor_by_job[j_id]
                    )
                else:
                    potential_val = (
                        parse_money(applicable_rates[0]["amount"]) if len(applicable_rates) == 1 else Decimal("0.00")
                    )
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

            # Duplicate invoices. No field in this snapshot says which document supersedes another,
            # so the engine does not pick the lowest id or book the extras as overbilling.
            if len(relevant_invoices) > 1:
                conflict_total = sum((parse_money(inv["amount"]) for inv in relevant_invoices), Decimal("0.00"))
                withheld += conflict_total
                evidence_records = [("job", job)] + [("invoice", inv) for inv in relevant_invoices]
                amounts = ", ".join(f"{inv['invoice_id']}={inv['amount']}" for inv in relevant_invoices)
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code="DUPLICATE_INVOICE_UNRESOLVED",
                        subject=j_id,
                        severity="CRITICAL",
                        records=evidence_records,
                        exposure=Decimal("0.00"),
                        now=(
                            f"Job {j_id} is referenced by {len(relevant_invoices)} invoices ({amounts}) "
                            f"totaling ${conflict_total}. Precedence is not established."
                        ),
                        changed="Conflicting bills were withheld from identified exposure instead of selecting a winner.",
                        next_action="Produce the authoritative invoice, correction, or void. Do not collect a guessed duplicate.",
                        why="Choosing the lowest invoice id would invent a legitimate bill and can inflate recoverable amounts.",
                        proof=f"Referenced invoice digests: {', '.join(digest(inv)[:16] for inv in relevant_invoices)}",
                    )
                )

            # Rate matching & reconciliation
            active_rates = _covering_rates(rates, cust_id, svc, j_date)
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
            elif len(relevant_invoices) == 1 and active_rates[0].get("unit") == "HOUR":
                self._append_priced_hours(
                    findings,
                    totals,
                    job,
                    active_rates[0],
                    relevant_invoices[0],
                    equipment_by_job[j_id],
                    labor_by_job[j_id],
                    rate_mismatch_ids,
                )
            elif len(relevant_invoices) == 1:
                # Exactly 1 active flat rate and 1 invoice: test for rate discrepancy
                target_rate = active_rates[0]
                target_inv = relevant_invoices[0]
                if equipment_by_job[j_id] or labor_by_job[j_id]:
                    findings.append(
                        self._create_finding(
                            exposure_class=UNVERIFIED,
                            code="EQUIPMENT_HOURS_UNPRICED",
                            subject=j_id,
                            severity="MEDIUM",
                            records=[("job", job), ("invoice", target_inv)],
                            exposure=Decimal("0.00"),
                            now=f"Job {j_id} has hour records but the governing rate is not an hourly rate.",
                            changed="Hour tickets were not converted into a second dollar total.",
                            next_action="Attach an hourly rate or remove the hour tickets from this flat-rate job.",
                            why="Pricing the same job twice, once flat and once by the hour, inflates exposure.",
                            proof=f"Rate digest: {digest(target_rate)}",
                        )
                    )
                billed_amt = parse_money(target_inv["amount"])
                expected_amt = parse_money(target_rate["amount"])
                diff = billed_amt - expected_amt
                if diff != Decimal("0.00"):
                    abs_diff = abs(diff)
                    exposure_class = UNDERBILLING if diff < 0 else OVERBILLING
                    totals[exposure_class] += abs_diff
                    rate_mismatch_ids.add(target_inv["invoice_id"])
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
            if not payments_for_inv and any(item["invoice_id"] == inv_id for item in misapplied):
                continue
            positive_misapplied = sum(
                (
                    amount
                    for amount in (
                        _signed_payment(item) for item in misapplied if item["invoice_id"] == inv_id
                    )
                    if amount > 0
                ),
                Decimal("0.00"),
            )
            total_paid = sum((_signed_payment(p) for p in payments_for_inv), Decimal("0.00"))
            billed = parse_money(inv["amount"])
            delta = total_paid - billed
            code = None
            if inv["status"] == "paid" and delta != 0:
                code = "PAID_STATUS_UNRECONCILED"
            elif inv["status"] != "paid" and delta == 0 and total_paid > 0:
                # Cash already matches the bill. Leaving the invoice open or disputed hides that.
                code = "STATUS_UNRECONCILED"
            elif inv["status"] != "paid" and delta > 0:
                code = "OVERPAYMENT"
            elif inv["status"] != "paid" and total_paid > 0 and delta < 0:
                code = "PARTIAL_PAYMENT"
            payment_kinds = {p.get("kind", "PAYMENT") for p in payments_for_inv}
            if len(payments_for_inv) > 1 and payment_kinds == {"PAYMENT"}:
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code="SPLIT_OR_DUPLICATE_PAYMENT_UNRESOLVED",
                        subject=inv_id,
                        severity="MEDIUM",
                        records=[("invoice", inv)] + [("payment", p) for p in payments_for_inv],
                        exposure=Decimal("0.00"),
                        now=(
                            f"Invoice {inv_id} has {len(payments_for_inv)} payments. "
                            "The snapshot cannot prove a split from a duplicate, so no extra cash is booked."
                        ),
                        changed="Net cash is applied once. Individual payments are not added again.",
                        next_action="Match each payment to remittance advice before treating any as a duplicate.",
                        why="Counting every payment as a separate recovery inflates exposure.",
                        proof=f"Payment ids: {', '.join(p['payment_id'] for p in payments_for_inv)}",
                    )
                )
            if code:
                abs_delta = abs(delta)
                # One dollar assignment per invoice. Orphan, unresolved duplicate, and rate-mismatch
                # findings already hold that invoice's economic event.
                overlaps = inv_id in orphan_ids or inv_id in duplicate_ids or inv_id in rate_mismatch_ids
                counted = Decimal("0.00") if overlaps or code == "STATUS_UNRECONCILED" else abs_delta
                # Misapplied cash was left out of total_paid, so the same dollars sit inside this gap.
                if counted > 0 and positive_misapplied > 0:
                    counted = max(Decimal("0.00"), counted - positive_misapplied)
                negative_net_withheld = Decimal("0.00")
                if counted > 0 and total_paid < 0:
                    capped = min(counted, billed)
                    negative_net_withheld = counted - capped
                    counted = capped
                    withheld += negative_net_withheld
                totals[UNVERIFIED] += counted
                evidence_records = [("invoice", inv)] + [("payment", p) for p in payments_for_inv]
                if code == "STATUS_UNRECONCILED":
                    now = f"Invoice {inv_id} is {inv['status']} but payments equal the billed ${billed}."
                    changed = "Cash application is complete while the invoice status still shows it is not paid."
                    next_action = (
                        "Confirm the remittance and correct the invoice status, "
                        "or reverse the cash posting if it was applied in error."
                    )
                    why = "A settled invoice left unpaid misstates accounts receivable."
                else:
                    now = (
                        f"Invoice {inv_id} ({inv['status']}) payments total ${total_paid} "
                        f"vs billed ${billed} (delta ${delta:+})."
                    )
                    changed = "General ledger status out of balance with cash application records."
                    next_action = (
                        "Review remittance advice and post missing payment, refund, or short-pay adjustment."
                    )
                    why = "Unreconciled payment status misstates accounts receivable and cash flow."
                if overlaps and counted == 0 and abs_delta != 0:
                    changed += " Dollar exposure for this invoice is already recorded on its primary finding."
                if positive_misapplied > 0 and counted < abs_delta:
                    changed += " Misapplied cash was not added again on top of this gap."
                if negative_net_withheld > 0:
                    changed += " A negative net is not proof of a second collection beyond the invoice."
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code=code,
                        subject=inv_id,
                        severity="HIGH" if code == "PAID_STATUS_UNRECONCILED" else "MEDIUM",
                        records=evidence_records,
                        exposure=counted,
                        now=now,
                        changed=changed,
                        next_action=next_action,
                        why=why,
                        proof=f"Invoice SHA:{digest(inv)[:12]}, Payments: {len(payments_for_inv)} records",
                    )
                )

        misapplied_counts: dict[str, int] = defaultdict(int)
        for payment in misapplied:
            misapplied_counts[str(payment["invoice_id"])] += 1
        for payment in misapplied:
            invoice = invoices_by_id.get(payment["invoice_id"])
            invoice_id = invoice["invoice_id"] if invoice is not None else ""
            already_assigned = invoice_id in orphan_ids or invoice_id in duplicate_ids or invoice_id in rate_mismatch_ids
            signed = _signed_payment(payment)
            repeated = misapplied_counts[str(payment["invoice_id"])] > 1
            amount = Decimal("0.00") if already_assigned or signed < 0 or repeated else signed
            if repeated and signed > 0 and not already_assigned:
                withheld += signed
            totals[UNVERIFIED] += amount
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="MISAPPLIED_PAYMENT",
                    subject=payment["payment_id"],
                    severity="HIGH",
                    records=[("payment", payment)],
                    exposure=amount,
                    now=(
                        f"Payment {payment['payment_id']} names job {payment.get('job_id')} "
                        f"but invoice {payment['invoice_id']} belongs to a different job."
                    ),
                    changed=(
                        "The snapshot cannot prove these wrong-job payments are separate events."
                        if repeated
                        else "The cash was not applied to the invoice and was not counted again as an orphan."
                    ),
                    next_action="Reallocate the payment to the invoice's job or correct the payment record.",
                    why="Applying the same cash to the invoice balance and to a wrong-job bucket would double-count it.",
                    proof=f"Payment digest: {digest(payment)}",
                )
            )

        # 3. Payment-level evaluation (orphan payments)
        for payment in payments:
            p_id = payment["payment_id"]
            if payment["invoice_id"] not in invoice_ids:
                signed = _signed_payment(payment)
                # A reversal without an invoice is not incoming cash.
                p_amt = Decimal("0.00") if signed < 0 else signed
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

        unbilled_jobs = [job for job in jobs if not by_job_invoices[job["job_id"]]]
        orphan_invoices = [inv for inv in invoices if inv["job_id"] not in job_ids]
        if len(unbilled_jobs) == 1 and len(invoices) == 1 and len(orphan_invoices) == 1:
            for finding in findings:
                if finding["code"] not in {"UNBILLED_JOB", "ORPHAN_INVOICE"}:
                    continue
                amount = parse_money(finding["exposure_usd"])
                if amount == 0:
                    continue
                finding.pop("finding_sha256", None)
                totals[finding["exposure_class"]] -= amount
                withheld += amount
                finding["exposure_usd"] = "0.00"
                finding["xaeli_explanation"]["changed"] += (
                    " Dollar exposure is withheld because this snapshot cannot prove"
                    " the unbilled job and the orphan invoice are different events."
                )
                finding["finding_sha256"] = digest(finding)
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
                "withheld_unresolved_usd": str(withheld),
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

    def _append_unbilled_hours(
        self,
        findings: list[dict[str, Any]],
        totals: dict[str, Decimal],
        job: dict[str, Any],
        rate: dict[str, Any],
        equipment: list[dict[str, Any]],
        labor: list[dict[str, Any]],
    ) -> None:
        """An hourly rate is not a flat job price. Missing hour evidence books nothing."""
        if equipment and labor:
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="HOURS_SOURCE_CONFLICT",
                    subject=job["job_id"],
                    severity="HIGH",
                    records=[("job", job), ("rate", rate)],
                    exposure=Decimal("0.00"),
                    now=f"Job {job['job_id']} has both equipment and labor records and no invoice.",
                    changed="Neither set of hours was priced.",
                    next_action="Choose the governing hour source before calculating an unbilled amount.",
                    why="Adding both sources would bill the same job twice.",
                    proof=f"Rate digest: {digest(rate)}",
                )
            )
            return
        rows = equipment or labor
        if not rows:
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="HOURS_EVIDENCE_MISSING",
                    subject=job["job_id"],
                    severity="MEDIUM",
                    records=[("job", job), ("rate", rate)],
                    exposure=Decimal("0.00"),
                    now=f"Job {job['job_id']} has an hourly rate and no invoice or hour record.",
                    changed="The hourly rate was not used as a flat job price.",
                    next_action="Supply the equipment ticket or labor record before estimating unbilled revenue.",
                    why="A missing ticket is not proof of a billable quantity.",
                    proof=f"Rate digest: {digest(rate)}",
                )
            )
            return
        if equipment:
            hours = sum((parse_money(row["billable_hours"]) for row in equipment), Decimal("0.00"))
            code = "UNBILLED_EQUIPMENT"
        else:
            hours = sum((parse_money(row["approved_hours"]) for row in labor), Decimal("0.00"))
            code = "UNBILLED_LABOR"
        exposure = _hours_amount(hours, parse_money(rate["amount"]))
        totals[UNDERBILLING] += exposure
        findings.append(
            self._create_finding(
                exposure_class=UNDERBILLING,
                code=code,
                subject=job["job_id"],
                severity="HIGH",
                records=[("job", job), ("rate", rate)] + [("equipment" if equipment else "labor", row) for row in rows],
                exposure=exposure,
                now=f"Job {job['job_id']} has {hours} billable hours and no invoice.",
                changed="Standby hours were not added. Only the recorded billable or approved hours were priced.",
                next_action="Invoice the hours or record why the work was not billable.",
                why="Completed hours without an invoice are unbilled revenue, not confirmed recovery.",
                proof=f"Hourly rate digest: {digest(rate)}",
            )
        )

    def _append_priced_hours(
        self,
        findings: list[dict[str, Any]],
        totals: dict[str, Decimal],
        job: dict[str, Any],
        rate: dict[str, Any],
        invoice: dict[str, Any],
        equipment: list[dict[str, Any]],
        labor: list[dict[str, Any]],
        rate_mismatch_ids: set[str],
    ) -> None:
        """One dollar event for an hourly job. Standby is not automatically billed."""
        if equipment and _duplicate_identity(equipment, "equipment_id", "service_date"):
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="DUPLICATE_FIELD_TICKET",
                    subject=job["job_id"],
                    severity="HIGH",
                    records=[("job", job), ("invoice", invoice)] + [("equipment", row) for row in equipment],
                    exposure=Decimal("0.00"),
                    now=f"Job {job['job_id']} has two tickets for the same equipment and service date.",
                    changed="Those hours were not added together.",
                    next_action="Keep one ticket. Do not price both.",
                    why="Duplicate tickets for the same machine and day are not two shifts.",
                    proof=f"Invoice digest: {digest(invoice)}",
                )
            )
            return
        if labor and any(parse_money(row.get("overtime_hours", "0.00")) > 0 for row in labor):
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="OVERTIME_UNPRICED",
                    subject=job["job_id"],
                    severity="MEDIUM",
                    records=[("job", job), ("invoice", invoice), ("rate", rate)],
                    exposure=Decimal("0.00"),
                    now=f"Job {job['job_id']} records overtime and the rate is not an overtime rate.",
                    changed="Overtime hours were withheld from the dollar total.",
                    next_action="Supply an overtime rate or remove the overtime hours.",
                    why="Pricing overtime at the straight-time rate would invent a recovery.",
                    proof=f"Rate digest: {digest(rate)}",
                )
            )
        if equipment and labor:
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="HOURS_SOURCE_CONFLICT",
                    subject=job["job_id"],
                    severity="HIGH",
                    records=[("job", job), ("invoice", invoice), ("rate", rate)],
                    exposure=Decimal("0.00"),
                    now=f"Job {job['job_id']} has equipment and labor records against one hourly rate.",
                    changed="No hour total was added to identified exposure.",
                    next_action="Separate the governing source before treating either total as the bill.",
                    why="Two hour sources for one job can double-count the same work.",
                    proof=f"Invoice digest: {digest(invoice)}",
                )
            )
            return
        if not equipment and not labor:
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="HOURS_EVIDENCE_MISSING",
                    subject=invoice["invoice_id"],
                    severity="MEDIUM",
                    records=[("job", job), ("invoice", invoice), ("rate", rate)],
                    exposure=Decimal("0.00"),
                    now=f"Invoice {invoice['invoice_id']} is governed by an hourly rate but has no hour record.",
                    changed="The invoice amount was not compared with the hourly rate as if the rate were a flat price.",
                    next_action="Attach the equipment ticket or labor record.",
                    why="Without hours, the billed amount cannot be proven wrong.",
                    proof=f"Rate digest: {digest(rate)}",
                )
            )
            return
        rate_amount = parse_money(rate["amount"])
        billed = parse_money(invoice["amount"])
        if equipment:
            hours = sum((parse_money(row["billable_hours"]) for row in equipment), Decimal("0.00"))
            code = "EQUIPMENT_HOURS_MISMATCH"
            rows = [("equipment", row) for row in equipment]
        else:
            hours = sum((parse_money(row["approved_hours"]) for row in labor), Decimal("0.00"))
            code = "LABOR_HOURS_MISMATCH"
            rows = [("labor", row) for row in labor]
        expected = _hours_amount(hours, rate_amount)
        delta = billed - expected
        if delta == 0:
            return
        if equipment:
            invoiced_hours = sum((parse_money(row["invoiced_hours"]) for row in equipment), Decimal("0.00"))
        else:
            invoiced_hours = sum((parse_money(row["billed_hours"]) for row in labor), Decimal("0.00"))
        exposure_class = UNDERBILLING if delta < 0 else OVERBILLING
        exposure = abs(delta)
        totals[exposure_class] += exposure
        rate_mismatch_ids.add(invoice["invoice_id"])
        findings.append(
            self._create_finding(
                exposure_class=exposure_class,
                code=code,
                subject=invoice["invoice_id"],
                severity="HIGH" if exposure > Decimal("100.00") else "MEDIUM",
                records=[("job", job), ("invoice", invoice), ("rate", rate)] + rows,
                exposure=exposure,
                now=(
                    f"Invoice {invoice['invoice_id']} billed ${billed} against {hours} hours "
                    f"at ${rate_amount} (${expected}). Invoiced hours on the ticket are {invoiced_hours}."
                ),
                changed="Standby was excluded. The invoice dollars were recorded once.",
                next_action="Correct the invoice or the hour ticket. Do not add a second finding for the same hours.",
                why="Hour and invoice disagreements are one economic event, not two recoveries.",
                proof=f"Rate digest: {digest(rate)}; invoice digest: {digest(invoice)}",
            )
        )

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
            "exposure_event_id": f"{code}:{subject}",
            "qualification": QUALIFICATION[code],
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
    """True when the unkeyed hash matches. A versioned receipt also needs its HMAC.

    The hash is an integrity check. It is not an authenticity signature. A report that
    carries ``receipt_auth`` or ``receipt_mac`` is accepted only when that MAC verifies.
    """
    body = {k: v for k, v in report.items() if k not in ("receipt_sha256", "receipt_auth", "receipt_mac")}
    try:
        sha_ok = hmac_equal(digest(body), str(report.get("receipt_sha256", "")))
    except (TypeError, ValueError):
        return False
    if not sha_ok:
        return False
    claims_mac = bool(
        report.get("receipt_auth")
        or report.get("receipt_mac")
        or report.get("receipt_binding") == "BOUND_V2"
    )
    if claims_mac:
        from aurex.dispater_receipt import verify_mac

        return verify_mac(report)
    return True


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
