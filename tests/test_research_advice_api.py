"""Adversarial HTTP boundary tests for experimental AUREX analysis.

The route is opt-in, authenticated and never an authorization or executor.
"""

from fastapi.testclient import TestClient

from aurex.api import app

TOKEN = "research-advice-ci-token-that-is-long-enough-0123456789"
PATH = "/v1/research/advice"


def headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOKEN}"}


def body() -> dict[str, object]:
    return {
        "problem_code": "TEST_FAILURE",
        "description": "mypy type mismatch in regression suite",
        "fixes": [
            {
                "key": "type_patch",
                "problem_code": "TEST_FAILURE",
                "lineage_group": "source-1",
                "fix": ["Prepare smallest isolated patch"],
                "verify": ["Run exact SHA CI and independent reviewer"],
                "rollback": ["Revert candidate branch"],
                "minutes": 5,
                "risk": 1,
                "cost_usd": "0",
                "impact": 10,
            }
        ],
    }


def test_route_refuses_absent_bearer(monkeypatch: object) -> None:
    # Used via monkeypatch in this suite; no actual bearer is stored or logged.
    from pytest import MonkeyPatch

    assert isinstance(monkeypatch, MonkeyPatch)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.setenv("AUREX_ENABLE_RESEARCH_ADVICE", "1")
    client = TestClient(app)
    assert client.post(PATH, json=body()).status_code == 401
    assert client.post(
        PATH, json=body(), headers={"Authorization": "Bearer wrong"}
    ).status_code == 401


def test_route_disabled_by_default(monkeypatch: object) -> None:
    from pytest import MonkeyPatch

    assert isinstance(monkeypatch, MonkeyPatch)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ENABLE_RESEARCH_ADVICE", raising=False)
    r = TestClient(app).post(PATH, json=body(), headers=headers())
    assert r.status_code == 503
    assert "disabled" in r.json()["detail"]


def test_valid_research_response_only_proposes_read_only_advice(monkeypatch: object) -> None:
    from pytest import MonkeyPatch

    assert isinstance(monkeypatch, MonkeyPatch)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.setenv("AUREX_ENABLE_RESEARCH_ADVICE", "1")
    r = TestClient(app).post(PATH, json=body(), headers=headers())
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "REVIEW_REQUIRED"
    assert data["authority"] == "NONE"
    assert data["independent_verification"] == "NOT VERIFIED"
    assert data["output"]["authority"] == "ADVISORY_ONLY_NO_EXECUTION"
    assert data["output"]["remediation"]["proposed"]["steps"][0]["key"] == "type_patch"
    assert data["output"]["remediation"]["proposed"]["steps"][0]["rollback"]
    assert TOKEN not in r.text


def test_paid_and_unverified_candidates_fail_closed(monkeypatch: object) -> None:
    from pytest import MonkeyPatch

    assert isinstance(monkeypatch, MonkeyPatch)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.setenv("AUREX_ENABLE_RESEARCH_ADVICE", "1")
    data = body()
    assert isinstance(data["fixes"], list)
    data["fixes"][0]["cost_usd"] = "0.01"
    data["probes"] = [
        {
            "probe_id": "probe-1",
            "sensitivity": 0.9,
            "specificity": 0.9,
            "risk": 1,
            "duration_seconds": 2,
            "cost_usd": "0",
        }
    ]
    data["prior"] = 0.5
    r = TestClient(app).post(PATH, json=data, headers=headers())
    assert r.status_code == 200
    assert r.json()["status"] == "HOLD"
    assert r.json()["output"]["test_next"] == []  # No signed calibration interface.


def test_callers_cannot_self_certify_calibration(monkeypatch: object) -> None:
    from pytest import MonkeyPatch

    assert isinstance(monkeypatch, MonkeyPatch)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.setenv("AUREX_ENABLE_RESEARCH_ADVICE", "1")
    data = body()
    data["probes"] = [
        {
            "probe_id": "probe",
            "sensitivity": 0.9,
            "specificity": 0.9,
            "duration_seconds": 2,
            "risk": 1,
            "cost_usd": "0",
            "calibration_reviewed": True,
        }
    ]
    assert TestClient(app).post(PATH, json=data, headers=headers()).status_code == 422


def test_unknown_failure_and_empty_options_hold(monkeypatch: object) -> None:
    from pytest import MonkeyPatch

    assert isinstance(monkeypatch, MonkeyPatch)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.setenv("AUREX_ENABLE_RESEARCH_ADVICE", "1")
    data = {"problem_code": "UNKNOWN", "description": "not recognized"}
    r = TestClient(app).post(PATH, json=data, headers=headers())
    assert r.status_code == 200
    assert r.json()["status"] == "HOLD"
    assert r.json()["output"]["remediation"]["proposed"] is None


def test_oversized_or_unbounded_requests_are_rejected(monkeypatch: object) -> None:
    from pytest import MonkeyPatch

    assert isinstance(monkeypatch, MonkeyPatch)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.setenv("AUREX_ENABLE_RESEARCH_ADVICE", "1")
    data = body()
    data["description"] = "X" * 513
    assert TestClient(app).post(PATH, json=data, headers=headers()).status_code == 422
    data = body()
    data["fixes"] = [data["fixes"][0]] * 13
    assert TestClient(app).post(PATH, json=data, headers=headers()).status_code == 422
    data = body()
    data["fixes"][0]["cost_usd"] = -1
    assert TestClient(app).post(PATH, json=data, headers=headers()).status_code == 422
