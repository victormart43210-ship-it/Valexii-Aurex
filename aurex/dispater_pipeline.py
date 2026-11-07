"""
DISPATER Canonical Unified Industrial Audit & Continuous Monitoring Pipeline.

Implements the 6-stage architecture under the LOCKED_DISPATER_MEDAURUS_BCXMET_DIRECTIVE:
Stage 1: Source Admission (bytes hash, MIME validation, 5MB body limits, tenant authorization)
Stage 2: Specialized Document Processing (task-appropriate adapter routing)
Stage 3: Canonical Evidence Normalization (versioned envelopes, immutability, field provenance)
Stage 4: Deterministic Financial Reconciliation (Decimal calculations, potential exposure separation)
Stage 5: AUREX Independent Verification (multi-root independence, negative checks, human review gates)
Stage 6: Audit Presentation (NOW -> CHANGED -> NEXT -> WHY -> PROOF dashboard contracts)

INVARIANTS:
- A model may never be its own verifier.
- System is never its own sole witness.
- Potential exposure is NEVER presented as recovered cash without verified payment proof.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from aurex.dispater_envelope import (
    CanonicalEvidenceEnvelope,
    DocumentCategory,
    EvidenceQualificationStatus,
    FieldProvenance,
    compute_sha256,
    normalize_currency_amount,
)
from aurex.dispater_intelligence import (
    RevenueLeakageEngine,
    digest,
)
from aurex.dispater_international import (
    DeterministicStructuredAdapter,
    PaddleOCRAdapter,
    QwenLocalInferenceAdapter,
    check_adapter_suitability,
)
from aurex.evidence_kernel import (
    ActorKind,
    EvidenceGraph,
    EvidenceRecord,
    challenge_finding,
)

MAX_SOURCE_BYTES = 5 * 1024 * 1024  # 5 MB ceiling


@dataclass
class PipelineProcessingResult:
    run_id: str
    tenant_id: str
    timestamp_utc: str
    envelopes_admitted: int
    reconciliation_summary: dict[str, Any]
    qualified_findings: list[dict[str, Any]]
    withheld_findings: list[dict[str, Any]]
    audit_receipt_sha256: str
    verification_status: str
    superseded_contracts: list[str] = field(default_factory=list)


class IndustrialAuditPipeline:
    """The canonical DISPATER 6-stage industrial audit pipeline."""

    def __init__(self, tenant_id: str) -> None:
        if not tenant_id or not isinstance(tenant_id, str):
            raise ValueError("Authorized tenant_id required for pipeline")
        self.tenant_id = tenant_id
        self.structured_adapter = DeterministicStructuredAdapter()
        self.ocr_adapter = PaddleOCRAdapter()
        self.qwen_advisory = QwenLocalInferenceAdapter()
        self.reconciliation_engine = RevenueLeakageEngine(tenant_id=tenant_id)
        self.evidence_graph = EvidenceGraph(tenant_id=tenant_id)
        self.admitted_envelopes: dict[str, CanonicalEvidenceEnvelope] = {}
        self.active_contracts: dict[str, dict[str, Any]] = {}

    # STAGE 1: Source Admission
    def admit_document(
        self,
        source_id: str,
        source_record_id: str,
        document_category: DocumentCategory,
        raw_bytes: bytes,
        media_type: str,
    ) -> CanonicalEvidenceEnvelope:
        if len(raw_bytes) > MAX_SOURCE_BYTES:
            raise ValueError(f"Payload exceeds 5MB ceiling: {len(raw_bytes)} bytes")
        if not source_id or not source_record_id:
            raise ValueError("source_id and source_record_id are mandatory")

        content_sha256 = compute_sha256(raw_bytes)
        envelope_id = f"env-{content_sha256[:16]}-{source_record_id}"

        # STAGE 2: Specialized Processing
        adapter_key = check_adapter_suitability(media_type)
        provenance_fields: list[FieldProvenance] = []

        if adapter_key == "china-paddleocr":
            ocr_res = self.ocr_adapter.process(raw_bytes, {"media_type": media_type})
            preview = f"OCR_{ocr_res.get('status')}"
            field_prov = FieldProvenance(
                field_name="ocr_text",
                raw_value=str(ocr_res.get("text", "")),
                normalized_value=str(ocr_res.get("text", "")),
                adapter_id=self.ocr_adapter.candidate_id,
                adapter_version=self.ocr_adapter.metadata.version,
                adapter_digest=self.ocr_adapter.metadata.code_or_model_digest,
                page_or_row_locator="page_1",
                confidence=0.90,
                qualification_status=EvidenceQualificationStatus.PENDING_QUALIFICATION,
            )
            provenance_fields.append(field_prov)
        else:
            struct_res = self.structured_adapter.process(raw_bytes, {"media_type": media_type})
            preview = json.dumps(struct_res.get("fields", {}))[:200]
            for k, v in struct_res.get("fields", {}).items():
                norm_val: Any = v
                if "amount" in k or "rate" in k or "total" in k:
                    try:
                        norm_val = normalize_currency_amount(v)
                    except ValueError:
                        norm_val = str(v)
                field_prov = FieldProvenance(
                    field_name=k,
                    raw_value=str(v),
                    normalized_value=norm_val,
                    adapter_id=self.structured_adapter.candidate_id,
                    adapter_version=self.structured_adapter.metadata.version,
                    adapter_digest=self.structured_adapter.metadata.code_or_model_digest,
                    page_or_row_locator="row_1",
                    confidence=1.0,
                    qualification_status=EvidenceQualificationStatus.QUALIFIED_INDEPENDENT,
                )
                provenance_fields.append(field_prov)

        # STAGE 3: Canonical Evidence Normalization
        envelope = CanonicalEvidenceEnvelope(
            envelope_id=envelope_id,
            schema_version="dispater.evidence.envelope.v1",
            tenant_id=self.tenant_id,
            source_id=source_id,
            source_record_id=source_record_id,
            document_category=document_category,
            source_content_sha256=content_sha256,
            byte_count=len(raw_bytes),
            media_type=media_type,
            ingested_at_utc=datetime.now(UTC).isoformat(),
            provenance_fields=provenance_fields,
            raw_payload_preview=preview,
        )

        self.admitted_envelopes[envelope_id] = envelope

        # Register root evidence in Evidence Integrity Kernel
        ev_rec = EvidenceRecord(
            evidence_id=envelope_id,
            tenant_id=self.tenant_id,
            source_system=source_id,
            source_record_id=source_record_id,
            content_sha256=content_sha256,
            acquired_at=datetime.now(UTC),
            parents=(),
        )
        self.evidence_graph.add(ev_rec)

        return envelope

    # Contract Invalidation / Freshness Check (BCXMET / MEDAURUS pattern)
    def register_or_update_contract(self, contract_id: str, contract_spec: dict[str, Any]) -> list[str]:
        """Ingests a contract or superseding contract. Returns affected prior findings invalidated."""
        invalidated_findings: list[str] = []
        if contract_id in self.active_contracts:
            prior = self.active_contracts[contract_id]
            if prior != contract_spec:
                # Mark supersession
                invalidated_findings.append(f"FINDINGS_FOR_CONTRACT_{contract_id}")
        self.active_contracts[contract_id] = contract_spec
        return invalidated_findings

    # STAGE 4, 5, 6: Reconciliation, Independent Verification, and Presentation
    def execute_audit_run(
        self,
        snapshot: dict[str, Any],
        actor_kind: ActorKind = ActorKind.HUMAN,
        reviewer_id: str = "auditor-principal-01",
    ) -> PipelineProcessingResult:
        run_id = f"run-audit-{compute_sha256(json.dumps(snapshot, sort_keys=True))[:16]}"
        now_ts = datetime.now(UTC).isoformat()

        # STAGE 4: Deterministic Financial Reconciliation
        raw_report = self.reconciliation_engine.reconcile_records(snapshot)

        qualified_findings: list[dict[str, Any]] = []
        withheld_findings: list[dict[str, Any]] = []

        # STAGE 5: AUREX Independent Verification
        for f in raw_report.get("findings", []):
            exposure = Decimal(str(f.get("exposure_usd", "0")))

            # Negative check: non-finite exposure
            if not exposure.is_finite() or exposure < 0:
                f["qualification"] = "WITHHELD_NON_FINITE_OR_NEGATIVE"
                withheld_findings.append(f)
                continue

            # Adversarial challenge check against known obligations
            challenge_problems = challenge_finding(f, self.tenant_id, set())
            if challenge_problems:
                f["qualification"] = f"WITHHELD_CHALLENGE_FAILED_{','.join(challenge_problems)}"
                withheld_findings.append(f)
                continue

            # Multi-root corroboration check:
            # We map evidence records to graph roots by matching envelope source_record_id or content hash
            ev_ids: list[str] = []
            for ev_item in f.get("evidence", []):
                rec_hash = ev_item.get("record_sha256", "")
                # Find matching envelope by hash or by subject/source record reference
                matched_env = next(
                    (e for e in self.admitted_envelopes.values()
                     if e.source_content_sha256 == rec_hash or e.source_record_id in f.get("subject", "")),
                    None
                )
                if matched_env and matched_env.envelope_id not in ev_ids:
                    ev_ids.append(matched_env.envelope_id)

            # If evidence has independent roots, qualify; else hold
            try:
                if len(ev_ids) >= 2 and self.evidence_graph.independent_root_count(ev_ids) >= 2:
                    # Non-model qualification check
                    if actor_kind is ActorKind.MODEL:
                        f["qualification"] = "HOLD_MODEL_CANNOT_VERIFY"
                        withheld_findings.append(f)
                    else:
                        f["qualification"] = "QUALIFIED_INDEPENDENT_CORROBORATION"
                        f["authority"] = "HUMAN_REVIEW_REQUIRED"
                        qualified_findings.append(f)
                else:
                    # Single-source or derived finding remains candidate with single-root tag
                    f["qualification"] = "SINGLE_ROOT_UNCONFIRMED"
                    f["authority"] = "HOLD_NEEDS_INDEPENDENT_WITNESS"
                    withheld_findings.append(f)
            except Exception as e:
                f["qualification"] = f"WITHHELD_ERROR_{e}"
                withheld_findings.append(f)

        # STAGE 6: Audit Presentation
        # Generate tamper-evident audit receipt
        summary_payload = {
            "run_id": run_id,
            "tenant_id": self.tenant_id,
            "timestamp_utc": now_ts,
            "admitted_documents": len(self.admitted_envelopes),
            "qualified_count": len(qualified_findings),
            "withheld_count": len(withheld_findings),
            "exposure_summary": raw_report.get("summary", {}),
            "limits": "Deterministic revenue audit. AI is advisory only. Not financial authority.",
        }
        receipt_sha256 = digest(summary_payload)

        return PipelineProcessingResult(
            run_id=run_id,
            tenant_id=self.tenant_id,
            timestamp_utc=now_ts,
            envelopes_admitted=len(self.admitted_envelopes),
            reconciliation_summary=raw_report.get("summary", {}),
            qualified_findings=qualified_findings,
            withheld_findings=withheld_findings,
            audit_receipt_sha256=receipt_sha256,
            verification_status="HOLD_PENDING_HUMAN_SIGNATURE",
        )
