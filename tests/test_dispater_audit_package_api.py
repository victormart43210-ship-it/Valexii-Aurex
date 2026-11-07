"""Audit package route: tenant isolation, bounds, and statelessness."""

import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aurex.api import app

TOKEN_A = "a" * 32
TOKEN_B = "b" * 32


def _sha(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _h(token: str) -> dict[str, str]:
    return {"Authorization": "Bearer " + token}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    grants = {_sha(TOKEN_A): ["tenant-a"], _sha(TOKEN_B): ["tenant-b"]}
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps(grants))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "d.db"))
    return TestClient(app, raise_server_exceptions=False)


BODY = {
    "tenant_id": "tenant-a",
    "vehicles": [{"vehicle_id": "T1"}],
    "drivers": [{"driver_id": "D1"}],
    "documents": [],
}


def test_requires_authentication(client: TestClient) -> None:
    assert client.post("/v1/dispater/audit-package/generate", json=BODY).status_code == 401


def test_cross_tenant_denied(client: TestClient) -> None:
    r = client.post("/v1/dispater/audit-package/generate", json=BODY, headers=_h(TOKEN_B))
    assert r.status_code == 403


def test_package_is_advisory_and_tenant_bound(client: TestClient) -> None:
    r = client.post("/v1/dispater/audit-package/generate", json=BODY, headers=_h(TOKEN_A))
    assert r.status_code == 200
    pkg = r.json()
    assert pkg["tenant_id"] == "tenant-a"
    assert pkg["authority_state"] == "ADVISORY_ONLY"
    assert pkg["contents"]["financial_reconciliation"] is None
    assert pkg["unresolved_exceptions_count"] > 0


def test_oversized_and_malformed_input_rejected(client: TestClient) -> None:
    big = {**BODY, "documents": [{}] * 2001}
    assert client.post("/v1/dispater/audit-package/generate", json=big, headers=_h(TOKEN_A)).status_code == 422
    bad = {**BODY, "tenant_id": "../x"}
    assert client.post("/v1/dispater/audit-package/generate", json=bad, headers=_h(TOKEN_A)).status_code == 422


def test_package_attaches_only_own_tenant_run(client: TestClient) -> None:
    ds = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [
            {"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01", "end": "2026-12-31", "amount": "100.00"}
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "150.00", "status": "open"}],
        "payments": [],
    }
    assert client.post("/v1/dispater/reconciliation", json=ds, headers=_h(TOKEN_A)).status_code == 200
    mine = client.post("/v1/dispater/audit-package/generate", json=BODY, headers=_h(TOKEN_A)).json()
    assert mine["contents"]["financial_reconciliation"]["tenant_id"] == "tenant-a"
    other = client.post(
        "/v1/dispater/audit-package/generate", json={**BODY, "tenant_id": "tenant-b"}, headers=_h(TOKEN_B)
    ).json()
    assert other["contents"]["financial_reconciliation"] is None
