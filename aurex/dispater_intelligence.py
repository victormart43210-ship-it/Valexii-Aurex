"""
AUREX DISPATER Sovereign Operational Intelligence Engine.

Provides deterministic revenue leakage detection across 10 exception rules,
evidence-based reconciliation, fleet maintenance intelligence with priority classifications,
operational value calculation, and secure integrations.
"""

import hashlib
import json
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from pydantic import BaseModel, Field


def _to_decimal(val: Any) -> Decimal:
    """Safely convert numeric or string values to 2-decimal place precision."""
    if isinstance(val, (int, float, str, Decimal)):
        return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal("0.00")


def _compute_sha256(payload: Any) -> str:
    """Compute deterministic SHA-256 digest of dict/list/model."""
    if isinstance(payload, BaseModel):
        data_str = payload.model_dump_json()
    elif isinstance(payload, (dict, list)):
        data_str = json.dumps(payload, sort_keys=True, default=str)
    else:
        data_str = str(payload)
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


# --- Models ---

class RevenueException(BaseModel):
    exception_id: str
    rule_type: str  # Rules 1-10
    description: str
    financial_exposure: float
    currency: str = "USD"
    tenant_id: str
    source_record_ids: list[str]
    evidence_hash: str
    reason: str
    confidence_limitations: str
    required_human_action: str
    audit_event_ref: str
    is_demo: bool = True


class Xaeli5StepFinding(BaseModel):
    exception_id: str
    now: str      # NOW: Current operational exception
    changed: str  # CHANGED: Newly detected discrepancy or status change
    next: str     # NEXT: Recommended human action
    why: str      # WHY: Explanation of the finding
    proof: str    # PROOF: Supporting records and evidence digest
    exposure_usd: float
    audit_event_ref: str


class ReconciliationResult(BaseModel):
    reconciliation_id: str
    tenant_id: str
    field_ticket_id: str
    purchase_order_id: str | None = None
    rate_sheet_id: str | None = None
    invoice_id: str | None = None
    matched: bool
    discrepancies: list[str]
    missing_evidence: list[str]
    total_amount_billed: float
    total_amount_expected: float
    exposure_amount: float
    evidence_hash: str
    human_review_status: str = "PENDING_REVIEW"
    audit_event_ref: str
    is_demo: bool = True


class MaintenanceRecord(BaseModel):
    equipment_id: str
    equipment_name: str
    tenant_id: str
    operating_hours: float
    current_mileage: float
    last_service_hours: float
    service_threshold_hours: float = 250.0
    last_service_mileage: float
    service_threshold_mileage: float = 10000.0
    status: str  # HEALTHY, OVERDUE_SERVICE, UPCOMING_SERVICE, MISSING_INSPECTION, DEFECT_REPORTED, DOWNTIME_RECORDED
    priority_classification: str = "ROUTINE"  # CRITICAL, HIGH, MEDIUM, ROUTINE
    downtime_hours: float = 0.0
    equipment_available: bool = True
    maintenance_history_count: int = 0
    detected_defects: list[str] = Field(default_factory=list)
    has_inspection_record: bool = True
    recommended_action: str
    evidence_hash: str
    is_demo: bool = True


class CalculatorAssumptions(BaseModel):
    monthly_job_volume: int = 150
    avg_ticket_value: float = 2500.0
    estimated_leakage_pct: float = 3.5
    admin_hours_per_job: float = 1.5
    hourly_admin_cost: float = 45.0
    dispater_automation_rate: float = 0.65


class ValueCalculationResult(BaseModel):
    tenant_id: str
    monthly_job_volume: int
    monthly_revenue_evaluated: float
    estimated_revenue_at_risk: float
    admin_hours_saved_monthly: float
    monthly_admin_cost_savings: float
    total_estimated_monthly_value: float
    assumptions_json: dict[str, Any]
    projection_disclaimer: str = (
        "PROJECTION ONLY — ALL ASSUMPTIONS ARE EDITABLE. "
        "DOES NOT CONSTITUTE VERIFIED FINANCIAL RECOVERY OR GUARANTEED SAVINGS."
    )


# --- Revenue Leakage Detection Engine (10 Rules) ---

