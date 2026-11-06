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
TOWING_SCHEMA = "dispater.synthetic.towing_recovery.v1"
MAX_FIELD_LEN = 256
SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
# Exposure classes: potential_* and unverified are candidates only; none is recovered revenue.
UNDERBILLING = "POTENTIAL_UNDERBILLING"
OVERBILLING = "POTENTIAL_OVERBILLING"
UNVERIFIED = "UNVERIFIED_EXPOSURE"
CONFIRMED_RECOVERY = "CONFIRMED_RECOVERY"


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

        if bool(dataset.get("dispatches")):
            return self._reconcile_towing_records(dataset)

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


    def _reconcile_towing_records(self, dataset: dict[str, Any]) -> dict[str, Any]:
        """Complete Towing Revenue Recovery & Audit Reconciliation."""
        dispatches = _validate_rows(
            dataset,
            "dispatches",
            {"dispatch_id", "contract_id", "service_type", "date", "status"},
        )
        contracts = _validate_rows(
            dataset,
            "contracts",
            {"contract_id", "customer_name", "effective_start", "effective_end"},
        )
        rates = _validate_rows(
            dataset,
            "rates",
            {"rate_id", "contract_id", "charge_type", "amount", "effective_start", "effective_end"},
        )
        invoices = _validate_rows(
            dataset,
            "invoices",
            {"invoice_id", "dispatch_id", "total_amount", "status"},
        )
        payments = _validate_rows(
            dataset,
            "payments",
            {"payment_id", "invoice_id", "amount", "payment_date", "source"},
        )
        deposits = _validate_rows(
            dataset,
            "deposits",
            {"deposit_id", "bank_reference", "amount", "deposit_date"},
        )

        _ensure_unique_ids(dispatches, "dispatch_id", "dispatches")
        _ensure_unique_ids(contracts, "contract_id", "contracts")
        _ensure_unique_ids(rates, "rate_id", "rates")
        _ensure_unique_ids(invoices, "invoice_id", "invoices")
        _ensure_unique_ids(payments, "payment_id", "payments")
        _ensure_unique_ids(deposits, "deposit_id", "deposits")

        for d in dispatches:
            parse_date(d["date"])
            if d["status"] not in ("completed", "cancelled", "en_route", "pending"):
                raise InvalidSnapshot(f"invalid dispatch status: {d['status']!r}")

        for c in contracts:
            s = parse_date(c["effective_start"])
            e = parse_date(c["effective_end"])
            if e < s:
                raise InvalidSnapshot(f"contract end precedes start: {c['contract_id']}")

        for r in rates:
            parse_money(r["amount"])
            s = parse_date(r["effective_start"])
            e = parse_date(r["effective_end"])
            if e < s:
                raise InvalidSnapshot(f"rate end precedes start: {r['rate_id']}")

        for inv in invoices:
            parse_money(inv["total_amount"])
            if inv["status"] not in ("open", "paid", "disputed", "voided"):
                raise InvalidSnapshot(f"invalid invoice status: {inv['status']!r}")

        for p in payments:
            parse_money(p["amount"])
            parse_date(p["payment_date"])

        for dep in deposits:
            parse_money(dep["amount"])
            parse_date(dep["deposit_date"])

        by_dispatch_invoices: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for inv in invoices:
            by_dispatch_invoices[inv["dispatch_id"]].append(inv)

        by_invoice_payments: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for p in payments:
            by_invoice_payments[p["invoice_id"]].append(p)

        by_contract_rates: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in rates:
            by_contract_rates[r["contract_id"]].append(r)

        contracts_by_id = {c["contract_id"]: c for c in contracts}

        findings: list[dict[str, Any]] = []
        totals = {
            UNDERBILLING: Decimal("0.00"),
            OVERBILLING: Decimal("0.00"),
            UNVERIFIED: Decimal("0.00"),
            CONFIRMED_RECOVERY: Decimal("0.00"),
        }

        for disp in dispatches:
            d_id = disp["dispatch_id"]
            c_id = disp["contract_id"]
            d_date = parse_date(disp["date"])
            invs = by_dispatch_invoices[d_id]
            svc = disp["service_type"]

            contract = contracts_by_id.get(c_id)
            if not contract:
                totals[UNVERIFIED] += Decimal("0.00")
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code="CONTRACT_MISSING",
                        subject=d_id,
                        severity="HIGH",
                        records=[("dispatch", disp)],
                        exposure=Decimal("0.00"),
                        now=f"Dispatch {d_id} references missing contract ID '{c_id}'.",
                        changed="Towing operation dispatched without counter-signed contract record.",
                        next_action="Establish master service agreement or verify customer account number.",
                        why="Uncontracted commercial tows cannot enforce agreed commercial pricing.",
                        proof=f"Dispatch digest: {digest(disp)}",
                    )
                )
                continue

            c_start = parse_date(contract["effective_start"])
            c_end = parse_date(contract["effective_end"])
            if not (c_start <= d_date <= c_end):
                totals[UNVERIFIED] += Decimal("0.00")
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code="CONTRACT_AMENDMENT_INVALID",
                        subject=d_id,
                        severity="HIGH",
                        records=[("dispatch", disp), ("contract", contract)],
                        exposure=Decimal("0.00"),
                        now=f"Dispatch {d_id} occurred on {disp['date']}, outside contract active term ({c_start} to {c_end}).",
                        changed="Service rendered on expired or pre-effective contract amendment.",
                        next_action="Obtain executed contract amendment covering tow operation date.",
                        why="Towing operations outside effective term risk dispute and audit disqualification.",
                        proof=f"Dispatch SHA:{digest(disp)[:12]}, Contract SHA:{digest(contract)[:12]}",
                    )
                )

            if disp["status"] == "completed" and not invs:
                active_base_rates = [
                    r
                    for r in by_contract_rates[c_id]
                    if r["charge_type"] == svc
                    and parse_date(r["effective_start"]) <= d_date <= parse_date(r["effective_end"])
                ]
                potential_exposure = (
                    parse_money(active_base_rates[0]["amount"])
                    if len(active_base_rates) == 1
                    else Decimal("0.00")
                )
                totals[UNDERBILLING] += potential_exposure
                findings.append(
                    self._create_finding(
                        exposure_class=UNDERBILLING,
                        code="DISPATCH_UNBILLED",
                        subject=d_id,
                        severity="CRITICAL",
                        records=[("dispatch", disp)],
                        exposure=potential_exposure,
                        now=f"Completed tow dispatch {d_id} has zero billing records in system.",
                        changed=f"Tow marked complete on {disp['date']} without invoice generated.",
                        next_action="Draft and transmit billing package to account owner with driver dispatch log.",
                        why="Unbilled completed tows represent direct bottom-line revenue leakage.",
                        proof=f"Dispatch payload digest: {digest(disp)}",
                    )
                )

            if len(invs) > 1:
                dup_exposure = sum((parse_money(i["total_amount"]) for i in invs[1:]), Decimal("0.00"))
                totals[OVERBILLING] += dup_exposure
                records = [("dispatch", disp)] + [("invoice", i) for i in invs]
                findings.append(
                    self._create_finding(
                        exposure_class=OVERBILLING,
                        code="DUPLICATE_INVOICE",
                        subject=d_id,
                        severity="CRITICAL",
                        records=records,
                        exposure=dup_exposure,
                        now=f"Dispatch {d_id} has {len(invs)} separate invoices issued.",
                        changed="Multiple invoices generated for a single tow dispatch event.",
                        next_action="Void duplicate billing statement and issue credit notice.",
                        why="Double billing violates motor carrier standards and triggers account clawbacks.",
                        proof=f"Invoices: {', '.join(digest(i)[:12] for i in invs)}",
                    )
                )

            if len(invs) == 1:
                inv = invs[0]
                active_base = [
                    r
                    for r in by_contract_rates[c_id]
                    if r["charge_type"] == svc
                    and parse_date(r["effective_start"]) <= d_date <= parse_date(r["effective_end"])
                ]
                if len(active_base) == 1 and "base_amount" in inv:
                    expected_base = parse_money(active_base[0]["amount"])
                    actual_base = parse_money(inv["base_amount"])
                    if actual_base != expected_base:
                        diff = actual_base - expected_base
                        abs_diff = abs(diff)
                        exp_cls = UNDERBILLING if diff < 0 else OVERBILLING
                        totals[exp_cls] += abs_diff
                        findings.append(
                            self._create_finding(
                                exposure_class=exp_cls,
                                code="RATE_MISMATCH",
                                subject=inv["invoice_id"],
                                severity="HIGH",
                                records=[("dispatch", disp), ("invoice", inv), ("rate", active_base[0])],
                                exposure=abs_diff,
                                now=f"Invoice {inv['invoice_id']} billed base ${actual_base} vs contracted ${expected_base} (delta ${diff:+}).",
                                changed=f"Contracted pricing variance on service '{svc}'.",
                                next_action="Re-issue invoice line with counter-signed rate schedule pricing.",
                                why="Departures from contracted pricing yield uncollectible balances or partner churn.",
                                proof=f"Rate SHA:{digest(active_base[0])[:12]}, Inv SHA:{digest(inv)[:12]}",
                            )
                        )

                storage_days = int(disp.get("storage_days", "0"))
                storage_rate_candidates = [
                    r
                    for r in by_contract_rates[c_id]
                    if r["charge_type"] == "DAILY_STORAGE"
                    and parse_date(r["effective_start"]) <= d_date <= parse_date(r["effective_end"])
                ]
                if storage_days > 0 and len(storage_rate_candidates) == 1:
                    per_day = parse_money(storage_rate_candidates[0]["amount"])
                    expected_storage = per_day * Decimal(storage_days)
                    billed_storage = parse_money(inv.get("storage_amount", "0.00"))
                    if billed_storage < expected_storage:
                        short_storage = expected_storage - billed_storage
                        totals[UNDERBILLING] += short_storage
                        findings.append(
                            self._create_finding(
                                exposure_class=UNDERBILLING,
                                code="STORAGE_UNBILLED",
                                subject=inv["invoice_id"],
                                severity="HIGH",
                                records=[("dispatch", disp), ("invoice", inv), ("rate", storage_rate_candidates[0])],
                                exposure=short_storage,
                                now=f"Dispatch recorded {storage_days} days in impound yard. Billed ${billed_storage} vs expected ${expected_storage}.",
                                changed=f"Unbilled storage fee of ${short_storage} identified.",
                                next_action="Issue supplementary invoice for verifiable impound yard storage days.",
                                why="Commercial yard daily storage requires complete billing capture prior to vehicle release.",
                                proof=f"Storage rate SHA:{digest(storage_rate_candidates[0])[:12]}, Days: {storage_days}",
                            )
                        )

                is_after_hours = disp.get("after_hours", "false").lower() in ("true", "1", "yes")
                after_hours_rates = [
                    r
                    for r in by_contract_rates[c_id]
                    if r["charge_type"] == "AFTER_HOURS_SURCHARGE"
                    and parse_date(r["effective_start"]) <= d_date <= parse_date(r["effective_end"])
                ]
                if is_after_hours and len(after_hours_rates) == 1:
                    expected_ah = parse_money(after_hours_rates[0]["amount"])
                    billed_ah = parse_money(inv.get("after_hours_amount", "0.00"))
                    if billed_ah != expected_ah:
                        ah_diff = billed_ah - expected_ah
                        abs_ah_diff = abs(ah_diff)
                        exp_cls = UNDERBILLING if ah_diff < 0 else OVERBILLING
                        totals[exp_cls] += abs_ah_diff
                        findings.append(
                            self._create_finding(
                                exposure_class=exp_cls,
                                code="AFTER_HOURS_SURCHARGE_MISMATCH",
                                subject=inv["invoice_id"],
                                severity="MEDIUM",
                                records=[("dispatch", disp), ("invoice", inv), ("rate", after_hours_rates[0])],
                                exposure=abs_ah_diff,
                                now=f"Dispatch took place after-hours. Billed ${billed_ah} vs contracted surcharge ${expected_ah}.",
                                changed=f"After-hours fee discrepancy of ${abs_ah_diff} identified.",
                                next_action="Correct after-hours premium line to align with night/weekend rate sheet.",
                                why="Night and emergency roadside dispatches incur contracted staff differential.",
                                proof=f"After-hours rate SHA:{digest(after_hours_rates[0])[:12]}",
                            )
                        )

        for inv in invoices:
            inv_id = inv["invoice_id"]
            billed = parse_money(inv["total_amount"])
            pays = by_invoice_payments[inv_id]
            total_paid = sum((parse_money(p["amount"]) for p in pays), Decimal("0.00"))

            if inv["status"] == "disputed":
                totals[UNVERIFIED] += billed
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code="DISPUTED_CHARGE",
                        subject=inv_id,
                        severity="HIGH",
                        records=[("invoice", inv)],
                        exposure=billed,
                        now=f"Invoice {inv_id} for ${billed} is placed in disputed status by customer.",
                        changed="Formal billing dispute lodged against towing charges.",
                        next_action="Examine GPS tracking, photo proof of drop-off, and customer agreement.",
                        why="Disputed charges cannot be recognized as earned revenue until dispute resolution.",
                        proof=f"Invoice payload digest: {digest(inv)}",
                    )
                )

            motor_club_pays = [p for p in pays if "motor_club" in p.get("source", "").lower()]
            if motor_club_pays and total_paid < billed and inv["status"] != "disputed":
                shortfall = billed - total_paid
                totals[UNDERBILLING] += shortfall
                records = [("invoice", inv)] + [("payment", p) for p in motor_club_pays]
                findings.append(
                    self._create_finding(
                        exposure_class=UNDERBILLING,
                        code="MOTOR_CLUB_SHORT_PAY",
                        subject=inv_id,
                        severity="HIGH",
                        records=records,
                        exposure=shortfall,
                        now=f"Motor club paid ${total_paid} on billed ${billed} (shortfall ${shortfall}).",
                        changed="Commercial motor club applied unauthorized contract discount or fee reduction.",
                        next_action="Submit secondary appeal with driver on-scene photo and signed customer slip.",
                        why="Motor clubs frequently underpay scheduled tow rates unless systematically contested.",
                        proof=f"Remittance payment digests: {', '.join(digest(p)[:12] for p in motor_club_pays)}",
                    )
                )

            if inv.get("recovery_status") == "SETTLED_BY_HUMAN":
                settled_amt = parse_money(inv.get("recovered_amount", "0.00"))
                if settled_amt > Decimal("0.00"):
                    totals[CONFIRMED_RECOVERY] += settled_amt
                    findings.append(
                        self._create_finding(
                            exposure_class=CONFIRMED_RECOVERY,
                            code="CONFIRMED_PAYMENT_RECOVERY",
                            subject=inv_id,
                            severity="LOW",
                            records=[("invoice", inv)],
                            exposure=settled_amt,
                            now=f"Invoice {inv_id} recovered ${settled_amt} cash following human review.",
                            changed="Previously contested or unbilled funds successfully settled and collected.",
                            next_action="Reconcile bank deposit batch and close recovery tracking record.",
                            why="Documenting verified cash collections provides true commercial ROI audit trail.",
                            proof=f"Invoice settlement SHA: {digest(inv)}",
                        )
                    )

        total_payments_sum = sum((parse_money(p["amount"]) for p in payments), Decimal("0.00"))
        total_deposits_sum = sum((parse_money(d["amount"]) for d in deposits), Decimal("0.00"))
        if deposits and total_payments_sum != total_deposits_sum:
            deposit_delta = abs(total_deposits_sum - total_payments_sum)
            totals[UNVERIFIED] += deposit_delta
            records = [("deposit", d) for d in deposits] + [("payment", p) for p in payments]
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="UNRECONCILED_DEPOSIT",
                    subject="DEP-TOTALS",
                    severity="HIGH",
                    records=records[:5],
                    exposure=deposit_delta,
                    now=f"Total bank deposits (${total_deposits_sum}) do not match payment receipts (${total_payments_sum}).",
                    changed=f"Unreconciled bank deposit delta of ${deposit_delta}.",
                    next_action="Audit credit card merchant batch and bank settlement statement.",
                    why="Deposits unlinked to receipts compromise audit integrity and tax reporting.",
                    proof=f"Deposits: {len(deposits)} records, Payments: {len(payments)} records",
                )
            )

        findings.sort(key=lambda x: (SEVERITY_RANK[x["severity"]], x["code"], x["subject"]))
        identified_exposure = totals[UNDERBILLING] + totals[OVERBILLING] + totals[UNVERIFIED]

        report = {
            "schema": TOWING_SCHEMA,
            "tenant_id": self.tenant_id,
            "dataset_sha256": digest(dataset),
            "status": "AUDIT_COMPLETE",
            "authority_state": "HOLD",
            "human_review_required": True,
            "counts": {
                "dispatches": len(dispatches),
                "contracts": len(contracts),
                "rates": len(rates),
                "invoices": len(invoices),
                "payments": len(payments),
                "deposits": len(deposits),
                "findings": len(findings),
            },
            "financial_summary": {
                "identified_exposure_usd": str(identified_exposure),
                "potential_underbilling_usd": str(totals[UNDERBILLING]),
                "potential_overbilling_usd": str(totals[OVERBILLING]),
                "unverified_exposure_usd": str(totals[UNVERIFIED]),
                "human_confirmed_discrepancy_usd": str(totals[CONFIRMED_RECOVERY]),
                "confirmed_recovery_usd": str(totals[CONFIRMED_RECOVERY]),
                "recovery_rate_disclaimer": "Potential exposure represents review candidates; confirmed recovery is $0.00 unless verified settlement.",
            },
            "findings": findings,
            "limits": (
                "Deterministic synthetic towing revenue recovery only. Not tax, accounting, or legal advice. "
                "No autonomous changes to dispatch software or ERP authorized. Human review required."
            ),
        }
        report["receipt_sha256"] = digest(report)
        return report

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


