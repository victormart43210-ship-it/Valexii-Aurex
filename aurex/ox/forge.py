"""Governed model acquisition and promotion. Nothing here downloads or self-approves.

The static registry in ``aurex.ox.registry`` stays a candidate catalog. This ledger
is a separate record of human-reviewed transitions. Training completion is not
deployment approval. QLoRA and GGUF conversion stay NOT_RUN without approved hardware
and a pinned converter.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

STAGES = (
    "DISCOVERED",
    "REVIEWED",
    "ACQUIRED",
    "TRAINED",
    "EVALUATED",
    "APPROVED",
    "STAGING",
)
# The revision was recorded in training/README.md on 2026-10-08. This module does not
# re-fetch the model card, so commercial approval is still an explicit human act.
ALLOWLIST = {
    "Qwen/Qwen2.5-0.5B-Instruct": {
        "revision": "7ae557604adf67be50417f59c2c2f167def9a775",
        "license_name": "Apache-2.0",
        "license_source": "training/README.md; not re-fetched in this process",
        "architecture": "Qwen2ForCausalLM",
        "parameter_count": None,
        "tasks": ["explanation", "structured_output"],
    }
}
DOMAINS = ("xaeli", "dispater", "aurex-ox", "medaurus")
FORBIDDEN_FIELDS = {
    "ssn",
    "password",
    "customer_id",
    "api_key",
    "secret",
    "credential",
    "account_number",
}


class ForgeError(ValueError):
    """The forge request is not admissible."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tasks(known: dict[str, Any] | None) -> list[str]:
    if not known:
        return []
    tasks = known["tasks"]
    if not isinstance(tasks, list) or not all(isinstance(item, str) for item in tasks):
        raise ForgeError("allowlist tasks are malformed")
    return list(tasks)