class RevenueLeakageEngine:
    @staticmethod
    def evaluate_records(
        tenant_id: str,
        field_tickets: list[dict[str, Any]],
        invoices: list[dict[str, Any]],
        purchase_orders: list[dict[str, Any]],
        rate_sheets: list[dict[str, Any]],
        is_demo: bool = True,
    ) -> list[RevenueException]:
        exceptions: list[RevenueException] = []

        po_map = {str(po.get("po_id")): po for po in purchase_orders if po.get("po_id")}
        invoice_map = {str(inv.get("invoice_id")): inv for inv in invoices if inv.get("invoice_id")}
        rate_map = {str(rs.get("rate_code")): _to_decimal(rs.get("approved_rate", 0)) for rs in rate_sheets if rs.get("rate_code")}

        seen_invoices: dict[str, str] = {}
        po_billed_totals: dict[str, Decimal] = {}

        # Evaluate Field Tickets
        for ft in field_tickets:
            ft_id = str(ft.get("ticket_id", "FT-UNKNOWN"))
            po_id = ft.get("po_id")
            invoice_id = ft.get("invoice_id")
            has_signature = ft.get("has_customer_signature", True)
            items = ft.get("items", [])
            ft_amount = float(_to_decimal(ft.get("total_amount", 0)))
            evidence_valid = bool(ft.get("evidence_valid", True))

            # Rule 10: Missing or conflicting supporting evidence
            if not evidence_valid:
                exc_hash = _compute_sha256({"ft_id": ft_id, "rule": "MISSING_CONFLICTING_EVIDENCE"})
                exceptions.append(RevenueException(
                    exception_id=f"EXC-EVIDENCE-{ft_id}",
                    rule_type="MISSING_CONFLICTING_EVIDENCE",
                    description=f"Field Ticket {ft_id} contains missing or conflicting supporting evidence digests.",
                    financial_exposure=ft_amount,
                    tenant_id=tenant_id,
                    source_record_ids=[ft_id],
                    evidence_hash=exc_hash,
                    reason="Digest verification failed or supporting field ticket image/attachment is missing.",
                    confidence_limitations="Requires original field ticket file upload for digest re-computation.",
                    required_human_action="Re-upload original field document to verify SHA-256 evidence chain.",
                    audit_event_ref=f"AUDIT-EVD-{ft_id}",
                    is_demo=is_demo,
                ))

            # Rule 1: Missing or unmatched purchase order
            if not po_id or str(po_id) not in po_map:
                exc_hash = _compute_sha256({"ft_id": ft_id, "rule": "UNMATCHED_PO", "amount": ft_amount})
                exceptions.append(RevenueException(
                    exception_id=f"EXC-PO-{ft_id}",
                    rule_type="UNMATCHED_PO",
                    description=f"Field Ticket {ft_id} has missing or unverified Purchase Order {po_id}.",
                    financial_exposure=ft_amount,
                    tenant_id=tenant_id,
                    source_record_ids=[ft_id] + ([str(po_id)] if po_id else []),
                    evidence_hash=exc_hash,
                    reason="Field ticket executed without an approved PO on record.",
                    confidence_limitations="Depends on completeness of PO intake register.",
                    required_human_action="Request customer PO or attach emergency approval document.",
                    audit_event_ref=f"AUDIT-PO-{ft_id}",
                    is_demo=is_demo,
                ))

            # Rule 2: Completed field ticket without corresponding invoice
            if not invoice_id or str(invoice_id) not in invoice_map:
                exc_hash = _compute_sha256({"ft_id": ft_id, "rule": "UNBILLED_FIELD_TICKET", "amount": ft_amount})
                exceptions.append(RevenueException(
                    exception_id=f"EXC-UNBILLED-{ft_id}",
                    rule_type="UNBILLED_FIELD_TICKET",
                    description=f"Field Ticket {ft_id} is marked complete but has no generated invoice.",
                    financial_exposure=ft_amount,
                    tenant_id=tenant_id,
                    source_record_ids=[ft_id],
                    evidence_hash=exc_hash,
                    reason="Completed field work has not been billed to customer.",
                    confidence_limitations="Assumes field ticket is finalized and billable.",
                    required_human_action="Generate customer invoice from verified ticket items.",
                    audit_event_ref=f"AUDIT-UNBILLED-{ft_id}",
                    is_demo=is_demo,
                ))

            # Rule 5: Missing customer signatures
            if not has_signature:
                exc_hash = _compute_sha256({"ft_id": ft_id, "rule": "MISSING_SIGNATURE", "amount": ft_amount})
                exceptions.append(RevenueException(
                    exception_id=f"EXC-SIG-{ft_id}",
                    rule_type="MISSING_SIGNATURE",
                    description=f"Field Ticket {ft_id} lacks customer representative signature.",
                    financial_exposure=ft_amount,
                    tenant_id=tenant_id,
                    source_record_ids=[ft_id],
                    evidence_hash=exc_hash,
                    reason="Customer signature absent, creating audit dispute risk.",
                    confidence_limitations="Digital ticket may have separate electronic sign-off.",
                    required_human_action="Obtain signed ticket or digital confirmation record.",
                    audit_event_ref=f"AUDIT-SIG-{ft_id}",
                    is_demo=is_demo,
                ))

            # Rule 6: Unbilled labor, equipment, or materials
            unbilled_items = [item for item in items if not item.get("billed", True)]
            if unbilled_items:
                unbilled_amount = sum(float(_to_decimal(item.get("subtotal", 0))) for item in unbilled_items)
                exc_hash = _compute_sha256({"ft_id": ft_id, "rule": "UNBILLED_ITEMS", "amount": unbilled_amount})
                exceptions.append(RevenueException(
                    exception_id=f"EXC-ITEMS-{ft_id}",
                    rule_type="UNBILLED_ITEMS",
                    description=f"Field Ticket {ft_id} contains {len(unbilled_items)} unbilled line item(s).",
                    financial_exposure=unbilled_amount,
                    tenant_id=tenant_id,
                    source_record_ids=[ft_id],
                    evidence_hash=exc_hash,
                    reason="Line items present on field ticket omitted from invoice.",
                    confidence_limitations="Requires verification against contract billable terms.",
                    required_human_action="Issue supplemental invoice or document explicit non-billable waiver.",
                    audit_event_ref=f"AUDIT-ITEMS-{ft_id}",
                    is_demo=is_demo,
                ))

            # Rule 7: Incorrect quantities and unit conversions
            for item in items:
                ft_qty = float(item.get("quantity", 0))
                expected_qty = float(item.get("expected_quantity", ft_qty))
                unit = str(item.get("unit", "hrs")).lower()
                expected_unit = str(item.get("expected_unit", unit)).lower()

                if ft_qty != expected_qty or unit != expected_unit:
                    diff_amount = float(_to_decimal(item.get("subtotal", 0)))
                    exc_hash = _compute_sha256({"ft_id": ft_id, "item": item.get("name"), "rule": "QUANTITY_UNIT_MISMATCH"})
                    exceptions.append(RevenueException(
                        exception_id=f"EXC-QTY-{ft_id}-{item.get('name', 'item')}",
                        rule_type="QUANTITY_UNIT_MISMATCH",
                        description=f"Field Ticket {ft_id} item {item.get('name')} quantity/unit mismatch: {ft_qty} {unit} vs expected {expected_qty} {expected_unit}.",
                        financial_exposure=diff_amount,
                        tenant_id=tenant_id,
                        source_record_ids=[ft_id],
                        evidence_hash=exc_hash,
                        reason="Billed quantities or unit of measure conflict with dispatch logs.",
                        confidence_limitations="Requires dispatcher verification.",
                        required_human_action="Reconcile dispatch logs and update quantity/unit conversion factor.",
                        audit_event_ref=f"AUDIT-QTY-{ft_id}",
                        is_demo=is_demo,
                    ))

        # Evaluate Invoices
        for inv in invoices:
            inv_id = str(inv.get("invoice_id", "INV-UNKNOWN"))
            inv_amount = _to_decimal(inv.get("total_amount", 0))
            po_id = inv.get("po_id")

            # Track PO Billed Totals
            if po_id:
                po_id_str = str(po_id)
                po_billed_totals[po_id_str] = po_billed_totals.get(po_id_str, Decimal("0.00")) + inv_amount

            # Rule 4: Duplicate supplier invoices
            duplicate_key = f"{inv.get('vendor_or_customer')}:{inv_amount}"
            if duplicate_key in seen_invoices:
                orig_inv_id = seen_invoices[duplicate_key]
                exc_hash = _compute_sha256({"inv_id": inv_id, "orig_id": orig_inv_id, "amount": float(inv_amount)})
                exceptions.append(RevenueException(
                    exception_id=f"EXC-DUP-{inv_id}",
                    rule_type="DUPLICATE_INVOICE",
                    description=f"Invoice {inv_id} duplicates amount ${inv_amount} and vendor of Invoice {orig_inv_id}.",
                    financial_exposure=float(inv_amount),
                    tenant_id=tenant_id,
                    source_record_ids=[inv_id, orig_inv_id],
                    evidence_hash=exc_hash,
                    reason="Matching vendor and billing amount detected across distinct invoices.",
                    confidence_limitations="Identical routine billing amounts may occur legitimately.",
                    required_human_action="Verify service dates and void duplicate invoice if re-submitted.",
                    audit_event_ref=f"AUDIT-DUP-{inv_id}",
                    is_demo=is_demo,
                ))
            else:
                seen_invoices[duplicate_key] = inv_id

            # Rule 3: Invoice amounts disagree with approved rate sheets
            line_items = inv.get("line_items", [])
            for item in line_items:
                rate_code = str(item.get("rate_code", ""))
                billed_rate = _to_decimal(item.get("unit_rate", 0))
                if rate_code in rate_map:
                    approved_rate = rate_map[rate_code]
                    if billed_rate != approved_rate:
                        inv_qty = Decimal(str(item.get("quantity", 1)))
                        rate_diff_dec = abs(billed_rate - approved_rate) * inv_qty
                        rate_diff = float(rate_diff_dec)
                        exc_hash = _compute_sha256({"inv_id": inv_id, "rate_code": rate_code, "diff": rate_diff})
                        exceptions.append(RevenueException(
                            exception_id=f"EXC-RATE-{inv_id}-{rate_code}",
                            rule_type="RATE_DISCREPANCY",
                            description=f"Invoice {inv_id} billed rate ${billed_rate} differs from approved rate ${approved_rate} for {rate_code}.",
                            financial_exposure=rate_diff,
                            tenant_id=tenant_id,
                            source_record_ids=[inv_id],
                            evidence_hash=exc_hash,
                            reason="Billed unit rate conflicts with effective master rate sheet.",
                            confidence_limitations="Custom project discounts may apply outside standard rate sheet.",
                            required_human_action="Verify rate sheet effective date and approve variance or issue credit memo.",
                            audit_event_ref=f"AUDIT-RATE-{inv_id}",
                            is_demo=is_demo,
                        ))

            # Rule 9: Invoice discrepancies across multiple records
            if inv.get("multi_record_mismatch", False):
                mismatch_amount = float(_to_decimal(inv.get("mismatch_amount", inv_amount)))
                exc_hash = _compute_sha256({"inv_id": inv_id, "rule": "MULTI_RECORD_DISCREPANCY"})
                exceptions.append(RevenueException(
                    exception_id=f"EXC-MULTI-{inv_id}",
                    rule_type="MULTI_RECORD_DISCREPANCY",
                    description=f"Invoice {inv_id} total ${inv_amount} disagrees with aggregated sum of supporting field tickets.",
                    financial_exposure=mismatch_amount,
                    tenant_id=tenant_id,
                    source_record_ids=[inv_id],
                    evidence_hash=exc_hash,
                    reason="Invoice header total does not equal sum of underlying field ticket subtotals.",
                    confidence_limitations="May reflect unattached line item surcharges.",
                    required_human_action="Audit underlying field tickets and align invoice line items.",
                    audit_event_ref=f"AUDIT-MULTI-{inv_id}",
                    is_demo=is_demo,
                ))

        # Rule 8: Partial purchase-order fulfillment / over-billing
        for po_id_str, total_billed in po_billed_totals.items():
            if po_id_str in po_map:
                po_limit = _to_decimal(po_map[po_id_str].get("amount_limit", 0))
                if po_limit > Decimal("0.00") and total_billed > po_limit:
                    over_amount = float(total_billed - po_limit)
                    exc_hash = _compute_sha256({"po_id": po_id_str, "rule": "PARTIAL_PO_FULFILLMENT", "over": over_amount})
                    exceptions.append(RevenueException(
                        exception_id=f"EXC-PO-OVER-{po_id_str}",
                        rule_type="PARTIAL_PO_FULFILLMENT",
                        description=f"Purchase Order {po_id_str} cumulative billing ${total_billed} exceeds approved PO limit ${po_limit}.",
                        financial_exposure=over_amount,
                        tenant_id=tenant_id,
                        source_record_ids=[po_id_str],
                        evidence_hash=exc_hash,
                        reason="Cumulative invoices exceed authorized PO cap.",
                        confidence_limitations="Change orders may be pending customer signature.",
                        required_human_action="Request PO limit increase or issue change order.",
                        audit_event_ref=f"AUDIT-PO-OVER-{po_id_str}",
                        is_demo=is_demo,
                    ))

        return exceptions

    @staticmethod
    def convert_to_xaeli_findings(exceptions: list[RevenueException]) -> list[Xaeli5StepFinding]:
        """Format exceptions into canonical 5-step XAELI findings (NOW, CHANGED, NEXT, WHY, PROOF)."""
        findings: list[Xaeli5StepFinding] = []
        for exc in exceptions:
            findings.append(Xaeli5StepFinding(
                exception_id=exc.exception_id,
                now=f"Operational Exception [{exc.rule_type}]: Exposure ${exc.financial_exposure:,.2f} USD.",
                changed=f"Discrepancy detected across source records: {', '.join(exc.source_record_ids)}.",
                next=exc.required_human_action,
                why=exc.reason,
                proof=f"SHA-256 Digest: {exc.evidence_hash} | Audit Ref: {exc.audit_event_ref}",
                exposure_usd=exc.financial_exposure,
                audit_event_ref=exc.audit_event_ref,
            ))
        return findings


