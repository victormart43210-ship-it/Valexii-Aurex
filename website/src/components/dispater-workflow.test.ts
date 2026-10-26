import { describe, expect, it } from "vitest";
import { runSyntheticTowingAudit, verifyAuditReceipt } from "@/lib/aurex-industrial";

describe("DISPATER Customer-Facing Towing Audit Workflow", () => {
  it("Step 1-4: Handles backend unconfigured state fail-closed", async () => {
    const res = await runSyntheticTowingAudit("towing_v1");
    expect(res.ok).toBe(false);
    if (!res.ok) {
      expect(res.error).toContain("503 Service Unavailable");
    }
  });

  it("Step 10: Verifies cryptographic receipts with deterministic validation", async () => {
    const validRes = await verifyAuditReceipt("rcpt-towing-20261025");
    expect(validRes.ok).toBe(true);
    if (validRes.ok) {
      expect(validRes.receipt.status).toBe("VERIFIED");
      expect(validRes.receipt.verifier).toBe("AUREX-OX-CUSTOS-V1");
      expect(validRes.receipt.evidence_digest.length).toBe(64);
    }

    const invalidRes = await verifyAuditReceipt("rcpt-invalid-tampered");
    expect(invalidRes.ok).toBe(true);
    if (invalidRes.ok) {
      expect(invalidRes.receipt.status).toBe("INVALID");
    }

    const badIdRes = await verifyAuditReceipt("bad!");
    expect(badIdRes.ok).toBe(false);
    if (!badIdRes.ok) {
      expect(badIdRes.error).toContain("Invalid audit receipt ID format");
    }
  });
});
