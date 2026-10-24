import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  BudgetSchema,
  CapabilitiesSchema,
  EvidenceListSchema,
  JobListSchema,
  JobSchema,
  capabilityBacked,
} from "@/lib/aurex-api-schema";
import {
  CXXV_CONTRACT_VERSION,
  NVIDIA_BRIDGE_CANDIDATES,
  OX_WORKSTATION_SECTIONS,
  candidateRegistry,
  projectWorkstationCandidate,
  stageSyntheticFieldAudit,
} from "@/lib/aurex-cxxv-bridge";

const checkedAt = "2026-10-22T12:00:00+00:00";
const caseOne = {
  case_id: "BETA-001",
  invoice_id: "INV-0001",
  invoice_cents: 250_000,
  ticket_cents: 245_000,
  approved_rate_cents_per_hour: 25_000,
  documented_hours: 10,
  synthetic: true,
};
const record = {
  id: "ev-0123456789abcdef01234567",
  capabilityId: "regression_scan",
  kind: "offline_probe",
  collectedAt: checkedAt,
  sha256: "a".repeat(64),
  summary: "Model candidate, not an independent witness",
};

describe("CXXV / Python to TypeScript API contract bridge", () => {
  it("parses canonical snake_case capabilities, evidence and idempotent jobs", () => {
    expect(CapabilitiesSchema.safeParse({ capabilities: [
      { id: "regression_scan", available: true, evidenceId: record.id, verifiedAt: null },
      { id: "memory_graph", available: false, evidenceId: null, verifiedAt: null },
      { id: "remote_inference", available: false, evidenceId: null, verifiedAt: null },
    ] }).success).toBe(true);
    expect(EvidenceListSchema.safeParse({ evidence: [record] }).success).toBe(true);
    expect(JobSchema.safeParse({
      id: "job-0123456789abcdef01234567",
      kind: "regression_scan", state: "succeeded",
      createdAt: checkedAt, updatedAt: checkedAt, reservationUsd: 0,
    }).success).toBe(true);
  });

  it("keeps OpenAPI and strict Zod capability and evidence contracts synchronized", () => {
    const spec = readFileSync("docs/aurex-api/openapi.yaml", "utf8");
    expect(spec).toContain('CapId: { type: string, pattern: "^[a-z][a-z0-9_-]{0,63}$" }');
    expect(spec).toContain("kind: { enum: [test_run, health_probe, benchmark_record, offline_probe] }");
    expect(spec).toContain('"200": { description: Created or idempotent replay');
    expect(CapabilitiesSchema.safeParse({ capabilities: [
      { id: "a", available: false, evidenceId: null, verifiedAt: null, token: "leak" },
    ] }).success).toBe(false);
    expect(EvidenceListSchema.safeParse({ evidence: [{ ...record, kind: "fraud_authorized" }] }).success).toBe(false);
  });

  it("never upgrades a linked record into independent verification", () => {
    const evidence = EvidenceListSchema.parse({ evidence: [record] }).evidence;
    const caps = CapabilitiesSchema.parse({ capabilities: [
      { id: "regression_scan", available: true, evidenceId: record.id, verifiedAt: null },
    ] }).capabilities;
    expect(capabilityBacked(caps[0], evidence, Date.parse(checkedAt) + 1_000)).toBe(true);
    const projected = projectWorkstationCandidate({
      capabilities: { capabilities: caps },
      evidence: { evidence },
      budgets: { limitUsd: 0, spentUsd: 0, reservedUsd: 0, period: "month" },
      jobs: { jobs: [], nextCursor: null },
      checkedAt,
    }, Date.parse(checkedAt) + 1_000);
    expect(projected.status).toBe("REACHABLE_NOT_VERIFIED");
    expect(projected.authority).toBe("NONE");
    if (projected.status !== "REACHABLE_NOT_VERIFIED") throw new Error("failed");
    expect(projected.supportedLinkCount).toBe(1);
    expect(projected.independentVerification).toBe("NOT VERIFIED");
    expect(projected.modelRuntime).toBe("NOT DEPLOYED");
  });

  it("rejects malformed capability identifiers and spoofed budget and jobs", () => {
    expect(CapabilitiesSchema.safeParse({ capabilities: [
      { id: "http://evil", available: true, evidenceId: null, verifiedAt: null },
    ] }).success).toBe(false);
    expect(BudgetSchema.safeParse({ limitUsd: -1, reservedUsd: 0, spentUsd: 0, period: "month" }).success).toBe(false);
    expect(JobListSchema.safeParse({ jobs: [{ state: "paid_success" }], nextCursor: null }).success).toBe(false);
  });
});

