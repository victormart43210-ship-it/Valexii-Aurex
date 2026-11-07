"""Health must name a missing dependency instead of calling the process ready."""

from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient

from aurex.api import app
from aurex.evidence_classes import evidence_class_for_claim
from aurex.readiness import readiness


def test_missing_store_is_not_healthy(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("aurex.readiness.DEFAULT_DB_PATH", str(tmp_path / "missing" / "jobs.db"))
    monkeypatch.setattr("aurex.readiness.db_path", lambda: str(tmp_path / "dispater.db"))
    report = readiness()
    assert report["readiness"] == "DEPENDENCY_UNAVAILABLE"
    assert report["process"] == "PROCESS_HEALTHY"
    response = TestClient(app).get("/health")
    assert response.status_code == 503
    assert response.json()["detail"]["readiness"] == "DEPENDENCY_UNAVAILABLE"


def test_open_ephemeral_store_is_degraded_and_the_model_is_not_called(monkeypatch, tmp_path) -> None:
    database = tmp_path / "jobs.db"
    sqlite3.connect(database).close()
    monkeypatch.setattr("aurex.readiness.DEFAULT_DB_PATH", str(database))
    monkeypatch.setattr("aurex.readiness.db_path", lambda: str(database))
    monkeypatch.delenv("AUREX_XAELI_STAGING_ENABLED", raising=False)
    monkeypatch.delenv("AUREX_QWEN_BASE_URL", raising=False)
    report = readiness()
    assert report["process"] == "PROCESS_HEALTHY"
    if report["stores"]["aurex"] == "EPHEMERAL":
        assert report["readiness"] == "DEGRADED"
    else:
        assert report["readiness"] == "READY"
    assert report["model"] == "NOT_CONFIGURED"
    assert report["provider"]["invocation"] == "NOT_PERFORMED"
    assert report["provider"]["paid_inference"] == "OFF"
    assert "://" not in str(report["provider"]["host_class"])


def test_private_qwen_off_railway_is_unavailable_without_a_request(monkeypatch, tmp_path) -> None:
    database = tmp_path / "jobs.db"
    sqlite3.connect(database).close()
    monkeypatch.setattr("aurex.readiness.DEFAULT_DB_PATH", str(database))
    monkeypatch.setattr("aurex.readiness.db_path", lambda: str(database))
    monkeypatch.setenv("AUREX_XAELI_STAGING_ENABLED", "1")
    monkeypatch.setenv("AUREX_XAELI_OPERATOR_APPROVED", "1")
    monkeypatch.setenv("AUREX_QWEN_BASE_URL", "http://qwen-private-staging.railway.internal:8080/v1")
    monkeypatch.delenv("RAILWAY_ENVIRONMENT_ID", raising=False)
    report = readiness()
    assert report["model"] == "MODEL_UNAVAILABLE"
    assert report["readiness"] == "DEGRADED"
    assert report["provider"]["host_class"] == "railway-private"
    assert report["provider"]["invocation"] == "NOT_PERFORMED"


def test_provider_inventory_requires_the_server_token(monkeypatch) -> None:
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "c" * 32)
    client = TestClient(app)
    assert client.get("/v1/providers").status_code == 401
    allowed = client.get("/v1/providers", headers={"Authorization": "Bearer " + ("c" * 32)})
    assert allowed.status_code == 200
    body = allowed.json()
    assert body["authority"] == "NONE"
    assert body["effect"] == "NONE"
    assert body["providers"][0]["self_permission"] == "FORBIDDEN"


def test_inferred_exposure_cannot_become_confirmed() -> None:
    assert evidence_class_for_claim("SUSPECTED_EXPOSURE", withheld=False) == "INFERRED"
    assert evidence_class_for_claim("CALCULATED_DISCREPANCY", withheld=False) == "CALCULATED"
    assert evidence_class_for_claim("CALCULATED_DISCREPANCY", withheld=True) == "WITHHELD"
    assert "CONFIRMED" not in {
        evidence_class_for_claim(claim, withheld=flag)
        for claim in ("SUSPECTED_EXPOSURE", "CALCULATED_DISCREPANCY", "UNVERIFIED_INTERPRETATION")
        for flag in (False, True)
    }
