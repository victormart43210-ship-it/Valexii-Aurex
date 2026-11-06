"""Independent file corpus -> ingest -> API/store -> dashboard -> monitoring rehearsal.

Run against the exact pinned Cursor commit; never imports its test oracle.
This harness is a verification artifact, not another product pipeline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    root = args.candidate_root.resolve()
    actual = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != args.expected_sha:
        raise SystemExit(f"Candidate SHA mismatch: {actual}")
    sys.path.insert(0, str(root))
    import aurex.dispater_ingest as ingest

    if not Path(ingest.__file__).resolve().is_relative_to(root):
        raise SystemExit("Imported a different checkout")
    from aurex.dispater_monitor import monitor_increment

    from aurex.dispater_intelligence import RevenueLeakageEngine

    corpus = Path(__file__).resolve().parents[2] / "tests/fixtures/ccxxxvi_golden"
    manifest = json.loads((corpus / "manifest.json").read_text())
    tenant = manifest["tenant_id"]
    combined = dict(
        tenant_id=tenant, dataset_type="SYNTHETIC_ONLY", jobs=[], invoices=[], rates=[], payments=[]
    )
    provenance_count = 0
    for item in manifest["files"]:
        raw = (corpus / item["filename"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        result = ingest.ingest_source(tenant, item["filename"], raw, kind="json")
        assert result["source_sha256"] == item["sha256"]
        source = json.loads(raw)
        for table in ("jobs", "invoices", "rates", "payments"):
            assert result["dataset"][table] == source[table], (item["filename"], table)
            combined[table].extend(result["dataset"][table])
        for entry in result["provenance"]:
            assert entry["source_sha256"] == item["sha256"]
            assert entry["tenant_id"] == tenant
            assert entry["source_filename"] == item["filename"]
            assert int(entry["row"]) >= 1
        provenance_count += len(result["provenance"])
    report = RevenueLeakageEngine(tenant).reconcile_records(combined)
    for key, value in manifest["expected"].items():
        assert report["financial_summary"][key] == value, (
            key,
            report["financial_summary"][key],
            value,
        )
    assert report["authority_state"] == "HOLD"
    assert all(f["qualification"] != "CONFIRMED_DISCREPANCY" for f in report["findings"])
    additions = dict(
        tenant_id=tenant,
        dataset_type="SYNTHETIC_ONLY",
        jobs=[dict(job_id="G37", customer_id="C", service_code="TOW", date="2027-01-01")],
        invoices=[],
        rates=[],
        payments=[],
    )
    movement = monitor_increment(tenant, combined, additions)
    for key, value in manifest["month37_expected"].items():
        assert movement[key] == value
    assert movement == monitor_increment(tenant, combined, additions)
    with tempfile.TemporaryDirectory(prefix="ccxxxvi-golden-") as tmp:
        token = secrets.token_hex(32)
        os.environ.update(
            AUREX_SERVICE_TOKEN=token,
            AUREX_DISPATER_DB=str(Path(tmp) / "audit.sqlite"),
            AUREX_DB_PATH=str(Path(tmp) / "jobs.sqlite"),
            AUREX_DISPATER_TENANT_GRANTS=json.dumps(
                {hashlib.sha256(token.encode()).hexdigest(): [tenant]}
            ),
            AUREX_DISPATER_RECEIPT_KEYS=json.dumps({"test": secrets.token_hex(32)}),
            AUREX_DISPATER_RECEIPT_ACTIVE_KID="test",
        )
        from fastapi.testclient import TestClient

        from aurex.api import app

        headers = {"Authorization": f"Bearer {token}"}
        with TestClient(app) as client:
            response = client.post("/v1/dispater/reconciliation", json=combined, headers=headers)
            assert response.status_code == 200, response.text
            stored = response.json()
            assert stored["receipt_binding"] == "BOUND_V2"
            dashboard = client.get(
                "/v1/dispater/dashboard", params={"tenant_id": tenant}, headers=headers
            )
            assert dashboard.status_code == 200
            for key, value in manifest["expected"].items():
                assert dashboard.json()[key] == value, key
            unauthorized = client.get(
                "/v1/dispater/dashboard", params={"tenant_id": "other"}, headers=headers
            )
            assert unauthorized.status_code == 403
            repeated = client.post("/v1/dispater/reconciliation", json=combined, headers=headers)
            assert repeated.json()["run_id"] == stored["run_id"]
        # A different process reopens the DB and verifies receipt authenticity.
        child_code = (
            "import json;from aurex.dispater_store import get_run;r=get_run("
            + repr(tenant)
            + ","
            + repr(stored["run_id"])
            + ');print(json.dumps(r["financial_summary"]))'
        )
        child_env = dict(os.environ, PYTHONPATH=str(root))
        restarted = json.loads(
            subprocess.check_output(
                [sys.executable, "-c", child_code], cwd=root, env=child_env, text=True
            )
        )
        for key, value in manifest["expected"].items():
            assert restarted[key] == value
    print(
        json.dumps(
            {
                "status": "PASS",
                "candidate_sha": actual,
                "files": len(manifest["files"]),
                "provenance_rows": provenance_count,
                "expected": manifest["expected"],
                "month37": manifest["month37_expected"],
                "api_dashboard": "PASS",
                "tenant_denial": "PASS",
                "receipt_v2": "PASS",
                "idempotency": "PASS",
                "store_process_restart": "PASS",
                "monitoring": "IN_MEMORY_ONLY; replay checked, no persistent monitor claimed",
                "browser": "NOT_RUN",
                "real_world_independent_verification": "REVIEW_PENDING",
            }
        )
    )


if __name__ == "__main__":
    main()
