#!/usr/bin/env bash
# Read-only: inspect an existing Hetzner GitLab runner without exposing tokens.
# Run ON the Hetzner host. No installations or configuration writes.
set -euo pipefail
printf '%s\n' '=== HETZNER / GITLAB RUNNER READ-ONLY PREFLIGHT ==='
if command -v gitlab-runner >/dev/null 2>&1; then
  echo 'gitlab-runner_binary=PRESENT'
  gitlab-runner --version | head -n 3
else
  echo 'gitlab-runner_binary=MISSING'
fi
if command -v systemctl >/dev/null 2>&1; then
  service_status="$(systemctl is-active gitlab-runner 2>/dev/null || true)"
  printf 'gitlab-runner_service=%s\n' "${service_status:-NOT_FOUND}"
fi
if command -v docker >/dev/null 2>&1; then
  echo 'docker_binary=PRESENT'
  docker info --format 'docker_server={{.ServerVersion}}' 2>/dev/null ||
    echo 'docker_daemon=UNAVAILABLE_TO_CALLER'
else
  echo 'docker_binary=MISSING'
fi
python3 - <<'PY'
import os
from pathlib import Path

try:
    import tomllib
except ImportError:
    print("toml_inspection=UNAVAILABLE_PYTHON_BELOW_3_11")
    raise SystemExit(0)

path = Path("/etc/gitlab-runner/config.toml")
if not path.exists():
    print("runner_config=NOT_FOUND")
    raise SystemExit(0)
if not os.access(path, os.R_OK):
    print("runner_config=NOT_READABLE_RUN_WITH_SUDO_TO_INSPECT")
    raise SystemExit(0)
try:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
except (OSError, ValueError) as error:
    print(f"runner_config=INVALID_OR_UNREADABLE_{type(error).__name__}")
    raise SystemExit(0)
runners = data.get("runners", [])
print(f"configured_runner_count={len(runners)}")
for i, item in enumerate(runners, start=1):
    docker = item.get("docker", {})
    vols = docker.get("volumes", [])
    # No server address, registration/auth tokens, user credentials or URL.
    print(f"runner_{i}_executor={item.get('executor', 'UNKNOWN')}")
    print(f"runner_{i}_docker_privileged={docker.get('privileged', 'UNKNOWN')}")
    print(f"runner_{i}_host_socket_mounted={any('docker.sock' in str(x) for x in vols)}")
    print(f"runner_{i}_default_image={docker.get('image', 'UNKNOWN')}")
    print(f"runner_{i}_identity=REDACTED")
print("active_runner_tag=CHECK_GITLAB_SETTINGS_CI_CD_RUNNERS")
PY
echo 'CAUTION: a configured runner is not necessarily ONLINE or available to the AUREX CI job.'
echo 'Never paste registration tokens, raw config.toml, SSH keys or environment variables.'
