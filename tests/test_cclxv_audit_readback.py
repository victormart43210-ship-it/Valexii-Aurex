"""Stored audit read-back and an approval claim that cannot move money."""

import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aurex.api import app

TOKEN = "e" * 32


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    grant = hashlib.sha256(TOKEN.encode()).hexdigest()
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps({grant: ["tenant-a"]}))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "readback.db"))
    return TestClient(app, raise_server_exceptions=False)


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOKEN}"}


def test_stored_run_matches_the_response_and_stays_at_zero_recovery(client: TestClient) -> None:
    created = client.post(
        "/v1/dispater/reconciliation",
        headers=_headers(),
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
    assert created.status_code == 200
    body = created.json()
    stored = client.get(f"/v1/dispater/runs/{body['run_id']}", headers=_headers(), params={"tenant_id": "tenant-a"})
    assert stored.status_code == 200
    again = stored.json()
    assert again["receipt_sha256"] == body["receipt_sha256"]
    assert again["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert again["authority_state"] == "HOLD"


def test_bad_money_is_rejected_and_an_approval_claim_has_no_effect(client: TestClient) -> None:
    bad = client.post(
        "/v1/dispater/reconciliation",
        headers=_headers(),
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
                    "amount": "not-money",
                }
            ],
            "invoices": [],
            "payments": [],
        },
    )
    assert bad.status_code == 400
    missing = client.post(
        "/v1/dispater/reconciliation",
        json={"tenant_id": "tenant-a", "dataset_type": "SYNTHETIC_ONLY", "jobs": [], "rates": [], "invoices": [], "payments": []},
    )
    assert missing.status_code in {401, 403}
    claim = client.post(
        "/v1/dispater/lifecycle/authorization-decision",
        headers=_headers(),
        json={
            "tenant_id": "tenant-a",
            "actor_id": "owner",
            "action": "approve-recovery",
            "scope": "tenant-a",
            "expires_at": "2026-12-31T00:00:00Z",
            "confirmed_recovery_usd": "50.00",
        },
    )
    assert claim.status_code == 200
    decision = claim.json()
    assert decision["effect"] == "NONE"
    assert decision["financial_action"] == "NONE"
    assert decision["verification"] == "UNVERIFIED"
