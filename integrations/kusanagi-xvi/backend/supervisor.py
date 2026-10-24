"""Fail-closed Unix process supervisor for the AUREX Railway candidate.

API runs in all modes. SQLite worker and observer require explicit opt-in.
Children have independent process groups and are all reaped on shutdown.
Production mount admission must be requested via AUREX_REQUIRED_VOLUME=true.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable, Mapping

from . import store


def validate_config(env: Mapping[str, str], mount_check: Callable[[str], bool] = os.path.ismount) -> str:
    db = env.get("AUREX_DB_PATH", "")
    if not db or not os.path.isabs(db) or db == ":memory:":
        raise ValueError("AUREX_DB_PATH must name an absolute, durable SQLite file")
    if os.path.basename(db) in ("", ".", ".."):
        raise ValueError("AUREX_DB_PATH must name a file, not a directory")
    port = env.get("PORT", "8080")
    if not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
        raise ValueError("Invalid service port")
    # Do not silently substitute ephemeral disk for durable jobs.
    if env.get("AUREX_REQUIRED_VOLUME") == "true" and not (
        os.path.realpath(db).startswith("/data/") and mount_check("/data")
    ):
        raise ValueError("Required persistent /data volume missing")
    return db


def child_commands(env: Mapping[str, str]) -> list[list[str]]:
    commands: list[list[str]] = []
    if env.get("AUREX_ENABLE_OFFLINE_LAB") == "true":
        commands.append([sys.executable, "-m", "backend.worker", "loop", "--interval", "10"])
    if env.get("AUREX_OBSERVER_ENABLED") == "true":
        commands.append([sys.executable, "-m", "backend.agent", "loop", "--interval", "60"])
    commands.append([
        sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0",
        "--port", env.get("PORT", "8080"), "--no-access-log",
    ])
    return commands


def _signal_group(child: subprocess.Popen[bytes], sig: int) -> None:
    if child.poll() is not None:
        return
    try:
        os.killpg(child.pid, sig)
    except ProcessLookupError:
        pass


def main() -> int:
    env = os.environ.copy()
    try:
        db = validate_config(env)
        store.initialize(db)
        if env.get("AUREX_STAGING_PERSISTENCE_PROBE") == "true":
            from . import staging_probe

            result = staging_probe.run(db, env)
            import json

            print(json.dumps(result, sort_keys=True), flush=True)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"FATAL: AUREX startup refused ({type(exc).__name__})", file=sys.stderr)
        return 2

    children: list[subprocess.Popen[bytes]] = []
    stopping = False

    def stop(*_args: object) -> None:
        nonlocal stopping
        stopping = True
        for child in children:
            _signal_group(child, signal.SIGTERM)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        # API and worker share one SQLite file. Never start work before
        # initialization and explicit configuration checks have passed.
        for command in child_commands(env):
            children.append(subprocess.Popen(command, env=env, start_new_session=True))
        while not stopping:
            if any(child.poll() is not None for child in children):
                print("FATAL: AUREX child exited; restarting whole service", file=sys.stderr)
                return 1
            time.sleep(1)
        return 0
    finally:
        stop()
        for child in children:
            try:
                child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                _signal_group(child, signal.SIGKILL)
                child.wait()


if __name__ == "__main__":
    raise SystemExit(main())
