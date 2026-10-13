"""API endpoint integration tests."""

from fastapi.testclient import TestClient

from aurex.api import app

client = TestClient(app)


def test_health_endpoint() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "authority": "none"}


def test_capabilities_endpoint() -> None:
    res = client.get("/api/v1/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert data["authority_boundary"] == "ADVISORY_ONLY"
    assert "capabilities" in data


def test_jobs_submission_endpoint() -> None:
    res = client.post(
        "/api/v1/jobs",
        json={"job_id": "job-101", "track": "synthetic", "payload": {}},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "QUEUED"


def test_evidence_summary_endpoint() -> None:
    res = client.get("/api/v1/evidence")
    assert res.status_code == 200
    assert res.json()["authority_granted"] is False
