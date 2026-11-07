"""Linked industrial records stay on the existing DISPATER engine."""

from __future__ import annotations

import importlib.util
import io
import json
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from aurex.api import app
from aurex.dispater_ingest import IngestError, ingest_source
from aurex.dispater_intelligence import InvalidSnapshot, RevenueLeakageEngine
from aurex.relationships.analytics import benchmark, duplicate_jobs, sum_hours_decimal
from aurex.relationships.documents import parser_inventory, require_not_inferred
from aurex.relationships.explain import explain_finding
from aurex.relationships.log import project


def _golden_fixture() -> ModuleType:
    """Load by path. ``import tests`` is not available to ``pytest -q``."""
    path = Path(__file__).resolve().parent / "test_dispater_golden_audit.py"
    spec = importlib.util.spec_from_file_location("cclxxvi_golden_fixture", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("golden fixture is missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_GOLDEN = _golden_fixture()
EXPECTED = _GOLDEN.EXPECTED
build_dataset = _GOLDEN.build_dataset

TOKEN = "d" * 32


def _client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    import hashlib

    grants = {hashlib.sha256(TOKEN.encode()).hexdigest(): ["tenant-a", "golden"]}
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps(grants))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "industrial.db"))
    return TestClient(app, raise_server_exceptions=False)


def _dataset() -> dict[str, object]:
    return {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [
            {
                "rate_id": "R1",
                "customer_id": "C1",
                "service_code": "S1",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            }
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "open"}],
        "payments": [{"payment_id": "P1", "invoice_id": "I1", "amount": "100.00"}],
        "equipment": [
            {
                "ticket_id": "T1",
                "job_id": "J1",
                "equipment_id": "E1",
                "service_date": "2026-03-01",
                "billable_hours": "2.00",
                "standby_hours": "0.00",
                "invoiced_hours": "2.00",
            }
        ],
        "contracts": [{"contract_id": "K1", "job_id": "J1"}],
        "approvals": [
            {"approval_id": "A1", "invoice_id": "I1", "disposition": "RECORDED_APPROVAL"}
        ],
    }


def test_projection_links_the_chain_and_does_not_invent_a_missing_invoice() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(_dataset())
    linked = project(_dataset(), report["dataset_sha256"])
    qualifiers = {(item["source_id"], item["qualifier"], item["target_id"]) for item in linked["relations"]}
    assert ("field_ticket:T1", "concerns", "job:J1") in qualifiers
    assert ("equipment:E1", "uses", "field_ticket:T1") in qualifiers
    assert ("invoice:I1", "bills", "job:J1") in qualifiers
    assert ("contract:K1", "governed_by", "job:J1") in qualifiers
    assert ("approval:A1", "approves", "invoice:I1") in qualifiers
    assert ("payment:P1", "settles", "invoice:I1") in qualifiers
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert linked["effect"] == "NONE"
    orphan = {
        **_dataset(),
        "payments": [{"payment_id": "P9", "invoice_id": "MISSING", "amount": "5.00"}],
    }
    report = RevenueLeakageEngine("tenant-a").reconcile_records(orphan)
    linked = project(orphan, report["dataset_sha256"])
    assert not any(item["source_id"] == "payment:P9" and item["qualifier"] == "settles" for item in linked["relations"])
    assert any(item["source_id"] == "payment:P9" and item["reason"] == "ENDPOINT_NOT_IN_SOURCE" for item in linked["unresolved"])


def test_recorded_approval_is_not_an_executable_effect() -> None:
    dataset = _dataset()
    approvals = dataset["approvals"]
    assert isinstance(approvals, list)
    approvals[0]["disposition"] = "APPROVED"
    with pytest.raises(InvalidSnapshot, match="disposition"):
        project(dataset, "a" * 64)


