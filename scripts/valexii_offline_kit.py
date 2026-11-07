#!/usr/bin/env python3
"""Standalone offline kit. Copy this file out of the repository and run it.

    python3 valexii_offline_kit.py --dest /path/to/separate-work

With no --root, it looks in the home directory (one level), Downloads, Desktop,
~/dispater-kit, ~/VALEXII_INSTALLER, /mnt, /media, and /mnt/shared/removable.
It does not install packages, push git, deploy, or download models. It refuses
to write into the folder that holds an archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

MAX_ZIP_BYTES = 512 * 1024 * 1024
MAX_ENTRIES = 5000
MAX_UNCOMPRESSED = 64 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
RATIO_FLOOR_BYTES = 1_000_000
SKIP_DIRS = {"node_modules", ".git"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_roots() -> list[Path]:
    home = Path.home()
    return [
        home,
        home / "Downloads",
        home / "Desktop",
        home / "dispater-kit",
        home / "VALEXII_INSTALLER",
        Path("/mnt"),
        Path("/media"),
        Path("/mnt/shared/removable"),
    ]


def entry_is_unsafe(name: str) -> bool:
    if not name or "\x00" in name or name.startswith(("/", "\\")) or ":" in name:
        return True
    return any(part in {"..", ""} for part in Path(name).parts)


def resource_violation(
    entries: int,
    uncompressed: int,
    compressed: int,
    *,
    max_entries: int = MAX_ENTRIES,
    max_uncompressed: int = MAX_UNCOMPRESSED,
) -> str | None:
    if entries > max_entries:
        return "TOO_MANY_ENTRIES"
    if uncompressed > max_uncompressed:
        return "UNCOMPRESSED_TOO_LARGE"
    if compressed > 0 and uncompressed > RATIO_FLOOR_BYTES and uncompressed / compressed > MAX_COMPRESSION_RATIO:
        return "COMPRESSION_RATIO"
    return None


def _walk(root: Path, suffixes: tuple[str, ...], limit: int, max_depth: int) -> list[Path]:
    found: list[Path] = []
    base = root.resolve()
    for dirpath, dirnames, filenames in os.walk(base):
        current = Path(dirpath)
        depth = len(current.relative_to(base).parts)
        if depth >= max_depth:
            dirnames[:] = []
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS and not name.startswith(".")]
        for name in filenames:
            if name.lower().endswith(suffixes):
                found.append(current / name)
                if len(found) >= limit:
                    return found
    return found


def discover_archives(roots: list[Path], max_depth: int = 8) -> tuple[list[Path], list[str]]:
    missing = [str(root) for root in roots if not root.exists()]
    found: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        depth = 1 if root.resolve() == Path.home().resolve() else max_depth
        for path in _walk(root, (".zip",), 200 - len(found), depth):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                found.append(path)
            if len(found) >= 200:
                break
    found.sort(key=lambda path: str(path))
    return found, missing


def _manifest_status(path: Path, digest: str) -> str:
    sidecar = path.parent / f"{path.name}.sha256"
    if not sidecar.is_file():
        return "ABSENT"
    recorded = sidecar.read_text().strip().split()[0].lower()
    return "MATCH" if recorded == digest else "MISMATCH"


def inventory_zip(path: Path, *, max_uncompressed: int = MAX_UNCOMPRESSED) -> dict[str, Any]:
    if path.stat().st_size > MAX_ZIP_BYTES:
        raise zipfile.BadZipFile("ARCHIVE_TOO_LARGE")
    unsafe: list[str] = []
    names: list[str] = []
    uncompressed = 0
    compressed = 0
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        for info in infos:
            names.append(info.filename)
            uncompressed += info.file_size
            compressed += info.compress_size
            if entry_is_unsafe(info.filename):
                unsafe.append(info.filename)
        problem = resource_violation(len(infos), uncompressed, compressed, max_uncompressed=max_uncompressed)
        if problem is None and not unsafe:
            bad = archive.testzip()
            if bad is not None:
                problem = f"BAD_MEMBER:{bad}"
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "entries": names,
        "unsafe_entries": unsafe,
        "resource_problem": problem,
        "manifest": "PENDING",
    }


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


def _rejected(path: Path, status: str, digest: str | None = None) -> dict[str, Any]:
    return {
        "path": str(path),
        "sha256": digest if digest is not None else sha256_file(path),
        "entries": [],
        "unsafe_entries": [],
        "status": status,
        "extracted_to": None,
        "manifest": "ABSENT",
    }


def extract_archive(archive: Path, dest_root: Path, *, max_uncompressed: int = MAX_UNCOMPRESSED) -> dict[str, Any]:
    try:
        record = inventory_zip(archive, max_uncompressed=max_uncompressed)
    except (zipfile.BadZipFile, OSError):
        return _rejected(archive, "REJECTED_INTEGRITY")
    record["manifest"] = _manifest_status(archive, record["sha256"])
    if record["manifest"] == "MISMATCH":
        record["status"] = "REJECTED_MANIFEST"
        record["extracted_to"] = None
        return record
    if record["unsafe_entries"]:
        record["status"] = "REJECTED_UNSAFE_PATH"
        record["extracted_to"] = None
        return record
    if record["resource_problem"]:
        record["status"] = "REJECTED_RESOURCE_LIMIT"
        record["extracted_to"] = None
        return record
    if not _destination_allowed(archive, dest_root):
        record["status"] = "REJECTED_WOULD_TOUCH_SOURCE"
        record["extracted_to"] = None
        return record
    target = dest_root.resolve() / record["sha256"][:16]
    marker = target / "INVENTORY.json"
    partial = target / ".partial"
    if marker.is_file():
        previous = json.loads(marker.read_text())
        if previous.get("sha256") == record["sha256"]:
            partial.unlink(missing_ok=True)
            record["status"] = "ALREADY_PRESENT"
            record["extracted_to"] = str(target)
            return record
    resuming = partial.is_file()
    target.mkdir(parents=True, exist_ok=True)
    partial.write_text(record["sha256"])
    with zipfile.ZipFile(archive) as zip_archive:
        for info in zip_archive.infolist():
            output = (target / info.filename).resolve()
            if target.resolve() not in output.parents and output != target.resolve():
                raise RuntimeError("zip entry escaped the destination")
            if info.is_dir():
                output.mkdir(parents=True, exist_ok=True)
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.is_file() and output.stat().st_size == info.file_size:
                continue
            output.write_bytes(zip_archive.read(info))
    record["status"] = "RESUMED" if resuming else "EXTRACTED"
    record["extracted_to"] = str(target)
    marker.write_text(json.dumps({key: record[key] for key in ("sha256", "entries")}, sort_keys=True))
    partial.unlink(missing_ok=True)
    return record


def inspect_sqlite(path: Path) -> dict[str, Any]:
    before = path.stat().st_mtime_ns
    try:
        connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
        try:
            tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        finally:
            connection.close()
    except sqlite3.Error as exc:
        return {"path": str(path), "status": "UNREADABLE", "error": type(exc).__name__, "authoritative": False}
    return {
        "path": str(path),
        "status": "DISCOVERED_READ_ONLY",
        "tables": tables,
        "mtime_unchanged": path.stat().st_mtime_ns == before,
        "authoritative": False,
    }


def discover_sqlite(roots: list[Path]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for root in roots:
        if not root.is_dir():
            continue
        depth = 1 if root.resolve() == Path.home().resolve() else 6
        for path in _walk(root, (".db", ".sqlite", ".sqlite3"), 20 - len(found), depth):
            found.append(inspect_sqlite(path))
            if len(found) >= 20:
                return found
    return found


def read_ocr_progress(roots: list[Path]) -> dict[str, Any]:
    manifests: list[dict[str, Any]] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in _walk(root, ("ocr-progress.json",), 20, 6):
            try:
                payload = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError):
                manifests.append({"path": str(path), "status": "UNREADABLE"})
                continue
            failed = payload.get("failed_pages")
            if not isinstance(failed, list):
                failed = []
            manifests.append(
                {
                    "path": str(path),
                    "status": "READ",
                    "pages_processed": payload.get("pages_processed"),
                    "pages_remaining": payload.get("pages_remaining"),
                    "numeric_candidates": payload.get("numeric_candidates"),
                    "failed_pages_retained": len(failed),
                    "numeric_candidates_are_findings": False,
                }
            )
    if not manifests:
        return {"status": "OCR_PROGRESS_ABSENT", "manifests": [], "numeric_candidates_are_findings": False}
    return {"status": "OCR_PROGRESS_PRESENT", "manifests": manifests, "numeric_candidates_are_findings": False}


def build_report(roots: list[Path], dest: Path, repository: Path | None) -> dict[str, Any]:
    archives, missing_roots = discover_archives(roots)
    inventories: list[dict[str, Any]] = []
    seen: dict[str, str | None] = {}
    for path in archives:
        try:
            digest = sha256_file(path)
        except OSError:
            inventories.append(_rejected(path, "REJECTED_INTEGRITY", digest=""))
            continue
        if digest in seen:
            inventories.append(
                {
                    "path": str(path),
                    "sha256": digest,
                    "entries": [],
                    "unsafe_entries": [],
                    "status": "DUPLICATE_CONTENT",
                    "extracted_to": seen[digest],
                    "manifest": "NOT_RECHECKED",
                }
            )
            continue
        record = extract_archive(path, dest)
        if record["status"] in {"EXTRACTED", "ALREADY_PRESENT", "RESUMED"}:
            seen[digest] = record["extracted_to"]
        inventories.append(record)
    existing = [root for root in roots if root.exists()]
    if not archives and not existing:
        asset_status = "LOCAL_ASSET_ACCESS_REQUIRED"
    elif not archives:
        asset_status = "NO_ARCHIVES_FOUND"
    else:
        asset_status = "ARCHIVES_INVENTORIED"
    return {
        "asset_status": asset_status,
        "missing_roots": missing_roots,
        "archives": inventories,
        "sqlite_checkpoints": discover_sqlite(existing),
        "ocr": read_ocr_progress(existing),
        "repository": assess_repository(repository) if repository else {"status": "NOT_REQUESTED"},
        "environment": {
            "network_contact": "NOT_ATTEMPTED",
            "roots_existing": len(existing),
            "roots_missing": len(missing_roots),
        },
        "numeric_candidates_are_findings": False,
        "confirmed_recovery_usd": "0.00",
        "downloads": "NOT_STARTED",
        "production": "HOLD",
    }


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "VALEXII offline kit",
        f"asset_status: {report['asset_status']}",
        f"archives: {len(report['archives'])}",
        f"sqlite_checkpoints: {len(report['sqlite_checkpoints'])}",
        f"ocr: {report['ocr']['status']}",
        f"repository: {report['repository']['status']}",
        f"confirmed_recovery_usd: {report['confirmed_recovery_usd']}",
        f"downloads: {report['downloads']}",
        "numeric candidates are not findings",
    ]
    for item in report["archives"]:
        lines.append(f"- {item['status']} {item['path']}")
    return "\n".join(lines)


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
    report = build_report(args.root or default_roots(), args.dest, args.repository)
    text = json.dumps(report, indent=2, sort_keys=True)
    rendered = render_report(report)
    if args.report:
        args.report.write_text(text + "\n")
        args.report.with_suffix(".txt").write_text(rendered + "\n")
    print(rendered)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
