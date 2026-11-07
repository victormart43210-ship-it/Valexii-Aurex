"""The website golden fixture and the relationship API agree on the ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_intelligence import RevenueLeakageEngine

TOKEN = "g" * 32
OTHER = "h" * 32
FIXTURE = Path("website/src/lib/golden-ledger.json")


def _client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    grants = {
        hashlib.sha256(TOKEN.encode()).hexdigest(): ["demo-oilfield-tenant"],
        hashlib.sha256(OTHER.encode()).hexdigest(): ["other-tenant"],
    }
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps(grants))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "golden.db"))
    return TestClient(app, raise_server_exceptions=False)


def test_committed_fixture_matches_the_independent_golden_totals() -> None:
    dataset = json.loads(FIXTURE.read_text())
    report = RevenueLeakageEngine("golden").reconcile_records(dataset)
    summary = report["financial_summary"]
    assert summary["identified_exposure_usd"] == "385.00"
    assert summary["withheld_unresolved_usd"] == "150.00"
    assert summary["confirmed_recovery_usd"] == "0.00"


def test_relationship_api_keeps_the_golden_ledger_and_blocks_the_other_tenant(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    client = _client(monkeypatch, tmp_path)
    dataset = json.loads(FIXTURE.read_text())
    dataset["tenant_id"] = "demo-oilfield-tenant"
    dataset["companies"] = [{"company_id": "CO-GOLDEN", "customer_id": "C1"}]
    dataset["contracts"] = [{"contract_id": "K-GOLDEN", "job_id": "J00"}]
    dataset["approvals"] = [
        {"approval_id": "A-GOLDEN", "invoice_id": "I00", "disposition": "PENDING_HUMAN_REVIEW"}
    ]
    headers = {"Authorization": f"Bearer {TOKEN}"}
    posted = client.post("/v1/dispater/relationships", json=dataset, headers=headers)
    assert posted.status_code == 200, posted.text
    body = posted.json()
    assert body["identified_exposure_usd"] == "385.00"
    assert body["withheld_unresolved_usd"] == "150.00"
    assert body["confirmed_recovery_usd"] == "0.00"
    assert body["financial_authority"] == "NONE"
    links = client.get(
        "/v1/dispater/relationships",
        params={"tenant_id": "demo-oilfield-tenant", "dataset_sha256": body["dataset_sha256"]},
        headers=headers,
    )
    assert links.status_code == 200
    stored = links.json()
    types = {item["object_type"] for item in stored["objects"]}
    assert {"company", "job", "invoice", "contract", "approval", "payment"} <= types
    assert "equipment" not in types
    assert any(item["reason"] == "ENDPOINT_NOT_IN_SOURCE" for item in body["relationships"]["unresolved"])
    explanation = client.get(
        "/v1/dispater/explanations",
        params={
            "tenant_id": "demo-oilfield-tenant",
            "finding_id": "FND-UNBILLED_JOB-J02",
            "run_id": body["run_id"],
        },
        headers=headers,
    )
    assert explanation.status_code == 200
    explained = explanation.json()
    assert explained["suspected_exposure_usd"] == "100.00"
    assert explained["calculated_discrepancy_usd"] is None
    assert explained["confirmed_recovery_usd"] == "0.00"
    assert explained["observed_facts"]
    denied = client.get(
        "/v1/dispater/relationships",
        params={"tenant_id": "demo-oilfield-tenant", "dataset_sha256": body["dataset_sha256"]},
        headers={"Authorization": f"Bearer {OTHER}"},
    )
    assert denied.status_code == 403
    missing = client.post("/v1/dispater/relationships", json=dataset)
    assert missing.status_code == 401
