#!/usr/bin/env bash
set -euo pipefail

HOST="127.0.0.1"
PORT="8000"

echo "Starting AUREX API server on http://:"
exec python3 -m uvicorn aurex.api:app --host "" --port ""
