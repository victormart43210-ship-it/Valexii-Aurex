"""AUREX Field Audit pilot: offline, evidence-first, *non-authorizing* gate.

Evaluates whether a proposed limited customer-data beta has enough declared
support to be independently reviewed. NEVER starts ingestion, infers auth from
passing tests, grants financial permissions, or signs commercial agreements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCHEMA = "aurex.field_pilot_admission.v1"
GATES = (
    "EXACT_HEAD_CI",
    "AUTHENTICATED_E2E",
    "TENANT_ISOLATION",
    "SOURCE_CUSTODY",
    "CONSENT_AND_RIGHTS",
    "SECURE_DOCUMENT_INTAKE",
    "DETERMINISTIC_QUALITY",
    "INDEPENDENT_SECURITY_REVIEW",
    "HUMAN_REVIEW",
    "BACKUP_AND_ROLLBACK",
    "CUSTOMER_CONTRACT",
)
FRESH_DAYS = {"EXACT_HEAD_CI": 7, "AUTHENTICATED_E2E": 7,
              "INDEPENDENT_SECURITY_REVIEW": 30, "DETERMINISTIC_QUALITY": 30}
IDENT = re.compile(r"[a-zA-Z0-9][\w.:-]{1,63}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
ALLOWED_STATES = {"PASS", "FAIL", "HOLD", "NOT_RUN", "NOT_VERIFIED"}
MAX_BYTES = 128 * 1024


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, val in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = val
    return obj


def _invalid_constant(_val: str) -> None:
    raise ValueError("non-finite JSON is not admissible")


def load(path: Path) -> tuple[dict[str, Any], str]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("manifest must be a regular non-symlink file")
    if not 1 <= path.stat().st_size <= MAX_BYTES:
        raise ValueError("manifest is outside size limits")
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8", errors="strict"),
                          object_pairs_hook=_pairs, parse_constant=_invalid_constant)
    except RecursionError as exc:
        raise ValueError("invalid nesting in admission manifest") from exc
    if type(data) is not dict:
        raise ValueError("manifest must be a JSON object")
    return data, hashlib.sha256(raw).hexdigest()


def evaluate(data: dict[str, Any], *, now: datetime, input_sha256: str = "NOT_PINNED") -> dict[str, Any]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("evaluation clock must be timezone-aware")
    if type(data) is not dict or set(data) != {
        "schema", "pilot_id", "model_mode", "owner", "implementer", "checks"
    }:
        raise ValueError("admission manifest shape invalid")
    if (data["schema"] != SCHEMA
            or not all(isinstance(data[k], str) and IDENT.fullmatch(data[k])
                       for k in ("pilot_id", "owner", "implementer"))
            or data["model_mode"] not in ("deterministic_only", "qwen_advisory")):
        raise ValueError("admission metadata invalid")
    checks = data["checks"]
    if type(checks) is not list or len(checks) != len(GATES):
        raise ValueError("all gate statuses required")
    by_id: dict[str, dict[str, Any]] = {}
    for rec in checks:
        if type(rec) is not dict or set(rec) != {
            "id", "status", "evidence_sha256", "evidence_ref", "reviewer", "reviewed_at"
        }:
            raise ValueError("gate record shape invalid")
        key = rec["id"]
        if (key not in GATES or key in by_id
                or type(rec["status"]) is not str or rec["status"] not in ALLOWED_STATES):
            raise ValueError("unknown or repeated gate/status")
        for fld in ("evidence_sha256", "evidence_ref", "reviewer", "reviewed_at"):
            if not isinstance(rec[fld], str):
                raise ValueError("gate evidence fields must be strings")
        by_id[key] = rec
    if set(by_id) != set(GATES):
        raise ValueError("missing gate")
    blocked: list[dict[str, str]] = []
    as_of = now.astimezone(timezone.utc)
    for key in GATES:
        rec = by_id[key]
        reason = None
        if rec["status"] != "PASS":
            reason = rec["status"]
        elif (not SHA.fullmatch(rec["evidence_sha256"])
              or not 8 <= len(rec["evidence_ref"]) <= 240
              or "\n" in rec["evidence_ref"]
              or not IDENT.fullmatch(rec["reviewer"])):
            reason = "MISSING_OR_INVALID_WITNESS"
        elif rec["reviewer"] in {data["implementer"], data["owner"]}:
            reason = "REVIEWER_NOT_SEPARATE"
        else:
            try:
                at = datetime.fromisoformat(rec["reviewed_at"])
                if at.tzinfo is None or at.utcoffset() is None:
                    reason = "WITNESS_TIME_NOT_AWARE"
                else:
                    age = as_of - at.astimezone(timezone.utc)
                    if age < -timedelta(minutes=5):
                        reason = "WITNESS_IN_FUTURE"
                    elif age > timedelta(days=FRESH_DAYS.get(key, 90)):
                        reason = "WITNESS_STALE"
            except ValueError:
                reason = "WITNESS_TIME_INVALID"
        if reason:
            blocked.append({"gate": key, "reason": reason})
    candidate = not blocked
    return {
        "schema": "aurex.field_pilot_assessment.v1",
        "pilot_id": data["pilot_id"],
        "assessment_as_of": as_of.isoformat(),
        "input_sha256": input_sha256,
        "model_mode": data["model_mode"],
        "checks_supplied": len(checks),
        "blocking_gates": blocked,
        "assessment": "INDEPENDENT_ADMISSION_REVIEW_REQUIRED" if candidate else "HOLD",
        "reviewer_identity_independently_verified": False,
        "evidence_authenticity_independently_verified": False,
        "actual_customer_data_handling_authorized": False,
        "customer_contract_executed": False,
        "production_release": "HOLD",
        "payment_or_billing_authority": "NONE",
        "external_spend_usd": 0,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Local Field Audit beta review readiness, never approval")
    p.add_argument("--manifest", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        input_data, digest = load(args.manifest)
        report = evaluate(input_data, now=datetime.now(timezone.utc), input_sha256=digest)
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"assessment": "HOLD_INVALID_INPUT", "production_release": "HOLD",
                          "error_category": type(exc).__name__}))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not report["blocking_gates"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
