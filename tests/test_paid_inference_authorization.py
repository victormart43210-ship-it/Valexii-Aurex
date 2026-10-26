"""Paid inference must require a strictly positive budget reservation."""

from decimal import Decimal

import pytest

from aurex.workflows.budget import BudgetDenied, BudgetGuard


@pytest.mark.parametrize(
    "amount",
    ["0", "0.00", Decimal("0"), "-0.01", "NaN", "Infinity"],
)
def test_paid_inference_rejects_invalid_reservations(amount):
    guard = BudgetGuard(limit_usd=Decimal("1.00"))

    with pytest.raises((BudgetDenied, ValueError)):
        guard.authorize_paid_inference(amount)

    assert guard.reserved_usd == Decimal("0")


def test_paid_inference_requires_available_budget():
    guard = BudgetGuard()

    with pytest.raises(BudgetDenied):
        guard.authorize_paid_inference("0.01")


def test_paid_inference_positive_reservation():
    guard = BudgetGuard(limit_usd=Decimal("1.00"))

    reservation = guard.authorize_paid_inference("0.25")

    assert reservation == Decimal("0.25")
    assert guard.reserved_usd == Decimal("0.25")
