"""Read-only continuity validation; never trusts a recorded SHA as remote HEAD."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

REQUIRED = (
    "RESUME.md",
    "CHECKPOINT.json",
    "PROGRESS_LOG.md",
    "TASK_LEDGER.json",
    "VERIFICATION.json",
    "DEPENDENCY_MAP.md",
)
STATES = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "IMPLEMENTED",
    "TESTED",
    "INDEPENDENTLY_VERIFIED",
    "BLOCKED",
    "DEFERRED",
}
SHA = re.compile(r"[0-9a-f]{40}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    directory = root / "docs/operations/WORK_CONTINUITY"
    for name in REQUIRED:
        if not (directory / name).is_file():
            errors.append(f"missing recovery file: {name}")
    if errors:
        return errors
    if (
        not (directory / "RESUME.md")
        .read_text()
        .startswith("# START HERE — RESUME WITHOUT REPEATING COMPLETED WORK")
    ):
        errors.append("resume entrypoint heading changed")
    try:
        checkpoint = json.loads((directory / "CHECKPOINT.json").read_text())
        ledger = json.loads((directory / "TASK_LEDGER.json").read_text())
        verification = json.loads((directory / "VERIFICATION.json").read_text())
    except (ValueError, OSError) as exc:
        return [f"invalid recovery JSON: {exc}"]
    if not all(isinstance(value, dict) for value in (checkpoint, ledger, verification)):
        return ["recovery JSON roots must be objects"]
    if not isinstance(ledger.get("tasks"), list) or not ledger["tasks"]:
        return ["task ledger requires a nonempty tasks list"]
    if not isinstance(verification.get("records"), list):
        return ["verification requires records list (use empty with NOT_RUN)"]
    fields = {
        "schema_version",
        "operation_id",
        "repository",
        "branch",
        "base_sha",
        "latest_checkpoint_sha",
        "checkpoint_timestamp_utc",
        "active_pr",
        "current_phase",
        "last_completed_task",
        "next_task",
        "completed_tasks",
        "pending_tasks",
        "blockers",
        "changed_files",
        "test_results",
        "independent_review_status",
        "cursor_overlap",
        "production_authority",
        "financial_authority",
    }
    errors.extend(f"missing checkpoint field: {key}" for key in sorted(fields - checkpoint.keys()))
    if (
        checkpoint.get("production_authority") != "HOLD"
        or checkpoint.get("financial_authority") != "NONE"
    ):
        errors.append("authority constraint changed")
    if checkpoint.get("repository") != "https://github.com/victormart43210-ship-it/Valexii-Aurex":
        errors.append("canonical repository mismatch")
    for key in ("base_sha", "latest_checkpoint_sha"):
        value = checkpoint.get(key)
        if value is not None and (not isinstance(value, str) or not SHA.fullmatch(value)):
            errors.append(f"invalid {key}")
    tasks = ledger.get("tasks", [])
    ids = [task.get("task_id") for task in tasks]
    if len(set(ids)) != len(ids):
        errors.append("duplicate task ids")
    graph: dict[str, list[str]] = {}
    for task in tasks:
        identifier = task.get("task_id")
        if not isinstance(identifier, str):
            errors.append("invalid task id")
            continue
        graph[identifier] = task.get("dependencies", [])
        if task.get("status") not in STATES:
            errors.append(f"invalid task status: {identifier}")
        for dep in graph[identifier]:
            if dep not in ids:
                errors.append(f"unknown dependency: {dep}")
        if task.get("status") == "INDEPENDENTLY_VERIFIED" and task.get("verification_status") in (
            "NOT_VERIFIED",
            "REVIEW_PENDING",
            None,
        ):
            errors.append(f"unsubstantiated independent task: {identifier}")
    visited: set[str] = set()

    def visit(node: str, active: set[str]) -> None:
        if node in active:
            errors.append(f"cyclic task dependencies: {node}")
            return
        if node in visited:
            return
        for dep in graph.get(node, []):
            visit(dep, active | {node})
        visited.add(node)

    for identifier in graph:
        visit(identifier, set())
    for key in ("completed_tasks", "pending_tasks"):
        for identifier in checkpoint.get(key, []):
            if identifier not in ids:
                errors.append(f"checkpoint references unknown task: {identifier}")
    for record in verification.get("records", []):
        if record.get("status") == "PASS" and record.get("exit_code") != 0:
            errors.append("PASS record has nonzero or missing exit code")
        location = record.get("evidence_location")
        if record.get("status") == "PASS" and not location:
            errors.append("PASS record requires evidence location")
        if location:
            resolved = (root / location).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                errors.append(f"missing or outside evidence file: {location}")
    return errors


def remote_head(root: Path, branch: str) -> str:
    if not branch or branch.startswith("-") or any(c.isspace() for c in branch):
        raise ValueError("invalid branch")
    output = subprocess.check_output(
        ["git", "ls-remote", "origin", f"refs/heads/{branch}"], cwd=root, text=True, timeout=30
    )
    lines = output.strip().splitlines()
    if len(lines) != 1 or not SHA.fullmatch(lines[0].split()[0]):
        raise ValueError("remote branch missing or ambiguous")
    return lines[0].split()[0]


def check_checkout(root: Path, checkpoint: dict[str, Any], actual: str) -> list[str]:
    """Validate local identity and ancestry after fetching the remote branch."""
    errors = []
    origin = subprocess.check_output(
        ["git", "remote", "get-url", "origin"], cwd=root, text=True
    ).strip()
    if origin.removesuffix(".git") != checkpoint["repository"]:
        return ["origin does not match canonical repository"]
    subprocess.run(
        ["git", "fetch", "--no-tags", "origin", f"refs/heads/{checkpoint['branch']}"],
        cwd=root,
        check=True,
        timeout=60,
        capture_output=True,
    )
    fetched = subprocess.check_output(
        ["git", "rev-parse", "FETCH_HEAD"], cwd=root, text=True
    ).strip()
    if fetched != actual:
        return ["remote advanced during verification; retry readback"]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if head != actual:
        errors.append(
            "local HEAD is not actual remote HEAD; use a clean checkout of the remote branch"
        )
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=root, text=True
    ).strip()
    if branch and branch != checkpoint["branch"]:
        errors.append("local branch differs from recovery branch")
    previous = checkpoint.get("latest_checkpoint_sha")
    if (
        previous is None
        or subprocess.run(
            ["git", "merge-base", "--is-ancestor", previous, actual], cwd=root, capture_output=True
        ).returncode
    ):
        errors.append("recorded checkpoint is not a verified ancestor of remote HEAD")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip():
        errors.append(
            "checkout has uncommitted changes; remote recovery readiness is not established"
        )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check-remote", action="store_true")
    args = parser.parse_args()
    errors = validate(args.root)
    result: dict[str, Any] = {"status": "FAIL" if errors else "PASS", "errors": errors}
    if not errors and args.check_remote:
        checkpoint = json.loads(
            (args.root / "docs/operations/WORK_CONTINUITY/CHECKPOINT.json").read_text()
        )
        actual = remote_head(args.root, checkpoint["branch"])
        errors.extend(check_checkout(args.root, checkpoint, actual))
        result.update(status="FAIL" if errors else "PASS", errors=errors)
        result.update(
            actual_remote_head=actual,
            recorded_preceding_checkpoint=checkpoint["latest_checkpoint_sha"],
            note="Actual remote HEAD is authoritative; a preceding recorded SHA is expected.",
        )
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
