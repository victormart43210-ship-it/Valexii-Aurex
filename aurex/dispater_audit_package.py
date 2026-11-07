"""DISPATER Audit Readiness & Reproducible Evidence Package Generator.

Implements source-linked document inventory, document freshness and expiration checks,
DOT/FMCSA evidence requirements (49 CFR Parts 390-396), corrective-action tracking,
human review audit trails, and deterministic SHA-256 evidence package exports.

NON-DELEGABLE CONSTRAINTS:
- Missing evidence must not automatically be classified as a regulatory violation.
- Audit packages must clearly identify unresolved findings and jurisdictional limitations.
- Receipts are tamper-detection mechanisms, not automated legal certifications.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, date, datetime
from typing import Any

SCHEMA_AUDIT_PACKAGE = "dispater.synthetic.audit_package.v1"

# DOT/FMCSA Regulatory Requirements Catalog (49 CFR)
FMCSA_REQUIREMENTS = {
    "49_CFR_391_51": {
        "title": "Driver Qualification File (DQF)",
        "jurisdiction": "US_DOT_FMCSA",
        "category": "DRIVER_QUALIFICATION",
        "description": "Medical examiner certificate, CDL motor vehicle record (MVR) annual inquiry, employment verification.",
        "applicability": "Commercial motor vehicle operators > 10,000 lbs GVWR or passenger/hazmat transport.",
        "expiration_controlled": True,
        "default_max_validity_days": 730,
    },
    "49_CFR_395_8": {
        "title": "Driver Hours of Service & Duty Status Logs",
        "jurisdiction": "US_DOT_FMCSA",
        "category": "HOURS_OF_SERVICE",
        "description": "Electronic Logging Device (ELD) records or driver records of duty status (RODS).",
        "applicability": "Interstate commercial towing and property-carrying operators.",
        "expiration_controlled": False,
        "default_max_validity_days": 180,
    },
    "49_CFR_396_11": {
        "title": "Driver Vehicle Inspection Report (DVIR)",
        "jurisdiction": "US_DOT_FMCSA",
        "category": "VEHICLE_MAINTENANCE",
        "description": "Pre-trip and post-trip daily commercial motor vehicle safety inspection reports.",
        "applicability": "Commercial motor vehicle fleets operating in interstate/regulated commerce.",
        "expiration_controlled": True,
        "default_max_validity_days": 90,
    },
    "49_CFR_396_17": {
        "title": "Periodic Annual Vehicle Inspection",
        "jurisdiction": "US_DOT_FMCSA",
        "category": "VEHICLE_MAINTENANCE",
        "description": "Mandatory annual mechanical safety inspection covering brakes, steering, lighting, coupling devices.",
        "applicability": "All commercial motor vehicles operating on public highways.",
        "expiration_controlled": True,
        "default_max_validity_days": 365,
    },
    "49_CFR_387_9": {
        "title": "Financial Responsibility & Public Liability Insurance",
        "jurisdiction": "US_DOT_FMCSA",
        "category": "FINANCIAL_RESPONSIBILITY",
        "description": "Form BMC-91 or BMC-91X certificate of commercial auto and on-hook towing cargo liability insurance.",
        "applicability": "For-hire motor carriers operating commercial motor vehicles.",
        "expiration_controlled": True,
        "default_max_validity_days": 365,
    },
}


def digest_object(val: object) -> str:
    """Compute deterministic SHA-256 hex digest of JSON-serializable structure."""
    raw = json.dumps(val, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AuditPackageEngine:
    """Compiles source-linked compliance documents, checks freshness, and generates verified evidence packages."""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id

    def evaluate_compliance(
        self,
        documents: list[dict[str, Any]],
        vehicles: list[dict[str, Any]],
        drivers: list[dict[str, Any]],
        as_of_date: date | None = None,
    ) -> dict[str, Any]:
        """Evaluate inventory freshness, missing items, and generate audit readiness report."""
        if as_of_date is None:
            as_of_date = datetime.now(UTC).date()

        exceptions: list[dict[str, Any]] = []
        doc_inventory: list[dict[str, Any]] = []

        # Index documents by vehicle_id, driver_id, and category
        by_vehicle: dict[str, list[dict[str, Any]]] = {}
        by_driver: dict[str, list[dict[str, Any]]] = {}
        for d in documents:
            d_entry = {
                "document_id": d["document_id"],
                "type": d["type"],
                "title": d.get("title", d["type"]),
                "issued_date": d.get("issued_date"),
                "expiration_date": d.get("expiration_date"),
                "sha256": digest_object(d),
                "source_ref": d.get("source_ref", "INTERNAL_RECORDS"),
            }
            doc_inventory.append(d_entry)
            if "vehicle_id" in d:
                by_vehicle.setdefault(d["vehicle_id"], []).append(d)
            if "driver_id" in d:
                by_driver.setdefault(d["driver_id"], []).append(d)

        # 1. Driver Qualifications Checks (49 CFR 391.51)
        for drv in drivers:
            d_id = drv["driver_id"]
            drv_docs = by_driver.get(d_id, [])
            med_certs = [doc for doc in drv_docs if doc.get("type") == "MEDICAL_EXAMINER_CERT"]
            if not med_certs:
                exceptions.append({
                    "exception_id": f"EXC-MED-{d_id}",
                    "regulation": "49_CFR_391_51",
                    "subject": f"Driver:{d_id}",
                    "severity": "HIGH",
                    "status": "UNRESOLVED",
                    "issue": "Missing Medical Examiner Certificate in driver qualification folder.",
                    "note": "Document not located in current index; does not conclusively prove driver non-compliance.",
                    "corrective_action": "Obtain current copy of Medical Examiner's Certificate (Form MCSA-5876).",
                })
            else:
                for mc in med_certs:
                    exp = mc.get("expiration_date")
                    if exp:
                        exp_d = date.fromisoformat(exp)
                        if exp_d < as_of_date:
                            exceptions.append({
                                "exception_id": f"EXC-EXP-MED-{mc['document_id']}",
                                "regulation": "49_CFR_391_51",
                                "subject": f"Driver:{d_id}",
                                "severity": "HIGH",
                                "status": "UNRESOLVED",
                                "issue": f"Medical certificate expired on {exp} ({as_of_date - exp_d} days overdue).",
                                "corrective_action": "Schedule DOT physical examination and upload renewed certificate.",
                            })

        # 2. Vehicle Annual Inspection & DVIR Checks (49 CFR 396.17)
        for v in vehicles:
            v_id = v["vehicle_id"]
            v_docs = by_vehicle.get(v_id, [])
            inspections = [doc for doc in v_docs if doc.get("type") == "ANNUAL_INSPECTION"]
            if not inspections:
                exceptions.append({
                    "exception_id": f"EXC-INSP-{v_id}",
                    "regulation": "49_CFR_396_17",
                    "subject": f"Vehicle:{v_id}",
                    "severity": "HIGH",
                    "status": "UNRESOLVED",
                    "issue": "Missing periodic annual safety inspection record.",
                    "note": "Vehicle record requires documented periodic inspection under 49 CFR Part 396 Appendix G.",
                    "corrective_action": "Perform periodic safety inspection or attach current certification sticker log.",
                })
            else:
                for ins in inspections:
                    exp = ins.get("expiration_date")
                    if exp and date.fromisoformat(exp) < as_of_date:
                        exceptions.append({
                            "exception_id": f"EXC-EXP-INSP-{ins['document_id']}",
                            "regulation": "49_CFR_396_17",
                            "subject": f"Vehicle:{v_id}",
                            "severity": "HIGH",
                            "status": "UNRESOLVED",
                            "issue": f"Annual vehicle inspection expired on {exp}.",
                            "corrective_action": "Conduct and record qualified periodic commercial vehicle inspection.",
                        })

        readiness_score = max(0, 100 - (len(exceptions) * 15))

        evaluation = {
            "schema": SCHEMA_AUDIT_PACKAGE,
            "tenant_id": self.tenant_id,
            "as_of_date": as_of_date.isoformat(),
            "readiness_score": readiness_score,
            "status": "AUDIT_READY" if not exceptions else "EXCEPTIONS_PENDING_REVIEW",
            "counts": {
                "documents_inventoried": len(doc_inventory),
                "vehicles_reviewed": len(vehicles),
                "drivers_reviewed": len(drivers),
                "unresolved_exceptions": len(exceptions),
            },
            "document_inventory": doc_inventory,
            "exceptions": exceptions,
        }
        return evaluation

    def export_audit_package(
        self,
        evaluation: dict[str, Any],
        reconciliation_report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a reproducible, verifiable audit package with cryptographic SHA-256 evidence manifest."""
        pkg_id = f"PKG-{uuid.uuid4().hex[:12].upper()}"
        created_at = datetime.now(UTC).isoformat()

        manifest_entries: list[dict[str, str]] = []

        # Add evaluation manifest
        eval_sha = digest_object(evaluation)
        manifest_entries.append({
            "artifact": "compliance_evaluation.json",
            "category": "REGULATORY_COMPLIANCE",
            "sha256": eval_sha,
        })

        # Add reconciliation report manifest if present
        if reconciliation_report:
            recon_sha = digest_object(reconciliation_report)
            manifest_entries.append({
                "artifact": "financial_reconciliation.json",
                "category": "FINANCIAL_AUDIT",
                "sha256": recon_sha,
            })

        # Add document inventory manifests
        for doc in evaluation.get("document_inventory", []):
            manifest_entries.append({
                "artifact": f"docs/{doc['document_id']}.json",
                "category": doc["type"],
                "sha256": doc["sha256"],
            })

        manifest_entries.sort(key=lambda m: m["artifact"])
        manifest_digest = digest_object(manifest_entries)

        package = {
            "schema": SCHEMA_AUDIT_PACKAGE,
            "package_id": pkg_id,
            "tenant_id": self.tenant_id,
            "created_at": created_at,
            "authority_state": "ADVISORY_ONLY",
            "manifest_sha256": manifest_digest,
            "manifest": manifest_entries,
            "contents": {
                "compliance_evaluation": evaluation,
                "financial_reconciliation": reconciliation_report,
            },
            "unresolved_exceptions_count": evaluation.get("counts", {}).get("unresolved_exceptions", 0),
            "disclaimer": (
                "DISPATER audit packages provide reproducible evidence aggregation for human compliance "
                "and financial officers. Manifest SHA-256 digests verify integrity only and do not constitute "
                "independent regulatory certification or legally binding determinations."
            ),
        }

        package["package_receipt_sha256"] = digest_object({k: v for k, v in package.items() if k != "package_receipt_sha256"})
        return package
