"""Offline, bounded, adversarial synthetic-company audit-preparation checks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from aurex.audit_pilot import _canonical, run_packet, verify_report
from workstation.audit_pilot_cli import main

SOURCE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_company_packet"


def packet(tmp_path: Path) -> Path:
    target = tmp_path / "packet"
    shutil.copytree(SOURCE, target)
    return target


def rewrite_document(root: Path, kind: str, updates: dict[str, object]) -> None:
    document_path = root / (kind + ".json")
    item = json.loads(document_path.read_text())
    item.update(updates)
    raw = (json.dumps(item, sort_keys=True, indent=2) + "\n").encode()
    document_path.write_bytes(raw)
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest["records"]:
        if entry["type"] == kind:
            entry["sha256"] = hashlib.sha256(raw).hexdigest()
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")


def test_one_consolidated_review_with_seven_real_deterministic_discrepancies() -> None:
    report = run_packet(SOURCE)
    assert report["source_count"] == 9
    assert report["finding_count"] == 7
    assert report["one_view"]["tabs_added"] == 0
    assert [x["code"] for x in report["findings"]] == [
        "DOT_SUPPORT_NOT_IN_PACKET", "INSURANCE_CERTIFICATE_EXPIRED",
        "INVOICE_EXCEEDS_PO", "INVOICE_VS_FIELD_TICKET", "LEDGER_VS_INVOICE",
        "PAYMENT_VS_BANK_STATEMENT", "TAX_SUMMARY_VS_LEDGER",
    ]
    assert all(len(x["sha256"]) == 64 for x in report["source_receipts"])
    assert all(x["disposition"] == "HUMAN_REVIEW_REQUIRED" for x in report["findings"])
    assert report["production_authority"] == "HOLD"
    assert report["audit_opinion"] == "NONE"
    assert report["irs_dot_insurance_compliance"] == "NOT_DETERMINED"
    assert report["llm_training"] == "DISABLED"
    assert verify_report(SOURCE, report)


def test_exact_decimal_differences() -> None:
    report = run_packet(SOURCE)
    observed = {x["code"]: x["observed"] for x in report["findings"]}
    assert observed["INVOICE_EXCEEDS_PO"] == "difference_usd=6000.00"
    assert observed["PAYMENT_VS_BANK_STATEMENT"] == "difference_usd=50.00"
    assert observed["LEDGER_VS_INVOICE"] == "difference_usd=2000.00"
    assert observed["TAX_SUMMARY_VS_LEDGER"] == "difference_usd=4000.00"


def test_no_original_bytes_modified(tmp_path: Path) -> None:
    root = packet(tmp_path)
    before = {item.name: item.read_bytes() for item in root.iterdir()}
    first = run_packet(root)
    second = run_packet(root)
    assert first == second
    assert before == {item.name: item.read_bytes() for item in root.iterdir()}


def test_unmanifested_file_and_manifest_digest_tamper_rejected(tmp_path: Path) -> None:
    root = packet(tmp_path)
    (root / "extra.json").write_text("{}")
    with pytest.raises(ValueError, match="undeclared"):
        run_packet(root)
    (root / "extra.json").unlink()
    (root / "invoice.json").write_text('{"tampered": true}')
    with pytest.raises(ValueError, match="digest mismatch"):
        run_packet(root)


def test_duplicate_json_keys_rejected(tmp_path: Path) -> None:
    root = packet(tmp_path)
    (root / "manifest.json").write_text('{"synthetic": true,"synthetic":true}')
    with pytest.raises(ValueError, match="malformed UTF-8 JSON"):
        run_packet(root)


def test_missing_original_rejected(tmp_path: Path) -> None:
    root = packet(tmp_path)
    (root / "field_ticket.json").unlink()
    with pytest.raises(ValueError):
        run_packet(root)


def test_symlink_input_denied(tmp_path: Path) -> None:
    root = packet(tmp_path)
    (root / "invoice.json").unlink()
    (root / "invoice.json").symlink_to(root / "purchase_order.json")
    with pytest.raises(ValueError):
        run_packet(root)


def test_path_traversal_manifest_refused(tmp_path: Path) -> None:
    root = packet(tmp_path)
    m = json.loads((root / "manifest.json").read_text())
    m["records"][0]["file"] = "../secret.json"
    (root / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(ValueError, match="invalid file"):
        run_packet(root)


def test_type_mismatch_and_invalid_decimal_rejected(tmp_path: Path) -> None:
    root = packet(tmp_path)
    rewrite_document(root, "invoice", {"declared_total_usd": "48000.001"})
    with pytest.raises(ValueError, match="fixed-cent"):
        run_packet(root)


def test_invoice_arithmetic_conflict_is_rejected(tmp_path: Path) -> None:
    root = packet(tmp_path)
    rewrite_document(root, "invoice", {"quantity": 12})
    with pytest.raises(ValueError, match="invoice line arithmetic"):
        run_packet(root)


def test_po_arithmetic_conflict_is_rejected(tmp_path: Path) -> None:
    root = packet(tmp_path)
    rewrite_document(root, "purchase_order", {"quantity": 9})
    with pytest.raises(ValueError, match="PO authorization arithmetic"):
        run_packet(root)


def test_date_validation_denies_bad_insurance_date(tmp_path: Path) -> None:
    root = packet(tmp_path)
    rewrite_document(root, "insurance_certificate", {"expires_on": "2026-02-30"})
    with pytest.raises(ValueError, match="ISO date"):
        run_packet(root)


def test_untagged_real_customer_packet_refused(tmp_path: Path) -> None:
    root = packet(tmp_path)
    m = json.loads((root / "manifest.json").read_text())
    m["synthetic"] = False
    (root / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(ValueError, match="fictional fixture"):
        run_packet(root)


def test_modified_final_report_detected(tmp_path: Path) -> None:
    root = packet(tmp_path)
    report = run_packet(root)
    report["findings"][0]["disposition"] = "APPROVED"
    assert not verify_report(root, report)


def test_recomputed_report_sha_without_original_sources_cannot_fool_replay(tmp_path: Path) -> None:
    root = packet(tmp_path)
    report = run_packet(root)
    report["findings"].clear()
    report["report_sha256"] = hashlib.sha256(
        _canonical({k: v for k, v in report.items() if k != "report_sha256"})
    ).hexdigest()
    assert not verify_report(root, report)


def test_cli_writes_secure_new_report_then_replays(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = packet(tmp_path)
    outfile = tmp_path / "report.json"
    assert main(["--packet", str(root), "--out", str(outfile)]) == 0
    assert outfile.exists()
    assert main(["--packet", str(root), "--verify", str(outfile)]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert json.loads(lines[-1])["status"] == "LOCAL_REPLAY_MATCH_NOT_INDEPENDENT_WITNESS"
    with pytest.raises(SystemExit):
        main(["--packet", str(root), "--out", str(outfile)])


def test_report_cannot_be_written_inside_original_packet(tmp_path: Path) -> None:
    root = packet(tmp_path)
    with pytest.raises(SystemExit):
        main(["--packet", str(root), "--out", str(root / "report.json")])
