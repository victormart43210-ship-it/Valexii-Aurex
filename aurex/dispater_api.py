"""DISPATER Industrial Revenue Audit & Dashboard API.

Routes under `/v1/dispater`:
- POST /reconciliation
- GET  /findings
- GET  /dashboard
- GET  /runs, GET /runs/{run_id}, GET /runs/{run_id}/export?format=json|csv
- POST /observations

Security model (fail closed):
- Bearer tokens are bound to tenants via AUREX_DISPATER_TENANT_GRANTS, a JSON object
  mapping the SHA-256 hex digest of a token to a list of authorized tenant IDs
  (e.g. {"<sha256(token)>": ["tenant-a"]}). No grants configured => every request is denied.
- A tenant ID supplied by the caller (query or body) is only a selector; it must be
  in the principal's grants. Unauthorized tenants get a uniform 403 whether or not they exist.
- Data is persisted per tenant in aurex.dispater_store. Financial authority is always NONE.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from aurex import dispater_store
from aurex.ascendancy.proposal import propose
from aurex.customer_sovereignty import assert_no_effect
from aurex.dispater_audit_package import AuditPackageEngine
from aurex.dispater_ingest import IngestError, ingest_source
from aurex.dispater_intelligence import (
    InvalidSnapshot,
    RevenueLeakageEngine,
    receipt_authenticity,
    report_to_csv,
)
from aurex.dispater_lifecycle import authorization_decision, deletion_request, retention_request

logger = logging.getLogger("aurex.dispater")

MAX_BODY_BYTES = 5 * 1024 * 1024


class _BodyTooLarge(Exception):
    pass


class BodyLimitMiddleware:
    """Enforce MAX_BODY_BYTES on the raw ASGI receive stream for DISPATER routes.

    FastAPI parses request bodies before route dependencies run, so the limit must
    sit below it to stop chunked or dishonest-Content-Length uploads from buffering.
    """

    prefix = "/v1/dispater"

    def __init__(self, app: Any, max_bytes: int | None = None) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or not scope["path"].startswith(self.prefix):
            await self.app(scope, receive, send)
            return
        limit = self.max_bytes if self.max_bytes is not None else MAX_BODY_BYTES
        exceeded = False

        async def guarded_send(message: Any) -> None:
            # Once the limit is hit, the framework's own error reply (e.g. 400) is discarded.
            if not exceeded:
                await send(message)

        async def reject() -> None:
            response = JSONResponse({"detail": "Request body too large"}, status_code=413)
            await response(scope, receive, send)

        for name, value in scope["headers"]:
            if name == b"content-length":
                text = value.decode("latin-1")
                if not text.isdigit() or int(text) > limit:
                    await reject()
                    return

        total = 0

        async def limited_receive() -> Any:
            nonlocal total, exceeded
            message = await receive()
            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > limit:
                    exceeded = True
                    raise _BodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, guarded_send)
        except _BodyTooLarge:
            pass
        if exceeded:
            await reject()


router = APIRouter(prefix="/v1/dispater", tags=["dispater"])

MAX_ROWS = 2000
TENANT_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$"
SYSTEM_STATE = {
    "production_release": "HOLD",
    "financial_authority": "NONE",
    "external_paid_inference": "OFF",
    "third_party_contact": "NONE",
    "training_reuse": "NOT_AUTHORIZED",
    "deletion": "NOT_IMPLEMENTED",
    "deletion_request": "RECORDED_NOT_EXECUTED",
    "external_anchor": "NOT_VERIFIED",
    "customer_decides": True,
}


def current_system_state() -> dict[str, Any]:
    from aurex.dispater_at_rest import encryption_status

    state = dict(SYSTEM_STATE)
    state["encryption_at_rest"] = encryption_status()
    return state


@dataclass(frozen=True)
class Principal:
    token_sha256: str
    tenants: frozenset[str]


def _load_grants() -> dict[str, frozenset[str]]:
    raw = os.environ.get("AUREX_DISPATER_TENANT_GRANTS", "")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("grants must be an object")
        return {
            str(k).lower(): frozenset(str(t) for t in v)
            for k, v in data.items()
            if isinstance(v, list)
        }
    except (ValueError, TypeError):
        logger.error("AUREX_DISPATER_TENANT_GRANTS is malformed; denying all DISPATER access")
        return {}


def authenticate_principal(authorization: Annotated[str | None, Header()] = None) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Missing or malformed Authorization header"
        )
    supplied = authorization[7:]
    if not supplied or not supplied.isascii() or supplied != supplied.strip():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Malformed authorization credentials")
    grants = _load_grants()
    if not grants:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "DISPATER tenant authorization is not configured"
        )
    digest = hashlib.sha256(supplied.encode()).hexdigest()
    match: frozenset[str] | None = None
    for key, tenants in grants.items():  # constant-time over every entry
        if hmac.compare_digest(key, digest):
            match = tenants
    if match is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid authorization credentials")
    return Principal(token_sha256=digest, tenants=match)


def authorize_tenant(principal: Principal, tenant_id: str) -> str:
    if tenant_id not in principal.tenants:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tenant not authorized")
    return tenant_id


PrincipalDep = Annotated[Principal, Depends(authenticate_principal)]
TenantQuery = Annotated[str, Query(pattern=TENANT_PATTERN, max_length=64)]


class ReconciliationRequest(BaseModel):
    tenant_id: str = Field(pattern=TENANT_PATTERN, max_length=64)
    dataset_type: str = Field(default="SYNTHETIC_ONLY")
    jobs: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    invoices: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    rates: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    payments: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    equipment: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)
    labor: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)

    @field_validator("dataset_type")
    @classmethod
    def _synthetic_only(cls, v: str) -> str:
        if v != "SYNTHETIC_ONLY":
            raise ValueError("Only SYNTHETIC_ONLY datasets are admitted for demonstration.")
        return v


def _internal_error(op: str, exc: BaseException | None = None) -> HTTPException:
    logger.error("dispater %s failed (%s)", op, type(exc).__name__ if exc else "error")
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal DISPATER error")


@router.post("/reconciliation")
def run_reconciliation(payload: ReconciliationRequest, principal: PrincipalDep) -> dict[str, Any]:
    assert_no_effect()
    authorize_tenant(principal, payload.tenant_id)
    try:
        # Preserve legacy request identity when optional hour collections were absent.
        dataset = payload.model_dump(exclude={"equipment", "labor"})
        for collection in ("equipment", "labor"):
            rows = getattr(payload, collection)
            if rows is not None:
                dataset[collection] = rows
        report = RevenueLeakageEngine(tenant_id=payload.tenant_id).reconcile_records(
            dataset
        )
    except InvalidSnapshot as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except Exception as exc:
        raise _internal_error("reconciliation", exc) from exc
    try:
        stored, _created = dispater_store.save_run(payload.tenant_id, report)
    except Exception as exc:
        raise _internal_error("persistence", exc) from exc
    return stored


class DocumentRequest(BaseModel):
    tenant_id: str = Field(pattern=TENANT_PATTERN, max_length=64)
    filename: str = Field(min_length=1, max_length=180)
    kind: Literal["csv", "json", "pdf", "xlsx", "png", "jpeg"]
    content_base64: str = Field(min_length=1, max_length=2_000_000)
    declared_byte_length: int | None = Field(default=None, ge=0, le=5_000_000)


@router.post("/documents")
def ingest_document(payload: DocumentRequest, principal: PrincipalDep) -> dict[str, Any]:
    """Ingest one synthetic document and reconcile it. The wrapper is not the receipt."""
    assert_no_effect()
    authorize_tenant(principal, payload.tenant_id)
    try:
        raw = base64.b64decode(payload.content_base64, validate=True)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid document base64") from exc
    try:
        if payload.declared_byte_length is not None and payload.declared_byte_length != len(raw):
            raise IngestError("declared byte length does not match the received source bytes")
        batch = ingest_source(payload.tenant_id, payload.filename, raw, kind=payload.kind)
        report = RevenueLeakageEngine(tenant_id=payload.tenant_id).reconcile_records(batch["dataset"])
        stored, _created = dispater_store.save_run(payload.tenant_id, report)
    except (IngestError, InvalidSnapshot) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except Exception as exc:
        raise _internal_error("document ingestion", exc) from exc
    return {
        "authority_state": "HOLD",
        "financial_authority": "NONE",
        "ingestion_authenticated": False,
        "ocr_status": "NOT_INSTALLED",
        "ingestion": {
            "source_sha256": batch["source_sha256"],
            "filename": batch["filename"],
            "kind": batch["kind"],
            "processor": batch["processor"],
            "provenance": batch["provenance"],
            "field_provenance": batch["field_provenance"],
            "limits": batch["limits"],
            "byte_length": batch["byte_length"],
            "byte_length_scope": batch["byte_length_scope"],
            "caller_declared_byte_length_accepted": False,
            "source_bytes_status": batch["source_bytes_status"],
            "source_identity": batch["source_identity"],
        },
        "report": stored,
    }


class AuditPackageRequest(BaseModel):
    tenant_id: str = Field(pattern=TENANT_PATTERN, max_length=64)
    documents: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    vehicles: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    drivers: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    include_reconciliation_report: bool = True


@router.post("/audit-package/generate")
def generate_audit_package(payload: AuditPackageRequest, principal: PrincipalDep) -> dict[str, Any]:
    """Stateless, advisory package. Nothing is cached in memory; the caller keeps the returned manifest."""
    assert_no_effect()
    authorize_tenant(principal, payload.tenant_id)
    engine = AuditPackageEngine(tenant_id=payload.tenant_id)
    try:
        evaluation = engine.evaluate_compliance(
            documents=payload.documents, vehicles=payload.vehicles, drivers=payload.drivers
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid audit package inputs") from exc
    report = _latest(payload.tenant_id) if payload.include_reconciliation_report else None
    try:
        return engine.export_audit_package(evaluation, report)
    except Exception as exc:
        raise _internal_error("audit-package", exc) from exc


def _latest(tenant_id: str) -> dict[str, Any] | None:
    try:
        return dispater_store.latest_run(tenant_id)
    except Exception as exc:
        raise _internal_error("read", exc) from exc


@router.get("/findings")
def get_findings(principal: PrincipalDep, tenant_id: TenantQuery) -> dict[str, Any]:
    authorize_tenant(principal, tenant_id)
    run = _latest(tenant_id)
    if not run:
        return {"tenant_id": tenant_id, "status": "NO_AUDIT_RUN", "findings": [], "count": 0}
    return {
        "tenant_id": tenant_id,
        "run_id": run["run_id"],
        "status": run.get("status"),
        "dataset_sha256": run.get("dataset_sha256"),
        "receipt_sha256": run.get("receipt_sha256"),
        "financial_summary": run.get("financial_summary"),
        "findings": run.get("findings", []),
        "count": len(run.get("findings", [])),
    }


@router.get("/dashboard")
def get_dashboard(principal: PrincipalDep, tenant_id: TenantQuery) -> dict[str, Any]:
    authorize_tenant(principal, tenant_id)
    run = _latest(tenant_id)
    if not run:
        return {
            "tenant_id": tenant_id,
            "status": "INITIALIZED",
            "last_reconciliation_sha256": None,
            "identified_exposure_usd": "0.00",
            "withheld_unresolved_usd": "0.00",
            "confirmed_recovery_usd": "0.00",
            "receipt_binding": None,
            "monitoring_event_count": dispater_store.monitor_event_count(tenant_id),
            "ocr_status": "NOT_INSTALLED",
            "finding_counts": {"total": 0, "critical": 0, "high": 0, "medium": 0},
            "recent_findings": [],
            "system_state": current_system_state(),
        }
    findings = run.get("findings", [])
    summary = run.get("financial_summary", {})
    return {
        "tenant_id": tenant_id,
        "run_id": run["run_id"],
        "status": run.get("status"),
        "last_reconciliation_sha256": run.get("receipt_sha256"),
        "identified_exposure_usd": summary.get("identified_exposure_usd", "0.00"),
        "potential_underbilling_usd": summary.get("potential_underbilling_usd", "0.00"),
        "potential_overbilling_usd": summary.get("potential_overbilling_usd", "0.00"),
        "unverified_exposure_usd": summary.get("unverified_exposure_usd", "0.00"),
        "withheld_unresolved_usd": summary.get("withheld_unresolved_usd", "0.00"),
        "human_confirmed_discrepancy_usd": "0.00",
        "confirmed_recovery_usd": "0.00",
        "receipt_binding": run.get("receipt_binding"),
        "monitoring_event_count": dispater_store.monitor_event_count(tenant_id),
        "ocr_status": "NOT_INSTALLED",
        "finding_counts": {
            "total": len(findings),
            "critical": sum(1 for f in findings if f.get("severity") == "CRITICAL"),
            "high": sum(1 for f in findings if f.get("severity") == "HIGH"),
            "medium": sum(1 for f in findings if f.get("severity") == "MEDIUM"),
        },
        "recent_findings": findings[:10],
        "system_state": current_system_state(),
    }


@router.get("/runs")
def get_runs(
    principal: PrincipalDep, tenant_id: TenantQuery, limit: Annotated[int, Query(ge=1, le=200)] = 50
) -> dict[str, Any]:
    authorize_tenant(principal, tenant_id)
    try:
        runs = dispater_store.list_runs(tenant_id, limit)
    except Exception as exc:
        raise _internal_error("history", exc) from exc
    return {"tenant_id": tenant_id, "runs": runs, "count": len(runs)}


def _run_or_404(tenant_id: str, run_id: str) -> dict[str, Any]:
    try:
        run = dispater_store.get_run(tenant_id, run_id)
    except Exception as exc:
        raise _internal_error("read", exc) from exc
    if not run:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Run not found")
    return run


@router.get("/runs/{run_id}")
def get_run(
    run_id: Annotated[str, Path(pattern=r"^run-[0-9a-f]{32}$")],
    principal: PrincipalDep,
    tenant_id: TenantQuery,
) -> dict[str, Any]:
    authorize_tenant(principal, tenant_id)
    return _run_or_404(tenant_id, run_id)


@router.get("/runs/{run_id}/export", response_model=None)
def export_run(
    run_id: Annotated[str, Path(pattern=r"^run-[0-9a-f]{32}$")],
    principal: PrincipalDep,
    tenant_id: TenantQuery,
    format: Literal["json", "csv"] = "json",
) -> Response | dict[str, Any]:
    assert_no_effect()
    authorize_tenant(principal, tenant_id)
    run = _run_or_404(tenant_id, run_id)
    if format == "csv":
        return Response(
            report_to_csv(run),
            media_type="text/csv",
            headers={
                "Cache-Control": "no-store",
                "X-Aurex-Third-Party-Release": "none",
                "X-Aurex-Training-Reuse": "not-authorized",
            },
        )
    return JSONResponse(
        {
            "export_authorization": "TENANT_BEARER",
            "third_party_release": False,
            "training_reuse": "NOT_AUTHORIZED",
            "deletion": "NOT_IMPLEMENTED",
            "receipt_authenticity": receipt_authenticity(run),
            "report": run,
        },
        headers={
            "Cache-Control": "no-store",
            "X-Aurex-Third-Party-Release": "none",
            "X-Aurex-Training-Reuse": "not-authorized",
        },
    )


class ObservationRequest(BaseModel):
    tenant_id: str = Field(pattern=TENANT_PATTERN, max_length=64)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    observed_at: datetime
    hypothesis: str = Field(min_length=1, max_length=500)
    counterevidence: list[str] = Field(default_factory=list, max_length=20)
    effect: str | None = Field(default="NONE", max_length=40)

    @field_validator("counterevidence")
    @classmethod
    def _bounded_lines(cls, value: list[str]) -> list[str]:
        if any(len(item) > 200 for item in value):
            raise ValueError("counterevidence line is too long")
        return value


@router.post("/observations")
def post_observation(payload: ObservationRequest, principal: PrincipalDep) -> dict[str, Any]:
    """Record an advisory observation. The caller cannot start an effect."""
    assert_no_effect()
    authorize_tenant(principal, payload.tenant_id)
    observed = payload.observed_at
    if observed.tzinfo is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "observed_at requires a timezone")
    result = propose(
        {
            "schema": "aurex.observation.v1",
            "source_sha256": payload.source_sha256,
            "observed_at": observed,
            "hypothesis": payload.hypothesis,
            "counterevidence": payload.counterevidence,
            "effect": payload.effect,
        },
        now=datetime.now(UTC),
        max_age=timedelta(hours=24),
    )
    result["tenant_id"] = payload.tenant_id
    return result


class DeletionRequest(BaseModel):
    tenant_id: str = Field(pattern=TENANT_PATTERN, max_length=64)


class RetentionRequest(BaseModel):
    tenant_id: str = Field(pattern=TENANT_PATTERN, max_length=64)
    retain_days: int = Field(ge=1, le=3650)


class AuthorizationClaim(BaseModel):
    tenant_id: str = Field(pattern=TENANT_PATTERN, max_length=64)
    actor_id: str = Field(default="", max_length=80)
    action: str = Field(default="", max_length=80)
    scope: str = Field(default="", max_length=120)
    expires_at: str = Field(default="", max_length=40)


@router.post("/lifecycle/deletion-request")
def post_deletion_request(payload: DeletionRequest, principal: PrincipalDep) -> dict[str, Any]:
    """Record a deletion request. No rows are removed."""
    assert_no_effect()
    authorize_tenant(principal, payload.tenant_id)
    before = dispater_store.list_runs(payload.tenant_id)
    decision = deletion_request(payload.tenant_id)
    if dispater_store.list_runs(payload.tenant_id) != before:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal DISPATER error")
    return decision


@router.post("/lifecycle/retention")
def post_retention(payload: RetentionRequest, principal: PrincipalDep) -> dict[str, Any]:
    """Record a retention preference. It is not enforced."""
    assert_no_effect()
    authorize_tenant(principal, payload.tenant_id)
    try:
        return retention_request(payload.tenant_id, retain_days=payload.retain_days)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post("/lifecycle/authorization-decision")
def post_authorization_decision(payload: AuthorizationClaim, principal: PrincipalDep) -> dict[str, Any]:
    """Return an unverified decision. The call does not approve a financial action."""
    assert_no_effect()
    authorize_tenant(principal, payload.tenant_id)
    return authorization_decision(payload.model_dump())


class PipelineIngestRequest(BaseModel):
    source_id: str = Field(min_length=1, max_length=120)
    source_record_id: str = Field(min_length=1, max_length=120)
    document_category: str = Field(default="INVOICE")
    media_type: str = Field(default="application/json")
    payload_base64: str = Field(min_length=1, max_length=2_000_000)


@router.post("/pipeline/audit")
def run_pipeline_audit(body: ReconciliationRequest, principal: PrincipalDep) -> dict[str, Any]:
    """Run the industrial audit pipeline. The result has no financial authority."""
    assert_no_effect()
    authorize_tenant(principal, body.tenant_id)
    from aurex.dispater_pipeline import IndustrialAuditPipeline

    pipeline = IndustrialAuditPipeline(tenant_id=body.tenant_id)
    result = pipeline.execute_audit_run(body.model_dump())
    return {
        "run_id": result.run_id,
        "tenant_id": result.tenant_id,
        "timestamp_utc": result.timestamp_utc,
        "envelopes_admitted": result.envelopes_admitted,
        "summary": result.reconciliation_summary,
        "qualified_findings": result.qualified_findings,
        "withheld_findings": result.withheld_findings,
        "receipt_sha256": result.audit_receipt_sha256,
        "verification_status": result.verification_status,
        "authority": "HUMAN_REVIEW_REQUIRED",
        "financial_authority": "NONE",
    }


@router.post("/pipeline/ingest")
def ingest_pipeline_document(
    tenant_id: TenantQuery,
    req: PipelineIngestRequest,
    principal: PrincipalDep,
) -> dict[str, Any]:
    """Hash and record one synthetic document. This does not approve a payment."""
    assert_no_effect()
    authorize_tenant(principal, tenant_id)
    from aurex.dispater_envelope import DocumentCategory
    from aurex.dispater_monitoring import ContinuousMonitoringEngine

    try:
        raw_bytes = base64.b64decode(req.payload_base64, validate=True)
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid base64 payload") from exc
    category = {item.value: item for item in DocumentCategory}.get(
        req.document_category, DocumentCategory.UNKNOWN
    )
    engine = ContinuousMonitoringEngine(tenant_id=tenant_id)
    try:
        env = engine.ingest_incremental_record(
            source_id=req.source_id,
            source_record_id=req.source_record_id,
            category=category,
            raw_bytes=raw_bytes,
            media_type=req.media_type,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return {
        "status": "ADMITTED",
        "envelope_id": env.envelope_id,
        "content_sha256": env.source_content_sha256,
        "tenant_id": env.tenant_id,
        "source_record_id": env.source_record_id,
        "byte_count": env.byte_count,
        "schema_version": env.schema_version,
        "recorded_at": env.ingested_at_utc,
        "financial_authority": "NONE",
    }
