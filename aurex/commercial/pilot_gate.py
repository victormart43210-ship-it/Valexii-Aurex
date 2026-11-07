"""Evidence-bounded, privacy-minimized financial pilot scorecard.

Checks claimed aggregate pilot measurements against proposed commercialization
thresholds. NOT a third-party audit, release admission or achieved product rating.
"""

from __future__ import annotations

import re
from typing import Any

TARGET_RATING = "9.9/10 (ASPIRATIONAL, NOT ACHIEVED)"
REQUIRED_KEYS = frozenset({
    "customer_pseudonym", "paid_pilot", "consent_attested", "contract_attested",
    "independent_review_attested", "measurement_days", "documents_reviewed",
    "documents_text_available", "critical_fields_labeled", "critical_fields_correct",
    "reconciliation_tp", "reconciliation_fp", "reconciliation_fn", "reconciliation_tn",
    "critical_discrepancy_misses", "baseline_review_minutes",
    "assisted_review_minutes", "collected_revenue_cents", "fully_loaded_cost_cents",
    "costs_attested", "privacy_incidents", "source_integrity_attested",
})
COUNT_FIELDS = frozenset({
    "measurement_days", "documents_reviewed", "documents_text_available",
    "critical_fields_labeled", "critical_fields_correct", "reconciliation_tp",
    "reconciliation_fp", "reconciliation_fn", "reconciliation_tn",
    "critical_discrepancy_misses", "baseline_review_minutes",
    "assisted_review_minutes", "collected_revenue_cents",
    "fully_loaded_cost_cents", "privacy_incidents",
})
ATTESTED_FIELDS = frozenset({
    "paid_pilot", "consent_attested", "contract_attested",
    "independent_review_attested", "costs_attested", "source_integrity_attested",
})
PSEUDONYM = re.compile(r"pilot-[A-Za-z0-9_-]{3,40}\Z")


def _int(v: Any) -> bool:
    return type(v) is int and 0 <= v <= 10**12


def _ratio(num: int, denominator: int) -> float | None:
    return round(num / denominator, 4) if denominator > 0 else None


