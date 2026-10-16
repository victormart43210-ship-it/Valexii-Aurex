"""Owner-operated, non-overwriting SQLite snapshot. Never restores over live data."""

import argparse
import os
import sqlite3
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path

from aurex.database import SCHEMA_VERSION


def backup_database(source: Path, destination: Path) -> None:
    """Publish a validated snapshot in a trusted owner-controlled directory."""
    source = source.resolve(strict=True)
    if not source.is_file() or destination.exists() or destination.is_symlink():
        raise ValueError("Unsafe source or occupied destination")
    fd, name = tempfile.mkstemp(prefix='.aurex-backup-', dir=destination.parent)
    os.close(fd)
    temporary = Path(name)
    deadline = time.monotonic() + 30

    def bounded_progress(status: int, remaining: int, total: int) -> None:
        if time.monotonic() > deadline:
            raise TimeoutError("Backup deadline exceeded")

    try:
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as original:
            with closing(sqlite3.connect(temporary)) as snapshot:
                original.backup(snapshot, pages=128, progress=bounded_progress, sleep=0.05)
                if snapshot.execute('PRAGMA user_version').fetchone()[0] != SCHEMA_VERSION:
                    raise ValueError("Unsupported schema")
                if snapshot.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                    raise ValueError("Integrity check failed")
                if snapshot.execute('PRAGMA foreign_key_check').fetchall():
                    raise ValueError("Foreign key check failed")
        with temporary.open('rb') as handle:
            os.fsync(handle.fileno())
        # Atomic no-replace publication; an existing destination is never overwritten.
        os.link(temporary, destination)
        directory_fd = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        backup_database(args.source, args.destination)
    except (OSError, sqlite3.Error, ValueError):
        print('Backup refused or failed; inspect storage and schema. No overwrite attempted.',
              file=sys.stderr)
        return 1
    print('Backup created; SQLite integrity checked. Evidence truth remains NOT VERIFIED.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
