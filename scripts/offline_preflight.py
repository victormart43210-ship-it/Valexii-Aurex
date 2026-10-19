#!/usr/bin/env python3
"""Run AUREX's local pre-merge checks without GitHub Actions.

Read-only with respect to GitHub/Railway. This does not admit or deploy a release.
Stores private logs and SHA-pinned evidence outside the checkout by default.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STEPS: tuple[tuple[str, tuple[str, ...], int], ...] = (
    ("compileall", ("-m", "compileall", "-q", "aurex", "training", "workstation"), 120),
    ("ruff", ("-m", "ruff", "check", "."), 120),
    ("mypy", ("-m", "mypy", "aurex", "--strict"), 240),
    ("pytest", ("-m", "pytest", "-q"), 600),
)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(root), *args), text=True,
        capture_output=True, check=True, timeout=15,
    )
    return result.stdout.strip()


def clean_checkout(root: Path) -> bool:
    """Reject both modified tracked files and untracked non-ignored files."""
    return not git(root, "status", "--porcelain=v1", "--untracked-files=all")


def safe_environment() -> dict[str, str]:
    """Avoid forwarding credentials into arbitrary local repository test code."""
    names = {
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "HF_TOKEN", "HUGGINGFACE_TOKEN",
        "GITHUB_TOKEN", "GH_TOKEN", "GITLAB_TOKEN", "RAILWAY_TOKEN", "RAILWAY_API_TOKEN",
        "DATABASE_URL", "LOVABLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS",
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    }
    env = {
        name: value for name, value in os.environ.items()
        if name not in names and not name.startswith("AUREX_")
    }
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["AUREX_WORKER_DISABLED"] = "1"
    env["AUREX_ENABLE_OFFLINE_LAB"] = "0"
    env["AUREX_ENABLE_RESEARCH_ADVICE"] = "0"
    return env


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def run_check(
    *, label: str, command: list[str], root: Path, output_dir: Path,
    timeout: int, env: dict[str, str],
) -> dict[str, Any]:
    log = output_dir / f"{label}.log"
    start = time.monotonic()
    outcome = "FAIL"
    rc: int | None = None
    with log.open("w", encoding="utf-8") as handle:
        os.chmod(log, 0o600)
        try:
            result = subprocess.run(
                command, cwd=root, env=env, stdout=handle,
                stderr=subprocess.STDOUT, timeout=timeout, check=False,
            )
            rc = result.returncode
            outcome = "PASS" if rc == 0 else "FAIL"
        except subprocess.TimeoutExpired:
            outcome = "TIMEOUT"
        except OSError as exc:
            handle.write(f"Could not start command: {type(exc).__name__}\n")
            outcome = "NOT RUN"
    return {
        "name": label,
        "status": outcome,
        "exit_code": rc,
        "duration_seconds": round(time.monotonic() - start, 3),
        "command": command,
        "log": log.name,
        "log_sha256": file_digest(log),
    }


def result_manifest(
    *, sha: str, tree: str, branch: str,
    steps: list[dict[str, Any]], clean_after: bool, docker_requested: bool,
) -> dict[str, Any]:
    all_pass = all(step["status"] == "PASS" for step in steps)
    return {
        "format": "aurex-local-check-evidence-v1",
        "target_sha": sha,
        "target_tree_sha": tree,
        "checked_branch": branch,
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "python_version": sys.version.split()[0],
        "python312_ci_equivalent": sys.version_info[:2] == (3, 12),
        "clean_checkout_before": True,
        "clean_checkout_after": clean_after,
        "steps": steps,
        "local_checks": "PASS" if all_pass and clean_after else "FAIL",
        "docker_requested": docker_requested,
        "independent_verification": "NOT VERIFIED",
        "github_actions_verification": "NOT VERIFIED",
        "release_authority": "NONE",
        "release_gate": "HOLD",
        "production_deployed": False,
        "note": "LOCAL EVIDENCE ONLY; passing tests cannot self-admit or authorize deployment",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-sha", required=True, help="Exact 40-char Git commit SHA")
    parser.add_argument("--docker-build", action="store_true", help="Opt-in local Docker image build")
    parser.add_argument("--output-dir", type=Path, help="Existing secure directory outside git checkout")
    opts = parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        sha = git(root, "rev-parse", "HEAD")
        tree = git(root, "rev-parse", "HEAD^{tree}")
        branch = git(root, "branch", "--show-current") or "DETACHED"
        if len(opts.expected_sha) != 40 or not all(x in "0123456789abcdef" for x in opts.expected_sha):
            raise ValueError("--expected-sha must be a full lowercase commit SHA")
        if sha != opts.expected_sha:
            raise ValueError(f"commit mismatch; expected {opts.expected_sha}, found {sha}")
        if not clean_checkout(root):
            raise ValueError("working tree is dirty; commit or move changes before measuring")
        if opts.output_dir:
            output = opts.output_dir.resolve()
            if not output.is_dir() or output == root or root in output.parents:
                raise ValueError("--output-dir must exist outside the source checkout")
            if output.stat().st_mode & 0o077:
                raise ValueError("--output-dir must be private (chmod 700)")
        else:
            output = Path(tempfile.mkdtemp(prefix="aurex-preflight-"))
        os.chmod(output, 0o700)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"PRECHECK HOLD: {exc}", file=sys.stderr)
        return 3

    env = safe_environment()
    steps: list[dict[str, Any]] = []
    for label, args, timeout in STEPS:
        command = [sys.executable, *args]
        steps.append(run_check(
            label=label, command=command, root=root,
            output_dir=output, timeout=timeout, env=env,
        ))
    if opts.docker_build:
        steps.append(run_check(
            label="docker-build", command=["docker", "build", "--tag", f"aurex-local:{sha[:12]}", "."],
            root=root, output_dir=output, timeout=900, env=env,
        ))
    clean_after = clean_checkout(root)
    manifest = result_manifest(
        sha=sha, tree=tree, branch=branch, steps=steps,
        clean_after=clean_after, docker_requested=opts.docker_build,
    )
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(manifest_path, 0o600)
    print(f"Checked SHA: {sha}")
    for step in steps:
        print(f"{step['name']}: {step['status']}")
    print(f"Local checks: {manifest['local_checks']}")
    print(f"CUSTOS release: {manifest['release_gate']} (independent verification NOT VERIFIED)")
    print(f"Private evidence directory: {output}")
    return 0 if manifest["local_checks"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
