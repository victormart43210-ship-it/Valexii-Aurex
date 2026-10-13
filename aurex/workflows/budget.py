"""Fail-closed, dependency-free execution budget guard for AUREX adapters.

This module does not make network requests or infer billing from token estimates.
Only an explicit, trusted actual_spend_usd update records completed charges.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class BudgetDenied(RuntimeError):
    """An operation must not be dispatched under the current budget."""


class ProviderQuotaExhausted(BudgetDenied):
    """Provider explicitly reported insufficient credits."""


def _amount(value: str | int | Decimal) -> Decimal:
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid monetary amount") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError("monetary amounts must be finite and nonnegative")
    return amount


@dataclass
class BudgetGuard:
    """Default-deny paid API calls; reserve before dispatch, settle afterward."""

    limit_usd: Decimal = Decimal("0")
    spent_usd: Decimal = Decimal("0")
    reserved_usd: Decimal = Decimal("0")
    quota_exhausted: bool = False

    def __post_init__(self) -> None:
        self.limit_usd = _amount(self.limit_usd)
        self.spent_usd = _amount(self.spent_usd)
        self.reserved_usd = _amount(self.reserved_usd)
        if self.spent_usd + self.reserved_usd > self.limit_usd:
            raise ValueError("initial budget exceeded")

    def reserve(self, estimated_max_usd: str | int | Decimal) -> Decimal:
        """Reserve a conservative maximum; caller must settle or release."""
        estimate = _amount(estimated_max_usd)
        if self.quota_exhausted:
            raise ProviderQuotaExhausted("provider quota exhausted")
        if self.spent_usd + self.reserved_usd + estimate > self.limit_usd:
            raise BudgetDenied("API budget exceeded")
        self.reserved_usd += estimate
        return estimate

    def settle(
        self, reserved_usd: str | int | Decimal, actual_spend_usd: str | int | Decimal
    ) -> None:
        """Settle a reserved request; fail closed if actual cost exceeds reservation."""
        reserved = _amount(reserved_usd)
        actual = _amount(actual_spend_usd)
        if reserved > self.reserved_usd:
            raise ValueError("reservation not found")
        if actual > reserved:
            raise BudgetDenied("actual cost exceeds reservation; reconcile externally")
        self.reserved_usd -= reserved
        self.spent_usd += actual

    def release(self, reserved_usd: str | int | Decimal) -> None:
        """Release an unspent reservation after a confirmed no-charge cancellation."""
        reserved = _amount(reserved_usd)
        if reserved > self.reserved_usd:
            raise ValueError("reservation not found")
        self.reserved_usd -= reserved

    def mark_insufficient_quota(self) -> None:
        """Permanently stop new paid dispatches until an operator creates a new guard."""
        self.quota_exhausted = True
