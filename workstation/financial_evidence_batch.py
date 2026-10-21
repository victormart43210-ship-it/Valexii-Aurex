"""Offline, resumable, local-only financial evidence receipts and XLSX formula witnesses.

Observe bytes and formulas; do NOT calculate tax, certify audits, ingest customer
materials without permission, train Qwen, approve payments, or move files online.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import stat
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

MAX_FILE = 32 * 1024 * 1024
MAX_EXPANDED = 160 * 1024 * 1024
MAX_MEMBERS = 5000
MAX_FORMULAS = 50000
FORMATS = {".pdf", ".xlsx", ".xls", ".xlsm", ".csv"}
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
OPAQUE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\\Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def extract_formulas(path: Path) -> tuple[list[tuple[str, str, str, str | None, str]], list[str]]:
    """Parse bounded XLSX parts; cached values and formulas remain UNVERIFIED."""
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if not infos or len(infos) > MAX_MEMBERS:
            raise ValueError("XLSX member count out of bounds")
        total = 0
        for item in infos:
            parts = PurePosixPath(item.filename)
            if (parts.is_absolute() or ".." in parts.parts or "\\" in item.filename
                    or item.flag_bits & 1
                    or (item.external_attr >> 16) & 0o170000 == stat.S_IFLNK):
                raise ValueError("unsafe XLSX ZIP member")
            total += item.file_size
            if total > MAX_EXPANDED or (item.file_size > 1048576
                    and item.file_size > max(1, item.compress_size) * 1000):
                raise ValueError("XLSX exceeds decompression bound")
        names = set(archive.namelist())
        if "xl/workbook.xml" not in names or "xl/_rels/workbook.xml.rels" not in names:
            raise ValueError("XLSX workbook manifest missing")
        root = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        mapping: dict[str, str] = {}
        flags: set[str] = set()
        if any(n.startswith("xl/externalLinks/") for n in names):
            flags.add("EXTERNAL_LINKS_PRESENT")
        if "xl/vbaProject.bin" in names:
            flags.add("MACROS_PRESENT")
        for link in rels.findall(REL + "Relationship"):
            target = link.get("Target", "")
            if link.get("TargetMode") == "External":
                flags.add("EXTERNAL_RELATIONSHIP_PRESENT")
                continue
            if ".." in PurePosixPath(target).parts or "\\" in target:
                raise ValueError("unsafe XLSX relationship target")
            full = target.lstrip("/") if target.startswith("/") else "xl/" + target
            if full in names and full.startswith("xl/worksheets/"):
                mapping[link.get("Id", "")] = full
        sheets = []
        for sheet in root.findall(".//" + NS + "sheet"):
            member = mapping.get(sheet.get(RID, ""))
            if member is None:
                flags.add("SHEET_SOURCE_UNAVAILABLE")
                continue
            if sheet.get("state", "visible") != "visible":
                flags.add("HIDDEN_SHEET_PRESENT")
            sheets.append((sheet.get("name", "[unnamed]")[:128], member))
        if not sheets:
            raise ValueError("XLSX has no accessible sheet")
        out: list[tuple[str, str, str, str | None, str]] = []
        for label, member in sheets:
            with archive.open(member) as stream:
                for _, cell in ET.iterparse(stream, events=("end",)):
                    if cell.tag != NS + "c":
                        continue
                    formula = cell.find(NS + "f")
                    if formula is not None:
                        raw = formula.text or ""
                        cached = cell.find(NS + "v")
                        out.append((
                            label, cell.get("r", "")[:24], raw[:8192],
                            cached.text[:1024] if cached is not None and cached.text is not None else None,
                            "FORMULA_UNVERIFIED" if raw else "SHARED_FORMULA_NOT_EXPANDED",
                        ))
                        if len(out) > MAX_FORMULAS:
                            raise ValueError("XLSX formula witness bound exceeded")
                    cell.clear()
        return out, sorted(flags)


def open_ledger(path: Path) -> sqlite3.Connection:
    if path.is_symlink():
        raise ValueError("database symlink forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ValueError("ledger file must be chmod 600")
    db = sqlite3.connect(path)
    os.chmod(path, 0o600)
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS documents (
      tenant TEXT NOT NULL, project TEXT NOT NULL, relative_path TEXT NOT NULL,
      sha256 TEXT NOT NULL, size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL,
      ctime_ns INTEGER NOT NULL, kind TEXT NOT NULL, state TEXT NOT NULL,
      formula_count INTEGER NOT NULL, flags TEXT NOT NULL, indexed_at TEXT NOT NULL,
      training_allowed INTEGER NOT NULL DEFAULT 0 CHECK(training_allowed=0),
      PRIMARY KEY(tenant,project,relative_path));
    CREATE TABLE IF NOT EXISTS formula_witnesses (
      tenant TEXT NOT NULL, project TEXT NOT NULL, relative_path TEXT NOT NULL,
      sheet TEXT NOT NULL, cell TEXT NOT NULL, formula_raw TEXT NOT NULL,
      cached_raw TEXT, state TEXT NOT NULL,
      PRIMARY KEY(tenant,project,relative_path,sheet,cell),
      FOREIGN KEY(tenant,project,relative_path)
        REFERENCES documents(tenant,project,relative_path));
    """)
    return db


