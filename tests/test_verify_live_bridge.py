from fastapi.testclient import TestClient

from aurex.api import app
from scripts.verify_live_bridge import run_bridge_verification, verify_live_endpoint

client = TestClient(app)
VALID_TOKEN = "a" * 32


def test_verify_live_endpoint_rejects_disallowed_host() -> None:
    res = verify_live_endpoint("https://malicious-external-host.com", "/health")
    assert res["status"] == "REJECTED"
    assert "not in allowlist" in res["reason"]


def test_verify_live_endpoint_allowlisted_host_format() -> None:
    res = verify_live_endpoint("http://127.0.0.1:8000", "/health", timeout=0.1)
    assert res["path"] == "/health"
    assert "status" in res


def test_local_fastapi_schema_compatibility(monkeypatch, tmp_path) -> None:
    db_file = str(tmp_path / "test_bridge.db")
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", VALID_TOKEN)
    monkeypatch.setenv("AUREX_DB_PATH", db_file)
    import aurex.api
    aurex.api.DEFAULT_DB_PATH = db_file

    h_res = client.get("/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "ok"

    c_res = client.get("/v1/capabilities", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert c_res.status_code == 200
    caps = [item["id"] for item in c_res.json()["capabilities"]]
    assert "regression_scan" in caps
    assert "regression-scan" in caps


def test_run_bridge_verification_structure() -> None:
    report = run_bridge_verification("http://127.0.0.1:8000", token="a" * 32)
    assert "report_sha256" in report
    assert "endpoint_results" in report
    assert report["base_url"] == "http://127.0.0.1:8000"
