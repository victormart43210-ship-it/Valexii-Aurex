#!/usr/bin/env python3
"""AUREX source-only convergence preflight: does not open any financial documents.

Run locally on the Chromebook repository. It NEVER copies, uploads, modifies,
or recursively enumerates the attached USB drive or its original documents.
The only file bytes read are explicitly scoped Python source/test files.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REQUIRED_MODULES = (
    "aurex/financial/scanner.py",
    "aurex/financial/dashboard.py",
    "aurex/financial/cli.py",
    "aurex/financial/reconciliation.py",
    "aurex/financial/pdf_batch.py",
)
SOURCE_LIMIT_BYTES = 2 * 1024 * 1024
FILE_LIMIT = 150


def _git_output(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=5, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    return result.stdout.strip()


def _inside_repo(root: Path, candidate: Path) -> bool:
    """Disallow all symlink components; code intake must remain inside source root."""
    try:
        rel = candidate.relative_to(root)
        current = root
        for segment in rel.parts:
            current = current / segment
            if current.is_symlink():
                return False
        return candidate.resolve().is_relative_to(root.resolve())
    except (OSError, ValueError):
        return False


def _paths(root: Path) -> list[Path]:
    files = [root / rel for rel in REQUIRED_MODULES]
    source = root / "aurex" / "financial"
    if source.is_dir() and _inside_repo(root, source):
        files.extend(source.rglob("*.py"))
    tests = root / "tests"
    if tests.is_dir() and _inside_repo(root, tests):
        files.extend(tests.glob("test_*financial*.py"))
        files.extend(tests.glob("test_*pdf*.py"))
    return sorted(set(files))


def inspect_source(root: Path, candidate: Path) -> dict[str, Any]:
    """Hash and syntax-check a single code file, never return source content."""
    rel = candidate.relative_to(root).as_posix()
    result: dict[str, Any] = {"path": rel, "status": "HOLD"}
    if candidate.suffix != ".py" or not _inside_repo(root, candidate):
        result["reason"] = "Non-source or unsafe symlink/path"
        return result
    if not candidate.is_file():
        result["reason"] = "Source module missing"
        return result
    try:
        if candidate.stat().st_size > SOURCE_LIMIT_BYTES:
            result["reason"] = "Source file exceeds 2 MiB bound"
            return result
        raw = candidate.read_bytes()
        if len(raw) > SOURCE_LIMIT_BYTES:
            result["reason"] = "Source file exceeds 2 MiB bound"
            return result
        result["sha256"] = hashlib.sha256(raw).hexdigest()
        result["bytes"] = len(raw)
        ast.parse(raw.decode("utf-8-sig"), filename=rel)
        result["status"] = "PASS"
    except (OSError, UnicodeError, SyntaxError, ValueError):
        result["reason"] = "Unreadable, non-UTF-8, or syntax-invalid source"
    return result


def inspect_local_source(
    source: Path, usb_root: Path | None = None
) -> dict[str, Any]:
    """No raw finance data, file contents, USB traversal, writes, or remote operations."""
    root = source.resolve()
    if not root.is_dir() or not (root / "aurex").is_dir():
        return {
            "status": "HOLD",
            "reason": "Not an AUREX repository directory",
            "authority": "NONE",
        }
    files = _paths(root)
    if len(files) > FILE_LIMIT:
        return {
            "status": "HOLD",
            "reason": "Source inventory exceeds bounded file limit",
            "authority": "NONE",
        }

    entries = [inspect_source(root, path) for path in files]
    required = set(REQUIRED_MODULES)
    required_ok = all(
        any(e["path"] == path and e["status"] == "PASS" for e in entries)
        for path in required
    )
    all_safe = all(e["status"] == "PASS" for e in entries)
    head = _git_output(root, "rev-parse", "HEAD")
    branch = _git_output(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    dirty = _git_output(root, "status", "--porcelain")
    result: dict[str, Any] = {
        "report_type": "AUREX_FINANCIAL_SOURCE_ONLY_PREFLIGHT",
        "checked_at": datetime.now(UTC).isoformat(),
        "status": "PASS_SOURCE_INVENTORY_ONLY" if required_ok and all_safe else "HOLD",
        "authority": "NONE",
        "privacy": "NO_DOCUMENT_CONTENT_READ_OR_UPLOADED",
        "git_head": head if head and len(head) == 40 else None,
        "git_branch": branch,
        "working_tree_dirty": None if dirty is None else bool(dirty),
        "usb_mount_present": usb_root.is_dir() if usb_root else None,
        "required_count": len(REQUIRED_MODULES),
        "required_ok": required_ok,
        "source_file_count": len(entries),
        "entries": entries,
        "production_integration": "NOT VERIFIED",
        "sensitive_data_upload": "NOT PERFORMED",
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["report_sha256"] = hashlib.sha256(canonical).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Existing local AUREX repo")
    parser.add_argument(
        "--usb-root", type=Path, default=None,
        help="OPTIONAL USB mount-presence test only; no traversal or reads",
    )
    args = parser.parse_args()
    report = inspect_local_source(args.source, args.usb_root)
    print(json.dumps(report, sort_keys=True, indent=2))
    if report["status"] != "PASS_SOURCE_INVENTORY_ONLY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
