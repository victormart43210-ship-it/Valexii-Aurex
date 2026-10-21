"""Adversarial synthetic-only tests for the local AUREX financial evidence spine."""
from __future__ import annotations

import sqlite3
import zipfile
from pathlib import Path

import pytest

from workstation.financial_evidence_batch import (
    extract_formulas, intake, report, sha256_file,
)


def fake_workbook(path: Path, *, modified: bool = False, bad_member: bool = False) -> None:
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rid = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        if bad_member:
            z.writestr("../evil", "do-not-extract")
        z.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="{ns}" xmlns:r="{rid}"><sheets>'
            '<sheet name="Ticket" sheetId="1" r:id="rId1"/>'
            '<sheet name="Hidden" sheetId="2" state="hidden" r:id="rId2"/>'
            "</sheets></workbook>",
        )
        z.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Target="worksheets/sheet2.xml"/>'
            "</Relationships>",
        )
        value = "7" if modified else "600"
        z.writestr(
            "xl/worksheets/sheet1.xml",
            f'<worksheet xmlns="{ns}"><sheetData><row r="1">'
            f'<c r="A1"><f>200*3</f><v>{value}</v></c>'
            '<c r="B1"><f t="shared" si="0"/><v>8</v></c>'
            "</row></sheetData></worksheet>",
        )
        z.writestr(
            "xl/worksheets/sheet2.xml",
            f'<worksheet xmlns="{ns}"><sheetData><row r="1">'
            '<c r="A1"><f>42</f><v>42</v></c>'
            "</row></sheetData></worksheet>",
        )
        z.writestr("xl/externalLinks/externalLink1.xml", "<externalLink/>")


def test_spreadsheet_formulas_are_observations_not_calculations(tmp_path: Path) -> None:
    file = tmp_path / "source.xlsx"
    fake_workbook(file)
    witnesses, flags = extract_formulas(file)
    assert len(witnesses) == 3
    assert ("Ticket", "A1", "200*3", "600", "FORMULA_UNVERIFIED") in witnesses
    assert ("Ticket", "B1", "", "8", "SHARED_FORMULA_NOT_EXPANDED") in witnesses
    assert "HIDDEN_SHEET_PRESENT" in flags
    assert "EXTERNAL_LINKS_PRESENT" in flags


def test_preflight_is_no_write(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file = source / "ticket.pdf"
    file.write_bytes(b"%PDF-1.5 synthetic")
    db = tmp_path / "aurex.db"
    out = intake(source, db, "tenant_1", "oilfield", limit=10)
    assert out["seen"] == 1
    assert out["indexed"] == 0
    assert out["mode"] == "PREFLIGHT_ONLY"
    assert not db.exists()
    assert file.read_bytes() == b"%PDF-1.5 synthetic"


def test_tenant_separation_and_repeatable_receipts(tmp_path: Path) -> None:
    src = tmp_path / "source"
    src.mkdir()
    fake_workbook(src / "ticket.xlsx")
    db = tmp_path / "private.db"
    first = intake(src, db, "tenant_a", "oilfield", limit=10, execute=True)
    assert first["indexed"] == 1 and first["formulas_observed"] == 3
    second = intake(src, db, "tenant_a", "oilfield", limit=10, execute=True)
    assert second["unchanged"] == 1 and second["indexed"] == 0
    assert report(db, "tenant_b", "oilfield")["documents"] == 0
    a = report(db, "tenant_a", "oilfield")
    assert a["formula_witnesses"] == 3
    assert a["source_issuer_authenticated"] is False
    assert a["training_authorization"] == "NONE"
    assert a["release"] == "HOLD"
    assert report(db, "tenant_a", "oilfield")["receipt_sha256"] == a["receipt_sha256"]
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT SUM(training_allowed) FROM documents").fetchone()[0] == 0


def test_batches_really_progress_to_next_files(tmp_path: Path) -> None:
    src = tmp_path / "source"
    src.mkdir()
    for i in range(5):
        (src / f"{i}.pdf").write_bytes(b"%PDF" + bytes([i]))
    db = tmp_path / "private.db"
    assert intake(src, db, "t", "p", limit=2, execute=True)["indexed"] == 2
    second = intake(src, db, "t", "p", limit=2, execute=True)
    assert second["indexed"] == 2 and second["unchanged"] == 2
    assert intake(src, db, "t", "p", limit=2, execute=True)["indexed"] == 1
    assert report(db, "t", "p")["documents"] == 5


def test_changed_source_replaces_stale_formula_witnesses(tmp_path: Path) -> None:
    src = tmp_path / "source"
    src.mkdir()
    xlsx = src / "invoice.xlsx"
    fake_workbook(xlsx)
    db = tmp_path / "private.db"
    assert intake(src, db, "t", "p", limit=2, execute=True)["indexed"] == 1
    fake_workbook(xlsx, modified=True)
    assert intake(src, db, "t", "p", limit=2, execute=True)["indexed"] == 1
    assert report(db, "t", "p")["formula_witnesses"] == 3


def test_malicious_zip_and_symlink_are_not_parsed(tmp_path: Path) -> None:
    src = tmp_path / "source"
    src.mkdir()
    fake_workbook(src / "malicious.xlsx", bad_member=True)
    clean = src / "good.pdf"
    clean.write_bytes(b"%PDF")
    (src / "alias.pdf").symlink_to(clean)
    db = tmp_path / "private.db"
    result = intake(src, db, "t", "p", limit=4, execute=True)
    assert result["indexed"] == 1
    assert result["failed_or_unsupported"] == 1
    assert report(db, "t", "p")["documents"] == 1
    assert sha256_file(clean)


def test_wrong_source_or_credentials_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    with pytest.raises(ValueError, match="tenant"):
        intake(source, tmp_path / "db", "../escape", "p", limit=2, execute=True)
    with pytest.raises(ValueError, match="outside"):
        intake(source, source / "db", "tenant", "p", limit=2, execute=True)
