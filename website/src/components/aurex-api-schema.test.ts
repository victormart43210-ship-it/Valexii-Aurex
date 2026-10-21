import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  BudgetSchema,
  CapabilitiesSchema,
  EvidenceListSchema,
  JobSchema,
  capabilityBacked,
} from "@/lib/aurex-api-schema";

/** Regression fixture drawn from canonical aurex/api.py + fenced_worker.py.
 * This is a typed-contract test, NOT live transport or independently verified evidence.
 */
const checkedAt = "2026-10-21T12:00:00+00:00";
const record = {
  id: "ev-0123456789abcdef01234567",
  capabilityId: "regression_scan",
  kind: "offline_probe",
  collectedAt: checkedAt,
  sha256: "a".repeat(64),
  summary: "Real SQLite observation; independently NOT VERIFIED",
};

describe("AUREX existing Python -> TypeScript transport schema", () => {
  it("accepts actual Python capability identifiers (snake_case)", () => {
    const caps = {
      capabilities: [
        { id: "regression_scan", available: true, evidenceId: record.id, verifiedAt: null },
        { id: "memory_graph", available: false, evidenceId: null, verifiedAt: null },
        { id: "remote_inference", available: false, evidenceId: null, verifiedAt: null },
      ],
    };
    expect(CapabilitiesSchema.parse(caps).capabilities).toHaveLength(3);
    const parsed = EvidenceListSchema.parse({ evidence: [record] });
    expect(parsed.evidence[0].kind).toBe("offline_probe");
  });

  it("parses persisted idempotent synthetic job and zero budget", () => {
    expect(
      JobSchema.safeParse({
        id: "job-0123456789abcdef01234567",
        kind: "regression_scan",
        state: "succeeded",
        createdAt: checkedAt,
        updatedAt: checkedAt,
        reservationUsd: 0,
      }).success,
    ).toBe(true);
    expect(BudgetSchema.parse({
      limitUsd: 0, reservedUsd: 0, spentUsd: 0, period: "month",
    }).limitUsd).toBe(0);
  });

  it("rejects malformed identifiers, unrecognized evidence and additional secrets", () => {
    expect(CapabilitiesSchema.safeParse({
      capabilities: [{ id: "http://evil", available: true, evidenceId: null, verifiedAt: null }],
    }).success).toBe(false);
    expect(EvidenceListSchema.safeParse({
      evidence: [{ ...record, kind: "autonomous_payment" }],
    }).success).toBe(false);
    expect(EvidenceListSchema.safeParse({
      evidence: [{ ...record, bearerToken: "leak" }],
    }).success).toBe(false);
  });

  it("never treats a recorded observation as independently verified authority", () => {
    const cap = CapabilitiesSchema.parse({ capabilities: [
      { id: "regression_scan", available: true, evidenceId: record.id, verifiedAt: null },
    ] }).capabilities[0];
    // Generic freshness/link support is not external witness validation.
    expect(capabilityBacked(cap, EvidenceListSchema.parse({ evidence: [record] }).evidence,
      Date.parse(checkedAt) + 1000)).toBe(true);
    expect(cap.verifiedAt).toBeNull();
    expect(record.summary).toContain("NOT VERIFIED");
  });

  it("pins source of the probe identifiers and evidence kind to Python code", () => {
    const api = readFileSync("../aurex/api.py", "utf8");
    const worker = readFileSync("../aurex/fenced_worker.py", "utf8");
    expect(api).toContain('id="regression_scan"');
    expect(api).toContain('id="remote_inference"');
    expect(worker).toContain("'offline_probe'");
    expect(worker).toContain("'UNVERIFIED'");
  });
});
