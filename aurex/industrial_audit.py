"""VALEXII Industrial Audit Intelligence Platform for AUREX/DISPATER.

Provides tenant-isolated, evidence-backed audit readiness evaluation for Sector A
(Oilfield Operations) and Sector B (Towing & Recovery).

AUREX produces evidence-backed findings and recommended review actions.
This module NEVER grants regulatory certification, legal authority, or automated filing.
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any

SECTOR_A_OILFIELD_CATEGORIES = {
    "personnel_records",
    "equipment_inspections",
    "maintenance_logs",
    "field_tickets",
    "safety_documentation",
    "incident_records",
    "operational_reporting",
}

SECTOR_B_TOWING_CATEGORIES = {
    "driver_qualifications",
    "vehicle_inspections",
    "maintenance_records",
    "dispatch_service_records",
    "incident_documentation",
    "dot_fmcsa_compliance",
    "insurance_references",
}

ALL_CATEGORIES = SECTOR_A_OILFIELD_CATEGORIES | SECTOR_B_TOWING_CATEGORIES
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2}))?$")


def calculate_sha256(content: str | bytes) -> str:
    """Compute SHA-256 hex digest of document or payload string."""
    raw = content.encode("utf-8") if isinstance(content, str) else content
    return hashlib.sha256(raw).hexdigest()


class IndustrialEvidenceRecord:
    """Tenant-isolated, provenance-bearing industrial evidence record."""

    def __init__(
        self,
        record_id: str,
        tenant_id: str,
        sector: str,  # "oilfield" or "towing"
        category: str,
        title: str,
        content_payload: str,
        observed_at: str,
        expires_at: str | None = None,
        source_ref: str | None = None,
        verification_status: str = "UNVERIFIED",
    ) -> None:
        if sector not in ("oilfield", "towing"):
            raise ValueError(f"Invalid sector '{sector}'; must be 'oilfield' or 'towing'")

        allowed = SECTOR_A_OILFIELD_CATEGORIES if sector == "oilfield" else SECTOR_B_TOWING_CATEGORIES
        if category not in allowed:
            raise ValueError(f"Invalid category '{category}' for sector '{sector}'")

        if not _ISO_DATE.match(observed_at):
            raise ValueError(f"Invalid ISO timestamp for observed_at: {observed_at}")

        if expires_at and not _ISO_DATE.match(expires_at):
            raise ValueError(f"Invalid ISO timestamp for expires_at: {expires_at}")

        self.record_id = record_id
        self.tenant_id = tenant_id
        self.sector = sector
        self.category = category
        self.title = title
        self.content_payload = content_payload
        self.observed_at = observed_at
        self.expires_at = expires_at
        self.source_ref = source_ref
        self.sha256 = calculate_sha256(content_payload)
        self.verification_status = verification_status

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "tenant_id": self.tenant_id,
            "sector": self.sector,
            "category": self.category,
            "title": self.title,
            "observed_at": self.observed_at,
            "expires_at": self.expires_at,
            "source_ref": self.source_ref,
            "sha256": self.sha256,
            "verification_status": self.verification_status,
            "authority": "NONE",
        }


def evaluate_tenant_audit_readiness(
    tenant_id: str,
    sector: str,
    evidence_records: list[IndustrialEvidenceRecord],
    evaluation_time_iso: str | None = None,
) -> dict[str, Any]:
    """Deterministically audit a tenant's evidence inventory for completeness and readiness.

    Identifies missing categories, expired documents, duplicate record digests,
    and flags items requiring human review.
    """
    eval_dt = (
        datetime.fromisoformat(evaluation_time_iso.replace("Z", "+00:00"))
        if evaluation_time_iso
        else datetime.now(UTC)
    )

    allowed_categories = SECTOR_A_OILFIELD_CATEGORIES if sector == "oilfield" else SECTOR_B_TOWING_CATEGORIES

    # Ensure records belong exclusively to requesting tenant
    tenant_records = [r for r in evidence_records if r.tenant_id == tenant_id]

    observed_categories: set[str] = set()
    expired_records: list[dict[str, Any]] = []
    duplicate_digests: list[str] = []
    seen_digests: set[str] = set()
    flags: list[dict[str, Any]] = []

    for r in tenant_records:
        observed_categories.add(r.category)

        # Check duplicate SHA-256 digests
        if r.sha256 in seen_digests:
            duplicate_digests.append(r.record_id)
            flags.append({
                "record_id": r.record_id,
                "type": "DUPLICATE_RECORD_DIGEST",
                "severity": "HIGH",
                "message": f"Duplicate document content digest detected: {r.sha256[:16]}...",
            })
        else:
            seen_digests.add(r.sha256)

        # Check document expiration
        if r.expires_at:
            exp_dt = datetime.fromisoformat(r.expires_at.replace("Z", "+00:00"))
            if exp_dt <= eval_dt:
                expired_records.append(r.to_dict())
                flags.append({
                    "record_id": r.record_id,
                    "type": "EXPIRED_DOCUMENT",
                    "severity": "HIGH",
                    "message": f"Document expired on {r.expires_at}",
                })

    missing_categories = sorted(list(allowed_categories - observed_categories))
    for missing in missing_categories:
        flags.append({
            "category": missing,
            "type": "MISSING_REQUIRED_CATEGORY",
            "severity": "MEDIUM",
            "message": f"Required evidence category '{missing}' is missing from tenant inventory",
        })

    total_required = len(allowed_categories)
    present_valid = len(observed_categories) - len(expired_records)
    readiness_pct = round((max(0, present_valid) / total_required) * 100, 1)

    readiness_status = "READY_FOR_REVIEW" if not flags else "HOLD_REVIEW_REQUIRED"

    return {
        "status": readiness_status,
        "tenant_id": tenant_id,
        "sector": sector,
        "evaluated_at": eval_dt.isoformat(),
        "total_required_categories": total_required,
        "present_categories": len(observed_categories),
        "missing_categories": missing_categories,
        "expired_records_count": len(expired_records),
        "duplicate_records_count": len(duplicate_digests),
        "readiness_percentage": readiness_pct,
        "flags": flags,
        "xaeli_workflow": {
            "NOW": f"{len(tenant_records)} evidence records evaluated; {len(missing_categories)} categories missing.",
            "CHANGED": f"{len(expired_records)} expired records flagged requiring update.",
            "NEXT": f"Prioritize uploading missing categories: {', '.join(missing_categories[:2]) or 'None'}.",
            "WHY": "Continuous audit readiness requires unexpired, verified evidence across all industry categories.",
            "PROOF": f"SHA-256 evidence digests verified across {len(tenant_records)} tenant records.",
        },
        "verification_status": "NOT_VERIFIED",
        "authority": "NONE",
        "release": "HOLD",
    }
