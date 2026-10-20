"""Original fail-closed tests of international beta control claims."""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aurex.field_assurance import (
    CONTROLS, blank_claims, assess, main, profile, read_claims,
)

T0 = datetime(2026, 10, 19, 20, 0, tzinfo=UTC)


def filled() -> dict[str, object]:
    c = blank_claims("a" * 40)
    for row in c["claims"]:
        row.update({"status": "PASS", "evidence_sha256": "b" * 64,
                    "implementer_id": "eng-one", "reviewer_id": "reviewer-two",
                    "observed_at": T0.isoformat()})
    return c


def test_controls_pin_sources_and_locations() -> None:
    assert len(CONTROLS) == 12
    assert len({x.id for x in CONTROLS}) == len(CONTROLS)
    assert all(x.provenance.startswith("https://") for x in CONTROLS)
    assert any("London" in x.region for x in CONTROLS)
    assert any("NYDFS" in x.region for x in CONTROLS)
    assert any("Singapore" in x.region for x in CONTROLS)
    assert profile() == profile()
    assert len(profile()["profile_sha256"]) == 64


def test_template_is_hold_with_all_controls_pending() -> None:
    report, reviewable = assess(blank_claims("a" * 40), now=T0)
    assert not reviewable and report["structurally_complete_claims"] == 0
    assert len(report["unsubstantiated_or_pending_controls"]) == 12
    assert report["production_release"] == "HOLD"


def test_filled_claims_never_become_authority_or_certification() -> None:
    report, reviewable = assess(filled(), now=T0)
    assert reviewable and report["structurally_complete_claims"] == 12
    assert report["claim_consistency"] == "REVIEWABLE_CLAIMS_NOT_ATTESTED"
    assert report["reviewer_identity_verified"] is False
    assert report["independent_verification"] == "NOT_VERIFIED"
    assert report["production_release"] == "HOLD"
    assert report["spend_authority"] == "NONE"


def test_bad_profile_sha_is_rejected() -> None:
    c = filled()
    c["profile_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="profile SHA"):
        assess(c, now=T0)


def test_missing_control_is_hold() -> None:
    c = filled()
    c["claims"].pop()
    report, reviewable = assess(c, now=T0)
    assert not reviewable and len(report["missing_controls"]) == 1


def test_duplicate_control_is_rejected() -> None:
    c = filled()
    c["claims"][1]["id"] = c["claims"][0]["id"]
    with pytest.raises(ValueError, match="duplicate control ID"):
        assess(c, now=T0)


def test_invalid_evidence_digest_downgrades_to_hold() -> None:
    c = filled()
    c["claims"][0]["evidence_sha256"] = "0" * 64
    report, reviewable = assess(c, now=T0)
    assert not reviewable and len(report["unsubstantiated_or_pending_controls"]) == 1


def test_self_reviewer_downgrades_to_hold() -> None:
    c = filled()
    c["claims"][0]["reviewer_id"] = "eng-one"
    report, reviewable = assess(c, now=T0)
    assert not reviewable and report["structurally_complete_claims"] == 11


@pytest.mark.parametrize("when", [
    T0 - timedelta(days=31), T0 + timedelta(hours=2),
])
def test_stale_or_future_evidence_downgrades(when: datetime) -> None:
    c = filled()
    c["claims"][0]["observed_at"] = when.isoformat()
    report, reviewable = assess(c, now=T0)
    assert not reviewable and report["production_release"] == "HOLD"


def test_failed_control_blocks_reviewable_claims() -> None:
    c = filled()
    c["claims"][0].update({"status": "FAIL", "evidence_sha256": None,
                            "observed_at": None, "implementer_id": None, "reviewer_id": None})
    report, reviewable = assess(c, now=T0)
    assert not reviewable and len(report["reported_failed_controls"]) == 1


def test_pending_evidence_payload_rejected() -> None:
    c = blank_claims("a" * 40)
    c["claims"][0]["evidence_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="only PASS"):
        assess(c, now=T0)


def test_bad_or_unnamed_status_rejected() -> None:
    c = filled()
    c["claims"][0]["status"] = "APPROVE_PAYMENT"
    with pytest.raises(ValueError, match="invalid claimed status"):
        assess(c, now=T0)


def test_manifest_json_duplicate_keys_and_symlink_rejected(tmp_path: Path) -> None:
    p = tmp_path / "claim.json"
    p.write_text('{"schema":"a","schema":"b"}')
    with pytest.raises(ValueError, match="malformed"):
        read_claims(p)
    l = tmp_path / "symlink.json"
    l.symlink_to(p)
    with pytest.raises(ValueError, match="non-symlink"):
        read_claims(l)


def test_cli_prints_profile_and_hold_for_template(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--profile"]) == 0
    assert json.loads(capsys.readouterr().out)["schema"].endswith("profile.v1")
    assert main(["--template"]) == 0
    template = json.loads(capsys.readouterr().out)
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(template))
    assert main(["--assess", str(p)]) == 1
    assert json.loads(capsys.readouterr().out)["production_release"] == "HOLD"
    p.write_text("{}")
    assert main(["--assess", str(p)]) == 2


def test_untrusted_extra_fields_and_non_synthetic_flag_denied() -> None:
    c = filled()
    c["claims"][0]["raw_customer_invoice"] = "PII"
    with pytest.raises(ValueError, match="unrecognized claim fields"):
        assess(c, now=T0)
    c = filled()
    c["synthetic"] = False
    with pytest.raises(ValueError, match="synthetic flag"):
        assess(c, now=T0)
