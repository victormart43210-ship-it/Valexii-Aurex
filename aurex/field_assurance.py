"""Original, offline and non-authoritative AUREX Field Audit beta assurance gate.

International guidance informs the control catalogue but does not define the
legal duties of a Texas oilfield business. This tool checks review *claims*
and metadata, never authenticates a witness or certifies compliance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, NamedTuple

SCHEMA = "aurex.field-assurance.claims.v1"
PROFILE_SCHEMA = "aurex.field-assurance.profile.v1"
MAX_BYTES = 128 * 1024
MAX_AGE_DAYS = 30
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")
_GIT_SHA = re.compile(r"[a-f0-9]{40}\Z")
_REVIEWER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{2,63}\Z")
_ALLOWED = {"PASS", "FAIL", "HOLD", "NOT_RUN"}


class Control(NamedTuple):
    id: str
    region: str
    objective: str
    provenance: str


# Original AUREX control selection, informed by the cited sources.
# No external source text or other repository code is copied.
CONTROLS: tuple[Control, ...] = (
    Control("record_provenance", "London / UK FRC", "Pin document and audit-rule versions before reconciliation", "https://www.frc.org.uk/library/standards-codes-policy/audit-assurance-and-ethics/guidance/ai-in-audit/"),
    Control("human_override_trace", "London / UK ICO", "Record meaningful independent human review and override reasons", "https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/artificial-intelligence/human-review/"),
    Control("privacy_processing_scope", "London / UK ICO", "Review lawful purpose, retention, processor access and consent boundaries", "https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/artificial-intelligence/governance-and-accountability-in-ai/"),
    Control("synthetic_sandbox_first", "London / UK FCA", "Validate with bounded synthetic cases before any live pilot", "https://www.fca.org.uk/firms/innovation/ai-lab"),
    Control("independent_eval_replay", "London / UK AISI", "Use reproducible independent evaluator and negative test cases", "https://inspect.aisi.org.uk/"),
    Control("third_party_dependency_inventory", "NYC / NYDFS design reference", "List API/model vendors, data flows and concentration risks", "https://www.dfs.ny.gov/industry_guidance/industry_letters/il20260910-cyber-risk-assessment"),
    Control("least_privilege_tool_access", "NYC / NYDFS design reference", "Keep service credentials off client and enforce scoped tool rights", "https://www.dfs.ny.gov/industry-guidance/industry-letters/il20241016-cyber-risks-ai-and-strategies-combat-related-risks"),
    Control("change_triggered_risk_review", "NYC / NYDFS design reference", "Reevaluate risks when models, tools, vendors or scopes change", "https://www.dfs.ny.gov/industry_guidance/industry_letters/il20260910-cyber-risk-assessment"),
    Control("resume_requires_authority", "Global / LangGraph", "Recheck authorization and idempotency after checkpoint resume", "https://docs.langchain.com/oss/python/langgraph/interrupts"),
    Control("unauthorized_action_adversarial", "Global / OWASP", "Test prompt injection, tool misuse and action boundary crossings", "https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/"),
    Control("agent_path_monitoring", "Singapore / IMDA", "Test full agent paths, tool calls, approvals and ongoing regression", "https://www.imda.gov.sg/about-imda/emerging-technologies-and-research/artificial-intelligence"),
    Control("zero_spend_no_side_effect", "AUREX / Internal", "Reject billable work and irreversible effects without fresh scoped permission", "https://github.com/victormart43210-ship-it/Valexii-Aurex/blob/main/AGENTS.md"),
)
_IDS = frozenset(c.id for c in CONTROLS)


def _canonical(v: object) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def profile() -> dict[str, Any]:
    item: dict[str, Any] = {"schema": PROFILE_SCHEMA, "guidance_not_certification": True,
                            "controls": [c._asdict() for c in CONTROLS]}
    item["profile_sha256"] = hashlib.sha256(_canonical(item)).hexdigest()
    return item


def blank_claims(source_sha: str = "0" * 40) -> dict[str, Any]:
    return {
        "schema": SCHEMA, "synthetic": True,
        "profile_sha256": profile()["profile_sha256"], "source_sha": source_sha,
        "claims": [{"id": c.id, "status": "NOT_RUN", "evidence_sha256": None,
                    "observed_at": None, "implementer_id": None, "reviewer_id": None}
                   for c in CONTROLS],
    }


def _date(value: object) -> datetime | None:
    if not isinstance(value, str) or not value or len(value) > 40:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(UTC)


def assess(claimed: dict[str, Any], *, now: datetime | None = None) -> tuple[dict[str, Any], bool]:
    """Fail closed on invalid review metadata; never attest genuine compliance."""
    if not isinstance(claimed, dict) or set(claimed) != {
        "schema", "synthetic", "profile_sha256", "source_sha", "claims"
    }:
        raise ValueError("invalid claim manifest keys")
    if (claimed["schema"] != SCHEMA or claimed["synthetic"] is not True
            or claimed["profile_sha256"] != profile()["profile_sha256"]
            or not isinstance(claimed["source_sha"], str)
            or _GIT_SHA.fullmatch(claimed["source_sha"]) is None
            or not isinstance(claimed["claims"], list)
            or len(claimed["claims"]) > len(CONTROLS)):
        raise ValueError("schema, profile SHA, source SHA, synthetic flag, or claim count invalid")
    clock = now or datetime.now(UTC)
    if clock.tzinfo is None:
        raise ValueError("reference clock must have timezone")
    clock = clock.astimezone(UTC)
    seen: set[str] = set()
    incomplete: set[str] = set()
    failed: set[str] = set()
    for row in claimed["claims"]:
        if (not isinstance(row, dict) or set(row) != {
            "id", "status", "evidence_sha256", "observed_at", "implementer_id", "reviewer_id"
        }):
            raise ValueError("unrecognized claim fields")
        cid, status = row["id"], row["status"]
        if not isinstance(cid, str) or cid not in _IDS or cid in seen:
            raise ValueError("unknown or duplicate control ID")
        seen.add(cid)
        if not isinstance(status, str) or status not in _ALLOWED:
            raise ValueError("invalid claimed status")
        if status == "FAIL":
            failed.add(cid)
        if status != "PASS":
            incomplete.add(cid)
            if any(row[key] is not None for key in (
                "evidence_sha256", "observed_at", "implementer_id", "reviewer_id"
            )):
                raise ValueError("only PASS claims may carry evidence metadata")
            continue
        evidence = row["evidence_sha256"]
        reviewer = row["reviewer_id"]
        implementer = row["implementer_id"]
        observed = _date(row["observed_at"])
        if (not isinstance(evidence, str) or _SHA256.fullmatch(evidence) is None
                or evidence == "0" * 64 or not isinstance(reviewer, str)
                or not isinstance(implementer, str)
                or _REVIEWER.fullmatch(reviewer) is None
                or _REVIEWER.fullmatch(implementer) is None
                or reviewer == implementer or observed is None
                or observed > clock + timedelta(minutes=1)
                or clock - observed > timedelta(days=MAX_AGE_DAYS)):
            incomplete.add(cid)
    missing = sorted(_IDS - seen)
    complete_claims = len(CONTROLS) - len(incomplete) - len(missing)
    source_commit_recorded = claimed["source_sha"] != "0" * 40
    claims_structurally_complete = not incomplete and not missing and source_commit_recorded
    report = {
        "kind": "AUREX_FIELD_ASSURANCE_REVIEW", "profile_sha256": profile()["profile_sha256"],
        "source_sha": claimed["source_sha"], "source_commit_recorded": source_commit_recorded,
        "control_count": len(CONTROLS),
        "structurally_complete_claims": complete_claims,
        "missing_controls": missing, "unsubstantiated_or_pending_controls": sorted(incomplete),
        "reported_failed_controls": sorted(failed),
        "claim_consistency": "REVIEWABLE_CLAIMS_NOT_ATTESTED" if claims_structurally_complete else "HOLD",
        "reviewer_identity_verified": False, "independent_verification": "NOT_VERIFIED",
        "compliance_certification": "NONE", "real_customer_documents": "NOT_AUTHORIZED",
        "audit_opinion": "NONE", "spend_authority": "NONE", "production_release": "HOLD",
        "source_metadata_trusted": False,
    }
    return report, claims_structurally_complete


def _reject_dupes(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for key, value in pairs:
        if key in parsed:
            raise ValueError("duplicate JSON key")
        parsed[key] = value
    return parsed


def _reject_constants(value: str) -> None:
    raise ValueError("nonfinite JSON number")


def read_claims(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("regular non-symlink claim manifest required")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("claim manifest too large")
    try:
        content = json.loads(path.read_bytes().decode("utf-8", errors="strict"),
                             object_pairs_hook=_reject_dupes, parse_constant=_reject_constants)
    except (UnicodeError, ValueError) as exc:
        raise ValueError("malformed UTF-8 JSON claim manifest") from exc
    if not isinstance(content, dict):
        raise ValueError("claim manifest must be JSON object")
    return content


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description="Offline AUREX international audit-assurance beta gate, never certifies")
    group = cli.add_mutually_exclusive_group(required=True)
    group.add_argument("--profile", action="store_true", help="print sourced original AUREX control catalogue")
    group.add_argument("--template", action="store_true", help="print synthetic-only claim manifest template")
    group.add_argument("--assess", type=Path, help="check external metadata; never certify evidence")
    args = cli.parse_args(argv)
    if args.profile:
        print(json.dumps(profile(), sort_keys=True, indent=2))
        return 0
    if args.template:
        print(json.dumps(blank_claims(), sort_keys=True, indent=2))
        return 0
    try:
        report, complete = assess(read_claims(args.assess))
    except (OSError, ValueError) as exc:
        print(json.dumps({"claim_consistency": "HOLD", "error": str(exc), "production_release": "HOLD"}))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
