#!/usr/bin/env bash
# Install the user-provided, synthetic-only AUREX audit core into this isolated checkout.
# This is a local source import, NOT a GitHub upload, merge, deployment, or financial authority.
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: bash scripts/install_financial_audit_kit.sh /path/to/VALEXII_AUREX_FINANCIAL_AUDIT_CORE_20261017.zip" >&2; exit 2; fi
ZIP="$(realpath "$1")"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
[[ -f "$ZIP" ]] || { echo "Missing ZIP: $ZIP" >&2; exit 2; }
[[ "$(git branch --show-current)" == feature/kusanagi-xc-financial-audit-linux-kit-20261017 ]] || { echo "Refusing unexpected branch" >&2; exit 2; }
[[ -z "$(git status --porcelain)" ]] || { echo "Refusing dirty checkout" >&2; exit 2; }
command -v python3 >/dev/null || { echo "Need python3"; exit 2; }
python3 - "$ZIP" "$ROOT" <<'PY'
import hashlib, io, pathlib, sys, zipfile
path, target = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
source_root = "VALEXII_AUREX_AUDIT_BUILD_20261017/"
allow = lambda p: p.startswith("aurex/financial_review/") or p.startswith("fixtures/") or p in {"tests/test_audit_engine.py", "tests/test_source_bytes.py", "web/index.html"}
with zipfile.ZipFile(path) as arc:
    payloads = []
    for info in arc.infolist():
        if info.is_dir(): continue
        if not info.filename.startswith(source_root): continue
        rel = info.filename[len(source_root):]
        if not allow(rel): continue
        dest = target / rel
        if dest.exists() or dest.is_symlink(): raise SystemExit("Refusing overwrite: " + rel)
        if info.file_size > 1_000_000: raise SystemExit("Oversized file: " + rel)
        payloads.append((dest, arc.read(info)))
    if len(payloads) < 15 or not any(str(p).endswith("/gate.py") for p, _ in payloads):
        raise SystemExit("Expected AUREX audit contents not found")
    for dest, data in payloads:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
print("Imported", len(payloads), "synthetic-only files; nothing committed or deployed.")
PY
echo "Next: python3 -m venv .venv && source .venv/bin/activate && python -m pip install -e '.[dev]'"
echo "Then: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_audit_engine.py tests/test_source_bytes.py"
echo "Then: python -m aurex.financial_review.cli serve --port 8767"