# --- Fleet Maintenance Intelligence Engine ---

class FleetMaintenanceEngine:
    @staticmethod
    def evaluate_fleet(tenant_id: str, fleet_data: list[dict[str, Any]], is_demo: bool = True) -> list[MaintenanceRecord]:
        records: list[MaintenanceRecord] = []
        for eq in fleet_data:
            eq_id = str(eq.get("equipment_id", "EQ-UNKNOWN"))
            eq_name = str(eq.get("equipment_name", "Equipment"))
            op_hours = float(eq.get("operating_hours", 0.0))
            mileage = float(eq.get("current_mileage", 0.0))
            last_hours = float(eq.get("last_service_hours", 0.0))
            last_mileage = float(eq.get("last_service_mileage", 0.0))
            thresh_hours = float(eq.get("service_threshold_hours", 250.0))
            thresh_mileage = float(eq.get("service_threshold_mileage", 10000.0))
            has_insp = bool(eq.get("has_inspection_record", True))
            defects = [str(d) for d in eq.get("detected_defects", [])]
            downtime = float(eq.get("downtime_hours", 0.0))
            avail = bool(eq.get("equipment_available", True))
            hist_count = int(eq.get("maintenance_history_count", 0))

            hours_since_service = op_hours - last_hours
            mileage_since_service = mileage - last_mileage

            status = "HEALTHY"
            priority = "ROUTINE"
            recommendation = "Routine operation; scheduled maintenance on track."

            if defects:
                status = "DEFECT_REPORTED"
                priority = "CRITICAL"
                avail = False
                recommendation = f"Immediate shop inspection required for defects: {', '.join(defects)}."
            elif not has_insp:
                status = "MISSING_INSPECTION"
                priority = "HIGH"
                avail = False
                recommendation = "Complete DOT / OSHA safety inspection before placing unit in service."
            elif hours_since_service >= thresh_hours or mileage_since_service >= thresh_mileage:
                status = "OVERDUE_SERVICE"
                priority = "CRITICAL" if hours_since_service >= (thresh_hours * 1.5) else "HIGH"
                recommendation = f"Overdue service ({hours_since_service:.1f} hrs / {mileage_since_service:.1f} mi since last service). Schedule PM immediately."
            elif hours_since_service >= (thresh_hours * 0.8) or mileage_since_service >= (thresh_mileage * 0.8):
                status = "UPCOMING_SERVICE"
                priority = "MEDIUM"
                recommendation = "PM service due within next 20% operating window. Pre-order filters and fluids."
            elif downtime > 0.0:
                status = "DOWNTIME_RECORDED"
                priority = "MEDIUM"

            ev_hash = _compute_sha256({"eq_id": eq_id, "op_hours": op_hours, "mileage": mileage, "status": status, "priority": priority})

            records.append(MaintenanceRecord(
                equipment_id=eq_id,
                equipment_name=eq_name,
                tenant_id=tenant_id,
                operating_hours=op_hours,
                current_mileage=mileage,
                last_service_hours=last_hours,
                service_threshold_hours=thresh_hours,
                last_service_mileage=last_mileage,
                service_threshold_mileage=thresh_mileage,
                status=status,
                priority_classification=priority,
                downtime_hours=downtime,
                equipment_available=avail,
                maintenance_history_count=hist_count,
                detected_defects=defects,
                has_inspection_record=has_insp,
                recommended_action=recommendation,
                evidence_hash=ev_hash,
                is_demo=is_demo,
            ))

        return records