def intake(root: Path, ledger: Path, tenant: str, project: str,
           *, limit: int = 250, execute: bool = False) -> dict:
    if not OPAQUE_ID.fullmatch(tenant) or not OPAQUE_ID.fullmatch(project):
        raise ValueError("tenant/project ID invalid")
    if not 1 <= limit <= 5000:
        raise ValueError("batch limit must be 1..5000")
    if root.is_symlink() or not root.is_dir():
        raise ValueError("root must be existing non-symlink directory")
    root = root.resolve(strict=True)
    if ledger.resolve() == root or root in ledger.resolve().parents:
        raise ValueError("ledger must be outside source tree")
    result = {
        "mode": "EXECUTE_LOCAL" if execute else "PREFLIGHT_ONLY",
        "seen": 0, "indexed": 0, "unchanged": 0, "failed_or_unsupported": 0,
        "formulas_observed": 0, "full_inventory_verified": False,
        "training_authorization": "NONE", "financial_authority": "NONE",
        "release": "HOLD", "independent_verification": "NOT_VERIFIED",
    }
    db = open_ledger(ledger) if execute else None
    scheduled = 0
    try:
        for folder, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not (Path(folder) / d).is_symlink())
            for name in sorted(names):
                path = Path(folder) / name
                if path.suffix.lower() not in FORMATS or path.is_symlink() or not path.is_file():
                    continue
                result["seen"] += 1
                if not execute:
                    if result["seen"] >= limit:
                        result["batch_limit_hit"] = True
                        return result
                    continue
                assert db is not None
                relative = path.relative_to(root).as_posix()
                try:
                    s0 = path.stat()
                    existing = db.execute(
                        """SELECT size,mtime_ns,ctime_ns FROM documents
                        WHERE tenant=? AND project=? AND relative_path=?""",
                        (tenant, project, relative),
                    ).fetchone()
                    if existing and tuple(existing) == (s0.st_size, s0.st_mtime_ns, s0.st_ctime_ns):
                        result["unchanged"] += 1
                        continue
                    if scheduled >= limit:
                        result["batch_limit_hit"] = True
                        return result
                    scheduled += 1
                    if not 1 <= s0.st_size <= MAX_FILE:
                        raise ValueError("file size outside policy")
                    hash_value = sha256_file(path)
                    s1 = path.stat()
                    if (s0.st_size, s0.st_mtime_ns, s0.st_ctime_ns) != (
                        s1.st_size, s1.st_mtime_ns, s1.st_ctime_ns
                    ):
                        raise ValueError("source changed during intake")
                    flags: list[str] = []
                    witnesses: list[tuple[str, str, str, str | None, str]] = []
                    if path.suffix.lower() == ".xlsx":
                        witnesses, flags = extract_formulas(path)
                        state = "FORMULAS_OBSERVED_NOT_RECALCULATED"
                    elif path.suffix.lower() in (".xls", ".xlsm"):
                        flags = ["LEGACY_OR_MACRO_FORMAT_NOT_PARSED"]
                        state = "INDEXED_EXTRACTION_HOLD"
                    else:
                        state = "INDEXED_CONTENT_NOT_EXTRACTED"
                    with db:
                        db.execute("""INSERT INTO documents
                          (tenant,project,relative_path,sha256,size,mtime_ns,ctime_ns,
                           kind,state,formula_count,flags,indexed_at,training_allowed)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0)
                          ON CONFLICT(tenant,project,relative_path) DO UPDATE SET
                            sha256=excluded.sha256,size=excluded.size,
                            mtime_ns=excluded.mtime_ns,ctime_ns=excluded.ctime_ns,
                            kind=excluded.kind,state=excluded.state,
                            formula_count=excluded.formula_count,flags=excluded.flags,
                            indexed_at=excluded.indexed_at,training_allowed=0""",
                          (tenant, project, relative, hash_value, s1.st_size, s1.st_mtime_ns,
                           s1.st_ctime_ns, path.suffix.lower(), state, len(witnesses),
                           json.dumps(flags), datetime.now(UTC).isoformat()))
                        db.execute("""DELETE FROM formula_witnesses
                            WHERE tenant=? AND project=? AND relative_path=?""",
                            (tenant, project, relative))
                        db.executemany("""INSERT INTO formula_witnesses
                          (tenant,project,relative_path,sheet,cell,formula_raw,cached_raw,state)
                          VALUES(?,?,?,?,?,?,?,?)""",
                          ((tenant, project, relative, *w) for w in witnesses))
                    result["indexed"] += 1
                    result["formulas_observed"] += len(witnesses)
                except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError, sqlite3.Error):
                    result["failed_or_unsupported"] += 1
                    # Keep document names, invoice amounts and other PII out of CLI output.
        return result
    finally:
        if db is not None:
            db.close()