describe("CXXV synthetic field financial audit staging", () => {
  it("stages canonical Python audit input without executing it", () => {
    const result = stageSyntheticFieldAudit([caseOne, {
      ...caseOne, case_id: "BETA-002", invoice_id: "INV-0001",
      approved_rate_cents_per_hour: null,
    }]);
    expect(result.status).toBe("STAGED");
    expect(result.authority).toBe("NONE");
    if (result.status === "STAGED") {
      expect(result.release).toBe("HOLD");
      expect(result.version).toBe(CXXV_CONTRACT_VERSION);
      expect(result.cases[1].approved_rate_cents_per_hour).toBeNull();
      expect(result.cases[1].invoice_id).toBe("INV-0001");
    }
  });

  it.each([
    null, [], {}, [caseOne, caseOne], Array(101).fill(caseOne),
    [{ ...caseOne, synthetic: false }],
    [{ ...caseOne, case_id: "CUSTOMER-123" }],
    [{ ...caseOne, invoice_cents: 0 }],
    [{ ...caseOne, invoice_cents: -1 }],
    [{ ...caseOne, ticket_cents: 0.1 }],
    [{ ...caseOne, invoice_cents: Number.MAX_SAFE_INTEGER }],
    [{ ...caseOne, documented_hours: 0 }],
    [{ ...caseOne, documented_hours: 10001 }],
    [{ ...caseOne, approved_rate_cents_per_hour: 0 }],
    [{ ...caseOne, invoice_id: "INV-0001", bank_account: "123456" }],
  ])("refuses malformed, sensitive or unsafely bounded input", (value) => {
    const result = stageSyntheticFieldAudit(value);
    expect(result).toEqual({
      status: "HOLD", authority: "NONE", reason: "INVALID_OR_NON_SYNTHETIC_INPUT",
    });
  });

  it("pins input shapes against Python contract without copying the engine", () => {
    const source = readFileSync("../aurex/api.py", "utf8");
    expect(source).toContain("class JobCreateRequest");
    const bridge = readFileSync("src/lib/aurex-cxxv-bridge.ts", "utf8");
    expect(bridge).not.toMatch(/\bfetch\s*\(|\bcreateJob\s*\(|\bXMLHttpRequest\b/);
    expect(bridge).not.toContain("AUTO_APPROVED");
  });
});

describe("CXXV NVIDIA and ten-lens workstation boundary", () => {
  it("registers exactly five research candidates without claiming deployment", () => {
    expect(NVIDIA_BRIDGE_CANDIDATES).toHaveLength(5);
    const registry = candidateRegistry();
    expect(new Set(registry.map((r) => r.id)).size).toBe(5);
    expect(registry.map((x) => x.sourcePr)).toEqual([106, 107, 107, 107, 107]);
    for (const r of registry) {
      expect(r.runtime).toBe("NOT DEPLOYED");
      expect(r.inference).toBe("NOT RUN");
      expect(r.release).toBe("HOLD");
      expect(r.authority).toBe("NONE");
      expect(r.financialEffect).toBe("NONE");
    }
  });

  it("preserves all ten original OX navigation sections", () => {
    expect(OX_WORKSTATION_SECTIONS).toEqual([
      "Intelligence Map", "Execute", "Evidence", "Context", "Agents",
      "Jobs", "Models", "Security", "Analytics", "Nexus",
    ]);
  });

  it("fails closed on stale, future, absent and malformed observations", () => {
    const valid = {
      capabilities: { capabilities: [] },
      evidence: { evidence: [] },
      budgets: { limitUsd: 0, reservedUsd: 0, spentUsd: 0, period: "month" },
      jobs: { jobs: [], nextCursor: null }, checkedAt,
    };
    const now = Date.parse(checkedAt);
    expect(projectWorkstationCandidate(valid, now).status).toBe("REACHABLE_NOT_VERIFIED");
    expect(projectWorkstationCandidate(valid, now + 200_000).status).toBe("HOLD");
    expect(projectWorkstationCandidate(valid, now - 10_000).status).toBe("HOLD");
    expect(projectWorkstationCandidate({ ...valid, capabilities: null }, now).status).toBe("HOLD");
    expect(projectWorkstationCandidate({ ...valid, secret: "unexpected" }, now).status).toBe("HOLD");
    expect(projectWorkstationCandidate(valid, Infinity).status).toBe("HOLD");
  });
});
