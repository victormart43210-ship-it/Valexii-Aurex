#!/usr/bin/env bash
# Restore the SYNTHETIC-ONLY AUREX financial review source from this Git branch.
# No network, deployment, protected-branch mutation, payments or auto-approval.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
BRANCH='feature/kusanagi-xc-financial-audit-linux-kit-20261017'
[[ "$(git branch --show-current)" == "$BRANCH" ]] || { echo "Refusing to install outside $BRANCH" >&2; exit 2; }
[[ -z "$(git status --porcelain)" ]] || { echo 'Refusing dirty checkout. Use a clean clone or commit/stash changes.' >&2; exit 2; }
python3 - "$ROOT" <<'PY'
from __future__ import annotations
import base64
import hashlib
import io
import pathlib
import sys
import tarfile

root = pathlib.Path(sys.argv[1]).resolve(strict=True)
pieces = root / "artifacts" / "financial-audit"
raw_b64 = "".join((pieces / f"chunk_{n:02d}.b64").read_text(encoding="ascii").strip() for n in range(1, 6))
archive = base64.b64decode(raw_b64, validate=True)
wanted = "69fd708ab0e9857036af3696d80c7cf914de6ca43d8738a605e93acf9722c7f2"
actual = hashlib.sha256(archive).hexdigest()
if actual != wanted:
    raise SystemExit(f"ARCHIVE HASH MISMATCH: expected {wanted}, got {actual}. No files installed.")
allow = lambda p: p.startswith("aurex/financial_review/") or p.startswith("fixtures/") or p in {
    "tests/test_audit_engine.py", "tests/test_source_bytes.py", "web/index.html"}
pending = []
with tarfile.open(fileobj=io.BytesIO(archive), mode="r:xz") as tar:
    members = tar.getmembers()
    if len(members) > 50:
        raise SystemExit("Archive member count exceeds limit")
    total_size = 0
    for member in members:
        # The archive may contain regular entries only; no symlinks, devices, directories with weird permissions.
        p = pathlib.PurePosixPath(member.name)
        if p.is_absolute() or ".." in p.parts:
            raise SystemExit(f"Unsafe archive path: {member.name}")
        if member.isdir():
            continue
        if not member.isfile() or not allow(member.name):
            raise SystemExit(f"Unexpected archive member: {member.name}")
        if member.size > 128 * 1024:
            raise SystemExit(f"Oversized archive member: {member.name}")
        total_size += member.size
        if total_size > 500 * 1024:
            raise SystemExit("Expanded archive exceeds 500 KiB")
        dest = root.joinpath(*p.parts)
        if dest.exists() or dest.is_symlink():
            raise SystemExit(f"Refusing overwrite: {member.name}")
        entry = tar.extractfile(member)
        if entry is None:
            raise SystemExit(f"Unreadable member: {member.name}")
        data = entry.read(128 * 1024 + 1)
        if len(data) != member.size:
            raise SystemExit(f"Size mismatch in: {member.name}")
        pending.append((dest, data))
if len(pending) < 15 or not any(str(x).endswith("aurex/financial_review/gate.py") for x, _ in pending):
    raise SystemExit("Expected financial module/tests/fixtures not found")
for dest, data in pending:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("xb") as file:
        file.write(data)
print(f"PASS: restored {len(pending)} files from SHA256-verified GitHub archive.")
print("Only local working-tree files were created; no commit, push or deployment.")
PY
echo "Next: python3 -m venv .venv && . .venv/bin/activate && python -m pip install -e '.[dev]'"
echo "Then: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_audit_engine.py tests/test_source_bytes.py"
echo "Then: python -m aurex.financial_review.cli serve --port 8767"
