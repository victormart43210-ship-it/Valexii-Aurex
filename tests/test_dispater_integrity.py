"""Financial adapter independently asserts lineage and conservative claims."""
from copy import deepcopy

from aurex.dispater_intelligence import RevenueLeakageEngine, digest, verify_receipt


def snapshot():
    return {"dataset_type": "SYNTHETIC_ONLY", "tenant_id": "t", "jobs": [
        {"job_id": "j", "customer_id": "c", "service_code": "tow", "date": "2026-11-01"}],
        "rates": [{"rate_id": "r", "customer_id": "c", "service_code": "tow",
                   "start": "2026-01-01", "end": "2026-12-31", "amount": "100.01"}],
        "invoices": [], "payments": []}


def test_unbilled_calculation_cites_rate_and_one_source_root():
    data = snapshot()
    report = RevenueLeakageEngine("t").reconcile_records(data)
    finding = report["findings"][0]
    assert finding["exposure_usd"] == "100.01"
    assert {e["kind"] for e in finding["evidence"]} == {"job", "rate"}
    integrity = finding["evidence_integrity"]
    assert integrity["independent_root_count"] == 1
    assert integrity["qualification"] == "CALCULATED"
    assert integrity["observation_state"] == "UNKNOWN"
    assert integrity["independent_verification"] == "NOT VERIFIED"
    assert integrity["source_root_sha256"] == digest(data)
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert report["evidence_bundle"]["submitted_snapshot"] == data
    assert verify_receipt(report)
    body = {k: v for k, v in finding.items() if k != "finding_sha256"}
    assert finding["finding_sha256"] == digest(body)


def test_original_and_normalized_records_are_distinct():
    data = snapshot()
    data["jobs"][0]["job_id"] = " j "
    report = RevenueLeakageEngine("t").reconcile_records(data)
    manifest = report["evidence_bundle"]["lineage"]
    job = next(item for item in manifest if item["kind"] == "job")
    assert job["original_sha256"] == digest(data["jobs"][0])
    assert job["normalized_sha256"] != job["original_sha256"]
    assert job["source_root_sha256"] == digest(data)
    changed = deepcopy(report)
    changed["evidence_bundle"]["submitted_snapshot"]["jobs"][0]["job_id"] = "forged"
    assert not verify_receipt(changed)


def test_contradiction_and_missing_rate_never_become_clean():
    data = snapshot()
    data["rates"].append(dict(data["rates"][0], rate_id="r2", amount="200.00"))
    report = RevenueLeakageEngine("t").reconcile_records(data)
    conflict = next(f for f in report["findings"] if f["code"] == "AMBIGUOUS_RATE")
    assert conflict["evidence_integrity"]["observation_state"] == "HIGH_CONFLICT"
    data["rates"] = []
    report = RevenueLeakageEngine("t").reconcile_records(data)
    missing = next(f for f in report["findings"] if f["code"] == "RATE_UNVERIFIED")
    assert missing["evidence_integrity"]["observation_state"] == "UNAVAILABLE"
    assert report["evidence_status"] == "NOT VERIFIED"
