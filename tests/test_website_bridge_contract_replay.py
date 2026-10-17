"""Cross-implementation, synthetic-only contract replay for the 5 AUREX v1 GETs.

This checks the deployed read-only *source* and canonical *source* in isolated
TestClient processes. It does not send requests to production, establish
website-origin identity, create jobs or authorize a release.
"""

from __future__ import annotations

import importlib.util
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "a" * 32
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
PATHS = (
    "/v1/health",
    "/v1/capabilities",
    "/v1/evidence",
    "/v1/budgets",
    "/v1/jobs",
)
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
CAP_ID = re.compile(r"^[a-z_-]{1,64}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^[A-Za-z0-9._-]{1,32}$")


def iso(value: Any) -> bool:
    if not isinstance(value, str) or len(value) > 48:
        return False
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return stamp.tzinfo is not None and stamp.utcoffset() is not None
    except ValueError:
        return False


def money(value: Any) -> bool:
    return type(value) in (float, int) and math.isfinite(value) and 0 <= value <= 10_000


def exact(value: Any, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def valid_json_contract(path: str, value: Any) -> bool:
    """Subset mirrored against website Zod contract: mandatory fields, types, bounds."""
    if path == "/v1/health":
        return (
            exact(value, {"status", "version", "time"})
            and value["status"] == "ok"
            and isinstance(value["version"], str)
            and bool(VERSION.fullmatch(value["version"]))
            and iso(value["time"])
        )
    if path == "/v1/capabilities":
        return (
            exact(value, {"capabilities"})
            and isinstance(value["capabilities"], list)
            and len(value["capabilities"]) <= 100
            and all(
                exact(c, {"id", "available", "evidenceId", "verifiedAt"})
                and isinstance(c["id"], str)
                and bool(CAP_ID.fullmatch(c["id"]))
                and type(c["available"]) is bool
                and (
                    c["evidenceId"] is None
                    or isinstance(c["evidenceId"], str) and bool(ID.fullmatch(c["evidenceId"]))
                )
                and (c["verifiedAt"] is None or iso(c["verifiedAt"]))
                for c in value["capabilities"]
            )
        )
    if path == "/v1/evidence":
        return (
            exact(value, {"evidence"})
            and isinstance(value["evidence"], list)
            and len(value["evidence"]) <= 200
            and all(
                exact(e, {"id", "capabilityId", "kind", "collectedAt", "sha256", "summary"})
                and isinstance(e["id"], str) and bool(ID.fullmatch(e["id"]))
                and isinstance(e["capabilityId"], str) and bool(CAP_ID.fullmatch(e["capabilityId"]))
                and isinstance(e["kind"], str)
                and e["kind"] in {"test_run", "health_probe", "benchmark_record", "offline_probe"}
                and iso(e["collectedAt"])
                and isinstance(e["sha256"], str) and bool(SHA256.fullmatch(e["sha256"]))
                and isinstance(e["summary"], str) and len(e["summary"]) <= 500
                for e in value["evidence"]
            )
        )
    if path == "/v1/budgets":
        return (
            exact(value, {"limitUsd", "reservedUsd", "spentUsd", "period"})
            and all(money(value[k]) for k in ("limitUsd", "reservedUsd", "spentUsd"))
            and isinstance(value["period"], str)
            and value["period"] in {"day", "month"}
        )
    if path == "/v1/jobs":
        return (
            exact(value, {"jobs", "nextCursor"})
            and isinstance(value["jobs"], list)
            and len(value["jobs"]) <= 200
            and (
                value["nextCursor"] is None
                or isinstance(value["nextCursor"], str) and len(value["nextCursor"]) <= 128
            )
            and all(
                exact(j, {"id", "kind", "state", "createdAt", "updatedAt", "reservationUsd"})
                and isinstance(j["id"], str) and bool(ID.fullmatch(j["id"]))
                and isinstance(j["kind"], str)
                and j["kind"] in {"regression_scan", "benchmark", "hypothesis_test"}
                and isinstance(j["state"], str)
                and j["state"] in {"queued", "running", "succeeded", "failed", "cancelled"}
                and iso(j["createdAt"]) and iso(j["updatedAt"])
                and money(j["reservationUsd"])
                for j in value["jobs"]
            )
        )
    return False


@pytest.fixture(params=["read_only_bridge", "canonical_main"])
def client(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "0")
    monkeypatch.setenv("AUREX_DB_PATH", str(tmp_path / "jobs.sqlite3"))
    if request.param == "read_only_bridge":
        from importlib.machinery import SourceFileLoader

        path = ROOT / "integrations/kusanagi-xvi/backend/app.py"
        spec = importlib.util.spec_from_loader("aurex_ro_contract", SourceFileLoader("aurex_ro_contract", str(path)))
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        target = module.app
    else:
        import aurex.api

        monkeypatch.setattr(aurex.api, "DEFAULT_DB_PATH", str(tmp_path / "jobs.sqlite3"))
        target = aurex.api.app
    with TestClient(target) as instance:
        yield request.param, instance


@pytest.mark.parametrize("path", PATHS)
def test_five_endpoint_shapes(client: tuple[str, TestClient], path: str) -> None:
    _, http = client
    response = http.get(path, headers=HEADERS)
    assert response.status_code == 200
    assert len(response.content) <= 256 * 1024
    assert valid_json_contract(path, response.json()), f"SCHEMA INVALID: {path}"


@pytest.mark.parametrize("path", PATHS)
def test_private_gets_reject_missing_and_wrong_bearer(
    client: tuple[str, TestClient], path: str
) -> None:
    _, http = client
    assert http.get(path).status_code in {401, 403}
    assert http.get(path, headers={"Authorization": "Bearer " + "b" * 32}).status_code in {401, 403}


def test_readonly_legacy_does_not_support_job_submission(
    client: tuple[str, TestClient],
) -> None:
    name, http = client
    if name == "read_only_bridge":
        assert http.post("/v1/jobs", headers=HEADERS, json={}).status_code == 405
    else:
        response = http.post(
            "/v1/jobs",
            headers=HEADERS,
            json={
                "kind": "regression_scan",
                "params": {"probe": "sqlite_roundtrip_v1"},
                "maxCostUsd": 0,
            },
        )
        assert response.status_code == 503


@pytest.mark.parametrize("path", PATHS)
def test_empty_object_does_not_satisfy_any_contract(path: str) -> None:
    assert valid_json_contract(path, {}) is False


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/v1/health", {"status": "ok", "version": "1.0"}),
        ("/v1/health", {"status": "ok", "version": "1.0", "time": "not-iso"}),
        ("/v1/capabilities", {"capabilities": [{"id": "regression_scan", "available": True}]}),
        ("/v1/capabilities", {"capabilities": [{"id": "regression_scan", "available": "true", "evidenceId": None, "verifiedAt": None}]}),
        ("/v1/evidence", {"evidence": [{"kind": "offline_probe"}]}),
        ("/v1/budgets", {"limitUsd": True, "reservedUsd": 0, "spentUsd": 0, "period": "month"}),
        ("/v1/budgets", {"limitUsd": float("nan"), "reservedUsd": 0, "spentUsd": 0, "period": "month"}),
        ("/v1/jobs", {"jobs": [{"state": "succeeded"}], "nextCursor": None}),
        ("/v1/jobs", {"jobs": [], "nextCursor": "a" * 129}),
        ("/v1/budgets", {"limitUsd": 0, "reservedUsd": 0, "spentUsd": 0, "period": []}),
        ("/v1/evidence", {"evidence": [{"id": "ev-a", "capabilityId": "regression_scan", "kind": [], "collectedAt": "2026-10-17T12:00:00Z", "sha256": "a" * 64, "summary": "unverified"}]}),
    ],
)
def test_invalid_payloads_fail_closed(path: str, payload: Any) -> None:
    assert not valid_json_contract(path, payload)


def test_offline_probe_is_an_admissible_record_type_not_proof() -> None:
    payload = {"evidence": [
        {"id": "ev-test", "capabilityId": "regression_scan",
         "kind": "offline_probe", "collectedAt": "2026-10-17T12:00:00Z",
         "sha256": "a" * 64, "summary": "Unverified synthetic observation"}
    ]}
    assert valid_json_contract("/v1/evidence", payload)
    assert payload["evidence"][0]["summary"].startswith("Unverified")


def test_checked_in_openapi_uses_real_offline_probe_and_capability_id_pattern() -> None:
    """The website's code may still be ahead; this checks documentation drift."""
    spec = (ROOT / "website/docs/aurex-api/openapi.yaml").read_text(encoding="utf-8")
    assert "offline_probe" in spec
    assert '^[a-z_-]{1,64}$' in spec
    assert "No server is deployed" not in spec
