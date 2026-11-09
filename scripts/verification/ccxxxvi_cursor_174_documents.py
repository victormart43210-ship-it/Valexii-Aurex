"""Bounded synthetic document review. Run from the pinned candidate checkout."""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import runpy
import subprocess
import sys
import tempfile
import zipfile
from importlib import metadata
from pathlib import Path


def main() -> None:
    target = "2d0b62400e0ad40f2780f51b26ba0d09261cd724"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if head != target:
        raise SystemExit("wrong candidate commit")
    sys.path.insert(0, str(Path.cwd()))
    from fastapi.testclient import TestClient
    from openpyxl import Workbook

    from aurex import dispater_documents
    from aurex.api import app
    from aurex.dispater_ingest import IngestError, ingest_source

    if Path(dispater_documents.__file__).resolve().parent.parent != Path.cwd():
        raise SystemExit("wrong loaded source")
    one_page = runpy.run_path("tests/test_dispater_documents.py")["_one_page"]
    observed = {}
    libraries = {}
    for name in ("pypdf", "openpyxl", "et-xmlfile"):
        dist = metadata.distribution(name)
        libraries[name] = {
            "version": dist.version,
            "license": dist.metadata.get("License-Expression") or dist.metadata.get("License"),
            "license_files": [str(path) for path in dist.files or [] if "license" in str(path).lower()],
        }
    lines = ["table: invoices", "invoice_id: I", "job_id: J", "amount: 10.00", "status: open"]
    raw = one_page(lines + ["amount: 999.00"])
    pdf = ingest_source("tenant-a", "d.pdf", raw, kind="pdf")
    observed["duplicate_pdf_amount"] = pdf["dataset"]["invoices"][0]["amount"]
    observed["conflicting_pdf_amounts"] = [f["value"] for f in pdf["field_provenance"] if f["field"] == "amount"]
    oversized = raw + b" " * (1_000_001 - len(raw))
    observed["oversize_pdf_bytes_admitted"] = len(oversized) if ingest_source("tenant-a", "d.pdf", oversized, kind="pdf") else 0
    wb = Workbook()
    ws = wb.active
    ws.title = "payments"
    ws.append(["payment_id", "invoice_id", "amount", "amount", "kind"])
    ws.append(["=2+2", "I", "10.00", "999.00", "REVERSAL"])
    stream = io.BytesIO()
    wb.save(stream)
    blob = stream.getvalue()
    xlsx = ingest_source("tenant-a", "d.xlsx", blob, kind="xlsx")
    observed["normalized_xlsx_payment"] = xlsx["dataset"]["payments"][0]
    observed["xlsx_field_provenance_count"] = len(xlsx["field_provenance"])
    # A single submitted reversal of an invoice has the opposite sign to a payment.
    from aurex.dispater_intelligence import RevenueLeakageEngine

    pay_book = Workbook()
    pay_sheet = pay_book.active
    pay_sheet.title = "payments"
    pay_sheet.append(["payment_id", "invoice_id", "amount", "kind"])
    pay_sheet.append(["P", "I", "40.00", "REVERSAL"])
    pay_stream = io.BytesIO()
    pay_book.save(pay_stream)
    row = ingest_source("tenant-a", "rev.xlsx", pay_stream.getvalue(), kind="xlsx")["dataset"]["payments"][0]
    fixture = {
        "tenant_id":"tenant-a", "dataset_type":"SYNTHETIC_ONLY",
        "jobs":[{"job_id":"J","customer_id":"C","service_code":"S","date":"2026-01-01"}],
        "rates":[{"rate_id":"R","customer_id":"C","service_code":"S","start":"2026-01-01","end":"2026-12-31","amount":"100.00"}],
        "invoices":[{"invoice_id":"I","job_id":"J","amount":"100.00","status":"paid"}],
        "payments":[{"payment_id":"P1","invoice_id":"I","amount":"100.00"},row],
    }
    engine = RevenueLeakageEngine("tenant-a")
    assumed = engine.reconcile_records(fixture)
    row["kind"] = "REVERSAL"
    explicit = engine.reconcile_records(fixture)
    observed["reversal_via_xlsx_codes"] = sorted(f["code"] for f in assumed["findings"])
    observed["reversal_explicit_codes"] = sorted(f["code"] for f in explicit["findings"])
    buf = io.BytesIO(blob)
    with zipfile.ZipFile(buf, "a") as archive:
        archive.writestr("xl/VBAPROJECT.BIN", b"inert synthetic marker")
    observed["uppercase_macro_name_admitted"] = bool(ingest_source("tenant-a", "marker.xlsx", buf.getvalue(), kind="xlsx"))
    for label, data, kind in [("bad_zip", b"bogus", "xlsx"), ("blank_pdf", one_page([]), "pdf")]:
        try:
            ingest_source("tenant-a", "synthetic", data, kind=kind)
        except IngestError:
            observed[label + "_rejected"] = True
    with tempfile.TemporaryDirectory() as tmp:
        token = "synthetic-test-principal-with-document-scope"
        os.environ["AUREX_DISPATER_TENANT_GRANTS"] = json.dumps({hashlib.sha256(token.encode()).hexdigest(): ["tenant-a"]})
        os.environ["AUREX_DISPATER_DB"] = str(Path(tmp) / "synthetic.db")
        os.environ["AUREX_DISPATER_RECEIPT_KEYS"] = json.dumps({"review": "aa" * 32})
        os.environ["AUREX_DISPATER_RECEIPT_ACTIVE_KID"] = "review"
        headers = {"Authorization": f"Bearer {token}"}
        client = TestClient(app, raise_server_exceptions=False)
        for label, tenant, data in [("invalid_base64", "tenant-a", "!!!!"), ("wrong_tenant", "tenant-b", "!!!!"), ("oversize_pdf", "tenant-a", base64.b64encode(oversized).decode())]:
            response = client.post("/v1/dispater/documents", headers=headers, json={"tenant_id":tenant, "kind":"pdf", "filename":"d.pdf", "content_base64":data})
            observed[label + "_http"] = response.status_code
    expected = {
        "reversal_via_xlsx_codes": ["PAID_STATUS_UNRECONCILED", "SPLIT_OR_DUPLICATE_PAYMENT_UNRESOLVED"],
        "reversal_explicit_codes": ["PAID_STATUS_UNRECONCILED"],
        "duplicate_pdf_amount": "999.00", "conflicting_pdf_amounts": ["10.00", "999.00"],
        "oversize_pdf_bytes_admitted": 1000001,
        "normalized_xlsx_payment": {"payment_id": "'=2+2", "invoice_id":"I", "amount":"999.00"},
        "xlsx_field_provenance_count": 0, "uppercase_macro_name_admitted": True,
        "bad_zip_rejected": True, "blank_pdf_rejected": True,
        "invalid_base64_http": 500, "wrong_tenant_http": 403,"oversize_pdf_http":200,
    }
    mismatches = [key for key in expected if observed.get(key) != expected[key]]
    print(json.dumps({"head": head, "libraries": libraries, "observations": observed, "expected_on_candidate": expected, "mismatches": mismatches}, indent=2))
    sys.exit(2 if mismatches else 1)


if __name__ == "__main__":
    main()
