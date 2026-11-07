"""Process health is not the same thing as a ready dependency.

The HTTP process can answer while SQLite is missing or the configured model
has never been reached. This module reports those states without calling a
model and without creating a database file.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Any
from urllib.parse import urlsplit

from aurex.database import DEFAULT_DB_PATH
from aurex.dispater_store import _is_ephemeral, db_path

MODEL_NAME = "qwen2.5-0.5b-instruct-q4_k_m"
PRIVATE_HOST = "qwen-private-staging.railway.internal"


def _store_state(path: str) -> str:
    parent = os.path.dirname(os.path.abspath(path)) or "."
    ephemeral = _is_ephemeral(parent)
    if os.path.exists(path):
        try:
            connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=1)
            try:
                connection.execute("select 1")
            finally:
                connection.close()
        except sqlite3.Error:
            return "DEPENDENCY_UNAVAILABLE"
        return "EPHEMERAL" if ephemeral else "DURABLE"
    if os.path.isdir(parent) and os.access(parent, os.W_OK):
        return "EPHEMERAL" if ephemeral else "DURABLE"
    return "DEPENDENCY_UNAVAILABLE"


def model_state() -> dict[str, Any]:
    """Describe the configured adapter. Do not open a socket to it."""
    enabled = os.environ.get("AUREX_XAELI_STAGING_ENABLED") == "1"
    approved = os.environ.get("AUREX_XAELI_OPERATOR_APPROVED") == "1"
    base_url = os.environ.get("AUREX_QWEN_BASE_URL", "")
    budget = os.environ.get("AUREX_BUDGET_USD", "0")
    paid = budget not in ("0", "0.0", "0.00", "")
    if not enabled or not approved or not base_url:
        availability = "NOT_CONFIGURED"
    else:
        host = urlsplit(base_url).hostname or ""
        on_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT_ID"))
        if host == PRIVATE_HOST and not on_railway:
            availability = "MODEL_UNAVAILABLE"
        else:
            availability = "CONFIGURED_UNVERIFIED"
    host_class = "unset"
    if base_url:
        host = urlsplit(base_url).hostname or ""
        if host in {"127.0.0.1", "::1", "localhost"}:
            host_class = "loopback"
        elif host == PRIVATE_HOST:
            host_class = "railway-private"
        else:
            host_class = "other"
    return {
        "provider": "llama.cpp",
        "model": MODEL_NAME,
        "availability": availability,
        "host_class": host_class,
        "invocation": "NOT_PERFORMED",
        "timeout_seconds": 90,
        "retries": 0,
        "paid_inference": "OFF" if not paid else "CONFIGURED",
        "cost_policy": "ZERO_UNLESS_AN_OPERATOR_SETS_A_BUDGET",
        "output_authority": "NONE",
        "self_permission": "FORBIDDEN",
    }


def readiness() -> dict[str, Any]:
    aurex_store = _store_state(DEFAULT_DB_PATH)
    dispater_store = _store_state(db_path())
    model = model_state()
    stores_down = "DEPENDENCY_UNAVAILABLE" in {aurex_store, dispater_store}
    ephemeral = "EPHEMERAL" in {aurex_store, dispater_store}
    model_gap = model["availability"] in {"MODEL_UNAVAILABLE", "CONFIGURED_UNVERIFIED"}
    if stores_down:
        state = "DEPENDENCY_UNAVAILABLE"
    elif ephemeral or model_gap:
        state = "DEGRADED"
    else:
        state = "READY"
    return {
        "process": "PROCESS_HEALTHY",
        "readiness": state,
        "stores": {"aurex": aurex_store, "dispater": dispater_store},
        "model": model["availability"],
        "provider": model,
    }
