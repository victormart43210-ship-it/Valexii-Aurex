#!/usr/bin/env bash
set -euo pipefail

echo "=== AUREX Full Verification Suite ==="

echo "1. Running Ruff lint check..."
ruff check .
echo "[PASS] Ruff lints"

echo "2. Running Mypy strict type check..."
python3 -m mypy aurex --strict
echo "[PASS] Mypy strict type checking"

echo "3. Running Pytest test matrix..."
python3 -m pytest tests training/tests workstation/tests
echo "[PASS] Pytest test matrix"

echo "=== ALL VERIFICATION CHECKS PASSED (STATUS: PASS) ==="
