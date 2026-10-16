#!/usr/bin/env python3
"""Read-only Chromebook & AUREX Environment Alignment Utility."""

import json
import os
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def run_cmd(cmd: list[str]) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return res.stdout.strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def check_port(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def generate_alignment_report() -> dict[str, object]:
    cwd = os.getcwd()
    repo_origin = run_cmd(["git", "remote", "get-url", "origin"])
    active_branch = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    head_sha = run_cmd(["git", "rev-parse", "HEAD"])
    git_status = run_cmd(["git", "status", "--porcelain"])

    required_files = [
        "aurex/api.py",
        "aurex/database.py",
        "aurex/offline_lab.py",
        "aurex/scientific_evidence.py",
        "aurex/sovereign_studio.py",
        "scripts/verify_release_integrity.py",
    ]
    file_checks = {f: Path(f).exists() for f in required_files}

    ports_to_check = [8000, 8080, 3000, 5173]
    port_status = {p: check_port(p) for p in ports_to_check}

    report = {
        "alignment_timestamp": datetime.now(UTC).isoformat(),
        "repository_path": cwd,
        "remote_origin": repo_origin,
        "active_branch": active_branch,
        "head_commit": head_sha,
        "uncommitted_changes": bool(git_status),
        "python_version": sys.version,
        "file_checks": file_checks,
        "active_ports": port_status,
        "status": "ALIGNED" if all(file_checks.values()) else "DEGRADED",
    }
    return report


def main() -> None:
    report = generate_alignment_report()
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2))
    else:
        print("=== AUREX Chromebook Alignment Summary ===")
        print(f"Path: {report['repository_path']}")
        print(f"Branch: {report['active_branch']}")
        print(f"HEAD SHA: {report['head_commit']}")
        print(f"Status: {report['status']}")
        print(f"Files Present: {sum(report['file_checks'].values())}/{len(report['file_checks'])}")


if __name__ == "__main__":
    main()
