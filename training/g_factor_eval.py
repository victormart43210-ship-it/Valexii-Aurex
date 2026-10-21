"""AUREX G-Factor: offline cross-domain *generalization* diagnostic.

"G-Factor" is a product mnemonic, NOT a psychometric general-intelligence
factor estimate. The model never judges itself: externally supplied references
and snapshots are compared by deterministic exact labels + evidence receipts.
Every output remains non-authoritative and production HOLD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

REFERENCE_SCHEMA = "aurex.gfactor.reference.v1"
PREDICTIONS_SCHEMA = "aurex.gfactor.predictions.v1"
MAX_INPUT_BYTES = 1024 * 1024
MAX_CASES = 2000
MIN_PER_DOMAIN = 5

DOMAINS = (
    "document_extraction",
    "spreadsheet_reasoning",
    "invoice_reconciliation",
    "contract_interpretation",
    "audit_evidence",
    "novel_transfer",
)
HEX = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}\Z")
LABEL = re.compile(r"[A-Z][A-Z0-9_]{0,47}\Z")


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate JSON key")
        out[k] = v
    return out


def _no_constant(_: str) -> None:
    raise ValueError("non-finite JSON value")


def read_json(path: Path) -> tuple[dict[str, Any], str]:
    """Bounded UTF-8, no symlink, no JSON duplicate keys or invalid constants."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("regular non-symlink JSON input required")
    if not 0 < path.stat().st_size <= MAX_INPUT_BYTES:
        raise ValueError("JSON input size out of bounds")
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"),
                           object_pairs_hook=_unique_pairs, parse_constant=_no_constant)
    except (UnicodeError, ValueError) as exc:
        raise ValueError("invalid JSON input") from exc
    if type(value) is not dict:
        raise ValueError("top-level JSON object required")
    return value, hashlib.sha256(raw).hexdigest()


def _hash(value: Any) -> bool:
    return type(value) is str and HEX.fullmatch(value) is not None


def _id(value: Any) -> bool:
    return type(value) is str and ID.fullmatch(value) is not None


def _label(value: Any) -> bool:
    return type(value) is str and LABEL.fullmatch(value) is not None


def _ids(value: Any, *, allow_empty: bool) -> bool:
    return (type(value) is list and (allow_empty or len(value) > 0)
            and len(value) <= 30 and all(_id(s) for s in value)
            and len(set(value)) == len(value))


def validate_reference(ref: dict[str, Any]) -> dict[str, dict[str, Any]]:
    required = {"schema", "benchmark_id", "reference_reviewer",
                "approved_for_evaluation", "training_group_hashes", "cases"}
    if type(ref) is not dict or set(ref) != required:
        raise ValueError("reference manifest schema fields invalid")
    if (ref["schema"] != REFERENCE_SCHEMA or not _id(ref["benchmark_id"])
            or not _id(ref["reference_reviewer"])
            or ref["approved_for_evaluation"] is not True):
        raise ValueError("benchmark declaration invalid")
    train_groups = ref["training_group_hashes"]
    if (type(train_groups) is not list or len(train_groups) > MAX_CASES
            or any(not _hash(x) for x in train_groups)
            or len(set(train_groups)) != len(train_groups)):
        raise ValueError("training group fingerprint list invalid")
    rows = ref["cases"]
    if type(rows) is not list or not 1 <= len(rows) <= MAX_CASES:
        raise ValueError("reference case count invalid")
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    cases: dict[str, dict[str, Any]] = {}
    for row in rows:
        if (type(row) is not dict or set(row) != {
            "case_id", "domain", "group_sha256", "novel",
            "expected_label", "required_evidence"
        }):
            raise ValueError("reference case fields invalid")
        cid = row["case_id"]
        if (not _id(cid) or cid in cases or row["domain"] not in DOMAINS
                or not _hash(row["group_sha256"])
                or row["group_sha256"] in train_groups
                or type(row["novel"]) is not bool
                or not _label(row["expected_label"])
                or not _ids(row["required_evidence"], allow_empty=False)):
            raise ValueError("duplicate/invalid case, training-group leak or label")
        cases[cid] = row
        by_domain[row["domain"]].append(row)
    for domain in DOMAINS:
        subset = by_domain[domain]
        if (len(subset) < MIN_PER_DOMAIN
                or len({r["group_sha256"] for r in subset}) < 2
                or not any(r["novel"] for r in subset)):
            raise ValueError(f"insufficient held-out diversity: {domain}")
    return cases


def validate_predictions(data: dict[str, Any], expected_ids: set[str],
                         benchmark_id: str) -> dict[str, dict[str, Any]]:
    if (type(data) is not dict
            or set(data) != {"schema", "benchmark_id", "snapshot_sha256", "answers"}
            or data["schema"] != PREDICTIONS_SCHEMA
            or data["benchmark_id"] != benchmark_id
            or not _hash(data["snapshot_sha256"])
            or type(data["answers"]) is not list
            or len(data["answers"]) != len(expected_ids)):
        raise ValueError("prediction manifest identity or count invalid")
    answers: dict[str, dict[str, Any]] = {}
    for a in data["answers"]:
        if (type(a) is not dict or set(a) != {
            "case_id", "label", "cited_evidence", "authority", "effect"
        } or not _id(a["case_id"]) or a["case_id"] in answers
                or not _label(a["label"]) or not _ids(a["cited_evidence"], allow_empty=True)
                or type(a["authority"]) is not str
                or type(a["effect"]) is not str):
            raise ValueError("prediction shape, evidence or duplicate ID invalid")
        answers[a["case_id"]] = a
    if set(answers) != expected_ids:
        raise ValueError("prediction IDs do not match reference")
    return answers


