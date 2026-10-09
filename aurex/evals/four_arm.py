"""Reference-separated generation and deterministic offline scoring for four arms."""

import json
import math
import time
from datetime import datetime
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from aurex.adapters.execution import InferenceClient
from aurex.evals.governance import Claim, Qualification, Witness, qualify
from aurex.provenance import fingerprint


class PromptItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    item_id: str = Field(min_length=1)
    prompt: str = Field(min_length=1)


def parse_claim(text: str | None) -> Claim:
    if text is None:
        return Claim(answer="", status="HOLD")
    try:
        return Claim.model_validate(json.loads(text))
    except (ValueError, ValidationError):
        return Claim(answer=text, status="NOT VERIFIED")


def run_four_arms(
    items: list[PromptItem],
    base: InferenceClient,
    tuned: InferenceClient | None,
    witnesses: dict[str, tuple[Witness, ...]],
    keys: dict[str, Ed25519PublicKey],
    now: datetime,
) -> dict[str, Any]:
    ids = [i.item_id for i in items]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("Empty or duplicate evaluation items")
    # Paired replay holds inference identical within A/B and C/D; only qualification differs.
    # This is an explicitly named ablation, not a multi-step answer-repair experiment.
    arms: dict[str, Any] = {}
    for raw_arm, qualified_arm, client in [("A", "B", base), ("C", "D", tuned)]:
        if client is None:
            for arm in (raw_arm, qualified_arm):
                arms[arm] = {"status": "NOT RUN", "rows": []}
            continue
        rows: list[dict[str, Any]] = []
        qualified: list[dict[str, Any]] = []
        for item in items:
            record = client.run(item.item_id, item.prompt)
            claim = parse_claim(record.output)
            qualification_clock = time.perf_counter()
            q = qualify(
                claim, witnesses.get(item.item_id, ()), keys, now, fingerprint(item.model_dump())
            )
            if record.status != "PASS":
                q = Qualification(status="HOLD", reason="Inference failed")
            row = {
                "item_id": item.item_id,
                "inference": record.model_dump(mode="json"),
                "answer": claim.answer,
                "decision": claim.status,
            }
            rows.append(row)
            qualified.append(
                {
                    **row,
                    "decision": q.status,
                    "answer": claim.answer if q.status == "PASS" else "",
                    "qualification": q.model_dump(mode="json"),
                    "qualification_seconds": time.perf_counter() - qualification_clock,
                }
            )
        status = "PASS" if all(r["inference"]["status"] == "PASS" for r in rows) else "HOLD"
        arms[raw_arm] = {"status": status, "config_sha256": client.config_digest(), "rows": rows}
        arms[qualified_arm] = {
            "status": status,
            "config_sha256": client.config_digest(),
            "rows": qualified,
        }
    body = {
        "schema_version": 1,
        "kind": "ORIGINAL_EVALUATION_NOT_HLE",
        "ablation": "paired-output qualification; no answer regeneration",
        "item_ids": ids,
        "prompts_sha256": fingerprint([i.model_dump() for i in items]),
        "witnesses_sha256": fingerprint(
            {k: [w.model_dump(mode="json") for w in v] for k, v in witnesses.items()}
        ),
        "qualification_time": now.isoformat(),
        "arms": arms,
    }
    return {**body, "run_sha256": fingerprint(body)}


