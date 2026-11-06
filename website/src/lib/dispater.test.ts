import { describe, it, expect } from "vitest";
import {
  DispaterConfigError,
  executeDispaterReconciliation,
  getFixture,
  resolveDispaterConfig,
} from "./dispater.server";

import {
  DispaterFindingSchema,
  DispaterReconciliationReportSchema,
  getDispaterEvidencePresentation,
} from "./dispater-contract";

const TOKEN = "t".repeat(32);
const REPORT = {
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
};

describe("dispater server config", () => {
  it("fails closed without configuration (no localhost or placeholder fallback)", async () => {
    await expect(executeDispaterReconciliation({})).rejects.toBeInstanceOf(DispaterConfigError);
    expect(() => resolveDispaterConfig({ serviceUrl: "https://x.example" })).toThrow();
    expect(() =>
      resolveDispaterConfig({ serviceUrl: "https://x.example", serviceToken: "short" }),
    ).toThrow();
  });
  it("rejects local and http URLs unless explicitly allowed outside production", () => {
    const base = { serviceToken: TOKEN };
    expect(() => resolveDispaterConfig({ ...base, serviceUrl: "http://127.0.0.1:8000" })).toThrow();
    expect(() => resolveDispaterConfig({ ...base, serviceUrl: "http://example.com" })).toThrow();
    expect(
      resolveDispaterConfig({ ...base, serviceUrl: "http://127.0.0.1:8000", allowLocal: true }).url
        .hostname,
    ).toBe("127.0.0.1");
  });
  it("forces the server-configured tenant and never leaks backend bodies", async () => {
    let sent: { tenant_id?: string } = {};
    const ok = (async (_u: unknown, init?: RequestInit) => {
      sent = JSON.parse(String(init?.body));
      return new Response(JSON.stringify({ ...REPORT, tenant_id: "tenant-x" }), { status: 200 });
    }) as typeof fetch;
    const r = await executeDispaterReconciliation(
      { serviceUrl: "https://a.example", serviceToken: TOKEN, tenantId: "tenant-x" },
      { ...getFixture("clean_control_v1"), tenant_id: "attacker-tenant" },
      ok,
    );
    expect(sent.tenant_id).toBe("tenant-x");
    expect(r.financial_summary.confirmed_recovery_usd).toBe("0.00");
    const fail = (async () =>
      new Response("secret internal trace", { status: 500 })) as typeof fetch;
    await expect(
      executeDispaterReconciliation(
        { serviceUrl: "https://a.example", serviceToken: TOKEN },
        undefined,
        fail,
      ),
    ).rejects.toThrow(/^DISPATER API error \(500\)$/);
  });
});

const FINDING = {
  finding_id: "finding-1",
  code: "UNBILLED_JOB",
  subject: "synthetic-job",
  severity: "HIGH",
  exposure_usd: "1250.00",
  evidence: [{ kind: "job", record_sha256: "record-digest" }],
  authority: "NONE",
  xaeli_explanation: { now: "n", changed: "c", next: "n", why: "w", proof: "p" },
  finding_sha256: "finding-digest",
};
const INTEGRITY = {
  qualification: "CALCULATED",
  observation_state: "OBSERVED",
  independent_root_count: 1,
  independent_verification: "NOT_VERIFIED",
  source_root_sha256: "source-digest",
  reasons: ["Single unverified snapshot"],
};

describe("dispater evidence contract", () => {
  it("preserves authenticated report structure through server validation and JSON export", async () => {
    const report = {
      ...REPORT,
      receipt_auth: { algorithm: "HMAC-SHA256", key_id: "test", future: { nested: true } },
      receipt_mac: "mac",
      future_metadata: { untouched: [1, { value: "x" }] },
      counts: { ...REPORT.counts, future_count: 3 },
      financial_summary: { ...REPORT.financial_summary, future_summary: { amount: "1.00" } },
      findings: [
        {
          ...FINDING,
          future_finding: { value: "retained" },
          evidence: [{ ...FINDING.evidence[0], lineage: { parent: "root" } }],
          evidence_integrity: { ...INTEGRITY, future_integrity: { timestamp: null } },
          xaeli_explanation: { ...FINDING.xaeli_explanation, advisory_metadata: { model: null } },
        },
      ],
    };
    const transport = (async () =>
      new Response(JSON.stringify(report), { status: 200 })) as typeof fetch;
    const parsed = await executeDispaterReconciliation(
      { serviceUrl: "https://a.example", serviceToken: TOKEN, tenantId: "tenant-x" },
      undefined,
      transport,
    );
    expect(JSON.parse(JSON.stringify(parsed))).toEqual(report);
  });
  it("keeps legacy AUDIT_COMPLETE reports unverified with unknown freshness and roots", () => {
    const report = DispaterReconciliationReportSchema.parse({ ...REPORT, findings: [FINDING] });
    expect(getDispaterEvidencePresentation(report.findings[0])).toMatchObject({
      verification: "NOT VERIFIED",
      qualification: "NOT VERIFIED",
      freshness: "UNKNOWN",
      observationState: "UNKNOWN",
      independentRootCount: null,
      sourceRootSha256: null,
    });
    expect(report.findings[0]).not.toHaveProperty("evidence_integrity");
  });
  it("does not promote self-reported verification to authority", () => {
    const finding = DispaterFindingSchema.parse({
      ...FINDING,
      evidence_integrity: { ...INTEGRITY, independent_verification: "VERIFIED" },
    });
    expect(getDispaterEvidencePresentation(finding)).toMatchObject({
      verification: "NOT VERIFIED",
      freshness: "UNKNOWN",
      qualification: "CALCULATED",
      reportedVerification: "VERIFIED",
      independentRootCount: 1,
      sourceRootSha256: "source-digest",
    });
  });
  it.each([-1, 1.5, "2"])("rejects malformed independent root count %s", (count) => {
    expect(
      DispaterFindingSchema.safeParse({
        ...FINDING,
        evidence_integrity: { ...INTEGRITY, independent_root_count: count },
      }).success,
    ).toBe(false);
  });
  it("rejects partial verification metadata", () => {
    expect(DispaterFindingSchema.safeParse({ ...FINDING, evidence_integrity: {} }).success).toBe(
      false,
    );
  });
});
