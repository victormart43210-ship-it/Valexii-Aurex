"""
DISPATER.AI Continuous Audit & Monitoring Engine.

Provides real-time ingestion of operational records, continuous rule evaluation
for missing inspections, operational measurement discrepancies, data quality failures,
and overdue corrective actions. Connects findings to AUREX Evidence Ledger
and XAELI 5-step explanations while enforcing AUREX-OX governance safeguards.
"""

from datetime import UTC, datetime
from typing import Any

from aurex.dispater_contracts import (
    AuditFinding,
    AuditReadinessAssessment,
    AuditRule,
    AuditVerificationReceipt,
    CorrectiveAction,
    MonitoringObservation,
    OperationalRecord,
    compute_sha256,
)
from aurex.dispater_intelligence import Xaeli5StepFinding
from aurex.evidence import EvidenceEnvelope

DEFAULT_AUDIT_RULES: list[AuditRule] = [
    AuditRule(
        rule_id="RULE-INSP-MISSING",
        rule_version="1.0.0",
        domain="SAFETY_COMPLIANCE",
        title="Mandatory Daily Pre-Job Safety Inspection",
        description="All pressure pumping, winch, and heavy towing equipment require an active inspection log before operation.",
        effective_date="2026-01-01",
        source_reference="OSHA 1910.120 / DOT CFR 396",
        severity="CRITICAL",
    ),
    AuditRule(
        rule_id="RULE-OPER-DISCREPANCY",
        rule_version="1.0.0",
        domain="OILFIELD_OPERATIONS",
        title="Operational Telemetry & Ticket Discrepancy",
        description="Field ticket reported operating hours/pressure must match physical sensor telemetry logs within 5% tolerance.",
        effective_date="2026-01-01",
        source_reference="API Spec 16D / Continuous Telemetry Audit Standard",
        severity="HIGH",
    ),
    AuditRule(
        rule_id="RULE-REMEDIATION-OVERDUE",
        rule_version="1.0.0",
        domain="SAFETY_COMPLIANCE",
        title="Overdue Audit Corrective Action",
        description="Corrective action items stemming from critical or high audit findings must be remediated within due date.",
        effective_date="2026-01-01",
        source_reference="ISO 9001:2015 Clause 10.2 / AUREX Audit Standard",
        severity="HIGH",
    ),
    AuditRule(
        rule_id="RULE-DATA-QUALITY",
        rule_version="1.0.0",
        domain="CONTRACTUAL_BILLING",
        title="Data Quality & Digest Integrity Check",
        description="Operational records must maintain valid cryptographic SHA-256 digests and complete field metadata.",
        effective_date="2026-01-01",
        source_reference="AUREX Evidence Ledgers Standard",
        severity="MEDIUM",
    ),
]


