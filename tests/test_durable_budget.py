"""Durable budget ledger security requirements.

These tests use temporary SQLite databases.
No external inference or provider requests.
"""

from decimal import Decimal

import pytest

from aurex.workflows.budget import BudgetDenied
from aurex.workflows.durable_budget import DurableBudgetLedger


def test_default_zero_budget_denies_paid_inference(tmp_path):
    db = tmp_path / "budget.db"
    ledger = DurableBudgetLedger(str(db), allow_temporary_for_testing=True)

    with pytest.raises(BudgetDenied):
        ledger.reserve("request-1", Decimal("0.01"))


def test_zero_reservation_cannot_authorize_paid_inference(tmp_path):
    db = tmp_path / "budget.db"
    ledger = DurableBudgetLedger(str(db), allow_temporary_for_testing=True)

    with pytest.raises((BudgetDenied, ValueError)):
        ledger.reserve("request-1", Decimal("0"))


def test_reservation_survives_restart(tmp_path):
    db = tmp_path / "budget.db"

    first = DurableBudgetLedger(
        str(db), limit_usd=Decimal("1.00"), allow_temporary_for_testing=True
    )

    first.reserve("request-1", Decimal("0.40"))

    restarted = DurableBudgetLedger(str(db), allow_temporary_for_testing=True)

    assert restarted.reserved_usd == Decimal("0.40")

    with pytest.raises(BudgetDenied):
        restarted.reserve("request-2", Decimal("0.70"))


def test_duplicate_request_cannot_reserve_twice(tmp_path):
    db = tmp_path / "budget.db"

    ledger = DurableBudgetLedger(
        str(db), limit_usd=Decimal("1.00"), allow_temporary_for_testing=True
    )

    ledger.reserve("request-1", Decimal("0.40"))

    with pytest.raises((BudgetDenied, ValueError)):
        ledger.reserve("request-1", Decimal("0.40"))

    assert ledger.reserved_usd == Decimal("0.40")


def test_unknown_billing_retains_reservation(tmp_path):
    db = tmp_path / "budget.db"

    ledger = DurableBudgetLedger(
        str(db), limit_usd=Decimal("1.00"), allow_temporary_for_testing=True
    )

    ledger.reserve("request-1", Decimal("0.40"))
    ledger.mark_unknown("request-1")

    assert ledger.reserved_usd == Decimal("0.40")

    restarted = DurableBudgetLedger(str(db), allow_temporary_for_testing=True)

    assert restarted.reserved_usd == Decimal("0.40")


def test_concurrent_reservations_cannot_exceed_budget(tmp_path):
    """Two simultaneous workers must not overspend."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    db = tmp_path / "concurrent_budget.db"

    DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    barrier = Barrier(2)

    def attempt(request_id):
        ledger = DurableBudgetLedger(
            str(db),
            allow_temporary_for_testing=True,
        )

        barrier.wait(timeout=10)

        try:
            ledger.reserve(request_id, Decimal("0.75"))
            return "approved"
        except BudgetDenied:
            return "denied"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(attempt, "worker-1"),
            executor.submit(attempt, "worker-2"),
        ]
        results = [future.result(timeout=15) for future in futures]

    assert sorted(results) == ["approved", "denied"]

    restarted = DurableBudgetLedger(
        str(db),
        allow_temporary_for_testing=True,
    )

    assert restarted.reserved_usd == Decimal("0.75")


def test_settlement_survives_restart(tmp_path):
    db = tmp_path / "settlement.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    ledger.reserve("request-1", Decimal("0.40"))
    ledger.settle("request-1", Decimal("0.25"))

    restarted = DurableBudgetLedger(
        str(db),
        allow_temporary_for_testing=True,
    )

    assert restarted.spent_usd == Decimal("0.25")
    assert restarted.reserved_usd == Decimal("0")

    with pytest.raises(BudgetDenied):
        restarted.reserve("request-2", Decimal("0.80"))


def test_settlement_cannot_exceed_reservation(tmp_path):
    db = tmp_path / "settlement_limit.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    ledger.reserve("request-1", Decimal("0.40"))

    with pytest.raises(BudgetDenied):
        ledger.settle("request-1", Decimal("0.50"))

    assert ledger.reserved_usd == Decimal("0.40")


def test_duplicate_settlement_is_rejected(tmp_path):
    db = tmp_path / "duplicate_settlement.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    ledger.reserve("request-1", Decimal("0.40"))
    ledger.settle("request-1", Decimal("0.25"))

    with pytest.raises((BudgetDenied, ValueError)):
        ledger.settle("request-1", Decimal("0.25"))

    assert ledger.spent_usd == Decimal("0.25")


def test_settled_request_id_cannot_be_reused(tmp_path):
    """A completed request must never receive another reservation."""
    db = tmp_path / "settled_replay.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    ledger.reserve("request-1", Decimal("0.40"))
    ledger.settle("request-1", Decimal("0.25"))

    restarted = DurableBudgetLedger(
        str(db),
        allow_temporary_for_testing=True,
    )

    with pytest.raises(BudgetDenied):
        restarted.reserve("request-1", Decimal("0.40"))

    assert restarted.spent_usd == Decimal("0.25")
    assert restarted.reserved_usd == Decimal("0")


def test_multiprocess_reservations_cannot_exceed_budget(tmp_path):
    """Independent processes must share one atomic budget."""
    import subprocess
    import sys

    db = tmp_path / "multiprocess_budget.db"

    DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    worker = """
