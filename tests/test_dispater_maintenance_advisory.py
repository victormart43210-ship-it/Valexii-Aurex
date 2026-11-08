"""Synthetic, original DISPATER EAM advisory contract tests."""
from copy import deepcopy

import pytest

from aurex.dispater_maintenance_advisory import MaintenanceInputError, assess_maintenance


def sample():
    return {
        "dataset_type": "SYNTHETIC_ONLY",
        "tenant_id": "T-1",
        "as_of": "2026-11-07",
        "assets": [{
            "asset_id": "PUMP-001", "tenant_id": "T-1",
            "last_service_date": "2026-10-01",
            "service_interval_days": 30,
            "meter_hours": "1250.00",
            "last_service_meter_hours": "1100.00",
            "service_interval_hours": "100.00",
        }],
    }


def test_calendar_and_meter_thresholds_are_deterministic():
    snapshot = sample()
    first = assess_maintenance(snapshot)
    assert first == assess_maintenance(deepcopy(snapshot))
    assert first["findings"][0]["reasons"] == "CALENDAR_DUE,METER_DUE"
    assert len(first["receipt_sha256"]) == 64


def test_no_autonomous_work_order_or_money_claim():
    report = assess_maintenance(sample())
    assert report["work_orders_created"] == 0
    assert report["confirmed_savings_usd"] == "0.00"
    assert report["financial_authority"] == "NONE"
    assert report["dispatch_authority"] == "NONE"
    assert report["findings"][0]["status"] == "PROPOSED_HUMAN_REVIEW"


def test_not_due_yields_no_findings():
    data = sample()
    data["assets"][0]["service_interval_days"] = 90
    data["assets"][0]["service_interval_hours"] = "300"
    assert assess_maintenance(data)["findings"] == []


@pytest.mark.parametrize("mutation", [
    lambda d: d.update(dataset_type="CUSTOMER_DATA"),
    lambda d: d["assets"][0].update(tenant_id="T-2"),
    lambda d: d["assets"].append(deepcopy(d["assets"][0])),
    lambda d: d["assets"][0].update(meter_hours="NaN"),
    lambda d: d["assets"][0].update(meter_hours="900"),
    lambda d: d["assets"][0].update(service_interval_days=0),
    lambda d: d["assets"][0].update(last_service_date="2027-01-01"),
])
def test_invalid_or_untrusted_inputs_fail_closed(mutation):
    data = sample()
    mutation(data)
    with pytest.raises(MaintenanceInputError):
        assess_maintenance(data)


def test_report_digest_changes_with_finding():
    a = sample()
    b = sample()
    b["assets"][0]["asset_id"] = "PUMP-002"
    assert assess_maintenance(a)["receipt_sha256"] != assess_maintenance(b)["receipt_sha256"]


def test_service_due_date_overflow_fails_closed():
    data = sample()
    data["as_of"] = "9999-12-31"
    data["assets"][0].update(last_service_date="9999-12-31", service_interval_days=1)
    with pytest.raises(MaintenanceInputError, match="due date"):
        assess_maintenance(data)
