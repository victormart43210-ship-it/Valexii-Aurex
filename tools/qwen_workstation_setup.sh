#!/usr/bin/env bash
# Read-only Qwen Workstation Environment Setup & Diagnostic Check

set -euo pipefail

echo "=== AUREX Qwen Workstation Diagnostic Check ==="
python3 -m aurex.qwen_diagnostic
