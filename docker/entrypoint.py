"""Start AUREX as uid 10001 after safely preparing the data directory.

Do not follow symlinks while changing ownership: /data can be a mounted
volume, and entries within it must not redirect root-owned startup operations.
"""

from __future__ import annotations

import os
import stat

SERVICE_UID = 10001
SERVICE_GID = 10001


def prepare_data_dir() -> None:
    os.makedirs("/data", mode=0o750, exist_ok=True)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory_fd = os.open("/data", flags)
    try:
        os.fchown(directory_fd, SERVICE_UID, SERVICE_GID)
        for name in os.listdir(directory_fd):
            # Open relative to the verified directory; O_NOFOLLOW prevents
            # an attacker-controlled symlink from redirecting fchown.
            try:
                entry_fd = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=directory_fd)
            except OSError:
                continue
            try:
                mode = os.fstat(entry_fd).st_mode
                if stat.S_ISREG(mode) or stat.S_ISDIR(mode):
                    os.fchown(entry_fd, SERVICE_UID, SERVICE_GID)
            except OSError:
                continue
            finally:
                os.close(entry_fd)
    finally:
        os.close(directory_fd)


def drop_privileges() -> None:
    if os.geteuid() != 0:
        return
    prepare_data_dir()
    os.setgroups([])
    os.setgid(SERVICE_GID)
    os.setuid(SERVICE_UID)


def main() -> None:
    drop_privileges()
    os.environ.setdefault("AUREX_DB_PATH", "/data/aurex_jobs.db")
    os.environ.setdefault("AUREX_DISPATER_DB", "/data/aurex_dispater.db")
    port = os.environ.get("PORT", "8080")
    os.execvp(
        "uvicorn",
        [
            "uvicorn",
            "aurex.api:app",
            "--host",
            "0.0.0.0",
            "--port",
            port,
            "--no-access-log",
        ],
    )


if __name__ == "__main__":
    main()
