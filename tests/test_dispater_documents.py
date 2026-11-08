"""File ingestion, hour reconciliation, and durable monitoring. OCR is not installed."""

from __future__ import annotations

import base64
import hashlib
import io
import json
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from aurex import dispater_store
from aurex.api import app
from aurex.dispater_documents import extract_pdf
from aurex.dispater_ingest import IngestError, ingest_source
from aurex.dispater_intelligence import RevenueLeakageEngine
from aurex.dispater_monitor import persist_increment


def _one_page(lines: list[str]) -> bytes:
    ops = ["BT /F1 12 Tf 72 720 Td"]
    for line in lines:
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        ops.append(f"({safe}) Tj")
        ops.append("0 -16 Td")
    ops.append("ET")
    content = " ".join(ops).encode()
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n",
        f"4 0 obj << /Length {len(content)} >> stream\n".encode() + content + b"\nendstream endobj\n",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets:
        pdf.extend(f"{off:010d} 00000 n \n".encode())
    pdf.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(pdf)


def _blank_pdf() -> bytes:
    return _one_page([])


def test_pdf_text_becomes_one_invoice_with_page_provenance() -> None:
    raw = _one_page(
        ["table: invoices", "invoice_id: I01", "job_id: J01", "amount: 150.00", "status: open"]
    )
    batch = ingest_source("tenant-a", "invoice.pdf", raw, kind="pdf")
    assert batch["dataset"]["invoices"] == [
        {"invoice_id": "I01", "job_id": "J01", "amount": "150.00", "status": "open"}
    ]
    assert batch["field_provenance"][0]["page"] == 1
    assert batch["field_provenance"][0]["method"] == "pdf_text"
    assert batch["field_provenance"][0]["qualification"] == "EXTRACTED"
    assert batch["processor"]["ocr"] == "NOT_INSTALLED"
    assert batch["source_sha256"] == hashlib.sha256(raw).hexdigest()


def test_blank_pdf_is_not_a_successful_extraction() -> None:
    with pytest.raises(IngestError, match="OCR runtime is not installed"):
        extract_pdf(_blank_pdf(), "ab" * 32)


@pytest.mark.parametrize("duplicate", ["table: invoices", "amount: 999.00"])
def test_pdf_rejects_ambiguous_fields(duplicate: str) -> None:
    raw = _one_page(["table: invoices", "invoice_id: I01", "job_id: J01", "amount: 150.00", "status: open", duplicate])
    with pytest.raises(IngestError, match="duplicate"):
        extract_pdf(raw, hashlib.sha256(raw).hexdigest())


def test_png_is_rejected_without_being_read_as_money() -> None:
    png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + (1).to_bytes(4, "big") + (1).to_bytes(4, "big")
    with pytest.raises(IngestError, match="OCR runtime is not installed"):
        ingest_source("tenant-a", "scan.png", png, kind="png")
    huge = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + (9000).to_bytes(4, "big") + (9000).to_bytes(4, "big")
    with pytest.raises(IngestError, match="dimensions"):
        ingest_source("tenant-a", "huge.png", huge, kind="png")


def test_xlsx_text_cells_and_formulas(tmp_path: Path) -> None:
    book = Workbook()
    sheet = book.active
    assert sheet is not None
    sheet.title = "invoices"
    sheet.append(["invoice_id", "job_id", "amount", "status"])
    sheet.append(["I1", "J1", "100.00", "open"])
    sheet["A3"] = "=CMD()"
    sheet["B3"] = "J1"
    sheet["C3"] = "10.00"
    sheet["D3"] = "open"
    buffer = io.BytesIO()
    book.save(buffer)
    batch = ingest_source("tenant-a", "invoices.xlsx", buffer.getvalue(), kind="xlsx")
    assert batch["dataset"]["invoices"][0]["amount"] == "100.00"
    assert batch["dataset"]["invoices"][1]["invoice_id"] == "'=CMD()"
    numeric = Workbook()
    numbers = numeric.active
    assert numbers is not None
    numbers.title = "invoices"
    numbers.append(["invoice_id", "job_id", "amount", "status"])
    numbers.append(["I1", "J1", 100, "open"])
    raw = io.BytesIO()
    numeric.save(raw)
    with pytest.raises(IngestError, match="numeric cell"):
        ingest_source("tenant-a", "bad.xlsx", raw.getvalue(), kind="xlsx")


def test_macro_workbook_is_rejected() -> None:
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("xl/vbaProject.bin", b"not-executed")
        archive.writestr("[Content_Types].xml", b"<Types></Types>")
    with pytest.raises(IngestError, match="macros"):
        ingest_source("tenant-a", "book.xlsx", buffer.getvalue(), kind="xlsx")


