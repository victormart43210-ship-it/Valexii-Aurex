"""The HTTP boundary must carry the same hour evidence as the canonical engine."""

from __future__ import annotations

import base64
import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_intelligence import digest


@pytest.fixture
def client(monkeypatch, tmp_path):
    token = "synthetic-cclvii-hour-token-1234567890"
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", token)
    monkeypatch.setenv(
        "AUREX_DISPATER_TENANT_GRANTS",
        json.dumps({hashlib.sha256(token.encode()).hexdigest(): ["hours"]}),
    )
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "hours.sqlite"))
    return TestClient(app), {"Authorization": f"Bearer {token}"}


def hourly(kind):
    data = {
        "tenant_id": "hours",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J", "customer_id": "C", "service_code": "TOW", "date": "2026-01-01"}],
        "rates": [
            {
                "rate_id": "R",
                "customer_id": "C",
                "service_code": "TOW",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "25.00",
                "unit": "HOUR",
            }
        ],
        "invoices": [],
        "payments": [],
    }
    if kind == "equipment":
        data[kind] = [
            {
                "ticket_id": "T",
                "job_id": "J",
                "equipment_id": "TRUCK",
                "service_date": "2026-01-01",
                "billable_hours": "8.00",
                "standby_hours": "0.00",
                "invoiced_hours": "8.00",
            }
        ]
    else:
        data[kind] = [
            {
                "record_id": "L",
                "job_id": "J",
                "role": "operator",
                "service_date": "2026-01-01",
                "approved_hours": "8.00",
                "billed_hours": "8.00",
                "overtime_hours": "0.00",
            }
        ]
    return data


@pytest.mark.parametrize("kind", ["equipment", "labor"])
def test_hours_are_priced_identically_through_both_api_paths(client, kind):
    http, headers = client
    data = hourly(kind)
    direct = http.post("/v1/dispater/reconciliation", json=data, headers=headers)
    assert direct.status_code == 200, direct.text
    assert direct.json()["financial_summary"]["identified_exposure_usd"] == "200.00"
    uploaded = http.post(
        "/v1/dispater/documents",
        json={
            "tenant_id": "hours",
            "filename": "hours.json",
            "kind": "json",
            "content_base64": base64.b64encode(json.dumps(data).encode()).decode(),
        },
        headers=headers,
    )
    assert uploaded.status_code == 200, uploaded.text
    report = uploaded.json()["report"]
    assert report["financial_summary"]["identified_exposure_usd"] == "200.00"
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert (
        uploaded.json()["ingestion"]["source_sha256"]
        == hashlib.sha256(json.dumps(data).encode()).hexdigest()
    )
    run = http.get(
        "/v1/dispater/runs/" + report["run_id"], params={"tenant_id": "hours"}, headers=headers
    )
    assert run.status_code == 200
    assert run.json()["receipt_sha256"] == report["receipt_sha256"]
    assert (
        http.get(
            "/v1/dispater/dashboard", params={"tenant_id": "other"}, headers=headers
        ).status_code
        == 403
    )
    dashboard = http.get(
        "/v1/dispater/dashboard", params={"tenant_id": "hours"}, headers=headers
    ).json()
    assert dashboard["identified_exposure_usd"] == "200.00"
    assert dashboard["confirmed_recovery_usd"] == "0.00"


def test_legacy_request_digest_and_replay_stay_compatible(client):
    http, headers = client
    data = hourly("equipment")
    del data["equipment"]
    first = http.post("/v1/dispater/reconciliation", json=data, headers=headers).json()
    assert first["dataset_sha256"] == digest(data)
    assert (
        http.post("/v1/dispater/reconciliation", json=data, headers=headers).json()["run_id"]
        == first["run_id"]
    )


def test_hour_collection_is_bounded_at_http_boundary(client):
    http, headers = client
    data = hourly("equipment")
    data["equipment"] *= 2001
    assert http.post("/v1/dispater/reconciliation", json=data, headers=headers).status_code == 422
