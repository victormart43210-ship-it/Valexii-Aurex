import { describe, it, expect } from "vitest";
import { DispaterDocumentIngestionSchema, DispaterReconciliationReportSchema } from "./dispater-contract";

const SIGNED = {
  schema: "s",
  tenant_id: "tenant-x",
  dataset_sha256: "a",
  status: "AUDIT_COMPLETE",
  authority_state: "HOLD",
  human_review_required: true,
  counts: { jobs: 0, invoices: 0, rates: 0, payments: 0, findings: 0 },
  financial_summary: {
    identified_exposure_usd: "0.00",
    confirmed_recovery_usd: "0.00",
    recovery_rate_disclaimer: "d",
  },
  findings: [],
  limits: "l",
  receipt_sha256: "r",
  receipt_auth: { alg: "HMAC-SHA256", kid: "k1" },
  receipt_mac: "ab".repeat(32),
};

describe("receipt export round-trip", () => {
  it("preserves every signed field through parse and JSON export", () => {
    const parsed = DispaterReconciliationReportSchema.parse(SIGNED);
    const exported = JSON.parse(JSON.stringify(parsed, null, 2));
    expect(exported).toEqual(SIGNED);
  });
  it("rejects malformed receipt fields instead of dropping them", () => {
    expect(
      DispaterReconciliationReportSchema.safeParse({ ...SIGNED, receipt_mac: 42 }).success,
    ).toBe(false);
    expect(
      DispaterReconciliationReportSchema.safeParse({ ...SIGNED, receipt_auth: "x" }).success,
    ).toBe(false);
  });
  it("keeps document provenance outside financial authority", () => {
    const parsed = DispaterDocumentIngestionSchema.parse({
      authority_state: "HOLD",
      financial_authority: "NONE",
      ingestion_authenticated: false,
      ocr_status: "NOT_INSTALLED",
      ingestion: {
        source_sha256: "ab".repeat(32),
        filename: "invoice.pdf",
        kind: "pdf",
        processor: { name: "dispater_ingest", version: "v1", model: null, ocr: "NOT_INSTALLED" },
        provenance: [{ source_sha256: "ab".repeat(32), row: "1", qualification: "EXTRACTED" }],
        field_provenance: [{ page: 1, method: "pdf_text", qualification: "EXTRACTED" }],
        limits: "OCR is not installed",
      },
      report: SIGNED,
    });
    expect(parsed.report.financial_summary.confirmed_recovery_usd).toBe("0.00");
    expect(parsed.ingestion.field_provenance[0]?.page).toBe(1);
    expect(parsed.financial_authority).toBe("NONE");
  });
  it("does not invent a MAC when the backend sent none", () => {
    const { receipt_mac: _m, receipt_auth: _a, ...unsigned } = SIGNED;
    const out = DispaterReconciliationReportSchema.parse(unsigned);
    expect(out.receipt_mac).toBeUndefined();
    expect(out.receipt_auth).toBeUndefined();
  });
});