class AuditPackageGenerator:
    """Generates reproducible, source-linked audit packages for regulatory and financial compliance."""

    def __init__(self, tenant_id: str) -> None:
        if not re.fullmatch(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$", tenant_id):
            raise InvalidSnapshot(f"invalid tenant_id format: {tenant_id!r}")
        self.tenant_id = tenant_id

    def generate_audit_package(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Generate a complete audit package from a compliance dataset."""
        if not isinstance(payload, dict):
            raise InvalidSnapshot("Payload must be a JSON object")

        if payload.get("dataset_type") != "SYNTHETIC_ONLY":
            raise InvalidSnapshot("Only explicitly labeled SYNTHETIC_ONLY datasets are admitted")

        p_tenant = payload.get("tenant_id")
        if not isinstance(p_tenant, str) or p_tenant != self.tenant_id:
            raise InvalidSnapshot(f"Tenant isolation mismatch: dataset '{p_tenant}' != engine '{self.tenant_id}'")

        as_of_date = parse_date(payload.get("as_of_date", str(date.today())))

        documents = _validate_rows(
            payload,
            "documents",
            {"document_id", "document_type", "title", "issue_date", "expiration_date", "jurisdiction"},
        )
        requirements = _validate_rows(
            payload,
            "requirements",
            {"requirement_id", "regulatory_body", "standard_code", "title", "mandatory"},
        )
        corrective_actions = _validate_rows(
            payload,
            "corrective_actions",
            {"action_id", "title", "assigned_to", "status", "due_date"},
        )

        _ensure_unique_ids(documents, "document_id", "documents")
        _ensure_unique_ids(requirements, "requirement_id", "requirements")
        _ensure_unique_ids(corrective_actions, "action_id", "corrective_actions")

        inventory = []
        expired_docs = []
        fresh_docs = []

        for doc in documents:
            i_date = parse_date(doc["issue_date"])
            e_date = parse_date(doc["expiration_date"])
            if e_date < i_date:
                raise InvalidSnapshot(f"document expiration precedes issue: {doc['document_id']}")

            is_expired = e_date < as_of_date
            days_to_expiry = (e_date - as_of_date).days

            doc_entry = {
                "document_id": doc["document_id"],
                "document_type": doc["document_type"],
                "title": doc["title"],
                "jurisdiction": doc["jurisdiction"],
                "issue_date": str(i_date),
                "expiration_date": str(e_date),
                "is_expired": is_expired,
                "days_to_expiry": days_to_expiry,
                "sha256": digest(doc),
            }
            inventory.append(doc_entry)
            if is_expired:
                expired_docs.append(doc_entry)
            else:
                fresh_docs.append(doc_entry)

        compliance_findings = []

        for req in requirements:
            req_id = req["requirement_id"]
            matched_docs = [d for d in fresh_docs if d["document_type"] == req.get("required_document_type")]
            is_satisfied = len(matched_docs) > 0
            if not is_satisfied and req.get("mandatory", "true").lower() in ("true", "1", "yes"):
                compliance_findings.append({
                    "finding_id": f"AUDIT-MISSING-{req_id}",
                    "severity": "HIGH",
                    "requirement_id": req_id,
                    "regulatory_body": req["regulatory_body"],
                    "standard_code": req["standard_code"],
                    "description": f"Mandatory requirement '{req['title']}' lacks active, unexpired supporting documentation.",
                    "authority": "HUMAN_REVIEW_REQUIRED",
                })

        open_actions = []
        resolved_actions = []
        for ca in corrective_actions:
            due = parse_date(ca["due_date"])
            is_overdue = due < as_of_date and ca["status"] not in ("completed", "closed", "verified")
            ca_entry = {
                "action_id": ca["action_id"],
                "title": ca["title"],
                "assigned_to": ca["assigned_to"],
                "status": ca["status"],
                "due_date": str(due),
                "is_overdue": is_overdue,
                "sha256": digest(ca),
            }
            if ca["status"] in ("completed", "closed", "verified"):
                resolved_actions.append(ca_entry)
            else:
                open_actions.append(ca_entry)

        manifest_items = [
            {"id": d["document_id"], "kind": "document", "sha256": d["sha256"]}
            for d in inventory
        ] + [
            {"id": c["action_id"], "kind": "corrective_action", "sha256": c["sha256"]}
            for c in open_actions + resolved_actions
        ]

        package = {
            "schema": "dispater.synthetic.audit_package.v1",
            "tenant_id": self.tenant_id,
            "as_of_date": str(as_of_date),
            "generated_at": str(date.today()),
            "status": "PACKAGE_GENERATED",
            "authority_state": "HOLD",
            "counts": {
                "total_documents": len(documents),
                "fresh_documents": len(fresh_docs),
                "expired_documents": len(expired_docs),
                "mandatory_requirements": len([r for r in requirements if r.get("mandatory") == "true"]),
                "compliance_exceptions": len(compliance_findings),
                "open_corrective_actions": len(open_actions),
                "resolved_corrective_actions": len(resolved_actions),
            },
            "document_inventory": inventory,
            "expired_documents": expired_docs,
            "compliance_findings": compliance_findings,
            "corrective_actions": {
                "open": open_actions,
                "resolved": resolved_actions,
            },
            "evidence_manifest": manifest_items,
            "disclaimer": (
                "Audit package generated for compliance readiness and evidentiary preparation only. "
                "Does not constitute legal certification or government regulatory clearance. Human verification required."
            ),
        }
        package["package_sha256"] = digest(package)
        return package
