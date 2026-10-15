#!/usr/bin/env bash
# Resource-conscious, disconnected-terminal verification launcher.
# This wrapper does NOT claim CI, release authority, or durable worker execution.
set -euo pipefail

repo="$(git rev-parse --show-toplevel)"
cd "$repo"
candidate="$(git rev-parse HEAD)"
if [[ -n "$(git status --porcelain --untracked-files=normal)" ]]; then
  echo "HOLD: tracked working tree is dirty; freeze an exact candidate first." >&2
  exit 2
fi
if [[ ! -f pyproject.toml ]]; then
  echo "HOLD: repository pyproject.toml is missing" >&2
  exit 2
fi
if [[ ! -f scripts/verify.sh ]]; then
  echo "HOLD: scripts/verify.sh is missing" >&2
  exit 2
fi

# Logs deliberately live outside git and never include environment variables.
log_root="${AUREX_VERIFICATION_LOG_DIR:-${TMPDIR:-/tmp}/aurex-verification}"
umask 077
mkdir -p "$log_root"
if [[ -L "$log_root" || ! -d "$log_root" ]]; then
  echo "HOLD: log directory is not a real directory" >&2
  exit 2
fi
chmod 700 "$log_root"
run_id="$(date -u +%Y%m%dT%H%M%SZ)-${candidate:0:12}-$$"
run_dir="$log_root/$run_id"
mkdir -m 700 "$run_dir"
printf '%s\n' "$candidate" > "$run_dir/candidate.sha"
printf '%s\n' "$repo" > "$run_dir/repository.path"
printf '%s\n' "LOCAL_ONLY=1 HOSTED_CI=NOT_VERIFIED RELEASE_AUTHORITY=NONE" > "$run_dir/admission.txt"

# Run tests sequentially and preserve exit status; never mistake nohup for durability.
# Use an absolute log directory to prevent writing logs into the source tree.
nohup nice -n 10 bash -c '
  set -uo pipefail
  cd "$1" || exit 2
  run_dir="$2"
  candidate="$3"
  echo "AUREX local verification: candidate=$candidate"
  if [[ "$(git rev-parse HEAD)" != "$candidate" || -n "$(git status --porcelain --untracked-files=normal)" ]]; then
    echo "HOLD: source tree changed before verification started"
    printf "2\n" > "$run_dir/exit.status"
    exit 2
  fi
  for required in python3 ruff; do
    if ! command -v "$required" >/dev/null 2>&1; then
      echo "HOLD: missing verification executable: $required"
      printf "2\n" > "$run_dir/exit.status"
      exit 2
    fi
  done
  echo "UTC_START=$(date -u +%FT%TZ)"
  echo "PYTHON=$(python3 --version 2>&1)"
  printf "RUFF="; (ruff --version || true)
  printf "MYPY="; (python3 -m mypy --version || true)
  printf "PYTEST="; (python3 -m pytest --version || true)
  status=0
  for check in ruff mypy pytest; do
    if [[ "$(git rev-parse HEAD)" != "$candidate" || -n "$(git status --porcelain --untracked-files=normal)" ]]; then
      echo "HOLD: source tree changed during verification"
      printf "2\n" > "$run_dir/exit.status"
      exit 2
    fi
    case "$check" in
      ruff) ruff check . ;;
      mypy) python3 -m mypy aurex --strict ;;
      pytest) python3 -m pytest -q -rs ;;
    esac
    rc=$?
    printf "%s=%s\n" "$check" "$rc" | tee -a "$run_dir/exit-codes.txt"
    if (( rc != 0 )); then status=1; fi
  done
  if [[ "$(git rev-parse HEAD)" != "$candidate" || -n "$(git status --porcelain --untracked-files=normal)" ]]; then
    echo "HOLD: source tree changed after verification"
    status=2
  fi
  printf "UTC_END=%s\n" "$(date -u +%FT%TZ)"
  printf "LOCAL_RESULT=%s\n" "$([[ $status -eq 0 ]] && echo PASS || echo FAIL)"
  echo "HOSTED_CI=NOT_VERIFIED"
  echo "RELEASE_AUTHORITY=NONE"
  printf "%s\n" "$status" > "$run_dir/exit.status.tmp"
  mv "$run_dir/exit.status.tmp" "$run_dir/exit.status"
  exit "$status"
' bash "$repo" "$run_dir" "$candidate" > "$run_dir/verification.log" 2>&1 < /dev/null &
pid=$!
printf '%s\n' "$pid" > "$run_dir/pid"
printf 'Started local verification PID=%s candidate=%s\n' "$pid" "$candidate"
printf 'Logs: %s\n' "$run_dir"
printf 'Monitor: tail -f %q\n' "$run_dir/verification.log"
printf 'Status: cat %q\n' "$run_dir/exit.status"
