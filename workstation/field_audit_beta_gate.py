"""Offline, synthetic-only 100-case acceptance gate for AUREX Field Audit.

Evaluates candidate outputs independently of the proposed audit engine; it does
not perform an invoice audit, verify documents, authorize spending, or run AI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SUITE_SCHEMA = "aurex.field-audit-beta.cases.v1"
RESULT_SCHEMA = "aurex.field-audit-beta.results.v1"
ALLOWED_FLAGS = frozenset({
    "INVOICE_TICKET_VARIANCE", "TICKET_RATE_VARIANCE",
    "MISSING_RATE_APPROVAL", "DUPLICATE_INVOICE_ID",
})
MAX_RESULT_BYTES = 128 * 1024


def _canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _digest(obj: object) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()


def synthetic_cases() -> list[dict[str, Any]]:
    """100 deterministic fictional invoice/field-ticket records, no user inputs."""
    out: list[dict[str, Any]] = []
    for i in range(100):
        invoice = 2_000_000
        ticket = 2_000_000
        approved = True
        if 40 <= i < 60:
            invoice += 70_000
        elif 60 <= i < 70:
            invoice -= 60_000
        elif 70 <= i < 80:
            ticket -= 100_000
        elif 80 <= i < 90:
            approved = False
        invoice_id = f"INV-{(i - 89 if i >= 90 else i + 1):04d}"
        out.append({
            "case_id": f"BETA-{i + 1:03d}",
            "invoice_id": invoice_id,
            "invoice_cents": invoice,
            "ticket_cents": ticket,
            "approved_rate_cents_per_hour": 10_000 if approved else None,
            "documented_hours": 200,
            "synthetic": True,
        })
    return out


def suite() -> dict[str, Any]:
    out: dict[str, Any] = {"schema": SUITE_SCHEMA, "synthetic": True, "cases": synthetic_cases()}
    out["suite_sha256"] = _digest(out)
    return out


def oracle() -> dict[str, frozenset[str]]:
    """Transparent, fixed-cent fixture expectation; NOT an independent witness."""
    seen: set[str] = set()
    expected: dict[str, frozenset[str]] = {}
    for c in synthetic_cases():
        flags: set[str] = set()
        if c["invoice_id"] in seen:
            flags.add("DUPLICATE_INVOICE_ID")
        seen.add(c["invoice_id"])
        if c["invoice_cents"] != c["ticket_cents"]:
            flags.add("INVOICE_TICKET_VARIANCE")
        if c["approved_rate_cents_per_hour"] is None:
            flags.add("MISSING_RATE_APPROVAL")
        elif c["ticket_cents"] != c["approved_rate_cents_per_hour"] * c["documented_hours"]:
            flags.add("TICKET_RATE_VARIANCE")
        expected[c["case_id"]] = frozenset(flags)
    return expected


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def _reject_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant {value}")


def load_candidate(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("candidate must be a regular non-symlink local file")
    if path.stat().st_size > MAX_RESULT_BYTES:
        raise ValueError("candidate exceeds 128 KiB")
    try:
        obj = json.loads(
            path.read_bytes().decode("utf-8", errors="strict"),
            object_pairs_hook=_no_duplicate_keys, parse_constant=_reject_constant,
        )
    except (UnicodeError, ValueError) as exc:
        raise ValueError("invalid candidate JSON") from exc
    if not isinstance(obj, dict):
        raise ValueError("candidate JSON object required")
    return obj


def score_candidate(candidate: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """No PASS if any case, source binding, status or flag is absent/invalid."""
    reference = suite()
    if (set(candidate) != {"schema", "synthetic", "suite_sha256", "results"}
            or candidate["schema"] != RESULT_SCHEMA
            or candidate["synthetic"] is not True
            or candidate["suite_sha256"] != reference["suite_sha256"]
            or not isinstance(candidate["results"], list)):
        raise ValueError("unrecognized results schema, synthetic flag or suite digest")
    expected = oracle()
    actual: dict[str, set[str]] = {}
    for row in candidate["results"]:
        if not isinstance(row, dict) or set(row) != {
            "case_id", "flags", "authority", "independent_verification", "effect"
        }:
            raise ValueError("invalid result fields")
        case_id = row["case_id"]
        if not isinstance(case_id, str) or case_id not in expected or case_id in actual:
            raise ValueError("unknown or duplicated case_id")
        flags = row["flags"]
        if (not isinstance(flags, list) or any(type(f) is not str for f in flags)
                or len(flags) != len(set(flags)) or not set(flags) <= ALLOWED_FLAGS):
            raise ValueError("invalid, duplicate or unrecognized finding flags")
        if (row["authority"] != "HOLD" or row["effect"] != "NONE"
                or row["independent_verification"] != "NOT_VERIFIED"):
            raise ValueError("candidate attempted to assert authority or independent verification")
        actual[case_id] = set(flags)
    tp = fp = fn = exact = 0
    for case_id, flags in actual.items():
        target = expected[case_id]
        tp += len(flags & target)
        fp += len(flags - target)
        fn += len(target - flags)
        exact += flags == target
    missing = len(expected) - len(actual)
    passed = missing == 0 and exact == 100 and fp == 0 and fn == 0
    return {
        "kind": "AUREX_FIELD_AUDIT_SYNTHETIC_ACCEPTANCE",
        "suite_sha256": reference["suite_sha256"],
        "total_cases": 100,
        "evaluated_cases": len(actual),
        "missing_cases": missing,
        "exact_case_matches": exact,
        "true_positive_flags": tp,
        "false_positive_flags": fp,
        "false_negative_flags": fn,
        "status": "SYNTHETIC_GATE_PASS_NOT_BETA_RELEASE" if passed else "HOLD",
        "authority": "NONE",
        "independent_verification": "NOT_VERIFIED",
        "real_document_accuracy": "NOT_MEASURED",
        "production_readiness": "HOLD",
    }, passed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUREX Field Audit — synthetic beta acceptance, no AI or customer data")
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("--cases", action="store_true", help="print sealed 100-case synthetic input suite")
    exclusive.add_argument("--score", type=Path, help="score JSON candidate outputs against fixture oracle")
    args = parser.parse_args(argv)
    if args.cases:
        print(json.dumps(suite(), sort_keys=True, indent=2))
        return 0
    try:
        report, passed = score_candidate(load_candidate(args.score))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc), "authority": "NONE"}))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
