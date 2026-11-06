"""
DISPATER Continuous Industrial Monitoring & Finding Invalidation Engine.

Inherited and adapted from MEDAURUS and BCXMET proven architecture:
- Evidence Freshness & Invalidation: When an approved rate or contract is superseded,
  all dependent historical findings are marked INVALIDATED or STALE and require requalification.
- Incremental Continuous Monitoring: Ingest newly arrived authorized operational tickets
  and evaluate against baseline rules without mutating historical audit records.
- Security Event Auditing: Log access rejections, tampering attempts, and boundary violations.
- Lifecycle Protection: Findings transition through strict states (DETECTED -> SUSPECTED -> CORROBORATED -> VERIFIED).
- Non-delegable: AI models NEVER close, verify, or execute financial actions.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from aurex.dispater_envelope import (
    CanonicalEvidenceEnvelope,
    DocumentCategory,
    compute_sha256,
)
from aurex.dispater_pipeline import IndustrialAuditPipeline, PipelineProcessingResult
from aurex.evidence_kernel import ActorKind


class MonitoringEventKind(enum.StrEnum):
    RECORD_INGESTED = "RECORD_INGESTED"
    CONTRACT_SUPERSEDED = "CONTRACT_SUPERSEDED"
    FINDING_INVALIDATED = "FINDING_INVALIDATED"
    TAMPER_DETECTED = "TAMPER_DETECTED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    INCREMENTAL_AUDIT_EVALUATED = "INCREMENTAL_AUDIT_EVALUATED"


GENESIS_SHA256 = "0" * 64


@dataclass(frozen=True)
class MonitoringAuditLogEntry:
    entry_id: str
    tenant_id: str
    event_kind: MonitoringEventKind
    timestamp_utc: str
    details: dict[str, Any]
    prev_sha256: str = GENESIS_SHA256
    entry_sha256: str = ""

    def __post_init__(self) -> None:
        if not self.entry_sha256:
            body = {
                "entry_id": self.entry_id,
                "tenant_id": self.tenant_id,
                "event_kind": self.event_kind.value,
                "timestamp_utc": self.timestamp_utc,
                "details": self.details,
                "prev_sha256": self.prev_sha256,
            }
            object.__setattr__(self, "entry_sha256", compute_sha256(body))

    def recompute_sha256(self) -> str:
        body = {
            "entry_id": self.entry_id,
            "tenant_id": self.tenant_id,
            "event_kind": self.event_kind.value,
            "timestamp_utc": self.timestamp_utc,
            "details": self.details,
            "prev_sha256": self.prev_sha256,
        }
        return compute_sha256(body)


class ContinuousMonitoringEngine:
    """Manages continuous stream evaluation, evidence freshness, and contract supersession."""

    def __init__(self, tenant_id: str) -> None:
        if not tenant_id:
            raise ValueError("tenant_id must be provided")
        self.tenant_id = tenant_id
        self.pipeline = IndustrialAuditPipeline(tenant_id=tenant_id)
        self.audit_log: list[MonitoringAuditLogEntry] = []
        self.historical_runs: list[PipelineProcessingResult] = []
        self.finding_lifecycle_registry: dict[str, dict[str, Any]] = {}

    def log_security_event(self, kind: MonitoringEventKind, details: dict[str, Any]) -> MonitoringAuditLogEntry:
        """Record immutable security / lifecycle events without secret leakage."""
        now_ts = datetime.now(UTC).isoformat()
        entry_id = f"sec-{compute_sha256(now_ts + str(len(self.audit_log)))[:16]}"
        entry = MonitoringAuditLogEntry(
            entry_id=entry_id,
            tenant_id=self.tenant_id,
            event_kind=kind,
            timestamp_utc=now_ts,
            details=details,
            prev_sha256=self.audit_log[-1].entry_sha256 if self.audit_log else GENESIS_SHA256,
        )
        self.audit_log.append(entry)
        return entry

    def verify_audit_chain(self) -> bool:
        """True only if every entry hash matches its content and links to its predecessor."""
        prev = GENESIS_SHA256
        for entry in self.audit_log:
            if entry.tenant_id != self.tenant_id or entry.prev_sha256 != prev:
                return False
            if entry.recompute_sha256() != entry.entry_sha256:
                return False
            prev = entry.entry_sha256
        return True

    def record_historical_audit(self, audit_result: PipelineProcessingResult) -> None:
        """Register completed historical audit run and index findings."""
        self.historical_runs.append(audit_result)
        all_findings = audit_result.qualified_findings + audit_result.withheld_findings
        for f in all_findings:
            fid = str(f.get("finding_id", "UNKNOWN"))
            state = "ACTIVE_QUALIFIED" if f in audit_result.qualified_findings else "HOLD_CANDIDATE"
            self.finding_lifecycle_registry[fid] = {
                "finding": f,
                "run_id": audit_result.run_id,
                "state": state,
                "registered_at": audit_result.timestamp_utc,
            }

    def process_contract_update(
        self, contract_id: str, new_contract_spec: dict[str, Any]
    ) -> list[str]:
        """Supersedes an active contract, invalidating affected prior findings."""
        is_update = contract_id in self.pipeline.active_contracts
        affected = self.pipeline.register_or_update_contract(contract_id, new_contract_spec)
        invalidated_ids: list[str] = []
        if affected or is_update or self.finding_lifecycle_registry:
            for fid, entry in self.finding_lifecycle_registry.items():
                finding_obj = entry["finding"]
                subject = str(finding_obj.get("subject", ""))
                code = str(finding_obj.get("code", ""))
                if contract_id in subject or "RATE" in code:
                    entry["state"] = "INVALIDATED_SUPERSEDED"
                    entry["invalidated_at"] = datetime.now(UTC).isoformat()
                    invalidated_ids.append(fid)

            self.log_security_event(
                MonitoringEventKind.CONTRACT_SUPERSEDED,
                {
                    "contract_id": contract_id,
                    "invalidated_count": len(invalidated_ids),
                    "invalidated_finding_ids": invalidated_ids,
                },
            )
        return invalidated_ids

    def ingest_incremental_record(
        self,
        source_id: str,
        source_record_id: str,
        category: DocumentCategory,
        raw_bytes: bytes,
        media_type: str,
    ) -> CanonicalEvidenceEnvelope:
        """Admit a newly received operational record in continuous monitoring mode."""
        env = self.pipeline.admit_document(
            source_id=source_id,
            source_record_id=source_record_id,
            document_category=category,
            raw_bytes=raw_bytes,
            media_type=media_type,
        )
        self.log_security_event(
            MonitoringEventKind.RECORD_INGESTED,
            {
                "source_record_id": source_record_id,
                "envelope_id": env.envelope_id,
                "content_sha256": env.source_content_sha256,
            },
        )
        return env

    def evaluate_incremental_monitoring(
        self, new_snapshot: dict[str, Any]
    ) -> PipelineProcessingResult:
        """Execute incremental continuous reconciliation without overwriting historical runs."""
        res = self.pipeline.execute_audit_run(
            snapshot=new_snapshot,
            actor_kind=ActorKind.SYSTEM,  # an automated monitor is never a human reviewer
            reviewer_id="monitoring-engine-continuous",
        )
        self.log_security_event(
            MonitoringEventKind.INCREMENTAL_AUDIT_EVALUATED,
            {
                "run_id": res.run_id,
                "qualified_findings": len(res.qualified_findings),
                "withheld_findings": len(res.withheld_findings),
            },
        )
        return res
