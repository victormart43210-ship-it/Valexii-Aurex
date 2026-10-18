"""APIS PRIME immutable display-name contract; names never grant authority."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

REGISTRY = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "architecture"
    / "apis_prime_registry.json"
)

EXPECTED = (
    "APIS-LEX",
    "KUKULKAN",
    "LYSIPHER",
    "SPECTRA",
    "SIFTRA",
    "ITZAMNAAJ",
    "ELNOESIS",
    "COATLICUE",
    "IACCHCODEX",
    "PROSOPHEX",
    "TEZCATLIPOCA",
    "XOLOTL",
    "ANTHOFORGE",
    "CRUCIBLE",
)


def _load() -> dict[str, Any]:
    with REGISTRY.open(encoding="utf-8") as source:
        return cast(dict[str, Any], json.load(source))


def test_exact_owner_approved_roster_and_stable_ids() -> None:
    registry = _load()
    systems = registry["system_names"]
    assert isinstance(systems, list)
    assert len(systems) == 14
    assert tuple(item["display_name"] for item in systems) == EXPECTED
    assert tuple(item["id"] for item in systems) == tuple(
        f"AP{n:02}" for n in range(1, 15)
    )
    assert len({item["display_name"].casefold() for item in systems}) == 14


def test_single_spine_names_match_owner_locked_registry() -> None:
    from aurex.apis_prime_spine import NAMES

    registry = _load()
    assert tuple(item["display_name"] for item in registry["system_names"]) == NAMES


def test_no_self_authority_and_technical_method_attribution() -> None:
    registry = _load()
    systems = registry["system_names"]
    assert isinstance(systems, list)
    assert all(item["authority"] == "NONE" for item in systems)
    assert all(item["technical_aliases"] for item in systems)
    methods = {item["display_name"]: item["technical_aliases"] for item in systems}
    assert "QWEN" in methods["ELNOESIS"]
    assert "OPUSFILTER" in methods["SIFTRA"]
    assert "LRPLAN" in methods["ITZAMNAAJ"]
    assert "LLULL" in methods["KUKULKAN"]
    assert "HURUF" in methods["APIS-LEX"]
    assert registry["unmodified_governance"][:2] == ["CUSTOS", "SHRIKE"]


def test_dashboard_and_release_cannot_be_authorized_by_names() -> None:
    registry = _load()
    assert registry["identity_scope"] == "names_and_functional_responsibilities_only"
    dashboard = registry["dashboard_policy"]
    deployment = registry["deployment_policy"]
    assert dashboard["display_country_labels"] is False
    assert dashboard["no_flags"] is True
    assert dashboard["status_must_come_from_independent_evidence"] is True
    assert deployment["no_automatic_merge"] is True
    assert deployment["no_automatic_deployment"] is True
    assert deployment["no_public_model_inference"] is True
    assert deployment["no_spend_without_owner_approval"] is True
