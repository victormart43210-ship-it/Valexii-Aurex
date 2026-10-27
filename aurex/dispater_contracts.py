"""
DISPATER.AI Versioned Audit Data Contracts and Schemas.

Defines Pydantic v2 schemas for operational records, monitoring observations,
versioned audit rules, findings, corrective actions, audit readiness,
and cryptographic verification receipts.
"""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def compute_sha256(data: Any) -> str:
    """Compute deterministic SHA-256 digest of dict, list, string, or Pydantic model."""
    if isinstance(data, BaseModel):
        serialized = data.model_dump_json()
    elif isinstance(data, (dict, list)):
        serialized = json.dumps(data, sort_keys=True, default=str)
    else:
        serialized = str(data)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class OperationalRecord(BaseModel):
    """Normalized ingestion contract for operational logs, tickets, and telemetry."""

    record_id: str
    tenant_id: str
    source: str  # e.g., "OILFIELD_FIELD_TICKET", "TOWING_DISPATCH", "EQUIPMENT_INSPECTION", "PRESSURE_TELEMETRY"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, Any] = Field(default_factory=dict)
    content_sha256: str = ""
    is_independently_verified: bool = False

    def model_post_init(self, __context: Any) -> None:
        if not self.content_sha256:
            self.content_sha256 = compute_sha256(self.payload)


class MonitoringObservation(BaseModel):
    """Continuous observation event emitted during continuous monitoring."""

    observation_id: str
    tenant_id: str
    record_ids: list[str] = Field(default_factory=list)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    observation_type: str  # "RECORD_INGESTED", "MISSING_INSPECTION", "RECORD_DISCREPANCY", "ANOMALY_DETECTED", "QUALITY_FAILURE"
    severity: str = "ROUTINE"  # "CRITICAL", "HIGH", "MEDIUM", "ROUTINE"
    details: dict[str, Any] = Field(default_factory=dict)
    evidence_sha256: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.evidence_sha256:
            self.evidence_sha256 = compute_sha256({
                "obs_id": self.observation_id,
                "type": self.observation_type,
                "records": self.record_ids,
                "details": self.details,
            })


class AuditRule(BaseModel):
    """Configurable and versioned operational/compliance audit rule."""

    rule_id: str
    rule_version: str = "1.0.0"
    domain: str  # "OILFIELD_OPERATIONS", "TOWING_RECOVERY", "EQUIPMENT_MAINTENANCE", "CONTRACTUAL_BILLING", "SAFETY_COMPLIANCE"
    title: str
    description: str
    effective_date: str
    source_reference: str
    severity: str = "HIGH"  # "CRITICAL", "HIGH", "MEDIUM", "ROUTINE"
    is_active: bool = True


class AuditFinding(BaseModel):
    """Discrepancy, non-compliance, or anomaly finding produced by audit evaluation."""

    finding_id: str
    rule_id: str
    tenant_id: str
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "ROUTINE"
    title: str
    description: str
    source_record_ids: list[str] = Field(default_factory=list)
    evidence_sha256: str = ""
    status: str = "OPEN"  # "OPEN", "ASSIGNED", "REMEDIATED", "INDEPENDENT_RETEST", "CLOSED"
    assigned_owner: str | None = None
    audit_event_ref: str = ""
    is_demo: bool = True


class CorrectiveAction(BaseModel):
    """Remediation tracking and independent retest workflow contract."""

    action_id: str
    finding_id: str
    tenant_id: str
    assigned_to: str
    due_date: str
    remediation_notes: str | None = None
    remediation_evidence_sha256: str | None = None
    retest_status: str = "PENDING"  # "PENDING", "RETEST_PASSED", "RETEST_FAILED"
    closed_at: str | None = None
    closed_by_human: str | None = None


class AuditReadinessAssessment(BaseModel):
    """Continuous audit readiness evaluation result."""

    tenant_id: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    total_records_evaluated: int
    evidence_coverage_pct: float
    open_findings_count: int
    critical_findings_count: int
    overdue_actions_count: int
    readiness_status: str  # "AUDIT_READY", "ACTION_REQUIRED", "CRITICAL_DEFICIT"
    assessment_sha256: str = ""
    disclaimer: str = (
        "COMPLIANCE READINESS ASSESSMENT ONLY — DOES NOT CONSTITUTE LEGAL "
        "CERTIFICATION OR GUARANTEED REGULATORY COMPLIANCE."
    )

    def model_post_init(self, __context: Any) -> None:
        if not self.assessment_sha256:
            self.assessment_sha256 = compute_sha256({
                "tenant": self.tenant_id,
                "records": self.total_records_evaluated,
                "coverage": self.evidence_coverage_pct,
                "open": self.open_findings_count,
                "critical": self.critical_findings_count,
            })


class AuditVerificationReceipt(BaseModel):
    """Cryptographic audit verification receipt."""

    receipt_id: str
    tenant_id: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    scope_record_count: int
    findings_summary: dict[str, int] = Field(default_factory=dict)
    root_evidence_sha256: str
    receipt_sha256: str = ""
    authority_disclaimer: str = (
        "AUREX-OX EVIDENCE RECEIPT ONLY. MODEL OUTPUT AUTHORITY = NONE. "
        "FINANCIAL AUTHORITY = NONE. INDUSTRIAL CONTROL AUTHORITY = NONE."
    )

    def model_post_init(self, __context: Any) -> None:
        if not self.receipt_sha256:
            self.receipt_sha256 = compute_sha256({
                "receipt_id": self.receipt_id,
                "tenant": self.tenant_id,
                "issued_at": self.issued_at.isoformat(),
                "root_sha256": self.root_evidence_sha256,
            })
