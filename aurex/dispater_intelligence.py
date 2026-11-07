"""DISPATER Industrial Revenue Intelligence & Audit Reconciliation Engine.

Implements deterministic, decimal-safe operational revenue reconciliation,
equipment ticket matching, approved rate schedule verification, SHA-256 evidence
digest generation, CSV formula-injection defenses, and canonical 5-step XAELI findings
(NOW -> CHANGED -> NEXT -> WHY -> PROOF).

Towing & Recovery Workflow Scope:
Dispatch -> Contract -> Rate -> Expected Charge -> Invoice -> Payment -> Deposit -> Finding -> Review -> Recovery

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

# Financial exposure classifications
UNDERBILLING = "POTENTIAL_UNDERBILLING"
OVERBILLING = "POTENTIAL_OVERBILLING"
UNVERIFIED = "UNVERIFIED_EXPOSURE"
CONFIRMED = "CONFIRMED_RECOVERY"


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
        raise InvalidSnapshot(f"failed to parse decimal amount: {value!r}") from exc


def parse_date(value: str) -> date:
    """Parse strict ISO-8601 YYYY-MM-DD date."""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise InvalidSnapshot(f"date must be ISO YYYY-MM-DD: {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidSnapshot(f"invalid calendar date: {value!r}") from exc


def _validate_rows(
    rows: list[dict[str, Any]],
    expected_fields: set[str],
    context: str,
) -> None:
    if not isinstance(rows, list):
        raise InvalidSnapshot(f"{context} must be a list of records")
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise InvalidSnapshot(f"{context}[{idx}] must be a dict")
        missing = expected_fields - set(row.keys())
        if missing:
            raise InvalidSnapshot(f"{context}[{idx}] missing required fields: {sorted(missing)}")
        for k, v in row.items():
            if isinstance(v, str):
                if len(v) > MAX_FIELD_LEN:
                    raise InvalidSnapshot(f"{context}[{idx}].{k} exceeds max field length of {MAX_FIELD_LEN}")


def _ensure_unique_ids(rows: list[dict[str, Any]], id_key: str, context: str) -> None:
    seen: set[str] = set()
    for row in rows:
        val = str(row[id_key])
        if val in seen:
            raise InvalidSnapshot(f"duplicate identifier {val!r} detected in {context}")
        seen.add(val)


class RevenueLeakageEngine:
    """Reconciles towing operational dispatch, contracts, billing, and settlements."""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id

    def reconcile_records(self, dataset: dict[str, Any]) -> dict[str, Any]:
        """Execute deterministic revenue reconciliation across operational and billing datasets."""
        if not isinstance(dataset, dict):
            raise InvalidSnapshot("Dataset must be a JSON object")

        if dataset.get("dataset_type") not in ("SYNTHETIC_ONLY", None):
            raise InvalidSnapshot("Only explicitly labeled SYNTHETIC_ONLY datasets are admitted")

        if dataset.get("dataset_type") == "SYNTHETIC_ONLY":
            dataset_tenant = dataset.get("tenant_id", "default")
            if dataset_tenant != self.tenant_id:
                raise InvalidSnapshot(
                    f"Tenant isolation mismatch: dataset tenant '{dataset_tenant}' != engine tenant '{self.tenant_id}'"
                )

        req_keys = {"jobs", "invoices", "rates", "payments"}
        missing_root = req_keys - set(dataset.keys())
        if missing_root:
            raise InvalidSnapshot(f"dataset missing top-level components: {sorted(missing_root)}")

        jobs = dataset["jobs"]
        invoices = dataset["invoices"]
        rates = dataset["rates"]
        payments = dataset["payments"]
        deposits = dataset.get("deposits", [])
        disputes = dataset.get("disputes", [])

        # Validate structure
        _validate_rows(jobs, {"job_id", "customer_id", "service_code", "date"}, "jobs")
        _validate_rows(invoices, {"invoice_id", "job_id", "amount", "status"}, "invoices")
        _validate_rows(rates, {"rate_id", "customer_id", "service_code", "amount", "start", "end"}, "rates")
        _validate_rows(payments, {"payment_id", "invoice_id", "amount"}, "payments")
        if deposits:
            _validate_rows(deposits, {"deposit_id", "amount", "date", "reference"}, "deposits")
        if disputes:
            _validate_rows(disputes, {"dispute_id", "invoice_id", "disputed_amount", "reason"}, "disputes")

        _ensure_unique_ids(jobs, "job_id", "jobs")
        _ensure_unique_ids(invoices, "invoice_id", "invoices")
        _ensure_unique_ids(rates, "rate_id", "rates")
        _ensure_unique_ids(payments, "payment_id", "payments")
        if deposits:
            _ensure_unique_ids(deposits, "deposit_id", "deposits")
        if disputes:
            _ensure_unique_ids(disputes, "dispute_id", "disputes")

        # Validate formats
        for j in jobs:
            parse_date(j["date"])
        for inv in invoices:
            parse_money(inv["amount"])
        for r in rates:
            parse_money(r["amount"])
            s = parse_date(r["start"])
            e = parse_date(r["end"])
            if s > e:
                raise InvalidSnapshot(f"rate {r['rate_id']} start date {s} is after end date {e}")
        for p in payments:
            parse_money(p["amount"])
        for d in deposits:
            parse_money(d["amount"])
            parse_date(d["date"])
        for disp in disputes:
            parse_money(disp["disputed_amount"])

        by_job_invoices: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for inv in invoices:
            by_job_invoices[inv["job_id"]].append(inv)

        by_invoice_payments: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for p in payments:
            by_invoice_payments[p["invoice_id"]].append(p)

        by_invoice_disputes: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for disp in disputes:
            by_invoice_disputes[disp["invoice_id"]].append(disp)

        findings: list[dict[str, Any]] = []
        totals = {
            UNDERBILLING: Decimal("0.00"),
            OVERBILLING: Decimal("0.00"),
            UNVERIFIED: Decimal("0.00"),
            CONFIRMED: Decimal("0.00"),
        }

        job_ids = {j["job_id"] for j in jobs}
        invoice_ids = {inv["invoice_id"] for inv in invoices}

        # 1. Job-level evaluation (Dispatch -> Rates -> Invoices)
        for job in jobs:
            j_id = job["job_id"]
            cust_id = job["customer_id"]
            svc = job["service_code"]
            j_date = parse_date(job["date"])
            relevant_invoices = sorted(by_job_invoices[j_id], key=lambda i: str(i["invoice_id"]))

            # Unbilled completed tow/job
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
                        next_action="Review field dispatch completion log and draft invoice according to agreed schedule.",
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

            # Contract & Rate schedule matching
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
                target_rate = active_rates[0]
                target_inv = relevant_invoices[0]
                billed_amt = parse_money(target_inv["amount"])
                expected_amt = parse_money(target_rate["amount"])

                # Check storage days surcharge
                storage_days = job.get("storage_days")
                if storage_days is not None:
                    try:
                        days = int(storage_days)
                        if days > 0:
                            daily_rate_items = [
                                r for r in rates
                                if r["customer_id"] == cust_id
                                and r["service_code"] == "STORAGE_DAILY"
                                and parse_date(r["start"]) <= j_date <= parse_date(r["end"])
                            ]
                            if daily_rate_items:
                                storage_expected = parse_money(daily_rate_items[0]["amount"]) * Decimal(days)
                                billed_storage = parse_money(str(target_inv.get("storage_amount", "0.00")))
                                storage_diff = billed_storage - storage_expected
                                if storage_diff < 0:
                                    s_exp = abs(storage_diff)
                                    totals[UNDERBILLING] += s_exp
                                    findings.append(
                                        self._create_finding(
                                            exposure_class=UNDERBILLING,
                                            code="UNBILLED_STORAGE_DAYS",
                                            subject=target_inv["invoice_id"],
                                            severity="HIGH",
                                            records=[("job", job), ("invoice", target_inv), ("rate", daily_rate_items[0])],
                                            exposure=s_exp,
                                            now=f"Impound lot storage for {days} days on job {j_id} billed ${billed_storage} vs expected ${storage_expected}.",
                                            changed=f"Underbilled storage days delta ${s_exp} identified from lot release logs.",
                                            next_action="Re-bill supplemental impound storage fee to registered owner or insurer.",
                                            why="Unbilled storage days accumulate substantial unrecovered yard holding costs.",
                                            proof=f"Job SHA:{digest(job)[:12]}, Rate SHA:{digest(daily_rate_items[0])[:12]}",
                                        )
                                    )
                    except ValueError:
                        pass

                # Check after hours surcharge
                if job.get("after_hours") is True or job.get("after_hours") == "true":
                    after_hours_rates = [
                        r for r in rates
                        if r["customer_id"] == cust_id
                        and r["service_code"] == "AFTER_HOURS_SURCHARGE"
                        and parse_date(r["start"]) <= j_date <= parse_date(r["end"])
                    ]
                    if after_hours_rates:
                        ah_expected = parse_money(after_hours_rates[0]["amount"])
                        billed_ah = parse_money(str(target_inv.get("after_hours_amount", "0.00")))
                        if billed_ah != ah_expected:
                            ah_diff = billed_ah - ah_expected
                            ah_exp_class = UNDERBILLING if ah_diff < 0 else OVERBILLING
                            ah_abs = abs(ah_diff)
                            totals[ah_exp_class] += ah_abs
                            findings.append(
                                self._create_finding(
                                    exposure_class=ah_exp_class,
                                    code="INCORRECT_AFTER_HOURS_SURCHARGE",
                                    subject=target_inv["invoice_id"],
                                    severity="MEDIUM",
                                    records=[("job", job), ("invoice", target_inv), ("rate", after_hours_rates[0])],
                                    exposure=ah_abs,
                                    now=f"After-hours tow {j_id} billed surcharge ${billed_ah} vs contracted rate ${ah_expected}.",
                                    changed=f"Surcharge discrepancy of ${ah_abs} detected on night/weekend dispatch ticket.",
                                    next_action="Adjust invoice surcharge line item according to contracted rate amendment.",
                                    why="Improper after-hours rate applications breach roadside club contracts.",
                                    proof=f"Job SHA:{digest(job)[:12]}, Rate SHA:{digest(after_hours_rates[0])[:12]}",
                                )
                            )

                # Base rate discrepancy
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

        # 2. Invoice-level evaluation (Orphans, Payments, Motor-Clubs, Disputes)
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

            # Check disputes
            for disp in by_invoice_disputes[inv_id]:
                disp_amt = parse_money(disp["disputed_amount"])
                totals[UNVERIFIED] += disp_amt
                findings.append(
                    self._create_finding(
                        exposure_class=UNVERIFIED,
                        code="DISPUTED_CHARGE",
                        subject=inv_id,
                        severity="HIGH",
                        records=[("invoice", inv), ("dispute", disp)],
                        exposure=disp_amt,
                        now=f"Customer dispute logged for invoice {inv_id}: ${disp_amt} disputed ({disp['reason']}).",
                        changed="Disputed billing status placed on hold pending proof of service.",
                        next_action="Assemble signed delivery receipt and photograph evidence for dispute adjudication.",
                        why="Unresolved billing disputes jeopardize commercial carrier relationships.",
                        proof=f"Dispute SHA:{digest(disp)[:12]}, Inv SHA:{digest(inv)[:12]}",
                    )
                )

            payments_for_inv = by_invoice_payments[inv_id]
            total_paid = sum((parse_money(p["amount"]) for p in payments_for_inv), Decimal("0.00"))
            billed = parse_money(inv["amount"])
            delta = total_paid - billed

            # Motor club partial payment evaluation
            is_motor_club = inv.get("customer_type") == "MOTOR_CLUB" or "club" in str(inv.get("customer_id", "")).lower()
            if is_motor_club and total_paid > 0 and total_paid < billed:
                abs_short = billed - total_paid
                totals[UNDERBILLING] += abs_short
                evidence_records = [("invoice", inv)] + [("payment", p) for p in payments_for_inv]
                findings.append(
                    self._create_finding(
                        exposure_class=UNDERBILLING,
                        code="MOTOR_CLUB_SHORT_PAY",
                        subject=inv_id,
                        severity="HIGH",
                        records=evidence_records,
                        exposure=abs_short,
                        now=f"Motor club {inv.get('customer_id', '')} short-paid invoice {inv_id}: paid ${total_paid} of ${billed} (short ${abs_short}).",
                        changed="Automated remittance deduction or disallowed mileage applied by motor club portal.",
                        next_action="Submit dispatch GPS geo-fence logs and secondary call-out proof to appeal deduction.",
                        why="Motor clubs routinely apply administrative deductions that can be reclaimed with evidence.",
                        proof=f"Invoice SHA:{digest(inv)[:12]}, Payments: {len(payments_for_inv)}",
                    )
                )
            else:
                code = None
                if inv["status"] == "paid" and delta != 0:
                    code = "PAID_STATUS_UNRECONCILED"
                elif inv["status"] != "paid" and delta > 0:
                    code = "OVERPAYMENT"
                elif inv["status"] != "paid" and total_paid > 0 and delta < 0:
                    code = "PARTIAL_PAYMENT"
                if code:
                    abs_delta = abs(delta)
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

        # 3. Payment & Deposit-level evaluation
        total_payments_amount = sum((parse_money(p["amount"]) for p in payments), Decimal("0.00"))
        total_deposits_amount = sum((parse_money(d["amount"]) for d in deposits), Decimal("0.00"))

        if deposits and total_payments_amount != total_deposits_amount:
            dep_delta = abs(total_payments_amount - total_deposits_amount)
            totals[UNVERIFIED] += dep_delta
            findings.append(
                self._create_finding(
                    exposure_class=UNVERIFIED,
                    code="DEPOSIT_RECONCILIATION_GAP",
                    subject="BANK_DEPOSIT_BATCH",
                    severity="HIGH",
                    records=[("deposit_summary", {"payments_total": str(total_payments_amount), "deposits_total": str(total_deposits_amount)})],
                    exposure=dep_delta,
                    now=f"Bank settlement deposits total ${total_deposits_amount} vs received payments ${total_payments_amount} (variance ${dep_delta}).",
                    changed="Bank settlement batch discrepancy detected between merchant gateway and bank statement.",
                    next_action="Reconcile daily credit card batch settlements against bank deposit credit entries.",
                    why="Unreconciled merchant deposits hide gateway processing fee anomalies or delayed funds.",
                    proof=f"Payments total: ${total_payments_amount}, Deposits total: ${total_deposits_amount}",
                )
            )

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
                "human_verified_amount_usd": "0.00",
                "recovery_rate_disclaimer": "Identified exposure is a candidate for human review, not confirmed recovery.",
                "collectible_amount_usd": str(totals[UNDERBILLING]),
                "submitted_recovery_usd": "0.00",
            },
            "findings": findings,
        }

        audit_summary["receipt_sha256"] = digest({k: v for k, v in audit_summary.items() if k != "receipt_sha256"})
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
        """Construct canonical 5-step XAELI audit finding."""
        evidence = [{"kind": kind, "record_sha256": digest(rec)} for kind, rec in records]
        finding_body = {
            "finding_id": f"FND-{code}-{subject}",
            "code": code,
            "subject": subject,
            "severity": severity,
            "exposure_usd": str(exposure.quantize(Decimal("0.01"))),
            "exposure_class": exposure_class,
            "evidence": evidence,
            "authority": "HUMAN_REVIEW_REQUIRED",
            "xaeli_explanation": {
                "now": sanitize_formula_field(now),
                "changed": sanitize_formula_field(changed),
                "next": sanitize_formula_field(next_action),
                "why": sanitize_formula_field(why),
                "proof": sanitize_formula_field(proof),
            },
        }
        finding_body["finding_sha256"] = digest(finding_body)
        return finding_body


def verify_receipt(report: dict[str, Any]) -> bool:
    """True only when report's receipt_sha256 matches recomputation over its body."""
    if not isinstance(report, dict) or "receipt_sha256" not in report:
        return False
    body = {k: v for k, v in report.items() if k not in ("receipt_sha256", "receipt_auth", "receipt_mac")}
    try:
        return hmac_equal(digest(body), str(report.get("receipt_sha256", "")))
    except (TypeError, ValueError):
        return False


def hmac_equal(a: str, b: str) -> bool:
    """Timing-safe string comparison."""
    import hmac
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


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