def test_golden_dollars_and_explanations_stay_separated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dataset = build_dataset()
    report = RevenueLeakageEngine("golden").reconcile_records(dataset)
    for key, value in EXPECTED.items():
        assert report["financial_summary"][key] == value
    claims = {explain_finding(finding)["claim_class"] for finding in report["findings"]}
    assert "SUSPECTED_EXPOSURE" in claims
    assert "UNVERIFIED_INTERPRETATION" in claims
    assert "CALCULATED_DISCREPANCY" in claims
    for finding in report["findings"]:
        explanation = explain_finding(finding)
        assert explanation["confirmed_recovery_usd"] == "0.00"
        assert explanation["authority"] == "NONE"
        assert explanation["observed_facts"]
        filled = [
            explanation["calculated_discrepancy_usd"],
            explanation["suspected_exposure_usd"],
            explanation["unverified_interpretation"],
        ]
        assert sum(item not in (None, False) for item in filled) == 1
    client = _client(monkeypatch, tmp_path)
    headers = {"Authorization": "Bearer " + TOKEN}
    response = client.post("/v1/dispater/relationships", json=dataset, headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["confirmed_recovery_usd"] == "0.00"
    assert body["identified_exposure_usd"] == "385.00"
    explanation = client.get(
        "/v1/dispater/explanations",
        params={"tenant_id": "golden", "finding_id": "FND-UNBILLED_JOB-J02"},
        headers=headers,
    )
    assert explanation.status_code == 200
    assert explanation.json()["suspected_exposure_usd"] == "100.00"
    assert explanation.json()["calculated_discrepancy_usd"] is None
    other = client.get(
        "/v1/dispater/relationships",
        params={"tenant_id": "tenant-a", "dataset_sha256": body["dataset_sha256"]},
        headers=headers,
    )
    assert other.status_code == 404


def test_xlsx_cells_keep_their_address_and_scans_are_not_guessed() -> None:
    book = Workbook()
    sheet = book.active
    assert sheet is not None
    sheet.title = "invoices"
    sheet.append(["invoice_id", "job_id", "amount", "status"])
    sheet.append(["I1", "J1", "100.00", "open"])
    buffer = io.BytesIO()
    book.save(buffer)
    batch = ingest_source("tenant-a", "invoices.xlsx", buffer.getvalue(), kind="xlsx")
    amount = next(item for item in batch["field_provenance"] if item["field"] == "amount")
    assert amount["cell"] == "C2"
    assert amount["sheet"] == "invoices"
    assert amount["inferred"] is False
    assert amount["value"] == "100.00"
    require_not_inferred(batch["field_provenance"])
    inventory = parser_inventory()
    assert inventory["docling"]["adopted"] is False
    assert inventory["docling"]["installed"] is False
    assert inventory["ocr"] == "NOT_INSTALLED"
    png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + (1).to_bytes(4, "big") + (1).to_bytes(4, "big")
    with pytest.raises(IngestError, match="OCR runtime is not installed"):
        ingest_source("tenant-a", "scan.png", png, kind="png")


def test_sqlite_cents_match_decimal_and_are_not_the_money_engine() -> None:
    invoices = [{"job_id": "J1" if index % 5 == 0 else f"J{index}"} for index in range(500)]
    hours = [
        {"equipment_id": f"E{index % 7}", "billable_hours": "1.25"}
        for index in range(500)
    ]
    assert duplicate_jobs(invoices)
    measured = benchmark(invoices, hours)
    assert measured["duplicates_match"] is True
    assert measured["hours_match"] is True
    assert measured["adopted_for_money_path"] is False
    assert sum_hours_decimal(hours)["E0"] == f"{Decimal('1.25') * (500 // 7 + (1 if 0 < 500 % 7 else 0)):.2f}"


def test_relationship_route_is_tenant_bound(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, tmp_path)
    denied = client.post("/v1/dispater/relationships", json=_dataset(), headers={"Authorization": "Bearer " + ("e" * 32)})
    assert denied.status_code == 401
    missing = client.get("/v1/dispater/parser-inventory", params={"tenant_id": "tenant-a"})
    assert missing.status_code == 401
