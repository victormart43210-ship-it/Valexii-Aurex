"""An observation can be recorded. It cannot gain an effect."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from aurex.api import app


@pytest.fixture
def client(monkeypatch, tmp_path):
    token = "synthetic-cclxix-observation-token-123456"
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", token)
    monkeypatch.setenv(
        "AUREX_DISPATER_TENANT_GRANTS",
        json.dumps({hashlib.sha256(token.encode()).hexdigest(): ["obs"]}),
    )
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "obs.sqlite"))
    return TestClient(app), {"Authorization": f"Bearer {token}"}


def _body(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "tenant_id": "obs",
        "source_sha256": "ab" * 32,
        "observed_at": datetime.now(UTC).isoformat(),
        "hypothesis": "The stored receipt matches the synthetic report.",
        "counterevidence": ["The same session produced both readings."],
        "effect": "NONE",
    }
    payload.update(overrides)
    return payload


def test_a_contested_observation_stays_advisory(client) -> None:
    http, headers = client
    response = http.post("/v1/dispater/observations", json=_body(), headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["decision"] == "RECORDED"
    assert body["effect"] == "NONE"
    assert body["authority"] == "NONE"
    assert body["financial_authority"] == "NONE"
    assert body["launch"] == "NOT_STARTED"
    assert body["production"] == "HOLD"


def test_a_requested_effect_is_refused(client) -> None:
    http, headers = client
    response = http.post("/v1/dispater/observations", json=_body(effect="DEPLOY"), headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["decision"] == "REFUSED"
    assert body["effect"] == "NONE"
    assert "EFFECT_REFUSED" in body["problems"]


def test_missing_counterevidence_abstains_and_other_tenants_are_denied(client) -> None:
    http, headers = client
    abstain = http.post("/v1/dispater/observations", json=_body(counterevidence=[]), headers=headers)
    assert abstain.status_code == 200, abstain.text
    assert abstain.json()["decision"] == "ABSTAIN"
    stale = http.post(
        "/v1/dispater/observations",
        json=_body(observed_at=(datetime.now(UTC) - timedelta(days=3)).isoformat()),
        headers=headers,
    )
    assert stale.json()["decision"] == "REFUSED"
    assert "STALE_EVIDENCE" in stale.json()["problems"]
    denied = http.post("/v1/dispater/observations", json=_body(tenant_id="other"), headers=headers)
    assert denied.status_code == 403
