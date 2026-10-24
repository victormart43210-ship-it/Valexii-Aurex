#!/usr/bin/env bash
# Local-only, $0 default AUREX FastAPI and read-only private preview.
set -euo pipefail
umask 077
cd "$(dirname "$0")/.."
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo 'Activate the Python virtualenv first: . .venv/bin/activate' >&2; exit 2
fi
if [[ "${AUREX_PREVIEW_MODE:-local}" != local && "${AUREX_PREVIEW_MODE:-local}" != access ]]; then
  echo 'Invalid AUREX_PREVIEW_MODE (local or access only)' >&2; exit 2
fi
if [[ "${AUREX_PREVIEW_MODE:-local}" == access ]]; then
  for field in CF_ACCESS_TEAM_DOMAIN CF_ACCESS_AUD CF_ACCESS_OWNER_EMAIL; do
    if [[ -z "${!field:-}" ]]; then echo "Missing $field; fail closed." >&2; exit 2; fi
  done
fi
STATE_DIR="${AUREX_DEV_STATE_DIR:-${HOME}/.local/state/valexii-aurex/dev}"
mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"
if [[ ! -f "$STATE_DIR/preview-password" ]]; then
  python -c 'import secrets,sys;open(sys.argv[1], "w").write(secrets.token_urlsafe(48)+"\n")' "$STATE_DIR/preview-password"
fi
if [[ ! -f "$STATE_DIR/service-token" ]]; then
  python -c 'import secrets,sys;open(sys.argv[1], "w").write(secrets.token_urlsafe(48)+"\n")' "$STATE_DIR/service-token"
fi
chmod 600 "$STATE_DIR/preview-password" "$STATE_DIR/service-token"
export AUREX_PREVIEW_PASSWORD="$(cat "$STATE_DIR/preview-password")"
export AUREX_SERVICE_TOKEN="$(cat "$STATE_DIR/service-token")"
unset AUREX_ADMIN_TOKEN || true
export AUREX_PREVIEW_MODE="${AUREX_PREVIEW_MODE:-local}"
export AUREX_ENABLE_OFFLINE_LAB=0
export AUREX_DB_PATH="$STATE_DIR/jobs.db"
export PYTHONDONTWRITEBYTECODE=1
python - <<'PY'
import socket
for port in (8766, 8788):
    s=socket.socket(); s.settimeout(.5)
    if s.connect_ex(('127.0.0.1', port))==0:
        raise SystemExit(f'Port {port} is occupied; leave existing process untouched.')
    s.close()
PY
python -m uvicorn aurex.api:app --host 127.0.0.1 --port 8766 --no-access-log &
BACKEND_PID=$!
cleanup() { kill "$BACKEND_PID" 2>/dev/null || true; wait "$BACKEND_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
printf '\nAUREX local API: http://127.0.0.1:8766\n'
printf 'Private preview: http://127.0.0.1:8788\n'
printf 'HTTP Basic username: aurex\nHTTP Basic password saved to: %s/preview-password\n' "$STATE_DIR"
printf 'Mode: %s (local mode is NEVER safe to attach a tunnel)\n' "$AUREX_PREVIEW_MODE"
printf 'Use Ctrl+C to stop both processes. Nothing is deployed.\n\n'
python -m uvicorn tools.private_dev_gateway:app --host 127.0.0.1 --port 8788 --no-access-log
