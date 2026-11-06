"""Independent multi-job/multi-invoice oracle (integer cents; shares no code with the engine).

Counts: synthetic/code-derived scenarios only; none are externally researched.
"""

import itertools
import random
from decimal import Decimal
from typing import Any

import pytest

from aurex.dispater_intelligence import RevenueLeakageEngine


def _money(c: int) -> str:
    return f"{c // 100}.{c % 100:02d}"


def _build(rng: random.Random) -> tuple[dict[str, Any], int, int, int]:
    jobs, rates, invoices = [], [], []
    under = over = unbilled = 0
    for n in range(rng.randint(2, 8)):
        jid, cust = f"J{n}", f"C{n}"
        rate = rng.randint(100, 900_000)
        jobs.append({"job_id": jid, "customer_id": cust, "service_code": "S", "date": "2026-03-01"})
        rates.append({"rate_id": f"R{n}", "customer_id": cust, "service_code": "S",
                      "start": "2026-01-01", "end": "2026-12-31", "amount": _money(rate)})
        kind = rng.choice(["exact", "under", "over", "none", "dup"])
        if kind == "none":
            unbilled += rate
        elif kind == "dup":
            first, second = rate, rng.randint(1, rate)
            invoices += [{"invoice_id": f"I{n}a", "job_id": jid, "amount": _money(first), "status": "open"},
                         {"invoice_id": f"I{n}b", "job_id": jid, "amount": _money(second), "status": "open"}]
            over += second  # invoice_id-ordered: 'a' is the primary charge, later ones are duplicates
        else:
            amt = {"exact": rate, "under": rate - rng.randint(1, rate), "over": rate + rng.randint(1, 5000)}[kind]
            invoices.append({"invoice_id": f"I{n}", "job_id": jid, "amount": _money(amt), "status": "open"})
            under += max(rate - amt, 0)
            over += max(amt - rate, 0)
    ds = {"tenant_id": "t", "dataset_type": "SYNTHETIC_ONLY", "jobs": jobs, "rates": rates,
          "invoices": invoices, "payments": []}
    return ds, under, over, unbilled


@pytest.mark.parametrize("seed", range(40))
def test_multijob_matches_oracle_and_ignores_row_order(seed: int) -> None:
    rng = random.Random(seed)
    ds, under, over, unbilled = _build(rng)
    s = RevenueLeakageEngine("t").reconcile_records(ds)["financial_summary"]
    assert Decimal(s["potential_overbilling_usd"]) == Decimal(over) / 100
    assert Decimal(s["potential_underbilling_usd"]) == Decimal(under + unbilled) / 100
    assert s["confirmed_recovery_usd"] == "0.00" and s["human_confirmed_discrepancy_usd"] == "0.00"
    shuffled = {**ds, "invoices": rng.sample(ds["invoices"], len(ds["invoices"]))}
    s2 = RevenueLeakageEngine("t").reconcile_records(shuffled)["financial_summary"]
    assert s2 == s


def test_duplicate_exposure_is_independent_of_invoice_order() -> None:
    base = {"tenant_id": "t", "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
            "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1",
                       "start": "2026-01-01", "end": "2026-12-31", "amount": "100.00"}],
            "payments": []}
    a = {"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "open"}
    b = {"invoice_id": "I2", "job_id": "J1", "amount": "60.00", "status": "open"}
    outs = {RevenueLeakageEngine("t").reconcile_records({**base, "invoices": list(p)})["financial_summary"]["potential_overbilling_usd"]
            for p in itertools.permutations([a, b])}
    assert outs == {"60.00"}
