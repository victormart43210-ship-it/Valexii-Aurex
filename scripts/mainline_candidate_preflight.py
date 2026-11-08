#!/usr/bin/env python3
"""Read-only, fail-closed mainline candidate preflight. No merge or deployment."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

CANDIDATES = {
    "forge_211": "e3244e7ae6304b1f4aecf82f70f6400decb3af91",
    "auseklis_dispater_212": "ad6a93201516a0ec9168f95128f396d38e39f158",
    "document_manuscript_214": "1eebb543b8d79b2effe45778d1885800a061f12e",
    "genesis_design_216": "de76be258231381db2504d204a3e1a136f5e6980",
}
EXPECTED_BASE = "fc2bed4dd98054503254ad1a4c11fbecd7b0deca"

def git(*args: str) -> str:
    p = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if p.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()[:400]}")
    return p.stdout.strip()

def main() -> int:
    report: dict = {"schema": "aurex.mainline.preflight.v1", "authority": "NONE",
                    "production": "HOLD", "integration_verified": False,
                    "candidates": {}, "overlaps": {}, "blockers": []}
    try:
        root = Path(git("rev-parse", "--show-toplevel"))
        if Path.cwd().resolve() != root.resolve():
            print(f"Repository root: {root}", file=sys.stderr)
        report["working_tree_clean"] = not bool(git("status", "--porcelain"))
        report["local_head"] = git("rev-parse", "HEAD")
        report["base_present"] = bool(git("cat-file", "-t", EXPECTED_BASE) == "commit")
        if not report["working_tree_clean"]:
            report["blockers"].append("DIRTY_WORKTREE")
        file_owners: dict[str, list[str]] = {}
        for name, sha in CANDIDATES.items():
            try:
                git("cat-file", "-e", sha + "^{commit}")
                ancestor = git("merge-base", EXPECTED_BASE, sha)
                files = git("diff", "--name-only", EXPECTED_BASE, sha).splitlines()
                report["candidates"][name] = {
                    "sha": sha, "merge_base": ancestor,
                    "same_base": ancestor == EXPECTED_BASE,
                    "changed_files": files,
                    "tests_on_combined_tree": "NOT_RUN",
                }
                if ancestor != EXPECTED_BASE:
                    report["blockers"].append("UNEXPECTED_ANCESTRY:" + name)
                for path in files:
                    file_owners.setdefault(path, []).append(name)
            except RuntimeError as e:
                report["candidates"][name] = {"sha": sha, "status": "UNAVAILABLE", "error": str(e)}
                report["blockers"].append("MISSING_CANDIDATE:" + name)
        report["overlaps"] = {p: owners for p, owners in file_owners.items() if len(owners) > 1}
        if report["overlaps"]:
            report["blockers"].append("OVERLAPPING_FILES_REQUIRE_RECONCILIATION")
        report["blockers"].extend(["MODEL_FORGE_APPROVAL_BYPASS_REVIEW_REQUIRED",
                                   "INDEPENDENT_COMBINED_SHA_TESTS_NOT_RUN",
                                   "OWNER_MERGE_APPROVAL_REQUIRED"])
    except RuntimeError as e:
        report["blockers"].append("PREFLIGHT_ERROR:" + str(e))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not report["blockers"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
