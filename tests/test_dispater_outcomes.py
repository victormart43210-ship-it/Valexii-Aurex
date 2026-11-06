"""Synthetic lifecycle replay, identity and arithmetic adversarial coverage."""

from copy import deepcopy
from hashlib import sha256
from typing import Any

import pytest

from aurex.dispater_outcomes import KINDS, STATES, InvalidRecovery, evaluate_recovery


def dataset(amount: str = "10.10", reference: str = "settlement-1") -> dict[str, Any]:
    evidence = [
        {"id": f"proof-{state}", "tenant_id": "default", "kind": KINDS[state],
         "amount": amount, "currency": "USD", "reference": reference,
         "source_roots": [f"source-{state}"],
         "content_sha256": sha256(f"{reference}-{state}".encode()).hexdigest()}
        for state in STATES
    ]
    return {
        "dataset_type": "SYNTHETIC_ONLY", "tenant_id": "default",
        "claims": [{"id": "claim-1", "tenant_id": "default", "amount": amount,
                    "currency": "USD", "reference": reference,
                    "evidence_id": "proof-EXPECTED"}],
        "evidence": evidence,
        "events": [{"id": f"event-{state}", "tenant_id": "default", "claim_id": "claim-1",
                    "state": state, "evidence_id": f"proof-{state}"} for state in STATES[1:]],
    }


@pytest.mark.parametrize("count", range(6))
def test_every_state_is_distinct_and_replayable(count: int) -> None:
    data = dataset()
    data["events"] = data["events"][:count]
    original = deepcopy(data)
    result = evaluate_recovery(data)
    assert data == original
    assert result == evaluate_recovery(deepcopy(data))
    assert result["claims"][0]["hypothetical_state"] == STATES[count]
    assert result["confirmed_recovery_usd"] == "0.00"
    assert result["independent_verification"] == "NOT VERIFIED"
    assert result["hypothetical_reconciled_usd"] == ("10.10" if count == 5 else "0.00")


def test_interruption_and_duplicate_delivery_preserve_replay() -> None:
    data = dataset()
    partial = deepcopy(data)
    partial["events"] = partial["events"][:2]
    assert evaluate_recovery(partial)["claims"][0]["hypothetical_state"] == "APPROVED"
    for collection in ("events", "claims", "evidence"):
        data[collection] += deepcopy(data[collection])
    assert evaluate_recovery(data) == evaluate_recovery(dataset())


@pytest.mark.parametrize("collection", ["claims", "evidence", "events"])
def test_conflicting_duplicate_identifiers_fail(collection: str) -> None:
    data = dataset()
    duplicate = deepcopy(data[collection][0])
    duplicate["extra"] = "changed"
    data[collection].append(duplicate)
    with pytest.raises(InvalidRecovery, match="conflicting duplicate"):
        evaluate_recovery(data)


def test_forged_flags_cannot_skip_steps_or_confirm_recovery() -> None:
    data = dataset()
    data.update(verified=True, approved=True, confirmed_recovery_usd="10000.00")
    data["claims"][0].update(state="DEPOSIT_RECONCILED", verified=True, approved=True)
    data["events"] = []
    result = evaluate_recovery(data)
    assert result["claims"][0]["hypothetical_state"] == "EXPECTED"
    assert result["confirmed_recovery_usd"] == "0.00"
    data["events"] = dataset()["events"][-1:]
    with pytest.raises(InvalidRecovery, match="exactly one"):
        evaluate_recovery(data)


@pytest.mark.parametrize("key,value", [
    ("amount", "10.11"), ("currency", "EUR"), ("reference", "other"),
    ("kind", "APPROVAL"), ("tenant_id", "other"),
])
def test_deposit_must_match_payment_and_tenant(key: str, value: str) -> None:
    data = dataset()
    data["evidence"][-1][key] = value
    with pytest.raises(InvalidRecovery):
        evaluate_recovery(data)


@pytest.mark.parametrize("collection", ["claims", "evidence", "events"])
def test_cross_tenant_records_fail(collection: str) -> None:
    data = dataset()
    data[collection][0]["tenant_id"] = "foreign"
    with pytest.raises(InvalidRecovery, match="tenant"):
        evaluate_recovery(data)


@pytest.mark.parametrize("same", ["root", "content", "overlapping_parent"])
def test_same_source_is_never_independent(same: str) -> None:
    data = dataset()
    payment, deposit = data["evidence"][-2:]
    if same == "content":
        deposit["content_sha256"] = payment["content_sha256"]
    elif same == "overlapping_parent":
        deposit["source_roots"] += payment["source_roots"]
    else:
        deposit["source_roots"] = payment["source_roots"]
    with pytest.raises(InvalidRecovery, match="distinct source"):
        evaluate_recovery(data)


def test_duplicate_claim_under_new_id_is_rejected() -> None:
    data = dataset()
    duplicate = deepcopy(data["claims"][0])
    duplicate["id"] = "renamed"
    data["claims"].append(duplicate)
    with pytest.raises(InvalidRecovery, match="duplicate claim"):
        evaluate_recovery(data)


def add_second_claim(data: dict[str, Any], amount: str = "0.20") -> None:
    second = dataset(amount, "settlement-2")
    for claim in second["claims"]:
        claim["id"] += "-2"
        claim["evidence_id"] += "-2"
    for row in second["evidence"]:
        row["id"] += "-2"
    for event in second["events"]:
        event["id"] += "-2"
        event["claim_id"] += "-2"
        event["evidence_id"] += "-2"
    for collection in ("claims", "evidence", "events"):
        data[collection] += second[collection]


def test_duplicate_deposit_content_cannot_settle_two_claims() -> None:
    data = dataset()
    add_second_claim(data, "10.10")
    data["evidence"][-1]["content_sha256"] = data["evidence"][5]["content_sha256"]
    with pytest.raises(InvalidRecovery, match="counted twice"):
        evaluate_recovery(data)


def test_decimal_arithmetic_is_exact() -> None:
    data = dataset("0.10")
    add_second_claim(data)
    assert evaluate_recovery(data)["hypothetical_reconciled_usd"] == "0.30"


@pytest.mark.parametrize("amount", ["0.005", "NaN", "Infinity", "-1", "1e2", "1000000000", True, 0.1])
def test_ambiguous_or_excess_precision_money_is_rejected(amount: Any) -> None:
    data = dataset()
    data["claims"][0]["amount"] = amount
    with pytest.raises(InvalidRecovery):
        evaluate_recovery(data)


def test_missing_evidence_and_live_inputs_fail() -> None:
    data = dataset()
    data["evidence"] = data["evidence"][:-1]
    with pytest.raises(InvalidRecovery, match="missing evidence"):
        evaluate_recovery(data)
    data = dataset()
    data["dataset_type"] = "LIVE"
    with pytest.raises(InvalidRecovery, match="SYNTHETIC_ONLY"):
        evaluate_recovery(data)
