"""Start AUREX as uid 10001 after making the data directory writable.

Railway volumes are often root-owned. The image may start as root only long
enough to chown /data, then the API process drops privileges. A non-root start
skips the chown and execs uvicorn directly.
"""

from __future__ import annotations

import os

SERVICE_UID = 10001
SERVICE_GID = 10001


def prepare_data_dir() -> None:
    os.makedirs("/data", mode=0o750, exist_ok=True)
    os.chown("/data", SERVICE_UID, SERVICE_GID)
    for name in os.listdir("/data"):
        try:
            os.chown(os.path.join("/data", name), SERVICE_UID, SERVICE_GID)
        except OSError:
            continue


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
