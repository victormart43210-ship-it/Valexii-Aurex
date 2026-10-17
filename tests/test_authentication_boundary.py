"""Adversarial boundary checks: malformed Bearer values always fail closed.

This suite does not access any network, token vault, external authentication
system, paid worker, or Railway service.
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from aurex.api import app, authenticate, get_token

TOKEN = "AUREX_local_testing_ascii_token_0123456789abcdef"


@pytest.fixture(autouse=True)
def configured_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)


def test_known_ascii_token_remains_accepted() -> None:
    assert get_token() == TOKEN
    assert authenticate("Bearer " + TOKEN) == "authenticated"
    response = TestClient(app).get(
        "/v1/capabilities", headers={"Authorization": "Bearer " + TOKEN}
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    "header",
    [
        None,
        "",
        "Bearer",
        "Basic " + TOKEN,
        "Bearer wrong",
        "Bearer " + ("x" * 513),
        "Bearer café",
        "Bearer snowman☃",
        "Bearer " + TOKEN + " ",
        "Bearer " + TOKEN + "\n",
    ],
)
def test_malformed_headers_always_deny_without_type_error(header: str | None) -> None:
    with pytest.raises(HTTPException) as error:
        authenticate(header)
    assert error.value.status_code == 401
    assert TOKEN not in str(error.value.detail)


@pytest.mark.parametrize(
    "server_token",
    [
        "",
        "short",
        "à" * 32,
        "b" * 513,
        " " + TOKEN,
        TOKEN + " ",
    ],
)
def test_malformed_server_secrets_fail_closed(
    server_token: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", server_token)
    with pytest.raises(HTTPException) as error:
        authenticate("Bearer " + TOKEN)
    assert error.value.status_code == 500
    assert TOKEN not in str(error.value.detail)


def test_conflicting_configured_tokens_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUREX_ADMIN_TOKEN", TOKEN + "different")
    with pytest.raises(HTTPException) as error:
        authenticate("Bearer " + TOKEN)
    assert error.value.status_code == 500
