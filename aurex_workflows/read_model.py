"""Read-only, fail-closed access to persisted AUREX workflow metadata."""

import base64
import json
import math
import sqlite3
from pathlib import Path
from typing import Any


class WorkflowReadModel:
    """Expose allowlisted job metadata without workflow mutation authority."""

    MAX_PAGE_SIZE = 100

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        if not self.db_path.is_file():
            raise FileNotFoundError(
                "AUREX workflow database is unavailable"
            )

        connection = sqlite3.connect(
            f"file:{self.db_path.resolve()}?mode=ro",
            uri=True,
            timeout=5,
        )
        connection.row_factory = sqlite3.Row
        return connection


    @staticmethod
    def _encode_cursor(timestamp: float, job_id: str) -> str:
        data = json.dumps([1, timestamp, job_id], allow_nan=False)
        return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")

    @staticmethod
    def _decode_cursor(cursor: str) -> tuple[float, str]:
        if not isinstance(cursor, str) or not 1 <= len(cursor) <= 4096:
            raise ValueError("Invalid pagination cursor")
        try:
            raw = base64.b64decode(
                cursor + "=" * (-len(cursor) % 4),
                altchars=b"-_",
                validate=True,
            )
            if len(raw) > 2048:
                raise ValueError("Invalid pagination cursor")
            data = json.loads(raw)
            if (
                not isinstance(data, list)
                or len(data) != 3
                or type(data[0]) is not int
                or data[0] != 1
                or type(data[1]) not in (int, float)
                or not math.isfinite(data[1])
                or not isinstance(data[2], str)
                or not data[2]
            ):
                raise ValueError("Invalid pagination cursor")
            return float(data[1]), data[2]
        except (ValueError, UnicodeError) as exc:
            raise ValueError("Invalid pagination cursor") from exc

    def list_jobs(
        self,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("Page size must be an integer")

        if not 1 <= limit <= self.MAX_PAGE_SIZE:
            raise ValueError("Page size must be between 1 and 100")

        if cursor is not None and (not isinstance(cursor, str) or not cursor):
            raise ValueError("Invalid pagination cursor")

        try:
            with self._connect() as connection:
                if cursor is None:
                    rows = connection.execute(
                        """
                        SELECT id, kind, state, created_at, updated_at
                        FROM jobs
                        ORDER BY created_at DESC, id DESC
                        LIMIT ?
                        """,
                        (limit + 1,),
                    ).fetchall()
                else:
                    timestamp, job_id = self._decode_cursor(cursor)

                    rows = connection.execute(
                        """
                        SELECT id, kind, state, created_at, updated_at
                        FROM jobs
                        WHERE created_at < ?
                           OR (created_at = ? AND id < ?)
                        ORDER BY created_at DESC, id DESC
                        LIMIT ?
                        """,
                        (
                            timestamp,
                            timestamp,
                            job_id,
                            limit + 1,
                        ),
                    ).fetchall()

        except sqlite3.DatabaseError as error:
            raise RuntimeError(
                "AUREX workflow database could not be read"
            ) from error

        has_more = len(rows) > limit
        visible = rows[:limit]

        jobs = [
            {
                "id": row["id"],
                "kind": row["kind"],
                "state": row["state"],
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"],
            }
            for row in visible
        ]

        return {
            "jobs": jobs,
            "nextCursor": (
                self._encode_cursor(visible[-1]["created_at"], visible[-1]["id"])
                if has_more and visible
                else None
            ),
        }
