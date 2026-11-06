import { describe, it, expect } from "vitest";
import { DispaterReconciliationReportSchema } from "./dispater-contract";

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
  receipt_auth: { alg: "HMAC-SHA256", kid: "k1", v: 2 },
  run_id: "run-" + "a".repeat(32),
  created_at: "2026-11-06T00:00:00+00:00",
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
  it("keeps the legacy untrusted-metadata marker through export", () => {
    const legacy = {
      ...SIGNED,
      receipt_auth: { alg: "HMAC-SHA256", kid: "k1" },
      unauthenticated_fields: ["run_id", "created_at"],
    };
    const out = JSON.parse(JSON.stringify(DispaterReconciliationReportSchema.parse(legacy)));
    expect(out.unauthenticated_fields).toEqual(["run_id", "created_at"]);
    expect(out.receipt_auth.v).toBeUndefined();
  });
  it("does not invent a MAC when the backend sent none", () => {
    const { receipt_mac: _m, receipt_auth: _a, ...unsigned } = SIGNED;
    const out = DispaterReconciliationReportSchema.parse(unsigned);
    expect(out.receipt_mac).toBeUndefined();
    expect(out.receipt_auth).toBeUndefined();
  });
});
