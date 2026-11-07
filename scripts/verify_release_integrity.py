#!/usr/bin/env python3
"""Fail-closed verification of a remote Git release candidate (stdlib only)."""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)

def verify(remote, branch):
    if not re.fullmatch(r"[A-Za-z0-9._/-]+", branch) or branch.startswith("-") or ".." in branch or "@{" in branch:
        raise ValueError("Invalid branch")
    ref = "refs/heads/" + branch
    before = git("ls-remote", "--exit-code", remote, ref)
    if before.returncode or len(before.stdout.splitlines()) != 1:
        raise RuntimeError("Remote branch missing or ambiguous")
    fields = before.stdout.strip().split()
    if len(fields) != 2 or fields[1] != ref or not SHA.fullmatch(fields[0]):
        raise RuntimeError("Malformed remote ref")
    sha = fields[0]
    fetched = git("fetch", "--no-tags", remote, ref)
    if fetched.returncode:
        raise RuntimeError("Fetch failed: " + fetched.stderr[-400:])
    resolved = git("rev-parse", "--verify", "FETCH_HEAD^{commit}")
    if resolved.returncode or resolved.stdout.strip() != sha:
        raise RuntimeError("Fetched commit differs from pinned remote HEAD")
    after = git("ls-remote", "--exit-code", remote, ref)
    if after.returncode or after.stdout.strip().split()[0] != sha:
        raise RuntimeError("Remote branch moved during verification")
    return sha

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--remote", default="origin")
    p.add_argument("--branch", required=True)
    p.add_argument("--output", default="release-integrity.json")
    args = p.parse_args()
    report = {"schema": 1, "branch": args.branch, "remote": args.remote,
              "checked_at": datetime.now(timezone.utc).isoformat(),
              "status": "HOLD", "sha": None, "reason": None}
    try:
        report["sha"] = verify(args.remote, args.branch)
        report["status"] = "IDENTITY_VERIFIED"
        report["reason"] = "Commit identity only; tests and release admission NOT VERIFIED"
    except (ValueError, RuntimeError, IndexError) as exc:
        report["reason"] = str(exc)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "IDENTITY_VERIFIED" else 1

if __name__ == "__main__":
    sys.exit(main())
