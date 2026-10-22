"""CXXV Python-side schema inventory, no network or database side effects.

Source level checks are NOT independent runtime efficacy or production authority.
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from aurex.api import (
    CapabilityItem,
    EvidenceItem,
    JobCreateRequest,
    app,
    authenticate,
    get_token,
)


def test_candidate_http_paths_exist_but_not_inference() -> None:
    methods = {(method, route.path) for route in app.routes for method in (route.methods or [])}
    for path in ("/v1/health", "/v1/capabilities", "/v1/evidence", "/v1/budgets", "/v1/jobs"):
        assert ("GET", path) in methods
    # NVIDIA document routes are NOT on canonical main; Jules owns their integration.
    # Their absence means source integration remains pending, not "verified".
    assert ("POST", "/v1/documents/analyze") not in methods


def test_python_capability_shape_agrees_with_cxxv_wire() -> None:
    item = CapabilityItem(id="regression_scan", available=False, evidenceId=None, verifiedAt=None)
    assert item.model_dump() == {
        "id": "regression_scan", "available": False,
        "evidenceId": None, "verifiedAt": None,
    }
    evidence = EvidenceItem(
        id="ev-example", capabilityId="regression_scan", kind="offline_probe",
        collectedAt="2026-10-22T12:00:00+00:00", sha256="a" * 64,
        summary="Local candidate observation; NOT VERIFIED",
    )
    assert evidence.model_dump()["kind"] == "offline_probe"


def test_job_create_kind_is_bounded_and_zero_price_is_accepted_as_input() -> None:
    valid = JobCreateRequest(
        kind="regression_scan", params={"probe": "sqlite_roundtrip_v1"}, maxCostUsd=0
    )
    assert valid.kind == "regression_scan"
    assert valid.maxCostUsd == 0
    for kind in ("nvidia_document", "autonomous_payment", "financial_fraud_block"):
        with pytest.raises(ValidationError):
            JobCreateRequest(kind=kind, params={}, maxCostUsd=0)


def test_service_auth_no_secret_no_access() -> None:
    with patch.dict(os.environ, {"AUREX_SERVICE_TOKEN": ""}, clear=True):
        with pytest.raises(Exception):
            get_token()
    with patch.dict(os.environ, {
        "AUREX_SERVICE_TOKEN": "A" * 40,
        "AUREX_ADMIN_TOKEN": "A" * 40,
    }, clear=True):
        assert authenticate("Bearer " + "A" * 40) == "authenticated"
        for value in (None, "", "Bearer bad", "Basic " + "A" * 40):
            with pytest.raises(Exception):
                authenticate(value)
