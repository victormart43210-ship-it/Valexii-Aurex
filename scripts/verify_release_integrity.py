#!/usr/bin/env python3
"""AUREX Permanent Release Integrity Gate Script."""

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# Ensure root repository directory is in sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return res.returncode, res.stdout + res.stderr
    except Exception as exc:
        return 1, str(exc)


def verify_integrity(target_sha: str | None = None) -> dict[str, object]:
    code_sha, git_out = run_cmd(["git", "rev-parse", "HEAD"])
    current_sha = git_out.strip()
    candidate_sha = target_sha or current_sha

    if candidate_sha != current_sha:
        return {
            "candidate_sha": candidate_sha,
            "current_sha": current_sha,
            "status": "HOLD",
            "reason": "Target commit SHA does not match current HEAD SHA",
        }

    # Run Ruff
    code_ruff, out_ruff = run_cmd(["ruff", "check", "."])
    # Run Mypy
    code_mypy, out_mypy = run_cmd(["python3", "-m", "mypy", "aurex", "--strict"])
    # Run Pytest
    code_pytest, out_pytest = run_cmd(["python3", "-m", "pytest"])

    passed = (code_ruff == 0) and (code_mypy == 0) and (code_pytest == 0)
    manifest = {
        "repository": "victormart43210-ship-it/Valexii-Aurex",
        "candidate_sha": candidate_sha,
        "verified_at": datetime.now(UTC).isoformat(),
        "code_checks_pass": passed,
        "ruff_pass": code_ruff == 0,
        "mypy_pass": code_mypy == 0,
        "pytest_pass": code_pytest == 0,
        "status": "ADMIT" if passed else "HOLD",
    }
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
    manifest["digest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
    return manifest


def main() -> None:
    target_sha = sys.argv[1] if len(sys.argv) > 1 else None
    result = verify_integrity(target_sha)
    print(json.dumps(result, indent=2))
    if result["status"] != "ADMIT":
        sys.exit(1)


if __name__ == "__main__":
    main()
