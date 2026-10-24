"""Security contract for the canonical synthetic industrial API."""
from fastapi.testclient import TestClient

from aurex.api import app


def test_demo_requires_authentication(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "s" * 40)
    monkeypatch.setenv("AUREX_ENABLE_INDUSTRIAL_DEMO", "1")
    monkeypatch.setenv("AUREX_DEPLOYMENT_SCOPE", "sandbox")
    client = TestClient(app)
    assert client.post("/v1/industrial/audit/demo", json={"fixture": "towing_v1"}).status_code == 401
    assert client.post("/v1/industrial/audit/demo", json={"fixture": "towing_v1"},
                       headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_demo_fails_closed_without_staging_scope(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "s" * 40)
    monkeypatch.setenv("AUREX_ENABLE_INDUSTRIAL_DEMO", "1")
    monkeypatch.setenv("AUREX_DEPLOYMENT_SCOPE", "production")
    response = TestClient(app).post("/v1/industrial/audit/demo",
                                    json={"fixture": "towing_v1"},
                                    headers={"Authorization": "Bearer " + "s" * 40})
    assert response.status_code == 503


def test_demo_rejects_customer_payload(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "s" * 40)
    monkeypatch.setenv("AUREX_ENABLE_INDUSTRIAL_DEMO", "1")
    monkeypatch.setenv("AUREX_DEPLOYMENT_SCOPE", "sandbox")
    client = TestClient(app)
    headers = {"Authorization": "Bearer " + "s" * 40}
    assert client.post("/v1/industrial/audit/demo",
                       json={"fixture": "towing_v1", "records": ["customer"]},
                       headers=headers).status_code == 422


def test_demo_returns_bounded_advisory_findings(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "s" * 40)
    monkeypatch.setenv("AUREX_ENABLE_INDUSTRIAL_DEMO", "1")
    monkeypatch.setenv("AUREX_DEPLOYMENT_SCOPE", "sandbox")
    response = TestClient(app).post("/v1/industrial/audit/demo",
                                    json={"fixture": "towing_v1"},
                                    headers={"Authorization": "Bearer " + "s" * 40})
    assert response.status_code == 200
    body = response.json()
    assert body["authority"] == "ADVISORY_ONLY_NO_CERTIFICATION"
    assert body["proof"]["status"] == "NOT_VERIFIED"
    assert body["changed"] == "NOT_VERIFIED_NO_PRIOR_SNAPSHOT"
    assert len(body["now"]) == 5
