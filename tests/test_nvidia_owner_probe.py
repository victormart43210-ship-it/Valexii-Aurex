"""Zero-spend NVIDIA readiness route stays fail-closed and never calls out."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

PATH = (
    Path(__file__).resolve().parents[1]
    / "integrations/kusanagi-xvi/backend/nvidia_owner_probe.py"
)
SPEC = importlib.util.spec_from_file_location("nvidia_owner_probe", PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

TOKEN = "t" * 40
app = FastAPI()
app.include_router(module.router)
client = TestClient(app)


def test_unconfigured_service_denies(monkeypatch) -> None:
    monkeypatch.delenv("AUREX_SERVICE_TOKEN", raising=False)
    assert client.post("/v1/owner/nvidia/probe").status_code == 503


def test_wrong_and_non_ascii_credentials_get_401(monkeypatch) -> None:
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    assert client.post("/v1/owner/nvidia/probe", headers={"Authorization": "Bearer x"}).status_code == 401
    raw = {"Authorization": "Bearer é".encode("latin-1")}
    assert client.post("/v1/owner/nvidia/probe", headers=raw).status_code == 401


def test_disabled_by_default_and_enabled_reports_no_connection(monkeypatch) -> None:
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    headers = {"Authorization": f"Bearer {TOKEN}"}
    monkeypatch.delenv("AUREX_NVIDIA_STAGING_ENABLED", raising=False)
    assert client.post("/v1/owner/nvidia/probe", headers=headers).status_code == 503
    monkeypatch.setenv("AUREX_NVIDIA_STAGING_ENABLED", "true")
    body = client.post("/v1/owner/nvidia/probe", headers=headers).json()
    assert body["connected"] is False and body["probeExecuted"] is False
    assert body["spendingUsd"] == 0 and body["authority"] == "NONE" and body["release"] == "HOLD"