# --- Operational Value Calculator Engine ---

class OperationalValueCalculator:
    @staticmethod
    def calculate_value(tenant_id: str, assumptions: CalculatorAssumptions) -> ValueCalculationResult:
        monthly_revenue = assumptions.monthly_job_volume * assumptions.avg_ticket_value
        estimated_exposure = monthly_revenue * (assumptions.estimated_leakage_pct / 100.0)
        total_admin_hours = assumptions.monthly_job_volume * assumptions.admin_hours_per_job
        saved_admin_hours = total_admin_hours * assumptions.dispater_automation_rate
        monthly_admin_savings = saved_admin_hours * assumptions.hourly_admin_cost

        total_value = estimated_exposure + monthly_admin_savings

        return ValueCalculationResult(
            tenant_id=tenant_id,
            monthly_job_volume=assumptions.monthly_job_volume,
            monthly_revenue_evaluated=round(monthly_revenue, 2),
            estimated_revenue_at_risk=round(estimated_exposure, 2),
            admin_hours_saved_monthly=round(saved_admin_hours, 1),
            monthly_admin_cost_savings=round(monthly_admin_savings, 2),
            total_estimated_monthly_value=round(total_value, 2),
            assumptions_json=assumptions.model_dump(),
        )


# --- Integration Foundation Adapters ---