def _hour_dataset(**over: object) -> dict:
    base = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "EQ", "date": "2026-03-01"}],
        "rates": [
            {
                "rate_id": "R1",
                "customer_id": "C1",
                "service_code": "EQ",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "25.00",
                "unit": "HOUR",
            }
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "250.00", "status": "open"}],
        "payments": [],
        "equipment": [
            {
                "ticket_id": "T1",
                "job_id": "J1",
                "equipment_id": "PUMP-1",
                "service_date": "2026-03-01",
                "billable_hours": "8.00",
                "standby_hours": "2.00",
                "invoiced_hours": "10.00",
            }
        ],
    }
    base.update(over)
    return base


def test_equipment_hours_price_billable_time_once() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(_hour_dataset())
    summary = report["financial_summary"]
    # Independent: 8.00 * 25.00 = 200.00. Invoice 250.00. Standby 2.00 is not added.
    assert summary["potential_overbilling_usd"] == "50.00"
    assert summary["identified_exposure_usd"] == "50.00"
    assert summary["confirmed_recovery_usd"] == "0.00"
    finding = next(item for item in report["findings"] if item["code"] == "EQUIPMENT_HOURS_MISMATCH")
    assert finding["exposure_usd"] == "50.00"
    assert finding["qualification"] == "SUSPECTED_DISCREPANCY"
    assert Decimal("8.00") * Decimal("25.00") == Decimal("200.00")


def test_labor_and_equipment_together_are_withheld() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(
        _hour_dataset(
            labor=[
                {
                    "record_id": "L1",
                    "job_id": "J1",
                    "role": "operator",
                    "service_date": "2026-03-01",
                    "approved_hours": "4.00",
                    "billed_hours": "4.00",
                }
            ]
        )
    )
    assert report["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert report["findings"][0]["code"] == "HOURS_SOURCE_CONFLICT"


def test_hourly_rate_without_a_ticket_is_not_a_flat_price() -> None:
    report = RevenueLeakageEngine("tenant-a").reconcile_records(_hour_dataset(equipment=[]))
    assert report["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert report["findings"][0]["code"] == "HOURS_EVIDENCE_MISSING"


def test_labor_hours_match_independent_arithmetic() -> None:
    dataset = _hour_dataset(
        equipment=[],
        invoices=[{"invoice_id": "I1", "job_id": "J1", "amount": "125.00", "status": "open"}],
        labor=[
            {
                "record_id": "L1",
                "job_id": "J1",
                "role": "operator",
                "service_date": "2026-03-01",
                "approved_hours": "4.00",
                "billed_hours": "5.00",
            }
        ],
    )
    report = RevenueLeakageEngine("tenant-a").reconcile_records(dataset)
    expected = Decimal("125.00") - (Decimal("4.00") * Decimal("25.00"))
    assert report["financial_summary"]["potential_overbilling_usd"] == f"{expected:.2f}"
    assert report["findings"][0]["code"] == "LABOR_HOURS_MISMATCH"


def test_reversal_is_netted_once() -> None:
    dataset = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
        "rates": [
            {
                "rate_id": "R1",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            }
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "paid"}],
        "payments": [
            {"payment_id": "P1", "invoice_id": "I1", "amount": "100.00", "kind": "PAYMENT"},
            {"payment_id": "P2", "invoice_id": "I1", "amount": "40.00", "kind": "REVERSAL"},
        ],
    }
    report = RevenueLeakageEngine("tenant-a").reconcile_records(dataset)
    assert report["financial_summary"]["unverified_exposure_usd"] == "40.00"
    assert report["financial_summary"]["identified_exposure_usd"] == "40.00"
    codes = {item["code"] for item in report["findings"]}
    assert "PAID_STATUS_UNRECONCILED" in codes
    assert "SPLIT_OR_DUPLICATE_PAYMENT_UNRESOLVED" not in codes


def test_monitor_checkpoint_survives_a_new_connection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "monitor.db"))
    baseline = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-01-01"}],
        "rates": [
            {
                "rate_id": "R1",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            }
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "paid"}],
        "payments": [{"payment_id": "P1", "invoice_id": "I1", "amount": "100.00"}],
    }
    additions = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [],
        "invoices": [{"invoice_id": "I2", "job_id": "MISSING", "amount": "15.00", "status": "open"}],
        "rates": [],
        "payments": [],
    }
    source = "cd" * 32
    first, created = persist_increment("tenant-a", baseline, additions, source)
    assert created is True
    assert first["payload"]["confirmed_recovery_usd"] == "0.00"
    assert first["payload"]["identified_exposure_usd"] == "15.00"
    again, created_again = persist_increment("tenant-a", baseline, additions, source)
    assert created_again is False
    assert again["event_id"] == first["event_id"]
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "monitor.db"))
    listed = dispater_store.list_monitor_events("tenant-a")
    assert len(listed) == 1
    assert dispater_store.list_monitor_events("tenant-b") == []


