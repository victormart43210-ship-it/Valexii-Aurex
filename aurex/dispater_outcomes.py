"""Read-only, synthetic recovery rehearsal; never verifies a real financial outcome.

Replay ordered events from EXPECTED through DEPOSIT_RECONCILED. Evidence and source
roots are supplied assertions, not authenticated external records. Even a complete
rehearsal has zero confirmed recovery and grants no financial authority.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Any

STATES = (
    "EXPECTED", "SUBMITTED", "APPROVED", "PAYMENT_PROMISED",
    "PAYMENT_RECEIVED", "DEPOSIT_RECONCILED",
)
KINDS = dict(zip(STATES, (
    "EXPECTATION", "SUBMISSION", "APPROVAL", "PROMISE", "PAYMENT", "DEPOSIT",
), strict=True))
LIMIT = 2000


class InvalidRecovery(ValueError):
    """A synthetic recovery dataset violates the replay contract."""


def _text(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise InvalidRecovery(f"{key} must be a nonempty bounded string")
    if value != value.strip():
        raise InvalidRecovery(f"{key} must not have surrounding whitespace")
    return value


def _money(row: dict[str, Any]) -> Decimal:
    value = _text(row, "amount")
    # Reject excess precision instead of silently rounding a financial assertion.
    if not re.fullmatch(r"[0-9]{1,9}(?:\.[0-9]{1,2})?", value):
        raise InvalidRecovery("amount must be nonnegative decimal USD with at most two places")
    if row.get("currency") != "USD":
        raise InvalidRecovery("only USD is supported")
    return Decimal(value).quantize(Decimal("0.01"))


def _rows(dataset: dict[str, Any], key: str, tenant_id: str) -> list[dict[str, Any]]:
    rows = dataset.get(key)
    if not isinstance(rows, list) or len(rows) > LIMIT:
        raise InvalidRecovery(f"{key} must be a list with at most {LIMIT} entries")
    unique: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("tenant_id") != tenant_id:
            raise InvalidRecovery(f"{key}: invalid record or tenant mismatch")
        identifier = _text(row, "id")
        try:
            json.dumps(row, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise InvalidRecovery("records must contain finite JSON values") from exc
        if identifier in unique and unique[identifier] != row:
            raise InvalidRecovery(f"{key}: conflicting duplicate id {identifier}")
        unique[identifier] = row
    return list(unique.values())


def evaluate_recovery(
    dataset: dict[str, Any], *, tenant_id: str = "default"
) -> dict[str, Any]:
    """Evaluate a bounded event log without I/O, mutation, or financial effects.

    Each claim has id, tenant_id, amount, currency, reference, evidence_id.
    Evidence has id, tenant_id, kind, amount, currency, reference, source_roots
    (nonempty string list), and content_sha256 (digest of original source bytes).
    Each event has id, tenant_id, claim_id, state, evidence_id. States must advance
    exactly one step. Identical repeated record IDs are replay-idempotent; changed
    duplicates fail. Distinct claims cannot reuse the same settlement reference.
    Supplied approval/verified/state flags on claims never establish a transition.
    """
    if not isinstance(dataset, dict) or dataset.get("dataset_type") != "SYNTHETIC_ONLY":
        raise InvalidRecovery("only SYNTHETIC_ONLY recovery datasets are admitted")
    if not isinstance(tenant_id, str) or not tenant_id or dataset.get("tenant_id") != tenant_id:
        raise InvalidRecovery("dataset tenant mismatch")
    evidence = {row["id"]: row for row in _rows(dataset, "evidence", tenant_id)}
    roots: dict[str, set[str]] = {}
    for identifier, row in evidence.items():
        _money(row)
        _text(row, "reference")
        if row.get("kind") not in KINDS.values():
            raise InvalidRecovery("unknown evidence kind")
        source_roots = row.get("source_roots")
        if (not isinstance(source_roots, list) or not source_roots
                or len(source_roots) > LIMIT
                or any(not isinstance(root, str) or not root.strip()
                       or root != root.strip() or len(root) > 256 for root in source_roots)):
            raise InvalidRecovery("evidence requires bounded source_roots")
        roots[identifier] = set(source_roots)
        if not re.fullmatch(r"[a-f0-9]{64}", _text(row, "content_sha256")):
            raise InvalidRecovery("content_sha256 must be a lowercase SHA-256 digest")

    def match(evidence_id: str, claim: dict[str, Any], state: str) -> dict[str, Any]:
        record = evidence.get(evidence_id)
        if record is None:
            raise InvalidRecovery("missing evidence")
        if (record["kind"] != KINDS[state]
                or _money(record) != _money(claim)
                or record["reference"] != claim["reference"]):
            raise InvalidRecovery("evidence kind, amount, currency or reference mismatch")
        return record

    claims = {row["id"]: row for row in _rows(dataset, "claims", tenant_id)}
    positions: dict[str, int] = {}
    used_references: set[str] = set()
    payment_evidence: dict[str, str] = {}
    for identifier, claim in claims.items():
        _money(claim)
        reference = _text(claim, "reference")
        if reference in used_references:
            raise InvalidRecovery("duplicate claim settlement reference")
        used_references.add(reference)
        match(_text(claim, "evidence_id"), claim, "EXPECTED")
        positions[identifier] = 0

    used_deposit_content: set[str] = set()
    for event in _rows(dataset, "events", tenant_id):
        claim_id = _text(event, "claim_id")
        if claim_id not in claims:
            raise InvalidRecovery("event refers to missing claim")
        state = _text(event, "state")
        position = positions[claim_id]
        if position + 1 >= len(STATES) or state != STATES[position + 1]:
            raise InvalidRecovery("events must advance exactly one lifecycle step")
        evidence_id = _text(event, "evidence_id")
        record = match(evidence_id, claims[claim_id], state)
        if state == "PAYMENT_RECEIVED":
            payment_evidence[claim_id] = evidence_id
        if state == "DEPOSIT_RECONCILED":
            payment_id = payment_evidence[claim_id]
            if (roots[payment_id] & roots[evidence_id]
                    or evidence[payment_id]["content_sha256"] == record["content_sha256"]):
                raise InvalidRecovery("payment and deposit require distinct source roots and content")
            if record["content_sha256"] in used_deposit_content:
                raise InvalidRecovery("deposit content cannot be counted twice")
            used_deposit_content.add(record["content_sha256"])
        positions[claim_id] += 1

    total = sum((_money(claims[key]) for key, position in positions.items()
                 if STATES[position] == "DEPOSIT_RECONCILED"), Decimal("0.00"))
    return {
        "schema": "dispater.synthetic.recovery.v1",
        "dataset_type": "SYNTHETIC_ONLY",
        "tenant_id": tenant_id,
        "claims": [{"claim_id": key, "hypothetical_state": STATES[positions[key]],
                    "amount_usd": format(_money(claims[key]), ".2f")}
                   for key in sorted(claims)],
        "confirmed_recovery_usd": "0.00",
        "hypothetical_reconciled_usd": format(total, ".2f"),
        "independent_verification": "NOT VERIFIED",
        "financial_authority": "NONE",
        "production_status": "HOLD",
        "limitation": "Synthetic rehearsal only. Source roots and approval records are untrusted "
                      "input assertions; authenticated external ingestion and human approval "
                      "integration are unavailable. No actual recovery is verified.",
    }
