import json
import secrets

import pytest


@pytest.fixture(autouse=True)
def _receipt_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Per-test random receipt key; no key material is ever committed."""
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", json.dumps({"test-k1": secrets.token_hex(32)}))
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_ACTIVE_KID", "test-k1")