def test_thirty_six_month_workbook_matches_independent_manifest() -> None:
    book = Workbook()
    jobs = book.active
    assert jobs is not None
    jobs.title = "jobs"
    invoices = book.create_sheet("invoices")
    rates = book.create_sheet("rates")
    payments = book.create_sheet("payments")
    jobs.append(["job_id", "customer_id", "service_code", "date"])
    invoices.append(["invoice_id", "job_id", "amount", "status"])
    rates.append(["rate_id", "customer_id", "service_code", "start", "end", "amount"])
    payments.append(["payment_id", "invoice_id", "amount"])
    rates.append(["R1", "C1", "S", "2024-01-01", "2026-12-31", "100.00"])
    for index in range(36):
        year = 2024 + index // 12
        month = index % 12 + 1
        day = f"{year}-{month:02d}-01"
        job_id = f"J{index:02d}"
        jobs.append([job_id, "C1", "S", day])
        if index == 12:
            invoices.append([f"I{index:02d}A", job_id, "100.00", "open"])
            invoices.append([f"I{index:02d}B", job_id, "100.00", "open"])
            continue
        amount = "150.00" if index == 3 else "100.00"
        status = "open" if index in {3, 20} else "paid"
        invoices.append([f"I{index:02d}", job_id, amount, status])
        if index == 20:
            payments.append([f"P{index:02d}", f"I{index:02d}", "40.00"])
        elif index != 3:
            payments.append([f"P{index:02d}", f"I{index:02d}", amount])
    buffer = io.BytesIO()
    book.save(buffer)
    batch = ingest_source("golden", "thirty-six.xlsx", buffer.getvalue(), kind="xlsx")
    report = RevenueLeakageEngine("golden").reconcile_records(batch["dataset"])
    summary = report["financial_summary"]
    # Month 3 bills 150 against 100. Month 12 withholds both 100 invoices.
    # Month 20 pays 40 of 100. No other month is a discrepancy.
    assert summary["potential_overbilling_usd"] == "50.00"
    assert summary["withheld_unresolved_usd"] == "200.00"
    assert summary["unverified_exposure_usd"] == "60.00"
    assert summary["identified_exposure_usd"] == "110.00"
    assert summary["confirmed_recovery_usd"] == "0.00"
    assert all(item["qualification"] != "CONFIRMED_DISCREPANCY" for item in report["findings"])


def test_document_api_reconciles_a_pdf_and_rejects_another_tenant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    token = "d" * 32
    monkeypatch.setenv(
        "AUREX_DISPATER_TENANT_GRANTS",
        json.dumps({hashlib.sha256(token.encode()).hexdigest(): ["tenant-a"]}),
    )
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "api.db"))
    raw = _one_page(["table: invoices", "invoice_id: I9", "job_id: " + "MISSING", "amount: 10.00", "status: open"])
    client = TestClient(app, raise_server_exceptions=False)
    invalid = client.post(
        "/v1/dispater/documents",
        headers={"Authorization": f"Bearer {token}"},
        json={"tenant_id": "tenant-a", "filename": "invoice.pdf", "kind": "pdf", "content_base64": "!!!"},
    )
    assert invalid.status_code == 400
    denied = client.post(
        "/v1/dispater/documents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tenant_id": "tenant-b",
            "filename": "invoice.pdf",
            "kind": "pdf",
            "content_base64": base64.b64encode(raw).decode(),
        },
    )
    assert denied.status_code == 403
    accepted = client.post(
        "/v1/dispater/documents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tenant_id": "tenant-a",
            "filename": "invoice.pdf",
            "kind": "pdf",
            "content_base64": base64.b64encode(raw).decode(),
        },
    )
    assert accepted.status_code == 200
    body = accepted.json()
    assert body["financial_authority"] == "NONE"
    assert body["ingestion_authenticated"] is False
    assert body["ocr_status"] == "NOT_INSTALLED"
    assert body["report"]["financial_summary"]["unverified_exposure_usd"] == "10.00"
    assert body["report"]["receipt_binding"] == "BOUND_V2"
    assert body["ingestion"]["field_provenance"][0]["page"] == 1