def evaluate_financial_pilots(payload: Any) -> dict[str, Any]:
    """Evaluate de-identified aggregates; never infer real-world evidence or authority.

    No private IDs, document content, customer names or raw evidence are returned.
    Even a completely passing claim set remains HOLD until externally verified.
    """
    report: dict[str, Any] = {
        "target": TARGET_RATING,
        "status": "HOLD",
        "candidate_thresholds_met": False,
        "independent_evidence_verified_by_this_tool": False,
        "production_admission": "NOT VERIFIED",
        "authority": "NONE",
        "pilot_count": 0,
        "measurements": {},
        "blocking_gates": [],
    }
    gates: list[str] = []
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "pilots"}:
        report["blocking_gates"] = ["INVALID_TOP_LEVEL_SCHEMA"]
        return report
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        report["blocking_gates"] = ["INVALID_SCHEMA_VERSION"]
        return report
    pilots = payload["pilots"]
    if not isinstance(pilots, list) or len(pilots) > 25:
        report["blocking_gates"] = ["INVALID_PILOT_COLLECTION"]
        return report
    report["pilot_count"] = len(pilots)
    if len(pilots) < 3:
        gates.append("THREE_INDEPENDENT_PAID_PILOTS_REQUIRED")
    seen: set[str] = set()
    for pilot in pilots:
        if not isinstance(pilot, dict) or set(pilot) != REQUIRED_KEYS:
            report["blocking_gates"] = ["INVALID_PILOT_SCHEMA"]
            return report
        pseudonym = pilot["customer_pseudonym"]
        if not isinstance(pseudonym, str) or not PSEUDONYM.fullmatch(pseudonym):
            report["blocking_gates"] = ["INVALID_PSEUDONYM"]
            return report
        if pseudonym in seen:
            report["blocking_gates"] = ["DUPLICATE_CUSTOMER_PILOT"]
            return report
        seen.add(pseudonym)
        if any(not _int(pilot[field]) for field in COUNT_FIELDS):
            report["blocking_gates"] = ["INVALID_NONNEGATIVE_INTEGER_MEASUREMENT"]
            return report
        if any(type(pilot[field]) is not bool for field in ATTESTED_FIELDS):
            report["blocking_gates"] = ["INVALID_ATTESTATION_TYPE"]
            return report
        if pilot["documents_text_available"] > pilot["documents_reviewed"]:
            report["blocking_gates"] = ["INCONSISTENT_DOCUMENT_COUNTS"]
            return report
        if pilot["critical_fields_correct"] > pilot["critical_fields_labeled"]:
            report["blocking_gates"] = ["INCONSISTENT_FIELD_COUNTS"]
            return report
        if pilot["assisted_review_minutes"] > pilot["baseline_review_minutes"]:
            gates.append("TIME_SAVINGS_NOT_POSITIVE")
        if pilot["fully_loaded_cost_cents"] > pilot["collected_revenue_cents"]:
            gates.append("NEGATIVE_GROSS_MARGIN")
        if pilot["measurement_days"] < 30:
            gates.append("THIRTY_DAY_CUSTOMER_EVIDENCE_REQUIRED")
        if pilot["documents_reviewed"] < 100:
            gates.append("ONE_HUNDRED_DOCUMENTS_PER_PILOT_REQUIRED")
        if not all(pilot[key] for key in ATTESTED_FIELDS):
            gates.append("MISSING_CUSTOMER_OR_REVIEW_ATTESTATION")
        if pilot["privacy_incidents"] > 0:
            gates.append("PRIVACY_INCIDENT_PRESENT")
        if pilot["critical_discrepancy_misses"] > 0:
            gates.append("CRITICAL_DISCREPANCY_MISS_PRESENT")

    def total(k: str) -> int:
        return sum(p[k] for p in pilots)

    docs = total("documents_reviewed")
    fields = total("critical_fields_labeled")
    tp = total("reconciliation_tp")
    fp = total("reconciliation_fp")
    fn = total("reconciliation_fn")
    tn = total("reconciliation_tn")
    revenue = total("collected_revenue_cents")
    baseline = total("baseline_review_minutes")
    coverage = _ratio(total("documents_text_available"), docs)
    accuracy = _ratio(total("critical_fields_correct"), fields)
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    time_saved = _ratio(baseline - total("assisted_review_minutes"), baseline)
    gross_margin = _ratio(revenue - total("fully_loaded_cost_cents"), revenue)
    report["measurements"] = {
        "documents_reviewed": docs,
        "critical_fields_labeled": fields,
        "reconciliation_decisions": tp + fp + fn + tn,
        "text_coverage": coverage,
        "critical_field_accuracy": accuracy,
        "reconciliation_precision": precision,
        "reconciliation_recall": recall,
        "human_time_saved_fraction": time_saved,
        "gross_margin_fraction": gross_margin,
    }
    if docs < 1000:
        gates.append("ONE_THOUSAND_REVIEWED_DOCUMENTS_REQUIRED")
    if fields < 5000:
        gates.append("FIVE_THOUSAND_LABELED_FIELDS_REQUIRED")
    if tp + fp + fn + tn < 1000:
        gates.append("ONE_THOUSAND_RECONCILIATION_DECISIONS_REQUIRED")
    # Compare integer counts, never rounded display ratios, to avoid boundary inflation.
    if docs == 0 or total("documents_text_available") * 100 < docs * 95:
        gates.append("TEXT_COVERAGE_BELOW_95_PERCENT")
    if fields == 0 or total("critical_fields_correct") * 100 < fields * 99:
        gates.append("CRITICAL_FIELD_ACCURACY_BELOW_99_PERCENT")
    if tp + fp == 0 or tp * 100 < (tp + fp) * 99:
        gates.append("RECONCILIATION_PRECISION_BELOW_99_PERCENT")
    if tp + fn == 0 or tp * 100 < (tp + fn) * 95:
        gates.append("RECONCILIATION_RECALL_BELOW_95_PERCENT")
    if baseline == 0 or (baseline - total("assisted_review_minutes")) * 100 < baseline * 40:
        gates.append("HUMAN_TIME_SAVING_BELOW_40_PERCENT")
    if revenue == 0 or (revenue - total("fully_loaded_cost_cents")) * 100 < revenue * 70:
        gates.append("GROSS_MARGIN_BELOW_70_PERCENT")
    report["blocking_gates"] = sorted(set(gates))
    report["candidate_thresholds_met"] = not gates
    # A self-reported input file is never an independent witness of a real paid pilot.
    report["status"] = "HOLD_EXTERNAL_AUDIT_REQUIRED" if not gates else "HOLD"
    return report