import sys
from decimal import Decimal
from aurex.workflows.budget import BudgetDenied
from aurex.workflows.durable_budget import DurableBudgetLedger

db, request_id = sys.argv[1:3]

ledger = DurableBudgetLedger(
    db,
    allow_temporary_for_testing=True,
)

try:
    ledger.reserve(request_id, Decimal("0.75"))
    print("APPROVED")
except BudgetDenied:
    print("DENIED")
"""

    processes = [
        subprocess.Popen(
            [
                sys.executable,
                "-c",
                worker,
                str(db),
                f"worker-{i}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for i in range(2)
    ]

    results = []

    for process in processes:
        stdout, stderr = process.communicate(timeout=15)

        assert process.returncode == 0, stderr
        results.append(stdout.strip())

    assert sorted(results) == ["APPROVED", "DENIED"]

    restarted = DurableBudgetLedger(
        str(db),
        allow_temporary_for_testing=True,
    )

    assert restarted.reserved_usd == Decimal("0.75")


def test_worker_crash_preserves_budget_reservation(tmp_path):
    """A worker crash must not release an unsettled reservation."""
    import subprocess
    import sys

    db = tmp_path / "crash_recovery.db"

    DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    worker = """
import os
import sys
from decimal import Decimal
from aurex.workflows.durable_budget import DurableBudgetLedger

ledger = DurableBudgetLedger(
    sys.argv[1],
    allow_temporary_for_testing=True,
)

ledger.reserve("crashed-worker", Decimal("0.75"))

# Simulate abrupt process termination after reservation commits.
os._exit(17)
"""

    result = subprocess.run(
        [sys.executable, "-c", worker, str(db)],
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 17, result.stderr

    restarted = DurableBudgetLedger(
        str(db),
        allow_temporary_for_testing=True,
    )

    assert restarted.reserved_usd == Decimal("0.75")

    with pytest.raises(BudgetDenied):
        restarted.reserve("new-worker", Decimal("0.50"))

    restarted.mark_unknown("crashed-worker")

    assert restarted.reserved_usd == Decimal("0.75")


def test_unknown_billing_cannot_be_settled_or_reused(tmp_path):
    """Unknown provider charges must remain locked after restart."""
    db = tmp_path / "unknown_billing.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    ledger.reserve("request-1", Decimal("0.75"))
    ledger.mark_unknown("request-1")

    restarted = DurableBudgetLedger(
        str(db),
        allow_temporary_for_testing=True,
    )

    assert restarted.reserved_usd == Decimal("0.75")

    with pytest.raises(BudgetDenied):
        restarted.settle("request-1", Decimal("0.25"))

    with pytest.raises(BudgetDenied):
        restarted.reserve("request-1", Decimal("0.10"))

    with pytest.raises(BudgetDenied):
        restarted.reserve("request-2", Decimal("0.50"))

    assert restarted.reserved_usd == Decimal("0.75")
    assert restarted.spent_usd == Decimal("0")


def test_corrupted_budget_limit_fails_closed(tmp_path):
    """Corrupted budget limits must never authorize spending."""
    import sqlite3

    db = tmp_path / "corrupted_limit.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    with sqlite3.connect(db) as conn:
        conn.execute(
            "UPDATE budget_control SET limit_usd = ? WHERE id = 1",
            ("NaN",),
        )

    with pytest.raises(BudgetDenied):
        ledger.reserve("request-1", Decimal("0.10"))


def test_negative_budget_limit_fails_closed(tmp_path):
    """Negative stored limits must never authorize spending."""
    import sqlite3

    db = tmp_path / "negative_limit.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    with sqlite3.connect(db) as conn:
        conn.execute(
            "UPDATE budget_control SET limit_usd = ? WHERE id = 1",
            ("-1.00",),
        )

    with pytest.raises(BudgetDenied):
        ledger.reserve("request-1", Decimal("0.10"))


def test_corrupted_reservation_amount_is_explicitly_denied(tmp_path):
    """Corrupt existing reservations must cause explicit denial."""
    import sqlite3

    db = tmp_path / "corrupt_reservation.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    ledger.reserve("original", Decimal("0.25"))

    with sqlite3.connect(db) as conn:
        conn.execute(
            "UPDATE budget_reservations "
            "SET amount_usd = ? WHERE request_id = ?",
            ("NaN", "original"),
        )

    with pytest.raises(BudgetDenied):
        ledger.reserve("new-request", Decimal("0.10"))


def test_unverified_provider_charge_cannot_reconcile(tmp_path):
    """Unverified provider charges cannot become authoritative."""
    db = tmp_path / "reconciliation.db"

    ledger = DurableBudgetLedger(
        str(db),
        limit_usd=Decimal("1.00"),
        allow_temporary_for_testing=True,
    )

    ledger.reserve("request-1", Decimal("0.50"))
    ledger.mark_unknown("request-1")

    with pytest.raises(BudgetDenied):
        ledger.reconcile(
            request_id="request-1",
            actual_usd=Decimal("0.20"),
            provider_verified=False,
        )

    assert ledger.reserved_usd == Decimal("0.50")
    assert ledger.spent_usd == Decimal("0")
