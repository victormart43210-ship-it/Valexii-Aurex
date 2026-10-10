#!/usr/bin/env bash
# One-command AUREX workstation startup. Does not require an LLM.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL="${AUREX_LOCAL_ROOT:-$HOME/aurex-offline-v3}"
LOG="$HOME/aurex-hle-lab.log"
cd "$ROOT"
echo "AUREX source: $ROOT"
echo "Local test project: $LOCAL"
python3 -m compileall -q workstation
if curl -fsS --max-time 2 http://127.0.0.1:8765/ >/dev/null 2>&1; then
  echo "Existing dashboard detected. Looking for its Python process..."
  python3 - <<'PY'
import os, signal, time
me = os.getpid()
stopped = []
for name in os.listdir("/proc"):
    if not name.isdigit() or int(name) == me:
        continue
    try:
        argv = open(f"/proc/{name}/cmdline", "rb").read().split(b"\\0")
        if not argv or b"python" not in argv[0].split(b"/")[-1]:
            continue
        if not any(arg.endswith(b"workstation/app.py") for arg in argv[1:]):
            continue
        os.kill(int(name), signal.SIGTERM)
        stopped.append(int(name))
    except (OSError, PermissionError, ProcessLookupError):
        pass
print("Stopped AUREX dashboard processes:", stopped)
PY
  sleep 2
  if curl -fsS --max-time 2 http://127.0.0.1:8765/ >/dev/null 2>&1; then
    echo "Another service still owns port 8765. Stop that service and retry."
    exit 1
  fi
fi
nohup env AUREX_LOCAL_ROOT="$LOCAL" AUREX_MODEL_ENDPOINT="${AUREX_MODEL_ENDPOINT:-http://127.0.0.1:8080/v1/chat/completions}" AUREX_MODEL_NAME="${AUREX_MODEL_NAME:-local-model}" python3 workstation/app.py > "$LOG" 2>&1 < /dev/null &
PID=$!
for i in 1 2 3 4 5; do
  if curl -fsS --max-time 2 http://127.0.0.1:8765/ >/dev/null 2>&1; then break; fi
  sleep 1
done
if ! curl -fsS --max-time 2 http://127.0.0.1:8765/ >/dev/null; then
  echo "Dashboard failed to start; log:"; tail -n 30 "$LOG"; exit 1
fi
echo "Dashboard ready: http://localhost:8765 (PID $PID)"
echo "Test endpoints:"
for check in tests gate hle local; do
  printf '%s: ' "$check"
  curl -fsS --max-time 100 -X POST "http://127.0.0.1:8765/api/check/$check" | python3 -c 'import sys,json; x=json.load(sys.stdin); print(x.get("status"), ("exit="+str(x["exit_code"])) if "exit_code" in x else "")' || echo "REQUEST FAILED"
done
echo "Full results: $LOG and dashboard. Local AI may still be unavailable."