def _digest(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def discover(repository: str, revision: str) -> dict[str, Any]:
    """Pin a repository. A name is not identity, and discovery does not download."""
    if (
        not isinstance(revision, str)
        or len(revision) != 40
        or not all(character in "0123456789abcdef" for character in revision)
    ):
        raise ForgeError("revision must be a 40-character commit")
    known = ALLOWLIST.get(repository)
    if known and known["revision"] != revision:
        raise ForgeError("revision does not match the pinned allowlist entry")
    return {
        "schema": "aurex.ox.forge.entry.v1",
        "repository": repository,
        "revision": revision,
        "state": "DISCOVERED",
        "allowlisted": known is not None,
        "license_name": known["license_name"] if known else None,
        "license_source": known["license_source"] if known else "UNVERIFIED",
        "architecture": known["architecture"] if known else "UNVERIFIED",
        "parameter_count": known["parameter_count"] if known else None,
        "tasks": _tasks(known),
        "commercial_use": "REVIEW_REQUIRED",
        "redistribution": "REVIEW_REQUIRED",
        "weights_present": False,
        "weight_digests": {},
        "tokenizer_digests": {},
        "training": "NOT_RUN",
        "qlora": "NOT_RUN",
        "gguf_conversion": "NOT_RUN",
        "hardware": "CPU_SMOKE_ONLY" if known else "UNVERIFIED",
        "evaluation_history": [],
        "adapter_lineage": [],
        "deployment_state": "NOT_DEPLOYED",
        "rollback_target": None,
        "financial_authority": "NONE",
        "paid_inference": "OFF",
        "self_approval_allowed": False,
        "history": [{"state": "DISCOVERED", "actor": "registry"}],
    }


def review(
    entry: dict[str, Any],
    *,
    reviewer: str,
    commercial_approved: bool,
    redistribution_approved: bool,
) -> dict[str, Any]:
    if entry.get("state") != "DISCOVERED":
        raise ForgeError("review starts from DISCOVERED")
    if not reviewer.strip() or reviewer == "registry" or reviewer.startswith("model:"):
        raise ForgeError("a person must review the license")
    if not commercial_approved or not redistribution_approved:
        raise ForgeError("commercial use and redistribution need explicit approval")
    if not entry.get("allowlisted"):
        raise ForgeError("an unpinned repository cannot be reviewed for acquisition")
    updated = dict(entry)
    updated["state"] = "REVIEWED"
    updated["commercial_use"] = "APPROVED_BY_REVIEWER"
    updated["redistribution"] = "APPROVED_BY_REVIEWER"
    updated["reviewer"] = reviewer
    updated["history"] = [*entry["history"], {"state": "REVIEWED", "actor": reviewer}]
    return updated


def acquire(
    entry: dict[str, Any],
    source: Path,
    destination: Path,
    manifest: list[dict[str, str]],
    *,
    actor: str,
) -> dict[str, Any]:
    """Copy an already-local artifact set. Remote code and unverified originals are refused."""
    if entry.get("state") != "REVIEWED":
        raise ForgeError("acquisition requires REVIEWED")
    if actor == entry.get("reviewer"):
        raise ForgeError("the reviewer does not acquire their own approval")
    source = Path(source)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    remaining = 0
    for item in manifest:
        name = item["name"]
        if Path(name).name != name or name in {".", ".."}:
            raise ForgeError("artifact name must be a single file")
        origin = source / name
        if origin.is_symlink() or not origin.is_file():
            raise ForgeError("incomplete download")
        expected = item["sha256"]
        if not _digest(expected):
            raise ForgeError("artifact digest is malformed")
        target = destination / name
        if target.exists():
            if target.is_symlink() or _sha256(target) != expected:
                raise ForgeError("refusing to overwrite a verified original")
            continue
        remaining += origin.stat().st_size
    free = shutil.disk_usage(destination).free
    if remaining > free:
        raise ForgeError("insufficient disk space")
    written: dict[str, str] = {}
    for item in manifest:
        name = item["name"]
        target = destination / name
        if not target.exists():
            shutil.copyfile(source / name, target)
            digest = _sha256(target)
            if digest != item["sha256"]:
                target.unlink()
                raise ForgeError("corrupt artifact")
        written[name] = item["sha256"]
    updated = dict(entry)
    updated["state"] = "ACQUIRED"
    updated["weights_present"] = True
    updated["artifacts"] = written
    updated["weight_digests"] = {
        name: digest for name, digest in written.items() if name.endswith(".safetensors")
    }
    updated["tokenizer_digests"] = {
        name: digest for name, digest in written.items() if "tokenizer" in name
    }
    updated["history"] = [*entry["history"], {"state": "ACQUIRED", "actor": actor}]
    return updated


def advance(
    entry: dict[str, Any],
    to_state: str,
    *,
    actor: str,
    reviewer: str | None = None,
    rollback_target: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Move one stage. The actor cannot approve or stage their own model."""
    if to_state not in STAGES:
        raise ForgeError("unknown stage")
    current = STAGES.index(str(entry.get("state")))
    target = STAGES.index(to_state)
    if target != current + 1:
        raise ForgeError("stages cannot be skipped or reversed here")
    if not actor.strip() or actor.startswith("model:"):
        raise ForgeError("a model cannot promote itself")
    if to_state in {"APPROVED", "STAGING"}:
        if not reviewer or reviewer == actor:
            raise ForgeError("approval requires a different reviewer")
    if to_state == "STAGING":
        if rollback_target is None or len(rollback_target) != 40:
            raise ForgeError("staging requires a rollback revision")
    updated = dict(entry)
    if to_state == "TRAINED":
        updated["training"] = "RECORDED_NOT_A_DEPLOYMENT"
        updated["adapter_lineage"] = [
            *entry.get("adapter_lineage", []),
            {"kind": "lora", "base_revision": entry.get("revision")},
        ]
    if to_state == "EVALUATED":
        if not evidence or evidence.get("judge") != "external_key":
            raise ForgeError("evaluation requires an external answer key")
        if evidence.get("authored_by") == "candidate_model":
            raise ForgeError("the candidate model cannot certify itself")
        if evidence.get("status") not in {"EVALUATED", "REJECTED"}:
            raise ForgeError("evaluation evidence has no admission")
        if evidence.get("deployment_approval") not in {None, "NOT_APPROVED"}:
            raise ForgeError("an evaluation cannot approve deployment")
        updated["admission"] = evidence["status"]
        updated["evaluation_history"] = [
            *entry.get("evaluation_history", []),
            {
                "actor": actor,
                "judge": "external_key",
                "status": evidence["status"],
                "independent_verification": "NOT VERIFIED",
            },
        ]
    if to_state == "APPROVED":
        if entry.get("admission") == "REJECTED":
            raise ForgeError("a rejected evaluation cannot be approved")
        if (
            not evidence
            or evidence.get("judge") != "external_key"
            or evidence.get("status") != "EVALUATED"
        ):
            raise ForgeError("approval requires an external evaluation")
    if to_state == "STAGING":
        updated["rollback_target"] = rollback_target
        updated["deployment_state"] = "STAGING_NOT_PRODUCTION"
    updated["state"] = to_state
    updated["history"] = [
        *entry["history"],
        {"state": to_state, "actor": actor, "reviewer": reviewer},
    ]
    updated["financial_authority"] = "NONE"
    updated["paid_inference"] = "OFF"
    updated["self_approval_allowed"] = False
    return updated


def _accepted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    clean: list[dict[str, Any]] = []
    for row in rows:
        if row.get("synthetic") is not True:
            raise ForgeError("synthetic examples must be marked synthetic")
        if row.get("domain") not in DOMAINS:
            raise ForgeError("unknown dataset domain")
        if FORBIDDEN_FIELDS.intersection(row) or "held_out_answer" in row:
            raise ForgeError("customer or secret fields are not training data")
        blob = json.dumps(row).lower()
        if "hle:3r2s:" in blob or "bearer " in blob:
            raise ForgeError("hidden evaluation or secret material")
        prompt = str(row.get("prompt", "")).strip()
        answer = str(row.get("answer", "")).strip()
        if not prompt or not answer or prompt in seen:
            raise ForgeError("empty or duplicate prompt")
        seen.add(prompt)
        clean.append(row)
    return clean


def _write_messages(
    output: Path, train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    output = Path(output)
    if output.exists():
        raise ForgeError("dataset output must be a new directory")
    if not train_rows or not eval_rows:
        raise ForgeError("train and eval must both be nonempty")
    output.mkdir(parents=True)
    for name, group in (("train.jsonl", train_rows), ("eval.jsonl", eval_rows)):
        lines = [
            json.dumps(
                {
                    "messages": [
                        {"role": "user", "content": item["prompt"]},
                        {"role": "assistant", "content": item["answer"]},
                    ]
                }
            )
            for item in group
        ]
        (output / name).write_text("\n".join(lines) + "\n")
    provenance = {
        "source": "aurex synthetic forge examples",
        "license": "synthetic-internal",
        "author": "aurex-ox-forge",
        "benchmark_data": False,
        "synthetic": True,
        "customer_data": False,
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2))
    return {"counts": {"train": len(train_rows), "eval": len(eval_rows)}, "synthetic": True}


def prepare_synthetic(rows: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    """Write a messages dataset. Every row must already say it is synthetic."""
    clean = _accepted_rows(rows)
    if len(clean) < 2:
        raise ForgeError("a train and eval split needs at least two examples")
    return _write_messages(output, clean[1:], clean[:1])


def prepare_domain_pack(rows: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    """One held-out example per domain. The eval prompts are not in the train file."""
    clean = _accepted_rows(rows)
    grouped: dict[str, list[dict[str, Any]]] = {domain: [] for domain in DOMAINS}
    for row in clean:
        grouped[str(row["domain"])].append(row)
    eval_rows: list[dict[str, Any]] = []
    train_rows: list[dict[str, Any]] = []
    for domain in DOMAINS:
        items = grouped[domain]
        if len(items) < 2:
            raise ForgeError("each domain needs a train example and a separate eval example")
        eval_rows.append(items[0])
        train_rows.extend(items[1:])
    report = _write_messages(output, train_rows, eval_rows)
    report["domains"] = list(DOMAINS)
    return report


def compare_adapter(
    baseline: dict[str, float],
    adapter: dict[str, float],
    *,
    security_failures_baseline: int,
    security_failures_adapter: int,
) -> dict[str, Any]:
    """Score an external key. The model under test is not the judge."""
    if set(baseline) != set(adapter) or not baseline:
        raise ForgeError("baseline and adapter must share the same tasks")
    if security_failures_adapter > security_failures_baseline:
        return {
            "status": "FAIL",
            "reason": "security regressions reject the adapter",
            "judge": "external_key",
            "promoted": False,
        }
    deltas = {task: adapter[task] - baseline[task] for task in baseline}
    return {
        "status": "PASS",
        "deltas": deltas,
        "judge": "external_key",
        "promoted": False,
        "independent_verification": "NOT VERIFIED",
    }


def select_model(task: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Choose an approved entry. Agreement between models is not proof."""
    eligible = [
        entry
        for entry in entries
        if entry.get("state") in {"APPROVED", "STAGING"} and task in entry.get("tasks", [])
    ]
    if not eligible:
        return {
            "selected": None,
            "reason": "no approved model for this task",
            "disagreement": False,
        }
    eligible.sort(key=lambda entry: int(entry.get("latency_ms", 10**9)))
    answers = {entry["repository"]: entry.get("answer") for entry in eligible if "answer" in entry}
    disagreement = len(set(answers.values())) > 1
    return {
        "selected": eligible[0]["repository"],
        "disagreement": disagreement,
        "answers": answers,
        "proof": False,
        "financial_authority": "NONE",
    }


def hardware_preflight() -> dict[str, str]:
    """Report the machine. Do not start a paid or full-size job."""
    import importlib.util

    cuda = False
    try:
        import torch

        cuda = bool(torch.cuda.is_available())
    except ImportError:
        cuda = False
    bitsandbytes = importlib.util.find_spec("bitsandbytes") is not None
    qlora = "NOT_RUN"
    if cuda and bitsandbytes:
        qlora = "READY_NOT_EXECUTED"
    return {
        "cuda": "PRESENT" if cuda else "ABSENT",
        "bitsandbytes": "PRESENT" if bitsandbytes else "ABSENT",
        "qlora": qlora,
        "full_qwen_training": "NOT_RUN",
        "gguf_conversion": "NOT_RUN",
        "paid_gpu": "NOT_REQUESTED",
    }


def acquire_from_manifest(
    manifest: dict[str, Any], source: Path, destination: Path
) -> dict[str, Any]:
    """Acquire a local tree described by a manifest. Remote code stays off."""
    if manifest.get("trust_remote_code") is not False:
        raise ForgeError("remote code execution is rejected")
    entry = discover(str(manifest["repository"]), str(manifest["revision"]))
    entry = review(
        entry,
        reviewer=str(manifest["reviewer"]),
        commercial_approved=manifest.get("commercial_use_approved") is True,
        redistribution_approved=manifest.get("redistribution_approved") is True,
    )
    acquired = acquire(
        entry,
        source,
        destination,
        list(manifest["files"]),
        actor=str(manifest["actor"]),
    )
    record = {
        "schema": "aurex.ox.forge.provenance.v1",
        "entry": acquired,
        "trust_remote_code": False,
        "independent_verification": "NOT VERIFIED",
    }
    (Path(destination) / "provenance.json").write_text(json.dumps(record, indent=2) + "\n")
    return acquired


def save_ledger(path: Path, entries: list[dict[str, Any]]) -> None:
    path = Path(path)
    if ".git" in path.parts:
        raise ForgeError("the ledger is not a git object")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema": "aurex.ox.forge.ledger.v1", "entries": entries}, indent=2) + "\n"
    )


def load_ledger(path: Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    if data.get("schema") != "aurex.ox.forge.ledger.v1" or not isinstance(
        data.get("entries"), list
    ):
        raise ForgeError("ledger schema mismatch")
    return list(data["entries"])


def serving_gate(entry: dict[str, Any], requested_model: str) -> dict[str, Any]:
    """Allow an existing adapter to serve only an approved ledger identity."""
    if entry.get("state") not in {"APPROVED", "STAGING"}:
        raise ForgeError("an unapproved model cannot be served")
    identity = entry.get("serving_id") or entry.get("repository")
    if identity != requested_model:
        raise ForgeError("model identity does not match the ledger")
    if entry.get("financial_authority") != "NONE" or entry.get("paid_inference") != "OFF":
        raise ForgeError("model output has no authority and paid inference stays off")
    return {
        "route": "existing-llama-cpp-adapter",
        "model": requested_model,
        "promoted_by_model": False,
        "financial_authority": "NONE",
    }


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="aurex.ox.forge")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    acquire_cmd = sub.add_parser("acquire")
    acquire_cmd.add_argument("--manifest", type=Path, required=True)
    acquire_cmd.add_argument("--source", type=Path, required=True)
    acquire_cmd.add_argument("--dest", type=Path, required=True)
    acquire_cmd.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        print(json.dumps(hardware_preflight(), indent=2))
        return
    manifest = json.loads(args.manifest.read_text())
    acquired = acquire_from_manifest(manifest, args.source, args.dest)
    entries = load_ledger(args.ledger)
    entries.append(acquired)
    save_ledger(args.ledger, entries)
    print(json.dumps({"status": "ACQUIRED", "state": acquired["state"]}, indent=2))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
