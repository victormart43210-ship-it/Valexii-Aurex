"""Repeated labor roles on one date are not two proven shifts."""

from __future__ import annotations

import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_intelligence import RevenueLeakageEngine


def _dataset(records: list[dict[str, str]], *, invoiced: str | None) -> dict[str, object]:
    return {
        "tenant_id": "labor",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J", "customer_id": "C", "service_code": "LAB", "date": "2026-04-01"}],
        "rates": [
            {
                "rate_id": "R",
                "customer_id": "C",
                "service_code": "LAB",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "25.00",
                "unit": "HOUR",
            }
        ],
        "invoices": []
        if invoiced is None
        else [{"invoice_id": "I", "job_id": "J", "amount": invoiced, "status": "open"}],
        "payments": [],
        "labor": records,
    }


def _row(record_id: str, role: str, hours: str = "8.00") -> dict[str, str]:
    return {
        "record_id": record_id,
        "job_id": "J",
        "role": role,
        "service_date": "2026-04-01",
        "approved_hours": hours,
        "billed_hours": hours,
        "overtime_hours": "0.00",
    }


@pytest.mark.parametrize(
    ("records", "invoiced", "code", "identified"),
    [
        ([_row("L1", "operator"), _row("L2", "operator")], None, "DUPLICATE_LABOR_RECORD", "0.00"),
        ([_row("L2", "operator"), _row("L1", "operator")], "200.00", "DUPLICATE_LABOR_RECORD", "0.00"),
        ([_row("L1", "operator")], None, "UNBILLED_LABOR", "200.00"),
        ([_row("L1", "operator"), _row("L2", "driver")], None, "UNBILLED_LABOR", "400.00"),
    ],
)
def test_same_role_and_date_cannot_inflate_hours(
    records: list[dict[str, str]], invoiced: str | None, code: str, identified: str
) -> None:
    report = RevenueLeakageEngine("labor").reconcile_records(_dataset(records, invoiced=invoiced))
    summary = report["financial_summary"]
    assert summary["identified_exposure_usd"] == identified
    assert summary["confirmed_recovery_usd"] == "0.00"
    assert report["findings"][0]["code"] == code
    if code == "DUPLICATE_LABOR_RECORD":
        assert report["findings"][0]["qualification"] == "INSUFFICIENT_EVIDENCE"
        assert report["findings"][0]["exposure_usd"] == "0.00"


@pytest.fixture
def client(monkeypatch, tmp_path):
    token = "synthetic-cclxvi-labor-token-1234567890"
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", token)
    monkeypatch.setenv(
        "AUREX_DISPATER_TENANT_GRANTS",
        json.dumps({hashlib.sha256(token.encode()).hexdigest(): ["labor"]}),
    )
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "labor.sqlite"))
    return TestClient(app), {"Authorization": f"Bearer {token}"}


def test_duplicate_labor_stays_withheld_through_http(client) -> None:
    http, headers = client
    payload = _dataset([_row("L1", "operator"), _row("L2", "operator")], invoiced=None)
    response = http.post("/v1/dispater/reconciliation", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert body["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert body["findings"][0]["code"] == "DUPLICATE_LABOR_RECORD"
    stored = http.get(
        "/v1/dispater/runs/" + body["run_id"], params={"tenant_id": "labor"}, headers=headers
    )
    assert stored.status_code == 200
    assert stored.json()["receipt_sha256"] == body["receipt_sha256"]
    assert stored.json()["financial_summary"]["identified_exposure_usd"] == "0.00"