def score_run(run: dict[str, Any], references: dict[str, dict[str, str]]) -> dict[str, Any]:
    body = {k: v for k, v in run.items() if k != "run_sha256"}
    if fingerprint(body) != run.get("run_sha256"):
        raise ValueError("Prediction artifact digest mismatch")
    arms = run.get("arms", {})
    if set(arms) != set("ABCD"):
        raise ValueError("All four arm slots are required")
    if any(a.get("status") not in {"PASS", "HOLD", "NOT RUN"} for a in arms.values()):
        raise ValueError("Invalid execution status")
    if any(arms[a]["status"] == "NOT RUN" for a in "AB"):
        raise ValueError("Baseline and qualified baseline must execute before scoring")
    if (arms["C"]["status"] == "NOT RUN") != (arms["D"]["status"] == "NOT RUN"):
        raise ValueError("Fine-tuned arms must be paired")
    for raw, qualified in (("A", "B"), ("C", "D")):
        if arms[raw]["status"] != arms[qualified]["status"]:
            raise ValueError("Paired execution status mismatch")
        if arms[raw].get("config_sha256") != arms[qualified].get("config_sha256"):
            raise ValueError("Paired model configuration mismatch")
    ids = run["item_ids"]
    if not ids or len(set(ids)) != len(ids) or set(ids) != set(references):
        raise ValueError("References must match the frozen unique item set")
    for ref in references.values():
        if set(ref) != {"answer", "status"} or ref["status"] not in (
            "PASS",
            "FAIL",
            "HOLD",
            "NOT RUN",
            "NOT VERIFIED",
        ):
            raise ValueError("Invalid reference schema")
    reports: dict[str, Any] = {}
    correctness: dict[str, list[bool]] = {}
    for name, arm in run["arms"].items():
        if arm["status"] == "NOT RUN":
            if arm.get("rows") != []:
                raise ValueError("Unexecuted arm must not contain outcomes")
            reports[name] = {"status": "NOT RUN"}
            continue
        rows = arm["rows"]
        if len(rows) != len(ids) or [r["item_id"] for r in rows] != ids:
            raise ValueError("Incomplete, reordered or duplicate outcomes")
        for index, row in enumerate(rows):
            if row["inference"]["status"] not in {"PASS", "FAIL"}:
                raise ValueError("Invalid inference status")
            if name in "BD":
                original = arms["A" if name == "B" else "C"]["rows"][index]
                if row["inference"] != original["inference"]:
                    raise ValueError("Paired replay inference mismatch")
                if row["decision"] != row.get("qualification", {}).get("status"):
                    raise ValueError("Qualification decision mismatch")
                if row["decision"] == "PASS" and row["answer"] != original["answer"]:
                    raise ValueError("Qualification must not rewrite the answer")
        good = [
            r["inference"]["status"] == "PASS"
            and r["answer"].strip() == references[r["item_id"]]["answer"].strip()
            for r in rows
        ]
        correctness[name] = good
        false_pass = sum(
            r["decision"] == "PASS" and (not ok or references[r["item_id"]]["status"] != "PASS")
            for r, ok in zip(rows, good, strict=True)
        )
        pass_calls = sum(r["decision"] == "PASS" for r in rows)
        errors = sum(r["inference"]["status"] != "PASS" for r in rows)
        holds = [r for r in rows if r["decision"] in ("HOLD", "NOT VERIFIED")]
        usage = [r["inference"]["output_tokens"] for r in rows]
        reports[name] = {
            "status": "HOLD" if errors else "PASS",
            "n": len(ids),
            "accuracy": sum(good) / len(ids),
            "correct": sum(good),
            "inference_errors": errors,
            "false_pass_count": false_pass,
            "false_pass_rate_among_pass": false_pass / pass_calls if pass_calls else None,
            "false_fail_count": sum(
                r["decision"] == "FAIL" and references[r["item_id"]]["status"] == "PASS"
                for r in rows
            ),
            "abstentions": len(holds),
            "appropriate_abstentions": sum(
                references[r["item_id"]]["status"] in ("HOLD", "NOT VERIFIED") for r in holds
            ),
            "traceable_pass_count": sum(
                r.get("qualification", {}).get("status") == "PASS" for r in rows
            ),
            "latency_seconds": sum(
                r["inference"]["elapsed_seconds"] + r.get("qualification_seconds", 0.0)
                for r in rows
            ),
            "output_tokens": sum(usage) if all(x is not None for x in usage) else None,
            "cost_usd": None,
        }
    paired: dict[str, Any] = {}
    for a, b in [("A", "B"), ("C", "D")]:
        if a not in correctness or b not in correctness:
            continue
        improved = sum(not x and y for x, y in zip(correctness[a], correctness[b], strict=True))
        regressed = sum(x and not y for x, y in zip(correctness[a], correctness[b], strict=True))
        n = improved + regressed
        p = (
            min(1.0, 2 * sum(math.comb(n, k) for k in range(min(improved, regressed) + 1)) / 2**n)
            if n
            else 1.0
        )
        base = reports[a]["accuracy"]
        delta = reports[b]["accuracy"] - base
        paired[a + b] = {
            "improved": improved,
            "regressed": regressed,
            "percentage_point_delta": 100 * delta,
            "relative_uplift": delta / base if base else None,
            "exact_mcnemar_p": p,
        }
    return {
        "status": "HOLD" if any(v["status"] == "HOLD" for v in reports.values()) else "PASS",
        "kind": "DETERMINISTIC_FIXTURE_SCORING_NOT_HLE",
        "arms": reports,
        "paired": paired,
        "run_sha256": run["run_sha256"],
        "reference_sha256": fingerprint(references),
        "independent_review": "NOT VERIFIED",
        "uncertainty": "Small original fixtures do not establish general efficacy",
    }
