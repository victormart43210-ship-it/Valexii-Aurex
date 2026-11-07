"""AUREX/OX shared business-record taxonomy for two-way research/audit intake.

Metadata-only routing: source declaration is not evidence of validity.
Company documents are NOT automatically financial documents.
No file content, payment action, compliance opinion, model training or secrets.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Visibility = Literal["public", "private"]
Kind = Literal[
    "invoice", "purchase_order", "field_ticket", "payment",
    "bank_statement", "general_ledger", "financial_statement",
    "tax_return", "tax_summary", "dot_inspection", "dot_audit",
    "insurance_certificate", "insurance_claim", "corporate_record",
    "contract", "source_code", "python_script", "manuscript",
    "research_dataset", "other", "unknown",
]
Route = Literal[
    "financial_review", "tax_review", "dot_review", "insurance_review",
    "corporate_review", "software_review", "research_review",
    "intake_triage",
]
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}\Z")
ROUTES: dict[str, Route] = {
    "invoice": "financial_review",
    "purchase_order": "financial_review",
    "field_ticket": "financial_review",
    "payment": "financial_review",
    "bank_statement": "financial_review",
    "general_ledger": "financial_review",
    "financial_statement": "financial_review",
    "tax_return": "tax_review",
    "tax_summary": "tax_review",
    "dot_inspection": "dot_review",
    "dot_audit": "dot_review",
    "insurance_certificate": "insurance_review",
    "insurance_claim": "insurance_review",
    "corporate_record": "corporate_review",
    "contract": "corporate_review",
    "source_code": "software_review",
    "python_script": "software_review",
    "manuscript": "research_review",
    "research_dataset": "research_review",
    "other": "intake_triage",
    "unknown": "intake_triage",
}
REVIEW_CHALLENGES: dict[Route, tuple[str, ...]] = {
    "financial_review": ("source_complete", "amount_and_unit_match", "independent_transaction_witness"),
    "tax_review": ("jurisdiction_and_period", "ledger_and_filing_reconciliation", "qualified_tax_review"),
    "dot_review": ("scope_and_effective_date", "inspection_and_safety_support", "qualified_compliance_review"),
    "insurance_review": ("coverage_and_effective_date", "underwriting_and_claim_support", "qualified_coverage_review"),
    "corporate_review": ("entity_identity", "contract_signatures", "authority_and_revision_history"),
    "software_review": ("commit_and_dependency_identity", "static_analysis", "reproducible_test"),
    "research_review": ("source_and_transcription", "alternative_hypotheses", "held_out_controls"),
    "intake_triage": ("source_origin", "domain_unknown", "human_classification_required"),
}


@dataclass(frozen=True, slots=True)
class EvidenceIntake:
    tenant_id: str
    source_id: str
    source_sha256: str
    declared_kind: Kind
    visibility: Visibility
    authorized_for_local_review: bool
    training_consent: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_id, str) or not _ID.fullmatch(self.tenant_id):
            raise ValueError("invalid tenant")
        if not isinstance(self.source_id, str) or not _ID.fullmatch(self.source_id):
            raise ValueError("invalid accession")
        if not isinstance(self.source_sha256, str) or not _SHA.fullmatch(self.source_sha256):
            raise ValueError("invalid source fingerprint")
        if self.declared_kind not in ROUTES or not isinstance(self.declared_kind, str):
            raise ValueError("invalid declared record type")
        if self.visibility not in ("public", "private"):
            raise ValueError("invalid visibility")
        if type(self.authorized_for_local_review) is not bool:
            raise ValueError("explicit review authorization required")
        if self.training_consent is not False:
            # Consent isn't granted through a catalog metadata bool.
            raise ValueError("separate verified training consent workflow required")


def propose_route(record: EvidenceIntake) -> dict[str, object]:
    """Return a proposed human-review route; never authorize file ingestion.

    Source type is customer-declared/unverified; authentication, actual bytes,
    authorization and independent classification are separate gates.
    """
    route = ROUTES[record.declared_kind]
    permitted_for_assessment = record.authorized_for_local_review
    return {
        "source_id": record.source_id,
        "tenant_id": record.tenant_id,
        "declared_kind": record.declared_kind,
        "candidate_route": route if permitted_for_assessment else "HOLD_NOT_AUTHORIZED",
        "review_challenges": list(REVIEW_CHALLENGES[route]) if permitted_for_assessment else [],
        "classification": "DECLARED_ONLY_NOT_CONTENT_VERIFIED",
        "capture": "METADATA_ONLY_NOT_FILE_READ",
        "visibility": record.visibility,
        "model_training": "DISABLED",
        "independent_verification": "NOT_VERIFIED",
        "regulatory_opinion": "NONE",
        "financial_authority": "HOLD",
        "effect_authority": "NONE",
    }
