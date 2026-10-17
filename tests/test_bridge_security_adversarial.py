from scripts.verify_live_bridge import (
    validate_endpoint_schema,
    verify_live_endpoint,
)


def test_schema_validation_rejects_empty_object() -> None:
    assert validate_endpoint_schema("/v1/health", {}) is False
    assert validate_endpoint_schema("/v1/capabilities", {}) is False
    assert validate_endpoint_schema("/v1/evidence", {}) is False
    assert validate_endpoint_schema("/v1/budgets", {}) is False
    assert validate_endpoint_schema("/v1/jobs", {}) is False


def test_schema_validation_accepts_valid_health() -> None:
    valid_health = {"status": "ok", "version": "0.1.0a1", "time": "2026-10-15T00:00:00Z"}
    assert validate_endpoint_schema("/v1/health", valid_health) is True


def test_production_endpoint_rejects_insecure_http() -> None:
    res = verify_live_endpoint("http://aurex-api-production-c535.up.railway.app", "/v1/health")
    assert res["status"] == "REJECTED"
    assert "requires HTTPS" in res["reason"]


def test_host_allowlist_rejects_unapproved_host() -> None:
    res = verify_live_endpoint("https://attacker-controlled-domain.org", "/v1/health")
    assert res["status"] == "REJECTED"
    assert "not in allowlist" in res["reason"]


def test_schema_validation_rejects_malformed_types() -> None:
    invalid_caps = {"capabilities": "not-a-list"}
    assert validate_endpoint_schema("/v1/capabilities", invalid_caps) is False
