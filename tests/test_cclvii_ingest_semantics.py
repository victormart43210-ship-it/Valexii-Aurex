"""Financial terms present in a source must survive extraction and normalization."""
import io
import json
from decimal import Decimal

from openpyxl import Workbook
from test_dispater_documents import _hour_dataset, _one_page

from aurex.dispater_ingest import ingest_source
from aurex.dispater_intelligence import RevenueLeakageEngine


def test_json_hourly_rate_and_supersession_survive_normalization():
    data = _hour_dataset(invoices=[])
    data["rates"][0]["supersedes"] = "R-older"
    batch = ingest_source("tenant-a", "audit.json", json.dumps(data).encode(), kind="json")
    assert batch["dataset"]["rates"][0]["supersedes"] == "R-older"
    report = RevenueLeakageEngine("tenant-a").reconcile_records(batch["dataset"])
    assert report["financial_summary"]["identified_exposure_usd"] == "200.00"


def test_csv_keeps_payment_direction_and_attribution():
    raw = (
        b"payments,payment_id,invoice_id,amount,kind,job_id,customer_id\n"
        b",P1,I1,100.00,PAYMENT,J1,C1\n"
        b",P2,I1,40.00,REVERSAL,J1,C1\n"
    )
    payments = ingest_source("tenant-a", "payment.csv", raw, kind="csv")["dataset"]["payments"]
    net = sum(Decimal(row["amount"]) * (-1 if row["kind"] == "REVERSAL" else 1) for row in payments)
    assert net == Decimal("60.00")
    assert payments[1]["job_id"] == "J1"
    assert payments[1]["customer_id"] == "C1"


def test_xlsx_keeps_overtime_and_ignores_unrecognized_columns():
    book = Workbook()
    sheet = book.active
    sheet.title = "labor"
    sheet.append(["record_id", "job_id", "role", "service_date", "approved_hours", "billed_hours", "overtime_hours", "guess"])
    sheet.append(["L1", "J1", "operator", "2026-03-01", "8", "8", "2.00", "untrusted"])
    sheet.append(["L2", "J2", "operator", "2026-03-02", "6", "6", None, None])
    buffer = io.BytesIO()
    book.save(buffer)
    rows = ingest_source("tenant-a", "hours.xlsx", buffer.getvalue(), kind="xlsx")["dataset"]["labor"]
    assert rows[0]["overtime_hours"] == "2.00"
    assert "guess" not in rows[0]
    assert "overtime_hours" not in rows[1]


def test_pdf_keeps_customer_id_and_page_evidence():
    raw = _one_page(["table: invoices", "invoice_id: I1", "job_id: J1", "amount: 25.00", "status: open", "customer_id: C1"])
    batch = ingest_source("tenant-a", "invoice.pdf", raw, kind="pdf")
    assert batch["dataset"]["invoices"][0]["customer_id"] == "C1"
    field = next(item for item in batch["field_provenance"] if item["field"] == "customer_id")
    assert (field["page"], field["source_sha256"]) == (1, batch["source_sha256"])
