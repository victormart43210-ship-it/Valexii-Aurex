"""Frozen shared contracts for industrial records.

Version ``valexii.industrial.contracts.v1`` is the only accepted contract version.
Existing DISPATER finding codes and qualifications are inputs. They are not renamed.
"""

from __future__ import annotations

CONTRACT_VERSION = "valexii.industrial.contracts.v1"
EXPLANATION_VERSION = "valexii.xaeli.explanation.v1"

OBJECT_TYPES = (
    "company",
    "job",
    "well",
    "equipment",
    "crew",
    "contract",
    "field_ticket",
    "invoice",
    "rate_schedule",
    "approval",
    "payment",
)

EVENT_TYPES = (
    "job_recorded",
    "equipment_used",
    "ticket_submitted",
    "invoice_issued",
    "rate_cited",
    "contract_cited",
    "approval_recorded",
    "payment_recorded",
)

QUALIFIERS = (
    "concerns",
    "uses",
    "bills",
    "governed_by",
    "priced_by",
    "approves",
    "settles",
    "assigns",
    "located_at",
)

# A recorded disposition is an observed label. It does not move money.
APPROVAL_DISPOSITIONS = (
    "PENDING_HUMAN_REVIEW",
    "RECORDED_APPROVAL",
    "RECORDED_REJECTION",
    "WITHHELD",
)

CLAIM_BY_QUALIFICATION = {
    "SUSPECTED_DISCREPANCY": "SUSPECTED_EXPOSURE",
    "INSUFFICIENT_EVIDENCE": "UNVERIFIED_INTERPRETATION",
    "STATUS_INCONSISTENCY": "CALCULATED_DISCREPANCY",
}

OPTIONAL_TABLES = {
    "companies": {"company_id", "customer_id"},
    "wells": {"well_id", "job_id"},
    "crews": {"crew_id", "job_id"},
    "contracts": {"contract_id", "job_id"},
    "approvals": {"approval_id", "invoice_id", "disposition"},
}


def object_id(object_type: str, raw_id: str) -> str:
    if object_type not in OBJECT_TYPES:
        raise ValueError(f"unknown object type: {object_type}")
    if not raw_id or len(raw_id) > 256:
        raise ValueError("object id is empty or too long")
    return f"{object_type}:{raw_id}"
