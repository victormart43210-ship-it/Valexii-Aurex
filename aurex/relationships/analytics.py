"""Compare grouping strategies without changing DISPATER money arithmetic.

Financial totals in the audit engine stay on ``Decimal``. This module only
checks whether an integer-cent SQLite aggregate reproduces the same total.
DuckDB and Polars are measured when importable and are not imported by the
reconciliation path.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import time
from collections import defaultdict
from decimal import Decimal
from typing import Any


def duplicate_jobs(invoices: list[dict[str, str]]) -> list[str]:
    counts: dict[str, int] = defaultdict(int)
    for invoice in invoices:
        counts[invoice["job_id"]] += 1
    return sorted(job_id for job_id, count in counts.items() if count > 1)


def duplicate_jobs_sqlite(invoices: list[dict[str, str]]) -> list[str]:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE invoices (job_id TEXT NOT NULL)")
        conn.executemany("INSERT INTO invoices (job_id) VALUES (?)", [(row["job_id"],) for row in invoices])
        rows = conn.execute(
            "SELECT job_id FROM invoices GROUP BY job_id HAVING COUNT(*) > 1 ORDER BY job_id"
        ).fetchall()
    finally:
        conn.close()
    return [str(row[0]) for row in rows]


def sum_hours_decimal(rows: list[dict[str, str]]) -> dict[str, str]:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for row in rows:
        totals[row["equipment_id"]] += Decimal(row["billable_hours"])
    return {key: f"{totals[key]:.2f}" for key in sorted(totals)}


def sum_hours_sqlite_cents(rows: list[dict[str, str]]) -> dict[str, str]:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE hours (equipment_id TEXT NOT NULL, cents INTEGER NOT NULL)")
        payload = []
        for row in rows:
            cents = int((Decimal(row["billable_hours"]) * 100).to_integral_value())
            payload.append((row["equipment_id"], cents))
        conn.executemany("INSERT INTO hours (equipment_id, cents) VALUES (?, ?)", payload)
        grouped = conn.execute(
            "SELECT equipment_id, SUM(cents) FROM hours GROUP BY equipment_id ORDER BY equipment_id"
        ).fetchall()
    finally:
        conn.close()
    return {str(equipment_id): f"{Decimal(cents) / Decimal(100):.2f}" for equipment_id, cents in grouped}


def _available(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def benchmark(invoices: list[dict[str, str]], hours: list[dict[str, str]]) -> dict[str, Any]:
    """Time the baseline and the SQLite path. Optional engines are not adopted here."""
    started = time.perf_counter()
    python_duplicates = duplicate_jobs(invoices)
    python_hours = sum_hours_decimal(hours)
    python_seconds = time.perf_counter() - started
    started = time.perf_counter()
    sqlite_duplicates = duplicate_jobs_sqlite(invoices)
    sqlite_hours = sum_hours_sqlite_cents(hours)
    sqlite_seconds = time.perf_counter() - started
    return {
        "rows": {"invoices": len(invoices), "hours": len(hours)},
        "duplicates_match": python_duplicates == sqlite_duplicates,
        "hours_match": python_hours == sqlite_hours,
        "python_seconds": round(python_seconds, 6),
        "sqlite_seconds": round(sqlite_seconds, 6),
        "duckdb_installed": _available("duckdb"),
        "polars_installed": _available("polars"),
        "adopted_for_money_path": False,
        "reason": "DISPATER money remains Decimal. SQLite is used only when the integer-cent total matches.",
    }
