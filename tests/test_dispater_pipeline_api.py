"""
Tests for CCXXXII DISPATER Industrial Pipeline API Endpoints.
"""

import base64
import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aurex.api import app


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    token = "12345678901234567890123456789012"
    grants = {hashlib.sha256(token.encode()).hexdigest(): ["TENANT-PIPE-01"]}
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", token)
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps(grants))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "dispater_pipe.db"))
    return TestClient(app)


def test_pipeline_api_audit_and_ingest(auth_client: TestClient) -> None:
    token = "12345678901234567890123456789012"
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Pipeline Ingest
    payload = {"test": "data", "invoice_id": "INV-P-1"}
    b64_payload = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    ingest_res = auth_client.post(
        "/v1/dispater/pipeline/ingest?tenant_id=TENANT-PIPE-01",
        headers=headers,
        json={
            "source_id": "accounting-erp",
            "source_record_id": "INV-P-1",
            "document_category": "INVOICE",
            "media_type": "application/json",
            "payload_base64": b64_payload,
        },
    )
    assert ingest_res.status_code == 200
    data = ingest_res.json()
    assert data["status"] == "ADMITTED"
    assert data["source_record_id"] == "INV-P-1"
    assert len(data["content_sha256"]) == 64

    # 2. Pipeline Audit Run
    snapshot = {
        "dataset_type": "SYNTHETIC_ONLY",
        "tenant_id": "TENANT-PIPE-01",
        "jobs": [
            {
                "job_id": "JOB-1",
                "customer_id": "CUST-1",
                "service_code": "PP",
                "date": "2026-01-01",
            }
        ],
        "rates": [
            {
                "rate_id": "RATE-1",
                "customer_id": "CUST-1",
                "service_code": "PP",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            }
        ],
        "invoices": [
            {
                "invoice_id": "INV-1",
                "job_id": "JOB-1",
                "amount": "150.00",
                "status": "open",
            }
        ],
        "payments": [],
    }
    audit_res = auth_client.post(
        "/v1/dispater/pipeline/audit",
        headers=headers,
        json=snapshot,
    )
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert audit_data["tenant_id"] == "TENANT-PIPE-01"
    assert audit_data["authority"] == "HUMAN_REVIEW_REQUIRED"
    assert len(audit_data["receipt_sha256"]) == 64
