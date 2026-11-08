"""Model registry v1. Entries are candidates until a human records an independent review.

Weight digests are null when no artifact is present. The SHA-256 of empty input
is not accepted as evidence that a model was installed.
"""

from __future__ import annotations

import copy
from typing import Any

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

REGISTRY: dict[str, Any] = {
    "schema": "aurex.ox.registry.v1",
    "financial_authority": "NONE",
    "paid_inference": "OFF",
    "training": "NOT_STARTED",
    "models": [
        {"entry_id": "qwen", "kind": "FOUNDATION_MODEL", "family": "Qwen", "developer": "Alibaba Cloud", "country": "China", "priority": 1, "model_identifier": "UNPINNED", "revision": "UNPINNED", "license": "Qwen license terms require separate review", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["explanation", "extraction_proposal"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": [], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "mistral", "kind": "FOUNDATION_MODEL", "family": "Mistral / Ministral", "developer": "Mistral AI", "country": "France", "priority": 2, "model_identifier": "UNPINNED", "revision": "UNPINNED", "license": "Varies by release; Apache-2.0 does not cover every Mistral weight", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["explanation", "comparison"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": [], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "k2-horizon", "kind": "FOUNDATION_MODEL", "family": "K2 Horizon", "developer": "Institute of Foundation Models", "country": "United Arab Emirates", "priority": 3, "model_identifier": "IFM/K2-Horizon-0.9B", "revision": "UNPINNED", "license": "Weight license was not re-verified in this run", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["challenger"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": ["https://huggingface.co/IFM/K2-Horizon-0.9B"], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "falcon-h1", "kind": "FOUNDATION_MODEL", "family": "Falcon-H1", "developer": "Technology Innovation Institute", "country": "United Arab Emirates", "priority": 4, "model_identifier": "tiiuae/Falcon-H1", "revision": "UNPINNED", "license": "Falcon-LLM license; commercial use requires legal review", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["challenger"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": ["https://github.com/tiiuae/falcon-H1"], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "deepseek", "kind": "FOUNDATION_MODEL", "family": "DeepSeek", "developer": "DeepSeek", "country": "China", "priority": 5, "model_identifier": "UNPINNED", "revision": "UNPINNED", "license": "Release-specific; not re-verified here", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["explanation"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": [], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "apertus", "kind": "FOUNDATION_MODEL", "family": "Apertus", "developer": "Swiss AI Initiative", "country": "Switzerland", "priority": 6, "model_identifier": "UNPINNED", "revision": "UNPINNED", "license": "Not re-verified in this run", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["explanation"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": [], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "exaone", "kind": "FOUNDATION_MODEL", "family": "EXAONE", "developer": "LG AI Research", "country": "South Korea", "priority": 7, "model_identifier": "UNPINNED", "revision": "UNPINNED", "license": "Not re-verified in this run", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["explanation"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": [], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "sarvam", "kind": "FOUNDATION_MODEL", "family": "Sarvam", "developer": "Sarvam AI", "country": "India", "priority": 8, "model_identifier": "UNPINNED", "revision": "UNPINNED", "license": "Not re-verified in this run", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["explanation"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": [], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "sea-lion", "kind": "FOUNDATION_MODEL", "family": "SEA-LION", "developer": "AI Singapore", "country": "Singapore", "priority": 9, "model_identifier": "UNPINNED", "revision": "UNPINNED", "license": "Not re-verified in this run", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["explanation"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": [], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
        {"entry_id": "llama", "kind": "FOUNDATION_MODEL", "family": "Llama", "developer": "Meta", "country": "United States", "priority": 11, "model_identifier": "UNPINNED", "revision": "UNPINNED", "license": "Llama community license; commercial thresholds require review", "commercial_use": "REVIEW_REQUIRED", "weight_digest": None, "tokenizer_digest": None, "architecture": "UNVERIFIED", "parameter_count": None, "runtime": "NOT_INSTALLED", "tasks": ["explanation"], "evaluation_status": "NOT_EVALUATED", "customization_eligibility": "PROPOSED", "evidence": [], "approval_state": "CANDIDATE", "live_connection": "NOT_VERIFIED", "self_approval_allowed": False},
    ],
    "research_frameworks": [
        {"entry_id": "sakana", "kind": "RESEARCH_FRAMEWORK", "family": "Sakana AI research", "developer": "Sakana AI", "country": "Japan", "priority": 10, "license": "Project-specific", "commercial_use": "REVIEW_REQUIRED", "runtime": "NOT_INSTALLED", "approval_state": "CANDIDATE", "executable_model": False},
        {"entry_id": "reana", "kind": "RESEARCH_FRAMEWORK", "family": "REANA", "developer": "CERN", "country": "Switzerland", "priority": 20, "license": "MIT", "commercial_use": "REVIEW_REQUIRED", "upstream": "https://github.com/reanahub/reana", "runtime": "NOT_INSTALLED", "approval_state": "CANDIDATE", "executable_model": False},
        {"entry_id": "rucio", "kind": "RESEARCH_FRAMEWORK", "family": "Rucio", "developer": "CERN", "country": "Switzerland", "priority": 21, "license": "Apache-2.0", "commercial_use": "REVIEW_REQUIRED", "upstream": "https://github.com/rucio/rucio", "runtime": "NOT_INSTALLED", "approval_state": "CANDIDATE", "executable_model": False},
        {"entry_id": "root", "kind": "RESEARCH_FRAMEWORK", "family": "ROOT", "developer": "CERN", "country": "Switzerland", "priority": 22, "license": "LGPL with exceptions; not used for money", "commercial_use": "REVIEW_REQUIRED", "upstream": "https://root.cern/", "runtime": "NOT_INSTALLED", "approval_state": "CANDIDATE", "executable_model": False},
        {"entry_id": "invenio-rdm", "kind": "RESEARCH_FRAMEWORK", "family": "InvenioRDM", "developer": "CERN", "country": "Switzerland", "priority": 23, "license": "Component licenses require review", "commercial_use": "REVIEW_REQUIRED", "upstream": "https://inveniosoftware.org/products/rdm/", "runtime": "NOT_INSTALLED", "approval_state": "CANDIDATE", "executable_model": False},
        {"entry_id": "kitab-bench", "kind": "RESEARCH_FRAMEWORK", "family": "KITAB-Bench", "developer": "MBZUAI", "country": "United Arab Emirates", "priority": 24, "license": "MIT repository; dataset licenses are separate", "commercial_use": "REVIEW_REQUIRED", "upstream": "https://github.com/mbzuai-oryx/KITAB-Bench", "runtime": "NOT_INSTALLED", "approval_state": "CANDIDATE", "executable_model": False},
        {"entry_id": "ain", "kind": "RESEARCH_FRAMEWORK", "family": "AIN", "developer": "MBZUAI", "country": "United Arab Emirates", "priority": 25, "license": "MIT code; weights were not downloaded", "commercial_use": "REVIEW_REQUIRED", "upstream": "https://github.com/mbzuai-oryx/AIN", "runtime": "NOT_INSTALLED", "approval_state": "CANDIDATE", "executable_model": False},
    ],
}

_MODEL_FIELDS = {
    "entry_id", "kind", "family", "developer", "country", "priority", "model_identifier",
    "revision", "license", "commercial_use", "weight_digest", "tokenizer_digest",
    "architecture", "parameter_count", "runtime", "tasks", "evaluation_status",
    "customization_eligibility", "evidence", "approval_state", "live_connection",
    "self_approval_allowed",
}


class RegistryError(ValueError):
    """The registry entry is not admissible."""


def _digest_ok(value: object) -> bool:
    if value is None:
        return True
    return isinstance(value, str) and len(value) == 64 and value != EMPTY_SHA256 and all(
        character in "0123456789abcdef" for character in value
    )


def validate_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fail closed on a missing license, a self-approval, or a fake empty digest."""
    data = REGISTRY if registry is None else registry
    if data.get("paid_inference") != "OFF" or data.get("financial_authority") != "NONE":
        raise RegistryError("paid inference and financial authority stay off")
    if data.get("training") != "NOT_STARTED":
        raise RegistryError("training is not started")
    seen: set[str] = set()
    for entry in data["models"]:
        if set(entry) != _MODEL_FIELDS:
            raise RegistryError(f"model fields do not match v1: {entry.get('entry_id')}")
        if not entry["license"] or not entry["entry_id"] or entry["entry_id"] in seen:
            raise RegistryError("every model needs a unique id and a license record")
        if entry["self_approval_allowed"] or entry["approval_state"] != "CANDIDATE":
            raise RegistryError("a registry entry cannot approve itself")
        if entry["live_connection"] != "NOT_VERIFIED" or entry["evaluation_status"] != "NOT_EVALUATED":
            raise RegistryError("this registry has no verified live model")
        if entry["runtime"] != "NOT_INSTALLED":
            raise RegistryError("a candidate runtime is not installed")
        if entry["commercial_use"] == "APPROVED" or entry["customization_eligibility"] == "APPROVED":
            raise RegistryError("commercial use and customization stay unapproved")
        if not _digest_ok(entry["weight_digest"]) or not _digest_ok(entry["tokenizer_digest"]):
            raise RegistryError("an empty or malformed digest is not an installed model")
        seen.add(str(entry["entry_id"]))
    for entry in data["research_frameworks"]:
        if entry["kind"] != "RESEARCH_FRAMEWORK" or entry.get("executable_model"):
            raise RegistryError("a research framework is not an installed foundation model")
        if not entry.get("license"):
            raise RegistryError("a framework still needs a license note")
        if entry.get("approval_state") != "CANDIDATE" or entry.get("runtime") != "NOT_INSTALLED":
            raise RegistryError("a framework cannot approve itself or claim a runtime")
        if entry.get("commercial_use") == "APPROVED" or entry.get("live_connection") not in (None, "NOT_VERIFIED"):
            raise RegistryError("a framework has no live approval")
    return copy.deepcopy(data)


def get_model(entry_id: str) -> dict[str, Any]:
    validate_registry()
    for entry in REGISTRY["models"]:
        if entry["entry_id"] == entry_id:
            return copy.deepcopy(entry)
    raise RegistryError(f"unknown model {entry_id}")


def static_catalog_is_not_an_inference_target(entry_id: str) -> dict[str, Any]:
    """A catalog row is not an approved serving identity."""
    entry = get_model(entry_id)
    if entry["approval_state"] != "CANDIDATE" or entry["runtime"] != "NOT_INSTALLED":
        raise RegistryError("the static catalog cannot describe an installed model")
    return {
        "entry_id": entry_id,
        "inference_allowed": False,
        "reason": "candidate records are not inference targets",
        "financial_authority": "NONE",
    }
