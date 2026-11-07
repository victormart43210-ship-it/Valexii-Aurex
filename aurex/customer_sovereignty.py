"""Customer sovereignty contract.

DISPATER discovers. The customer decides. This module does not send mail, call a
webhook, or change a financial record. A caller-supplied HUMAN label, a checkbox,
or a model instruction is not an authorization.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

THIRD_PARTY_CONTACT = "NONE"
FINANCIAL_ACTION = "NONE"
TRAINING_REUSE = "NOT_AUTHORIZED"
DELETION = "NOT_IMPLEMENTED"


class SovereigntyError(PermissionError):
    """A consequential effect was requested and is refused."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def assert_no_effect() -> None:
    """Fail closed if this process is configured to act or to contact anyone."""
    if THIRD_PARTY_CONTACT != "NONE" or FINANCIAL_ACTION != "NONE":
        raise SovereigntyError("EFFECT_AUTHORITY_CHANGED")


def _decision(proposal: Mapping[str, Any] | None) -> dict[str, Any]:
    assert_no_effect()
    if not isinstance(proposal, Mapping):
        reason = "DECISION_MISSING"
    elif proposal.get("grantor_kind") == "HUMAN" or proposal.get("approved") is True:
        reason = "FORGED_OR_UNVERIFIED_APPROVAL"
    elif isinstance(proposal.get("instruction"), str) and proposal.get("instruction"):
        reason = "MODEL_INSTRUCTION_IS_NOT_AUTHORITY"
    else:
        reason = "ACTION_NOT_IMPLEMENTED"
    return {
        "executed": False,
        "contacted": False,
        "training_started": False,
        "reason_code": reason,
        "financial_authority": "NONE",
        "third_party_contact": "NONE",
        "identity_verification": "UNVERIFIED",
    }


def external_contact(proposal: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Refuse every outbound contact. No message is sent."""
    decision = _decision(proposal)
    decision["channel"] = None
    return decision


def financial_action(proposal: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Refuse collections, disputes, payments, and record modifications."""
    decision = _decision(proposal)
    decision["records_modified"] = False
    return decision


def training_reuse(consent: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Customer records are not a training set. Consent text does not start training."""
    decision = _decision(consent)
    decision["allowed"] = False
    decision["customer_data_in_training"] = False
    decision["reason_code"] = "TRAINING_REUSE_NOT_AUTHORIZED"
    return decision