def report(ledger: Path, tenant: str, project: str) -> dict:
    if ledger.is_symlink() or not ledger.is_file():
        raise ValueError("ledger unavailable")
    db = sqlite3.connect(f"file:{ledger.resolve()}?mode=ro", uri=True)
    try:
        rows = db.execute("""SELECT state,COUNT(*),SUM(formula_count) FROM documents
                         WHERE tenant=? AND project=? GROUP BY state""",
                          (tenant, project)).fetchall()
        payload = {
            "schema": "aurex.financial-evidence-receipt.v1",
            "tenant": tenant, "project": project,
            "documents": sum(row[1] for row in rows),
            "formula_witnesses": sum(row[2] or 0 for row in rows),
            "states": {row[0]: row[1] for row in rows},
            "missing_documents": "UNKNOWN",
            "formula_verification": "NOT_RUN",
            "source_issuer_authenticated": False,
            "customer_audit_readiness": "NOT_VERIFIED",
            "training_authorization": "NONE",
            "financial_authority": "NONE",
            "release": "HOLD",
            "independent_verification": "NOT_VERIFIED",
        }
        payload["receipt_sha256"] = hashlib.sha256(json.dumps(
            payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return payload
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    cmd = argparse.ArgumentParser(description="Local AUREX evidence-only intake; HOLD")
    sub = cmd.add_subparsers(dest="command", required=True)
    i = sub.add_parser("intake")
    i.add_argument("--root", type=Path, required=True)
    i.add_argument("--db", type=Path, required=True)
    i.add_argument("--tenant", required=True)
    i.add_argument("--project", required=True)
    i.add_argument("--limit", type=int, default=250)
    i.add_argument("--execute", action="store_true")
    r = sub.add_parser("report")
    r.add_argument("--db", type=Path, required=True)
    r.add_argument("--tenant", required=True)
    r.add_argument("--project", required=True)
    a = cmd.parse_args(argv)
    try:
        result = (intake(a.root, a.db, a.tenant, a.project, limit=a.limit,
                         execute=a.execute) if a.command == "intake"
                  else report(a.db, a.tenant, a.project))
    except (OSError, ValueError, sqlite3.Error) as e:
        print(json.dumps({"status": "HOLD", "error_class": type(e).__name__}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
