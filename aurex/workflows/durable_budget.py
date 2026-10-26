"""Durable, default-deny SQLite budget reservation ledger.

This module does not authorize remote network dispatch.
Financial authority remains NONE.
"""

import sqlite3
from decimal import Decimal
from pathlib import Path

from aurex.workflows.budget import BudgetDenied, _amount


def _stored_amount(value: object) -> Decimal:
    """Fail closed when persisted financial data is invalid."""
    try:
        if not isinstance(value, (str, int, Decimal)):
            raise BudgetDenied("Corrupted stored financial amount")
        amount = _amount(value)
    except (ValueError, TypeError, ArithmeticError) as exc:
        raise BudgetDenied(
            "Corrupted stored financial amount"
        ) from exc

    if not amount.is_finite() or amount < 0:
        raise BudgetDenied("Corrupted stored financial amount")

    return amount


class DurableBudgetLedger:
    def __init__(
        self,
        db_path: str,
        limit_usd: Decimal | None = None,
        allow_temporary_for_testing: bool = False,
    ) -> None:
        self.db_path = str(db_path)

        # Reject accidental use of a temporary or in-memory database.
        path = Path(self.db_path).resolve()
        temporary_path = (
            self.db_path == ":memory:"
            or path == Path("/tmp")
            or Path("/tmp") in path.parents
        )
        if temporary_path and not allow_temporary_for_testing:
            raise ValueError("Durable budget requires persistent storage")

        if not path.parent.is_dir():
            raise ValueError("Budget database directory does not exist")

        requested_limit = (
            _amount(limit_usd) if limit_usd is not None else None
        )

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS budget_control (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    limit_usd TEXT NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS budget_spending (
                    request_id TEXT PRIMARY KEY,
                    amount_usd TEXT NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS budget_reservations (
                    request_id TEXT PRIMARY KEY,
                    amount_usd TEXT NOT NULL,
                    state TEXT NOT NULL CHECK (
                        state IN (CHAR(114,101,115,101,114,118,101,100), CHAR(117,110,107,110,111,119,110))
                    )
                )
                """
            )

            row = conn.execute(
                "SELECT limit_usd FROM budget_control WHERE id = 1"
            ).fetchone()

            if row is None:
                initial_limit = (
                    requested_limit
                    if requested_limit is not None
                    else Decimal("0")
                )
                conn.execute(
                    "INSERT INTO budget_control (id, limit_usd) VALUES (1, ?)",
                    (str(initial_limit),),
                )
            elif (
                requested_limit is not None
                and requested_limit != _stored_amount(row[0])
            ):
                raise BudgetDenied(
                    "Budget limit change requires separate authorization"
                )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    @property
    def reserved_usd(self) -> Decimal:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT amount_usd FROM budget_reservations"
            ).fetchall()
        return sum(
            (_stored_amount(row[0]) for row in rows),
            Decimal("0"),
        )

    def reserve(
        self,
        request_id: str,
        estimated_max_usd: Decimal | str | int,
    ) -> Decimal:
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("Request ID required")

        amount = _amount(estimated_max_usd)
        if amount <= 0:
            raise BudgetDenied("Positive reservation required")

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")

            existing = conn.execute(
                "SELECT 1 FROM budget_reservations WHERE request_id = ?",
                (request_id,),
            ).fetchone()

            if existing:
                raise BudgetDenied("Duplicate reservation request")

            previously_settled = conn.execute(
                "SELECT 1 FROM budget_spending WHERE request_id = ?",
                (request_id,),
            ).fetchone()

            if previously_settled:
                raise BudgetDenied(
                    "Previously settled request cannot reserve again"
                )

            row = conn.execute(
                "SELECT limit_usd FROM budget_control WHERE id = 1"
            ).fetchone()

            if row is None:
                raise BudgetDenied("Budget not initialized")

            limit = _stored_amount(row[0])

            rows = conn.execute(
                "SELECT amount_usd FROM budget_reservations"
            ).fetchall()

            reserved = sum(
                (_stored_amount(item[0]) for item in rows),
                Decimal("0"),
            )

            spent_rows = conn.execute(
                "SELECT amount_usd FROM budget_spending"
            ).fetchall()

            spent = sum(
                (_stored_amount(item[0]) for item in spent_rows),
                Decimal("0"),
            )

            if reserved + spent + amount > limit:
                raise BudgetDenied("Budget exceeded")

            conn.execute(
                """
                INSERT INTO budget_reservations
                    (request_id, amount_usd, state)
                VALUES (?, ?, CHAR(114,101,115,101,114,118,101,100))
                """,
                (request_id, str(amount)),
            )

        return amount

    def mark_unknown(self, request_id: str) -> None:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")

            result = conn.execute(
                """
                UPDATE budget_reservations
                SET state = CHAR(117,110,107,110,111,119,110)
                WHERE request_id = ?
                  AND state IN (CHAR(114,101,115,101,114,118,101,100), CHAR(117,110,107,110,111,119,110))
                """,
                (request_id,),
            )

            if result.rowcount != 1:
                raise ValueError("Reservation not found")


    @property
    def spent_usd(self) -> Decimal:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT amount_usd FROM budget_spending"
            ).fetchall()

        return sum(
            (_stored_amount(row[0]) for row in rows),
            Decimal("0"),
        )

    def settle(
        self,
        request_id: str,
        actual_usd: Decimal | str | int,
    ) -> None:
        amount = _amount(actual_usd)

        if amount < 0:
            raise BudgetDenied("Negative settlement prohibited")

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")

            row = conn.execute(
                """
                SELECT amount_usd, state
                FROM budget_reservations
                WHERE request_id = ?
                """,
                (request_id,),
            ).fetchone()

            if row is None:
                raise BudgetDenied("Reservation not found")

            reserved_amount = _stored_amount(row[0])
            state = row[1]

            if state != "reserved":
                raise BudgetDenied("Reservation cannot be settled")

            if amount > reserved_amount:
                raise BudgetDenied(
                    "Settlement exceeds authorized reservation"
                )

            existing = conn.execute(
                "SELECT 1 FROM budget_spending WHERE request_id = ?",
                (request_id,),
            ).fetchone()

            if existing:
                raise BudgetDenied("Duplicate settlement")

            conn.execute(
                """
                INSERT INTO budget_spending
                    (request_id, amount_usd)
                VALUES (?, ?)
                """,
                (request_id, str(amount)),
            )

            conn.execute(
                "DELETE FROM budget_reservations WHERE request_id = ?",
                (request_id,),
            )


    def reconcile(
        self,
        request_id: str,
        actual_usd: Decimal | str | int,
        provider_verified: bool = False,
    ) -> None:
        """Deny reconciliation until trusted evidence verification exists.

        The provider_verified argument is not accepted as proof.
        This method must not release reservations or modify spending.
        """
        raise BudgetDenied(
            "Provider billing reconciliation requires independent "
            "evidence verification"
        )
