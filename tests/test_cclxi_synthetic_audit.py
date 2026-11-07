"""Authenticated synthetic audit through the existing DISPATER route."""

import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aurex.api import app

TOKEN = "d" * 32


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    grant = hashlib.sha256(TOKEN.encode()).hexdigest()
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps({grant: ["tenant-a"]}))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "audit.db"))
    return TestClient(app, raise_server_exceptions=False)


def test_authorized_synthetic_audit_returns_proof_and_zero_recovery(client: TestClient) -> None:
    response = client.post(
        "/v1/dispater/reconciliation",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
            "rates": [
                {
                    "rate_id": "R1",
                    "customer_id": "C1",
                    "service_code": "S",
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "amount": "100.00",
                }
            ],
            "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "110.00", "status": "open"}],
            "payments": [],
        },
    )
    assert response.status_code == 200
    body = response.json()
    summary = body["financial_summary"]
    assert summary["confirmed_recovery_usd"] == "0.00"
    assert summary["identified_exposure_usd"] == "10.00"
    assert body["authority_state"] == "HOLD"
    finding = body["findings"][0]
    explanation = finding["xaeli_explanation"]
    assert set(explanation) >= {"now", "changed", "next", "why", "proof"}
    assert body["receipt_sha256"]


def test_missing_token_is_denied(client: TestClient) -> None:
    response = client.post(
        "/v1/dispater/reconciliation",
        json={"tenant_id": "tenant-a", "dataset_type": "SYNTHETIC_ONLY", "jobs": [], "rates": [], "invoices": [], "payments": []},
    )
    assert response.status_code in {401, 403}