class ContinuousMonitoringEngine:
    """Continuous audit monitoring and governance engine for DISPATER.AI."""

    def __init__(self, rules: list[AuditRule] | None = None) -> None:
        self.rules: dict[str, AuditRule] = {
            r.rule_id: r for r in (rules or DEFAULT_AUDIT_RULES)
        }
        self.records: dict[str, list[OperationalRecord]] = {}
        self.observations: dict[str, list[MonitoringObservation]] = {}
        self.findings: dict[str, list[AuditFinding]] = {}
        self.corrective_actions: dict[str, list[CorrectiveAction]] = {}
        self.evidence_ledger: dict[str, list[EvidenceEnvelope]] = {}

    def ingest_record(self, record: OperationalRecord) -> MonitoringObservation:
        """Ingest operational record, store evidence envelope, and record observation."""
        tenant_id = record.tenant_id
        if tenant_id not in self.records:
            self.records[tenant_id] = []
            self.observations[tenant_id] = []
            self.findings[tenant_id] = []
            self.corrective_actions[tenant_id] = []
            self.evidence_ledger[tenant_id] = []

        self.records[tenant_id].append(record)

        # Create EvidenceEnvelope in AUREX ledger
        envelope = EvidenceEnvelope(
            evidence_id=f"EV-{record.record_id}",
            source=record.source,
            observed_at=record.timestamp,
            content_sha256=record.content_sha256,
            claims=[f"Ingested record {record.record_id} from {record.source}"],
        )
        self.evidence_ledger[tenant_id].append(envelope)

        # Emit Monitoring Observation
        obs = MonitoringObservation(
            observation_id=f"OBS-{record.record_id}-{len(self.observations[tenant_id]) + 1}",
            tenant_id=tenant_id,
            record_ids=[record.record_id],
            observed_at=record.timestamp,
            observation_type="RECORD_INGESTED",
            severity="ROUTINE",
            details={"source": record.source, "content_sha256": record.content_sha256},
        )
        self.observations[tenant_id].append(obs)
        return obs

    def evaluate_tenant_monitoring(self, tenant_id: str) -> list[AuditFinding]:
        """Evaluate continuous monitoring rules against ingested operational records."""
        tenant_recs = self.records.get(tenant_id, [])
        new_findings: list[AuditFinding] = []

        for rec in tenant_recs:
            p = rec.payload

            # Rule 1: Missing Inspection Check
            has_inspection = p.get("has_inspection_record", True)
            if not has_inspection:
                f_id = f"FND-INSP-{rec.record_id}"
                if not any(f.finding_id == f_id for f in self.findings.get(tenant_id, [])):
                    finding = AuditFinding(
                        finding_id=f_id,
                        rule_id="RULE-INSP-MISSING",
                        tenant_id=tenant_id,
                        severity="CRITICAL",
                        title=f"Missing Safety Inspection for Record {rec.record_id}",
                        description=f"Equipment unit '{p.get('equipment_id', 'UNKNOWN')}' operated without active pre-job safety inspection log.",
                        source_record_ids=[rec.record_id],
                        evidence_sha256=rec.content_sha256,
                        status="OPEN",
                        audit_event_ref=f"AUDIT-INSP-{rec.record_id}",
                    )
                    new_findings.append(finding)

            # Rule 2: Telemetry Discrepancy Check
            reported_hrs = float(p.get("operating_hours", p.get("pump_hours", 0.0)))
            sensor_hrs = float(p.get("telemetry_sensor_hours", reported_hrs))
            if abs(reported_hrs - sensor_hrs) > 1.0:
                f_id = f"FND-TELEMETRY-{rec.record_id}"
                if not any(f.finding_id == f_id for f in self.findings.get(tenant_id, [])):
                    finding = AuditFinding(
                        finding_id=f_id,
                        rule_id="RULE-OPER-DISCREPANCY",
                        tenant_id=tenant_id,
                        severity="HIGH",
                        title=f"Telemetry Hours Mismatch on Record {rec.record_id}",
                        description=f"Reported operating hours ({reported_hrs:.1f} hrs) conflict with sensor telemetry ({sensor_hrs:.1f} hrs).",
                        source_record_ids=[rec.record_id],
                        evidence_sha256=rec.content_sha256,
                        status="OPEN",
                        audit_event_ref=f"AUDIT-TELEMETRY-{rec.record_id}",
                    )
                    new_findings.append(finding)

            # Rule 4: Data Quality & Digest Verification Check
            expected_hash = compute_sha256(rec.payload)
            if rec.content_sha256 and rec.content_sha256 != expected_hash:
                f_id = f"FND-QUAL-{rec.record_id}"
                if not any(f.finding_id == f_id for f in self.findings.get(tenant_id, [])):
                    finding = AuditFinding(
                        finding_id=f_id,
                        rule_id="RULE-DATA-QUALITY",
                        tenant_id=tenant_id,
                        severity="MEDIUM",
                        title=f"Data Digest Mismatch on Record {rec.record_id}",
                        description="Content SHA-256 digest does not match recomputed payload hash.",
                        source_record_ids=[rec.record_id],
                        evidence_sha256=rec.content_sha256,
                        status="OPEN",
                        audit_event_ref=f"AUDIT-QUAL-{rec.record_id}",
                    )
                    new_findings.append(finding)

        # Rule 3: Overdue Corrective Action Check
        now_str = datetime.now(UTC).strftime("%Y-%m-%d")
        for ca in self.corrective_actions.get(tenant_id, []):
            if ca.retest_status == "PENDING" and ca.due_date < now_str:
                f_id = f"FND-OVERDUE-{ca.action_id}"
                if not any(f.finding_id == f_id for f in self.findings.get(tenant_id, [])):
                    finding = AuditFinding(
                        finding_id=f_id,
                        rule_id="RULE-REMEDIATION-OVERDUE",
                        tenant_id=tenant_id,
                        severity="HIGH",
                        title=f"Overdue Remediation Action {ca.action_id}",
                        description=f"Action item assigned to {ca.assigned_to} passed due date {ca.due_date} without remediation evidence.",
                        source_record_ids=[ca.finding_id],
                        evidence_sha256=ca.remediation_evidence_sha256 or "MISSING",
                        status="OPEN",
                        audit_event_ref=f"AUDIT-OVERDUE-{ca.action_id}",
                    )
                    new_findings.append(finding)

        if tenant_id not in self.findings:
            self.findings[tenant_id] = []
        self.findings[tenant_id].extend(new_findings)
        return self.findings[tenant_id]

    def convert_findings_to_xaeli(self, findings: list[AuditFinding]) -> list[Xaeli5StepFinding]:
        """Convert findings into canonical 5-step XAELI explanations."""
        xaeli_list: list[Xaeli5StepFinding] = []
        for f in findings:
            rule = self.rules.get(f.rule_id)
            rule_ref = rule.source_reference if rule else "AUREX Rule Engine"
            xaeli_list.append(Xaeli5StepFinding(
                exception_id=f.finding_id,
                now=f"Operational Audit Finding [{f.severity}]: {f.title}.",
                changed=f"Discrepancy detected across records: {', '.join(f.source_record_ids)}.",
                next="Assign corrective action to owner for remediation and independent retest.",
                why=f"{f.description} (Governing Reference: {rule_ref}).",
                proof=f"SHA-256 Digest: {f.evidence_sha256} | Audit Event: {f.audit_event_ref}",
                exposure_usd=0.0,
                audit_event_ref=f.audit_event_ref,
            ))
        return xaeli_list

    def assign_corrective_action(
        self, tenant_id: str, finding_id: str, assigned_to: str, due_date: str
    ) -> CorrectiveAction:
        """Assign corrective action for a finding."""
        ca_id = f"ACT-{finding_id}"
        ca = CorrectiveAction(
            action_id=ca_id,
            finding_id=finding_id,
            tenant_id=tenant_id,
            assigned_to=assigned_to,
            due_date=due_date,
            retest_status="PENDING",
        )
        if tenant_id not in self.corrective_actions:
            self.corrective_actions[tenant_id] = []
        self.corrective_actions[tenant_id].append(ca)

        # Update finding status
        for f in self.findings.get(tenant_id, []):
            if f.finding_id == finding_id:
                f.status = "ASSIGNED"
                f.assigned_owner = assigned_to

        return ca

    def submit_remediation_evidence(
        self, tenant_id: str, action_id: str, remediation_notes: str, evidence_payload: dict[str, Any]
    ) -> CorrectiveAction:
        """Submit remediation notes and compute evidence digest."""
        ev_digest = compute_sha256(evidence_payload)
        for ca in self.corrective_actions.get(tenant_id, []):
            if ca.action_id == action_id:
                ca.remediation_notes = remediation_notes
                ca.remediation_evidence_sha256 = ev_digest
                ca.retest_status = "INDEPENDENT_RETEST_REQUIRED"

                # Update finding status to REMEDIATED
                for f in self.findings.get(tenant_id, []):
                    if f.finding_id == ca.finding_id:
                        f.status = "REMEDIATED"
                return ca

        raise ValueError(f"Corrective action '{action_id}' not found for tenant '{tenant_id}'")

    def execute_independent_retest(
        self, tenant_id: str, action_id: str, retest_record: OperationalRecord, closed_by_human: str | None = None
    ) -> CorrectiveAction:
        """Execute independent retest on remediation evidence. Enforces human review for critical/high findings."""
        for ca in self.corrective_actions.get(tenant_id, []):
            if ca.action_id == action_id:
                target_finding = None
                for f in self.findings.get(tenant_id, []):
                    if f.finding_id == ca.finding_id:
                        target_finding = f
                        break

                # Governance Rule: Critical/High findings CANNOT be closed without human reviewer identification
                if target_finding and target_finding.severity in ("CRITICAL", "HIGH"):
                    if not closed_by_human or len(closed_by_human.strip()) == 0:
                        raise PermissionError(
                            f"AUREX SAFEGUARD: Critical/High finding '{target_finding.finding_id}' requires explicit human reviewer signature for closure. AI model self-closure prohibited."
                        )

                ca.retest_status = "RETEST_PASSED"
                ca.closed_at = datetime.now(UTC).isoformat()
                ca.closed_by_human = closed_by_human or "System Auditor"

                if target_finding:
                    target_finding.status = "CLOSED"

                return ca

        raise ValueError(f"Corrective action '{action_id}' not found for tenant '{tenant_id}'")

    def evaluate_audit_readiness(self, tenant_id: str) -> AuditReadinessAssessment:
        """Compute transparent audit readiness assessment based on actual evidence completeness."""
        recs = self.records.get(tenant_id, [])
        all_findings = self.findings.get(tenant_id, [])
        actions = self.corrective_actions.get(tenant_id, [])

        open_findings = [f for f in all_findings if f.status in ("OPEN", "ASSIGNED", "REMEDIATED")]
        critical_open = [f for f in open_findings if f.severity == "CRITICAL"]

        now_str = datetime.now(UTC).strftime("%Y-%m-%d")
        overdue_actions = [ca for ca in actions if ca.retest_status == "PENDING" and ca.due_date < now_str]

        coverage = 100.0 if recs else 0.0
        if recs:
            verified_count = sum(1 for r in recs if r.content_sha256)
            coverage = round((verified_count / len(recs)) * 100.0, 1)

        status = "AUDIT_READY"
        if critical_open or overdue_actions:
            status = "CRITICAL_DEFICIT"
        elif open_findings:
            status = "ACTION_REQUIRED"

        return AuditReadinessAssessment(
            tenant_id=tenant_id,
            total_records_evaluated=len(recs),
            evidence_coverage_pct=coverage,
            open_findings_count=len(open_findings),
            critical_findings_count=len(critical_open),
            overdue_actions_count=len(overdue_actions),
            readiness_status=status,
        )

    def generate_audit_receipt(self, tenant_id: str) -> AuditVerificationReceipt:
        """Generate immutable cryptographic audit receipt for tenant state."""
        recs = self.records.get(tenant_id, [])
        findings = self.findings.get(tenant_id, [])

        summary = {
            "OPEN": sum(1 for f in findings if f.status == "OPEN"),
            "ASSIGNED": sum(1 for f in findings if f.status == "ASSIGNED"),
            "REMEDIATED": sum(1 for f in findings if f.status == "REMEDIATED"),
            "CLOSED": sum(1 for f in findings if f.status == "CLOSED"),
        }

        root_data = [r.content_sha256 for r in recs]
        root_hash = compute_sha256(root_data)

        receipt = AuditVerificationReceipt(
            receipt_id=f"RCPT-{tenant_id}-{len(recs)}",
            tenant_id=tenant_id,
            scope_record_count=len(recs),
            findings_summary=summary,
            root_evidence_sha256=root_hash,
        )
        return receipt
