"""One-shot privileged Railway mount initialization; drop to dedicated non-root UID.

This module has NO external network, token, shell, or user-provided path support.
It is not the AUREX agent. Runtime supervisor/API always execute as uid 10001.
"""
from __future__ import annotations

import os
import pwd
import stat
import sys
from pathlib import Path

MOUNT = "/data"
DB = "/data/aurex.sqlite3"
IDENTITY = "aurex"
UID = 10001


def check_environment() -> tuple[int, int]:
    if os.environ.get("RAILWAY_ENVIRONMENT_NAME") != "aurex-staging":
        # Boot also supports later production ONLY after a separate reviewed release.
        if os.environ.get("AUREX_BOOT_RELEASE_APPROVED") != "true":
            raise RuntimeError("Boot only admitted in aurex-staging; release gate HOLD")
    if os.environ.get("AUREX_DB_PATH") != DB:
        raise RuntimeError("AUREX_DB_PATH must be the fixed durable /data/aurex.sqlite3")
    if os.environ.get("AUREX_REQUIRED_VOLUME") != "true":
        raise RuntimeError("AUREX_REQUIRED_VOLUME must be true")
    if not os.path.ismount(MOUNT):
        raise RuntimeError("Railway /data mount is not present")
    user = pwd.getpwnam(IDENTITY)
    if user.pw_uid != UID:
        raise RuntimeError("Unexpected aurex user uid")
    if os.geteuid() != 0:
        raise RuntimeError("Railway privileged boot requires uid 0 for mount repair")
    return user.pw_uid, user.pw_gid


def repair_volume(uid: int, gid: int) -> None:
    # Open the actual mount root, not a potentially swapped pathname.
    flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(MOUNT, flags)
    try:
        if not stat.S_ISDIR(os.fstat(fd).st_mode):
            raise RuntimeError("Invalid volume mount")
        os.fchown(fd, uid, gid)
        os.fchmod(fd, 0o700)
        for name in ("aurex.sqlite3", "aurex.sqlite3-wal", "aurex.sqlite3-shm"):
            try:
                child = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0), dir_fd=fd)
            except FileNotFoundError:
                continue
            try:
                if not stat.S_ISREG(os.fstat(child).st_mode):
                    raise RuntimeError("Volume database entry must be regular, no links or devices")
                os.fchown(child, uid, gid)
                os.fchmod(child, 0o600)
            finally:
                os.close(child)
    finally:
        os.close(fd)


def main() -> None:
    try:
        uid, gid = check_environment()
        repair_volume(uid, gid)
        # Capability/privilege drop before the first API/worker byte executes.
        os.setgroups([])
        os.setgid(gid)
        os.setuid(uid)
        if os.geteuid() != uid:
            raise RuntimeError("Privilege drop not confirmed")
        print("AUREX BOOT: durable mount ready; process uid=10001; HOLD", flush=True)
        os.execv(sys.executable, [sys.executable, "-m", "backend.supervisor"])
    except (OSError, RuntimeError, KeyError) as exc:
        # No credentials or provider connection details are ever logged.
        print(f"AUREX BOOT: fail closed: {type(exc).__name__}", file=sys.stderr, flush=True)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