class IntegrationFoundationAdapters:
    @staticmethod
    def import_csv_tickets(csv_text: str) -> list[dict[str, Any]]:
        """Parse CSV content into structured field tickets."""
        tickets: list[dict[str, Any]] = []
        lines = [line.strip() for line in csv_text.strip().split("\n") if line.strip()]
        if not lines:
            return tickets

        headers = [h.strip().lower() for h in lines[0].split(",")]
        for line in lines[1:]:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < len(headers):
                continue
            row = dict(zip(headers, parts))
            tickets.append({
                "ticket_id": row.get("ticket_id", "FT-CSV"),
                "po_id": row.get("po_id") if row.get("po_id") != "none" else None,
                "invoice_id": row.get("invoice_id") if row.get("invoice_id") != "none" else None,
                "total_amount": float(row.get("total_amount", "0.0")),
                "has_customer_signature": row.get("has_signature", "true").lower() == "true",
            })
        return tickets

    @staticmethod
    def export_accounting_format(exceptions: list[RevenueException]) -> dict[str, Any]:
        """Export exceptions into standardized accounting CSV/JSON adjustment feed."""
        entries = []
        for exc in exceptions:
            entries.append({
                "adjustment_id": f"ADJ-{exc.exception_id}",
                "rule": exc.rule_type,
                "exposure_usd": exc.financial_exposure,
                "source_ref": exc.source_record_ids[0] if exc.source_record_ids else "N/A",
                "evidence_hash": exc.evidence_hash,
                "status": "REQUIRES_HUMAN_APPROVAL",
            })
        return {"tenant_id": exceptions[0].tenant_id if exceptions else "N/A", "adjustments_count": len(entries), "entries": entries}

    @staticmethod
    def export_teams_notification(exception: RevenueException) -> dict[str, Any]:
        """Format a disabled-by-default MS Teams notification payload."""
        return {
            "status": "DISABLED_BY_DEFAULT",
            "integration": "MS_TEAMS_WEBHOOK",
            "external_transmission_allowed": False,
            "message_card": {
                "@type": "MessageCard",
                "summary": f"DISPATER Revenue Exception Alert: {exception.exception_id}",
                "themeColor": "E74C3C" if exception.financial_exposure > 5000 else "F39C12",
                "title": f"Revenue Leakage Exception — {exception.rule_type}",
                "sections": [
                    {
                        "facts": [
                            {"name": "Exception ID", "value": exception.exception_id},
                            {"name": "Tenant", "value": exception.tenant_id},
                            {"name": "Financial Exposure", "value": f"${exception.financial_exposure:,.2f} USD"},
                            {"name": "Description", "value": exception.description},
                            {"name": "Required Action", "value": exception.required_human_action},
                        ],
                    }
                ],
            },
        }
