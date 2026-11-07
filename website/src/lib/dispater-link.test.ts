import { describe, expect, it } from "vitest";
import type { DispaterReconciliationReport } from "./dispater-contract";
import { dispaterLinkState, documentSourceLine, isCurrentRequest, storedRunAgrees } from "./dispater-link";

const REPORT = {
  schema: "s",
  tenant_id: "tenant-x",
  dataset_sha256: "a",
  status: "AUDIT_COMPLETE",
  authority_state: "HOLD",
  human_review_required: true,
  counts: { jobs: 0, invoices: 0, rates: 0, payments: 0, findings: 0 },
  financial_summary: {
    identified_exposure_usd: "385.00",
    confirmed_recovery_usd: "0.00" as const,
    recovery_rate_disclaimer: "d",
  },
  findings: [],
  limits: "l",
  receipt_sha256: "abc",
  run_id: "run-" + "a".repeat(32),
} satisfies DispaterReconciliationReport;

describe("dispater link state", () => {
  it("keeps an idle console disconnected and a missing backend unavailable", () => {
    expect(dispaterLinkState(false, null, null)).toBe("DISCONNECTED");
    expect(dispaterLinkState(true, null, null)).toBe("LOADING");
    expect(dispaterLinkState(false, null, "DISPATER backend is not configured")).toBe("UNAVAILABLE");
    expect(dispaterLinkState(false, null, "DISPATER backend unreachable")).toBe("DISCONNECTED");
    expect(dispaterLinkState(false, null, "DISPATER API error (401)")).toBe("ERROR");
  });

  it("accepts a stored run only when the receipt, identity, and dollars agree", () => {
    expect(storedRunAgrees(REPORT, REPORT)).toBe(true);
    expect(
      storedRunAgrees(REPORT, {
        ...REPORT,
        financial_summary: { ...REPORT.financial_summary, identified_exposure_usd: "1.00" },
      }),
    ).toBe(false);
    expect(storedRunAgrees(REPORT, { ...REPORT, receipt_sha256: "other" })).toBe(false);
    expect(storedRunAgrees(REPORT, { ...REPORT, run_id: "run-" + "b".repeat(32) })).toBe(false);
  });

  it("ignores an older audit response after a newer request starts", () => {
    expect(isCurrentRequest(2, 2)).toBe(true);
    expect(isCurrentRequest(1, 2)).toBe(false);
  });

  it("shows the synthetic document source without treating it as recovered money", () => {
    expect(
      documentSourceLine({
        filename: "synthetic-invoice.csv",
        source_sha256: "ab".repeat(32),
        rows: ["2"],
      }),
    ).toBe("synthetic-invoice.csv · abababababababab · rows 2");
  });
});