def _correct(reference: dict[str, Any], answer: dict[str, Any]) -> bool:
    # Unreferenced sources may be fabricated. Only allowlisted source IDs count.
    required = set(reference["required_evidence"])
    return (answer["label"] == reference["expected_label"]
            and set(answer["cited_evidence"]) == required)


def score(ref: dict[str, Any], candidate: dict[str, Any],
          baseline: dict[str, Any], *, reference_sha256: str = "NOT_PINNED",
          candidate_sha256: str = "NOT_PINNED",
          baseline_sha256: str = "NOT_PINNED") -> tuple[dict[str, Any], bool]:
    """Compare fixed reference labels; NEVER grant authority or attest review."""
    cases = validate_reference(ref)
    ids = set(cases)
    c = validate_predictions(candidate, ids, ref["benchmark_id"])
    b = validate_predictions(baseline, ids, ref["benchmark_id"])
    if candidate["snapshot_sha256"] == baseline["snapshot_sha256"]:
        raise ValueError("candidate and baseline must have distinct model snapshots")

    domain_results = []
    total_unsafe_candidate = 0
    total_unsafe_baseline = 0
    regressions: list[str] = []
    improved = []
    for domain in DOMAINS:
        subset = [x for x in cases.values() if x["domain"] == domain]
        c_pass = b_pass = c_novel = b_novel = c_covered = b_covered = 0
        novel_count = 0
        for r in subset:
            cid = r["case_id"]
            ca, ba = c[cid], b[cid]
            safe_c = ca["authority"] == "HOLD" and ca["effect"] == "NONE"
            safe_b = ba["authority"] == "HOLD" and ba["effect"] == "NONE"
            total_unsafe_candidate += not safe_c
            total_unsafe_baseline += not safe_b
            cp = _correct(r, ca) and safe_c
            bp = _correct(r, ba) and safe_b
            c_pass += cp
            b_pass += bp
            c_covered += ca["label"] != "ABSTAIN"
            b_covered += ba["label"] != "ABSTAIN"
            if r["novel"]:
                novel_count += 1
                c_novel += cp
                b_novel += bp
        if c_pass < b_pass or c_novel < b_novel:
            regressions.append(domain)
        if c_pass > b_pass and c_novel >= b_novel:
            improved.append(domain)
        domain_results.append({
            "domain": domain, "held_out_cases": len(subset),
            "distinct_held_out_groups": len({x["group_sha256"] for x in subset}),
            "novel_cases": novel_count,
            "baseline_supported": b_pass, "candidate_supported": c_pass,
            "baseline_novel_supported": b_novel, "candidate_novel_supported": c_novel,
            "candidate_abstained": len(subset) - c_covered,
            "baseline_abstained": len(subset) - b_covered,
        })
    if total_unsafe_candidate:
        gate = "HOLD_UNAUTHORIZED_OUTPUT"
    elif total_unsafe_baseline:
        gate = "HOLD_UNSAFE_COMPARISON_BASELINE"
    elif regressions:
        gate = "HOLD_DOMAIN_REGRESSION"
    elif not improved:
        gate = "HOLD_NO_OBSERVED_TRANSFER_GAIN"
    else:
        gate = "REVIEWABLE_SYNTHETIC_GENERALIZATION_GAIN"
    report = {
        "kind": "AUREX_GFACTOR_CROSS_DOMAIN_DIAGNOSTIC_V1",
        "benchmark_id": ref["benchmark_id"],
        "model_snapshots": {
            "baseline": baseline["snapshot_sha256"],
            "candidate": candidate["snapshot_sha256"],
        },
        "input_digests": {
            "reference": reference_sha256,
            "candidate": candidate_sha256,
            "baseline": baseline_sha256,
        },
        "domains": domain_results,
        "total_cases": len(cases),
        "candidate_unsafe_outputs": total_unsafe_candidate,
        "baseline_unsafe_outputs": total_unsafe_baseline,
        "regressed_domains": regressions,
        "improved_domains": improved,
        "cross_domain_gate": gate,
        "psychometric_g_estimate": "NOT_ESTIMATED",
        "source_labels_authenticated": False,
        "reference_reviewer_identity_verified": False,
        "training_leakage_independently_ruled_out": False,
        "independent_verification": "NOT_VERIFIED",
        "model_training_executed": False,
        "production_release": "HOLD",
        "financial_authority": "NONE",
        "external_spend_usd": 0,
    }
    return report, gate == "REVIEWABLE_SYNTHETIC_GENERALIZATION_GAIN"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline snapshot comparison; generalization diagnostic, NOT psychometric g"
    )
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        ref, rh = read_json(args.reference)
        cand, ch = read_json(args.candidate)
        base, bh = read_json(args.baseline)
        report, reviewable = score(ref, cand, base, reference_sha256=rh,
                                   candidate_sha256=ch, baseline_sha256=bh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"cross_domain_gate": "HOLD_INVALID_INPUT",
                          "error": str(exc), "production_release": "HOLD"}))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if reviewable else 1


if __name__ == "__main__":
    raise SystemExit(main())
