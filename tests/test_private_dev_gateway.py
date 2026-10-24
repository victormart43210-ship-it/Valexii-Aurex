"""Synthetic, zero-network security and read-only probe regression tests."""
import base64
import json
import time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from fastapi.testclient import TestClient

from tools import private_dev_gateway as gateway


def _auth() -> dict[str, str]:
    return {"Authorization": "Basic " + base64.b64encode(b"aurex:" + b"X" * 42).decode()}


def test_default_without_config_fails_closed(monkeypatch):
    monkeypatch.delenv("AUREX_PREVIEW_PASSWORD", raising=False)
    assert TestClient(gateway.app).get("/").status_code == 503


def test_local_requires_basic_and_only_gets(monkeypatch):
    monkeypatch.setenv("AUREX_PREVIEW_PASSWORD", "X" * 42)
    monkeypatch.setenv("AUREX_PREVIEW_MODE", "local")
    client = TestClient(gateway.app)
    assert client.get("/").status_code == 401
    assert client.get("/", headers=_auth()).status_code == 200
    assert client.post("/api/status", headers=_auth()).status_code == 405
    assert client.get("/dashboard.js", headers=_auth()).status_code == 200
    assert "no-store" in client.get("/", headers=_auth()).headers["cache-control"]


def test_remote_fails_without_verified_access_jwt(monkeypatch):
    monkeypatch.setenv("AUREX_PREVIEW_PASSWORD", "X" * 42)
    monkeypatch.setenv("AUREX_PREVIEW_MODE", "access")
    assert TestClient(gateway.app).get("/", headers=_auth()).status_code == 403
    assert TestClient(gateway.app).get("/", headers={**_auth(), "Cf-Access-Jwt-Assertion": "forged"}).status_code == 403


def test_valid_access_jwt_and_rejections(monkeypatch):
    monkeypatch.setenv("CF_ACCESS_TEAM_DOMAIN", "example.cloudflareaccess.com")
    monkeypatch.setenv("CF_ACCESS_AUD", "dev-app-audience")
    monkeypatch.setenv("CF_ACCESS_OWNER_EMAIL", "owner@example.org")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    numbers = key.public_key().public_numbers()

    def b64(data):
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    def asint(num):
        return b64(num.to_bytes((num.bit_length() + 7) // 8, "big"))

    monkeypatch.setattr(
        gateway, "_certs_cached",
        lambda *_: {"keys": [{"kid": "test", "kty": "RSA", "n": asint(numbers.n), "e": asint(numbers.e)}]},
    )

    def mint(**overrides):
        claims = {
            "iss": "https://example.cloudflareaccess.com",
            "aud": ["dev-app-audience"],
            "email": "owner@example.org",
            "exp": int(time.time()) + 120,
            "nbf": int(time.time()) - 1,
        }
        claims.update(overrides)
        head = b64(json.dumps({"alg": "RS256", "kid": "test"}).encode())
        body = b64(json.dumps(claims).encode())
        sig = key.sign((head + "." + body).encode(), padding.PKCS1v15(), hashes.SHA256())
        return head + "." + body + "." + b64(sig)

    assert gateway._verify_access_jwt(mint()) is True
    assert gateway._verify_access_jwt(mint(aud=["other"])) is False
    assert gateway._verify_access_jwt(mint(email="attacker@example.org")) is False
    assert gateway._verify_access_jwt(mint(exp=int(time.time()) - 1)) is False
    assert gateway._verify_access_jwt(mint(iss="https://attacker.com")) is False


def test_status_is_sanitized_and_no_service_token_escapes(monkeypatch):
    monkeypatch.setenv("AUREX_PREVIEW_PASSWORD", "X" * 42)
    monkeypatch.setenv("AUREX_PREVIEW_MODE", "local")
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "S" * 42)
    payloads = {
        "health": {"status": "ok", "version": "v-local", "time": "now"},
        "capabilities": {"capabilities": [{"id": "test"}]},
        "evidence": {"evidence": [{"summary": "private evidence"}]},
        "budgets": {"limitUsd": 0, "reservedUsd": 0, "spentUsd": 0},
        "jobs": {"jobs": [{"id": "private job"}]},
    }
    monkeypatch.setattr(gateway, "_limited_get", lambda url, **kw: json.dumps(payloads[url.rsplit("/", 1)[-1]]).encode())
    r = TestClient(gateway.app).get("/api/status", headers=_auth())
    assert r.status_code == 200 and r.json()["overall"] == "PASS"
    assert "private evidence" not in r.text and "private job" not in r.text and "S" * 42 not in r.text
    assert r.json()["checks"][3]["zeroDollarBudget"] is True
    monkeypatch.setattr(gateway, "_limited_get", lambda url, **kw: b"invalid")
    assert TestClient(gateway.app).get("/api/status", headers=_auth()).json()["overall"] == "HOLD"


def test_readonly_budget_reports_nonzero_without_claiming_zero_budget(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "S" * 42)
    monkeypatch.setattr(gateway, "_limited_get", lambda url, **kw: json.dumps({"limitUsd": 50, "reservedUsd": 0, "spentUsd": 0}).encode())
    assert gateway._fetch_readonly("budgets") == {"endpoint": "budgets", "status": "PASS", "zeroDollarBudget": False}


def test_no_backend_token_fails_closed(monkeypatch):
    monkeypatch.delenv("AUREX_SERVICE_TOKEN", raising=False)
    assert gateway._fetch_readonly("health")["status"] == "HOLD"


def test_invalid_access_team_domain_does_not_leave_network(monkeypatch):
    monkeypatch.setenv("CF_ACCESS_TEAM_DOMAIN", "evil.example.com")
    monkeypatch.setenv("CF_ACCESS_AUD", "expected")
    monkeypatch.setenv("CF_ACCESS_OWNER_EMAIL", "owner@example.org")
    assert gateway._verify_access_jwt("bad.bad.bad") is False


def test_readonly_probe_rejects_redirect_and_oversized_payload(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "S" * 42)
    monkeypatch.setattr(gateway, "_limited_get", lambda url, **kw: (_ for _ in ()).throw(ValueError("response too large")))
    assert gateway._fetch_readonly("evidence")["status"] == "HOLD"
