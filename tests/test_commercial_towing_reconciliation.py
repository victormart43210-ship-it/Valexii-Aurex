"""Workstream C & D: Commercial Towing Reconciliation & Tenant Isolation Test Suite."""
from aurex.governance_math.industrial_demo import build_demo


def test_towing_reconciliation_eight_exception_scenarios() -> None:
    demo = build_demo(fixture="towing_v1")
    now_map = {item["category"]: item for item in demo["now"]}

    # 1. Driver CDL Qualification
    assert "driver_qualification" in now_map
    assert now_map["driver_qualification"]["status"] == "PRESENT_NOT_VERIFIED"

    # 2. Expired Vehicle Inspection
    assert "vehicle_inspection" in now_map
    assert now_map["vehicle_inspection"]["status"] == "EXPIRED"

    # 3. Conflicting Winch Maintenance Logs
    assert "maintenance" in now_map
    assert now_map["maintenance"]["status"] == "CONFLICTING"

    # 4. Unverified Service Ticket
    assert "service_ticket" in now_map
    assert now_map["service_ticket"]["status"] == "NOT_VERIFIED"

    # 5. Missing Incident Register
    assert "incident_register" in now_map
    assert now_map["incident_register"]["status"] == "MISSING"

    # 6. Advisory Authority Check
    assert demo["authority"] == "ADVISORY_ONLY_NO_CERTIFICATION"

    # 7. Snapshot Delta
    assert demo["changed"] == "NOT_VERIFIED_NO_PRIOR_SNAPSHOT"

    # 8. Human Review Action Required
    assert len(demo["next"]) > 0
    assert all(n["action"] == "HUMAN_REVIEW_REQUIRED" for n in demo["next"])


def test_tenant_isolation_negative_cases() -> None:
    # Verify Company A (Towing) vs Company B (Oilfield) records do not bleed
    towing_demo = build_demo(fixture="towing_v1")
    oilfield_demo = build_demo(fixture="oilfield_v1")

    assert towing_demo["operator"] == "Permian Recovery Services (fictional)"
    assert oilfield_demo["operator"] == "Permian Field Operations (fictional)"

    towing_cats = {item["category"] for item in towing_demo["now"]}
    oilfield_cats = {item["category"] for item in oilfield_demo["now"]}

    assert "driver_qualification" in towing_cats
    assert "crew_qualification" in oilfield_cats
    assert "driver_qualification" not in oilfield_cats
