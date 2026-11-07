"""Contract checks for two-way AUREX/OX company-record classification."""
from __future__ import annotations

import pytest

from aurex.company_evidence_taxonomy import EvidenceIntake, ROUTES, propose_route


def record(kind: str = "unknown", **updates: object) -> EvidenceIntake:
    fields: dict[str, object] = {
        "tenant_id": "sample-tenant",
        "source_id": "DOC-001",
        "source_sha256": "a" * 64,
        "declared_kind": kind,
        "visibility": "private",
        "authorized_for_local_review": True,
    }
    fields.update(updates)
    return EvidenceIntake(**fields)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("invoice", "financial_review"),
        ("bank_statement", "financial_review"),
        ("tax_return", "tax_review"),
        ("dot_audit", "dot_review"),
        ("dot_inspection", "dot_review"),
        ("insurance_claim", "insurance_review"),
        ("corporate_record", "corporate_review"),
        ("python_script", "software_review"),
        ("manuscript", "research_review"),
        ("unknown", "intake_triage"),
    ],
)
def test_claimed_record_type_never_silently_relabels_all_company_records_finance(
    kind: str, expected: str,
) -> None:
    result = propose_route(record(kind))
    assert result["candidate_route"] == expected
    assert result["classification"] == "DECLARED_ONLY_NOT_CONTENT_VERIFIED"
    assert result["capture"] == "METADATA_ONLY_NOT_FILE_READ"
    assert result["financial_authority"] == "HOLD"
    assert result["effect_authority"] == "NONE"
    assert result["model_training"] == "DISABLED"


def test_all_routes_have_nonempty_adversarial_review_questions() -> None:
    from aurex.company_evidence_taxonomy import REVIEW_CHALLENGES

    assert len(ROUTES) == 21
    assert set(ROUTES.values()) == set(REVIEW_CHALLENGES)
    assert all(REVIEW_CHALLENGES[route] for route in ROUTES.values())


def test_auth_missing_is_hold_without_returning_sensitive_details() -> None:
    result = propose_route(record("bank_statement", authorized_for_local_review=False))
    assert result["candidate_route"] == "HOLD_NOT_AUTHORIZED"
    assert result["review_challenges"] == []
    assert result["effect_authority"] == "NONE"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"declared_kind": "unrecognized_custom_class"},
        {"tenant_id": "../parent"},
        {"source_id": "/tmp/secret.txt"},
        {"source_sha256": "no-checksum"},
        {"training_consent": True},
        {"visibility": "external"},
        {"authorized_for_local_review": 1},
    ],
)
def test_invalid_or_permission_expanding_input_fails_closed(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        record(**kwargs)


def test_no_model_or_network_called_during_route_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import socket

    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("unexpected network")

    monkeypatch.setattr(socket, "create_connection", blocked)
    assert propose_route(record("dot_audit"))["candidate_route"] == "dot_review"
