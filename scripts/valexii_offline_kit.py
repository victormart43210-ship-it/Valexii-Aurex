#!/usr/bin/env python3
"""Standalone offline kit. Copy this file out of the repository and run it.

    python3 valexii_offline_kit.py --root /path/to/archives --dest /path/to/work

It does not install packages, push git, deploy, or download models. It refuses
to write into the folder that holds an archive, so a USB original is not replaced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def entry_is_unsafe(name: str) -> bool:
    if not name or "\x00" in name or name.startswith(("/", "\\")) or ":" in name:
        return True
    parts = Path(name).parts
    return any(part in {"..", ""} for part in parts)


def discover_archives(roots: list[Path]) -> tuple[list[Path], list[str]]:
    missing = [str(root) for root in roots if not root.exists()]
    found: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        found.extend(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() == ".zip")
    found.sort(key=lambda path: str(path))
    return found, missing


def inventory_zip(path: Path) -> dict[str, Any]:
    unsafe: list[str] = []
    names: list[str] = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            names.append(info.filename)
            if entry_is_unsafe(info.filename):
                unsafe.append(info.filename)
    return {"path": str(path), "sha256": sha256_file(path), "entries": names, "unsafe_entries": unsafe}


def assess_repository(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {"status": "REPOSITORY_ABSENT", "remote": None, "head": None}
    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(path), *args],
            check=False,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip() if completed.returncode == 0 else ""
    remote = git("remote", "get-url", "origin")
    head = git("rev-parse", "HEAD")
    return {
        "status": "REPOSITORY_PRESENT" if head else "REPOSITORY_UNREADABLE",
        "remote": remote or None,
        "head": head or None,
    }


def _destination_allowed(archive: Path, dest_root: Path) -> bool:
    archive_home = archive.resolve().parent
    destination = dest_root.resolve()
    if destination == archive_home or archive_home in destination.parents:
        return False
    try:
        destination.relative_to(archive_home)
    except ValueError:
        return True
    return False


def extract_archive(archive: Path, dest_root: Path) -> dict[str, Any]:
    record = inventory_zip(archive)
    if record["unsafe_entries"]:
        record["status"] = "REJECTED_UNSAFE_PATH"
        record["extracted_to"] = None
        return record
    if not _destination_allowed(archive, dest_root):
        record["status"] = "REJECTED_WOULD_TOUCH_SOURCE"
        record["extracted_to"] = None
        return record
    target = dest_root.resolve() / record["sha256"][:16]
    marker = target / "INVENTORY.json"
    if marker.is_file():
        previous = json.loads(marker.read_text())
        if previous.get("sha256") == record["sha256"]:
            record["status"] = "ALREADY_PRESENT"
            record["extracted_to"] = str(target)
            return record
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zip_archive:
        for info in zip_archive.infolist():
            output = (target / info.filename).resolve()
            if target.resolve() not in output.parents and output != target.resolve():
                raise RuntimeError("zip entry escaped the destination")
            if info.is_dir():
                output.mkdir(parents=True, exist_ok=True)
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(zip_archive.read(info))
    record["status"] = "EXTRACTED"
    record["extracted_to"] = str(target)
    marker.write_text(json.dumps({k: record[k] for k in ("sha256", "entries")}, sort_keys=True))
    return record


def build_report(roots: list[Path], dest: Path, repository: Path | None) -> dict[str, Any]:
    archives, missing_roots = discover_archives(roots)
    inventories = [extract_archive(path, dest) for path in archives] if dest else []
    if not archives and missing_roots:
        asset_status = "LOCAL_ASSET_ACCESS_REQUIRED"
    elif not archives:
        asset_status = "NO_ARCHIVES_FOUND"
    else:
        asset_status = "ARCHIVES_INVENTORIED"
    return {
        "asset_status": asset_status,
        "missing_roots": missing_roots,
        "archives": inventories,
        "repository": assess_repository(repository) if repository else {"status": "NOT_REQUESTED"},
        "numeric_candidates_are_findings": False,
        "confirmed_recovery_usd": "0.00",
        "downloads": "NOT_STARTED",
        "production": "HOLD",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory offline ZIP kits without touching their source folders.")
    parser.add_argument("--root", action="append", default=[], type=Path)
    parser.add_argument("--dest", type=Path)
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    if args.dest is None:
        print("A separate --dest directory is required. The kit will not write next to the archives.", file=sys.stderr)
        return 2
    report = build_report(args.root, args.dest, args.repository)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        args.report.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
