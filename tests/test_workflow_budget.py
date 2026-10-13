"""Adversarial budget-guard tests: no provider calls or real charges."""
from decimal import Decimal

import pytest

from aurex.workflows.budget import BudgetDenied, BudgetGuard, ProviderQuotaExhausted


def test_default_denies_paid_api() -> None:
    guard = BudgetGuard()
    with pytest.raises(BudgetDenied):
        guard.reserve("0.01")
    assert guard.reserve("0") == Decimal(0)


def test_reservation_and_settlement() -> None:
    guard = BudgetGuard(limit_usd=Decimal("0.10"))
    reservation = guard.reserve("0.07")
    with pytest.raises(BudgetDenied):
        guard.reserve("0.04")
    guard.settle(reservation, "0.03")
    assert guard.spent_usd == Decimal("0.03")
    assert guard.reserved_usd == Decimal(0)
    assert guard.reserve("0.07") == Decimal("0.07")


def test_overrun_does_not_silently_change_ledger() -> None:
    guard = BudgetGuard(limit_usd=Decimal(1))
    reservation = guard.reserve("0.20")
    with pytest.raises(BudgetDenied):
        guard.settle(reservation, "0.21")
    assert guard.spent_usd == Decimal(0)
    assert guard.reserved_usd == Decimal("0.20")


def test_quota_failure_is_terminal_for_guard() -> None:
    guard = BudgetGuard(limit_usd=Decimal(1))
    guard.mark_insufficient_quota()
    with pytest.raises(ProviderQuotaExhausted):
        guard.reserve("0")


@pytest.mark.parametrize("value", ["-0.01", "NaN", "Infinity", "bad"])
def test_invalid_money_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        BudgetGuard(limit_usd=Decimal(1)).reserve(value)


def test_release_requires_valid_reservation() -> None:
    guard = BudgetGuard(limit_usd=Decimal(1))
    guard.reserve("0.4")
    with pytest.raises(ValueError):
        guard.release("0.5")
    guard.release("0.4")
    assert guard.reserved_usd == Decimal(0)
