"""Independent test suite and financial reference oracle for Towing Revenue Recovery & Audit Readiness.

Tests all 10 towing scenarios deterministically:
1. Unbilled completed tow (DISPATCH_UNBILLED)
2. Contracted rate mismatch (RATE_MISMATCH)
3. Unbilled storage days (STORAGE_UNBILLED)
4. Incorrect after-hours surcharge (AFTER_HOURS_SURCHARGE_MISMATCH)
5. Partial motor-club payment / short pay (MOTOR_CLUB_SHORT_PAY)
6. Duplicate invoice (DUPLICATE_INVOICE)
7. Missing deposit reconciliation (UNRECONCILED_DEPOSIT)
8. Contract amendment and effective-date changes (CONTRACT_AMENDMENT_INVALID)
9. Disputed charges (DISPUTED_CHARGE)
10. Confirmed payment recovery (CONFIRMED_PAYMENT_RECOVERY)
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_intelligence import (
    AuditPackageGenerator,
    RevenueLeakageEngine,
    report_to_csv,
    verify_receipt,
)


def independent_towing_oracle(dataset: dict[str, Any]) -> dict[str, Any]:
    """Independent financial reference calculator for towing operations."""
    totals = {
        "POTENTIAL_UNDERBILLING": Decimal("0.00"),
        "POTENTIAL_OVERBILLING": Decimal("0.00"),
        "UNVERIFIED_EXPOSURE": Decimal("0.00"),
        "CONFIRMED_RECOVERY": Decimal("0.00"),
    }
    findings_count = 0

    dispatches = dataset.get("dispatches", [])
    contracts = {c["contract_id"]: c for c in dataset.get("contracts", [])}
    rates = dataset.get("rates", [])
    invoices = dataset.get("invoices", [])
    payments = dataset.get("payments", [])
    deposits = dataset.get("deposits", [])

    invs_by_disp: dict[str, list[dict[str, Any]]] = {}
    for inv in invoices:
        invs_by_disp.setdefault(inv["dispatch_id"], []).append(inv)

    rates_by_contract: dict[str, list[dict[str, Any]]] = {}
    for r in rates:
        rates_by_contract.setdefault(r["contract_id"], []).append(r)

    for d in dispatches:
        cid = d["contract_id"]
        c = contracts.get(cid)
        if not c:
            totals["UNVERIFIED_EXPOSURE"] += Decimal("0.00")
            findings_count += 1
            continue

        c_start = c["effective_start"]
        c_end = c["effective_end"]
        d_date = d["date"]
        if not (c_start <= d_date <= c_end):
            totals["UNVERIFIED_EXPOSURE"] += Decimal("0.00")
            findings_count += 1

        invs = invs_by_disp.get(d["dispatch_id"], [])
        svc = d["service_type"]

        if d["status"] == "completed" and not invs:
            active_base = [r for r in rates_by_contract.get(cid, []) if r["charge_type"] == svc and r["effective_start"] <= d_date <= r["effective_end"]]
            if len(active_base) == 1:
                amt = Decimal(active_base[0]["amount"])
                totals["POTENTIAL_UNDERBILLING"] += amt
            findings_count += 1

        if len(invs) > 1:
            for inv in invs[1:]:
                totals["POTENTIAL_OVERBILLING"] += Decimal(inv["total_amount"])
            findings_count += 1

        if len(invs) == 1:
            inv = invs[0]
            active_base = [r for r in rates_by_contract.get(cid, []) if r["charge_type"] == svc and r["effective_start"] <= d_date <= r["effective_end"]]
            if len(active_base) == 1 and "base_amount" in inv:
                expected_b = Decimal(active_base[0]["amount"])
                actual_b = Decimal(inv["base_amount"])
                if actual_b != expected_b:
                    diff = actual_b - expected_b
                    if diff < 0:
                        totals["POTENTIAL_UNDERBILLING"] += abs(diff)
                    else:
                        totals["POTENTIAL_OVERBILLING"] += abs(diff)
                    findings_count += 1

            storage_days = int(d.get("storage_days", "0"))
            storage_rates = [r for r in rates_by_contract.get(cid, []) if r["charge_type"] == "DAILY_STORAGE" and r["effective_start"] <= d_date <= r["effective_end"]]
            if storage_days > 0 and len(storage_rates) == 1:
                exp_stor = Decimal(storage_rates[0]["amount"]) * Decimal(storage_days)
                billed_stor = Decimal(inv.get("storage_amount", "0.00"))
                if billed_stor < exp_stor:
                    totals["POTENTIAL_UNDERBILLING"] += (exp_stor - billed_stor)
                    findings_count += 1

            if d.get("after_hours") in ("true", "1", "yes"):
                ah_rates = [r for r in rates_by_contract.get(cid, []) if r["charge_type"] == "AFTER_HOURS_SURCHARGE" and r["effective_start"] <= d_date <= r["effective_end"]]
                if len(ah_rates) == 1:
                    exp_ah = Decimal(ah_rates[0]["amount"])
                    billed_ah = Decimal(inv.get("after_hours_amount", "0.00"))
                    if billed_ah != exp_ah:
                        diff_ah = billed_ah - exp_ah
                        if diff_ah < 0:
                            totals["POTENTIAL_UNDERBILLING"] += abs(diff_ah)
                        else:
                            totals["POTENTIAL_OVERBILLING"] += abs(diff_ah)
                        findings_count += 1

    for inv in invoices:
        billed = Decimal(inv["total_amount"])
        inv_pays = [p for p in payments if p["invoice_id"] == inv["invoice_id"]]
        total_p = sum((Decimal(p["amount"]) for p in inv_pays), Decimal("0.00"))

        if inv["status"] == "disputed":
            totals["UNVERIFIED_EXPOSURE"] += billed
            findings_count += 1

        mc_pays = [p for p in inv_pays if "motor_club" in p.get("source", "").lower()]
        if mc_pays and total_p < billed and inv["status"] != "disputed":
            totals["POTENTIAL_UNDERBILLING"] += (billed - total_p)
            findings_count += 1

        if inv.get("recovery_status") == "SETTLED_BY_HUMAN":
            settled = Decimal(inv.get("recovered_amount", "0.00"))
            if settled > 0:
                totals["CONFIRMED_RECOVERY"] += settled
                findings_count += 1

    tot_pay = sum((Decimal(p["amount"]) for p in payments), Decimal("0.00"))
    tot_dep = sum((Decimal(d["amount"]) for d in deposits), Decimal("0.00"))
    if deposits and tot_pay != tot_dep:
        totals["UNVERIFIED_EXPOSURE"] += abs(tot_dep - tot_pay)
        findings_count += 1

    total_exp = totals["POTENTIAL_UNDERBILLING"] + totals["POTENTIAL_OVERBILLING"] + totals["UNVERIFIED_EXPOSURE"]
    return {
        "identified_exposure_usd": str(total_exp),
        "potential_underbilling_usd": str(totals["POTENTIAL_UNDERBILLING"]),
        "potential_overbilling_usd": str(totals["POTENTIAL_OVERBILLING"]),
        "unverified_exposure_usd": str(totals["UNVERIFIED_EXPOSURE"]),
        "confirmed_recovery_usd": str(totals["CONFIRMED_RECOVERY"]),
        "findings_count": findings_count,
    }


def make_full_towing_dataset(tenant: str = "TOW-CO-101") -> dict[str, Any]:
    """Dataset covering all 10 towing recovery scenarios."""
    return {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "contracts": [
            {
                "contract_id": "CNT-AAA",
                "customer_name": "AAA Motor Club",
                "effective_start": "2026-01-01",
                "effective_end": "2026-12-31",
            },
            {
                "contract_id": "CNT-PD",
                "customer_name": "Metro Police Impound",
                "effective_start": "2026-06-01",
                "effective_end": "2026-12-31",
            },
        ],
        "rates": [
            {
                "rate_id": "RATE-AAA-STANDARD",
                "contract_id": "CNT-AAA",
                "charge_type": "STANDARD_TOW",
                "amount": "125.00",
                "effective_start": "2026-01-01",
                "effective_end": "2026-12-31",
            },
            {
                "rate_id": "RATE-AAA-AH",
                "contract_id": "CNT-AAA",
                "charge_type": "AFTER_HOURS_SURCHARGE",
                "amount": "45.00",
                "effective_start": "2026-01-01",
                "effective_end": "2026-12-31",
            },
            {
                "rate_id": "RATE-PD-HEAVY",
                "contract_id": "CNT-PD",
                "charge_type": "HEAVY_DUTY_TOW",
                "amount": "450.00",
                "effective_start": "2026-06-01",
                "effective_end": "2026-12-31",
            },
            {
                "rate_id": "RATE-PD-STORAGE",
                "contract_id": "CNT-PD",
                "charge_type": "DAILY_STORAGE",
                "amount": "60.00",
                "effective_start": "2026-06-01",
                "effective_end": "2026-12-31",
            },
        ],
        "dispatches": [
            {
                "dispatch_id": "DSP-001",
                "contract_id": "CNT-AAA",
                "service_type": "STANDARD_TOW",
                "date": "2026-07-10",
                "status": "completed",
            },
            {
                "dispatch_id": "DSP-002",
                "contract_id": "CNT-AAA",
                "service_type": "STANDARD_TOW",
                "date": "2026-07-11",
                "status": "completed",
                "after_hours": "true",
            },
            {
                "dispatch_id": "DSP-003",
                "contract_id": "CNT-PD",
                "service_type": "HEAVY_DUTY_TOW",
                "date": "2026-07-12",
                "status": "completed",
                "storage_days": "3",
            },
            {
                "dispatch_id": "DSP-004",
                "contract_id": "CNT-AAA",
                "service_type": "STANDARD_TOW",
                "date": "2026-07-13",
                "status": "completed",
            },
            {
                "dispatch_id": "DSP-005",
                "contract_id": "CNT-PD",
                "service_type": "HEAVY_DUTY_TOW",
                "date": "2026-05-01",
                "status": "completed",
            },
        ],
        "invoices": [
            {
                "invoice_id": "INV-002",
                "dispatch_id": "DSP-002",
                "base_amount": "115.00",
                "after_hours_amount": "30.00",
                "total_amount": "145.00",
                "status": "open",
            },
            {
                "invoice_id": "INV-003",
                "dispatch_id": "DSP-003",
                "base_amount": "450.00",
                "storage_amount": "60.00",
                "total_amount": "510.00",
                "status": "open",
            },
            {
                "invoice_id": "INV-004-A",
                "dispatch_id": "DSP-004",
                "total_amount": "125.00",
                "status": "open",
            },
            {
                "invoice_id": "INV-004-B",
                "dispatch_id": "DSP-004",
                "total_amount": "125.00",
                "status": "open",
            },
            {
                "invoice_id": "INV-005-MC",
                "dispatch_id": "DSP-NONE-5",
                "total_amount": "200.00",
                "status": "open",
            },
            {
                "invoice_id": "INV-006-DISPUTED",
                "dispatch_id": "DSP-NONE-6",
                "total_amount": "350.00",
                "status": "disputed",
            },
            {
                "invoice_id": "INV-007-SETTLED",
                "dispatch_id": "DSP-NONE-7",
                "total_amount": "100.00",
                "status": "paid",
                "recovery_status": "SETTLED_BY_HUMAN",
                "recovered_amount": "100.00",
            },
        ],
        "payments": [
            {
                "payment_id": "PAY-005",
                "invoice_id": "INV-005-MC",
                "amount": "150.00",
                "payment_date": "2026-07-20",
                "source": "motor_club_remit",
            },
            {
                "payment_id": "PAY-007",
                "invoice_id": "INV-007-SETTLED",
                "amount": "100.00",
                "payment_date": "2026-07-21",
                "source": "customer_check",
            },
        ],
        "deposits": [
            {
                "deposit_id": "DEP-001",
                "bank_reference": "BNK-BATCH-99",
                "amount": "200.00",
                "deposit_date": "2026-07-22",
            }
        ],
    }


def test_towing_reconciliation_against_independent_oracle() -> None:
    """Gate: Full towing reconciliation matches independent oracle exactly."""
    tenant = "TOW-CO-101"
    dataset = make_full_towing_dataset(tenant)
    engine = RevenueLeakageEngine(tenant_id=tenant)
    report = engine.reconcile_records(dataset)

    oracle = independent_towing_oracle(dataset)

    assert report["schema"] == "dispater.synthetic.towing_recovery.v1"
    assert report["tenant_id"] == tenant
    assert report["status"] == "AUDIT_COMPLETE"
    assert report["authority_state"] == "HOLD"
    assert report["human_review_required"] is True

    fin = report["financial_summary"]
    assert fin["identified_exposure_usd"] == oracle["identified_exposure_usd"]
    assert fin["potential_underbilling_usd"] == oracle["potential_underbilling_usd"]
    assert fin["potential_overbilling_usd"] == oracle["potential_overbilling_usd"]
    assert fin["unverified_exposure_usd"] == oracle["unverified_exposure_usd"]
    assert fin["confirmed_recovery_usd"] == oracle["confirmed_recovery_usd"]
    assert len(report["findings"]) == oracle["findings_count"]

    assert Decimal(fin["confirmed_recovery_usd"]) == Decimal("100.00")
    assert verify_receipt(report) is True


def test_clean_towing_dataset_zero_findings() -> None:
    """Verify that a perfectly matched towing operational dataset yields 0 findings."""
    tenant = "CLEAN-TOW-202"
    clean_dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "contracts": [
            {
                "contract_id": "CNT-CLEAN",
                "customer_name": "Clean Commercial Fleet",
                "effective_start": "2026-01-01",
                "effective_end": "2026-12-31",
            }
        ],
        "rates": [
            {
                "rate_id": "RATE-CLEAN",
                "contract_id": "CNT-CLEAN",
                "charge_type": "STANDARD_TOW",
                "amount": "150.00",
                "effective_start": "2026-01-01",
                "effective_end": "2026-12-31",
            }
        ],
        "dispatches": [
            {
                "dispatch_id": "DSP-CLEAN-1",
                "contract_id": "CNT-CLEAN",
                "service_type": "STANDARD_TOW",
                "date": "2026-06-15",
                "status": "completed",
            }
        ],
        "invoices": [
            {
                "invoice_id": "INV-CLEAN-1",
                "dispatch_id": "DSP-CLEAN-1",
                "base_amount": "150.00",
                "total_amount": "150.00",
                "status": "paid",
            }
        ],
        "payments": [
            {
                "payment_id": "PAY-CLEAN-1",
                "invoice_id": "INV-CLEAN-1",
                "amount": "150.00",
                "payment_date": "2026-06-16",
                "source": "ach_direct",
            }
        ],
        "deposits": [
            {
                "deposit_id": "DEP-CLEAN-1",
                "bank_reference": "BNK-1001",
                "amount": "150.00",
                "deposit_date": "2026-06-17",
            }
        ],
    }
    engine = RevenueLeakageEngine(tenant_id=tenant)
    report = engine.reconcile_records(clean_dataset)

    assert len(report["findings"]) == 0
    assert report["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert report["financial_summary"]["potential_underbilling_usd"] == "0.00"
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"


def test_towing_csv_formula_injection_defense() -> None:
    """Verify formula injection sanitization in towing export."""
    tenant = "TOW-INJECT-99"
    dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "contracts": [
            {
                "contract_id": "=cmd|' /C calc'!A0",
                "customer_name": "@MALICIOUS_CORP",
                "effective_start": "2026-01-01",
                "effective_end": "2026-12-31",
            }
        ],
        "rates": [
            {
                "rate_id": "RATE-INJECT",
                "contract_id": "'=cmd|' /C calc'!A0",
                "charge_type": "+EXCEL_POISON",
                "amount": "100.00",
                "effective_start": "2026-01-01",
                "effective_end": "2026-12-31",
            }
        ],
        "dispatches": [
            {
                "dispatch_id": "DSP-INJECT",
                "contract_id": "'=cmd|' /C calc'!A0",
                "service_type": "'+EXCEL_POISON",
                "date": "2026-06-01",
                "status": "completed",
            }
        ],
        "invoices": [],
        "payments": [],
        "deposits": [],
    }
    engine = RevenueLeakageEngine(tenant_id=tenant)
    report = engine.reconcile_records(dataset)
    csv_out = report_to_csv(report)
    for line in csv_out.splitlines():
        if line:
            for cell in line.split(","):
                assert not cell.startswith(("=", "+", "-", "@", "\t", "\r")), f"Unsanitized formula cell: {cell}"


def test_audit_package_generation_and_freshness() -> None:
    """Verify AuditPackageGenerator with document inventory, expirations, and DOT/FMCSA checks."""
    tenant = "TOW-AUDIT-303"
    payload = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "as_of_date": "2026-11-05",
        "documents": [
            {
                "document_id": "DOC-CDL-01",
                "document_type": "COMMERCIAL_DRIVER_LICENSE",
                "title": "Lead Driver Class A CDL",
                "issue_date": "2022-01-01",
                "expiration_date": "2027-01-01",
                "jurisdiction": "TX",
            },
            {
                "document_id": "DOC-DOT-INSP-01",
                "document_type": "ANNUAL_DOT_INSPECTION",
                "title": "Wrecker #104 Annual Inspection",
                "issue_date": "2024-01-01",
                "expiration_date": "2025-01-01",
                "jurisdiction": "FMCSA",
            },
        ],
        "requirements": [
            {
                "requirement_id": "REQ-FMCSA-396",
                "regulatory_body": "FMCSA",
                "standard_code": "49 CFR 396.17",
                "title": "Periodic vehicle inspection",
                "required_document_type": "ANNUAL_DOT_INSPECTION",
                "mandatory": "true",
            },
            {
                "requirement_id": "REQ-TX-TDLR",
                "regulatory_body": "TDLR",
                "standard_code": "TX-TOW-2026",
                "title": "Incident Management Tow Operator License",
                "required_document_type": "OPERATOR_LICENSE",
                "mandatory": "true",
            },
        ],
        "corrective_actions": [
            {
                "action_id": "CA-001",
                "title": "Schedule DOT Level 1 reinspection for Wrecker #104",
                "assigned_to": "Fleet Safety Mgr",
                "status": "in_progress",
                "due_date": "2026-10-01",
            }
        ],
    }

    gen = AuditPackageGenerator(tenant_id=tenant)
    pkg = gen.generate_audit_package(payload)

    assert pkg["schema"] == "dispater.synthetic.audit_package.v1"
    assert pkg["tenant_id"] == tenant
    assert pkg["status"] == "PACKAGE_GENERATED"
    assert pkg["authority_state"] == "HOLD"
    assert pkg["counts"]["total_documents"] == 2
    assert pkg["counts"]["fresh_documents"] == 1
    assert pkg["counts"]["expired_documents"] == 1
    assert pkg["counts"]["compliance_exceptions"] == 2
    assert len(pkg["evidence_manifest"]) > 0
    assert len(pkg["package_sha256"]) == 64


def test_towing_api_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify authenticated API execution of towing reconciliation and audit package export."""
    token = "a" * 32
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    tenant = "TOW-CO-101"
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps({token_hash: [tenant]}))

    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    dataset = make_full_towing_dataset(tenant)
    res = client.post("/v1/dispater/reconciliation", json=dataset, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["schema"] == "dispater.synthetic.towing_recovery.v1"
    assert data["tenant_id"] == tenant
    assert "run_id" in data

    audit_req = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "as_of_date": "2026-11-05",
        "documents": [
            {
                "document_id": "DOC-1",
                "document_type": "CERTIFICATE_OF_INSURANCE",
                "title": "Garagekeepers Liability 2026",
                "issue_date": "2026-01-01",
                "expiration_date": "2027-01-01",
                "jurisdiction": "TX",
            }
        ],
        "requirements": [
            {
                "requirement_id": "REQ-1",
                "regulatory_body": "TDLR",
                "standard_code": "TDLR-86",
                "title": "Minimum Insurance Requirements",
                "required_document_type": "CERTIFICATE_OF_INSURANCE",
                "mandatory": "true",
            }
        ],
        "corrective_actions": [],
    }
    pkg_res = client.post("/v1/dispater/audit-package", json=audit_req, headers=headers)
    assert pkg_res.status_code == 200
    pkg_data = pkg_res.json()
    assert pkg_data["status"] == "PACKAGE_GENERATED"
    assert "package_id" in pkg_data

    get_res = client.get(
        f"/v1/dispater/audit-package/{pkg_data['package_id']}?tenant_id={tenant}",
        headers=headers,
    )
    assert get_res.status_code == 200
    assert get_res.json()["package_sha256"] == pkg_data["package_sha256"]
