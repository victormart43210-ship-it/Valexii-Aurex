"""Contract tests for the zero-cost synthetic industrial demo."""
from datetime import date

from aurex.governance_math.industrial_demo import build_demo


def test_demo_expected_findings() -> None:
    result = build_demo(date(2026, 10, 24))
    statuses = {f["category"]: f["status"] for f in result["now"]}
    assert statuses == {
        "driver_qualification": "PRESENT_NOT_VERIFIED",
        "vehicle_inspection": "EXPIRED",
        "maintenance": "CONFLICTING",
        "service_ticket": "NOT_VERIFIED",
        "incident_register": "MISSING",
    }


def test_demo_never_claims_compliance_or_verified_proof() -> None:
    result = build_demo(date(2026, 10, 24))
    assert result["demo"] is True
    assert result["authority"] == "ADVISORY_ONLY_NO_CERTIFICATION"
    assert result["proof"]["status"] == "NOT_VERIFIED"
    assert result["changed"] == "NOT_VERIFIED_NO_PRIOR_SNAPSHOT"
    assert len(result["next"]) == 4
