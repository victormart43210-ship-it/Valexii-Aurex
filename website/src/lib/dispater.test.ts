import { describe, it, expect } from "vitest";
import {
  DispaterConfigError,
  executeDispaterDocument,
  executeDispaterReconciliation,
  exportVerifiedDispaterRun,
  getFixture,
  listDispaterRuns,
  readDispaterRun,
  recordSyntheticObservation,
  resolveDispaterConfig,
} from "./dispater.server";

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
    const doc = (async (_u: unknown, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body)) as { tenant_id?: string; kind?: string };
      expect(body.tenant_id).toBe("tenant-x");
      expect(body.kind).toBe("csv");
      return new Response(
        JSON.stringify({
          authority_state: "HOLD",
          financial_authority: "NONE",
          ingestion_authenticated: false,
          ocr_status: "NOT_INSTALLED",
          ingestion: {
            source_sha256: "ab".repeat(32),
            filename: "synthetic-invoice.csv",
            kind: "csv",
            processor: { name: "dispater_ingest", version: "v1", model: null, ocr: "NOT_INSTALLED" },
            provenance: [{ source_sha256: "ab".repeat(32), row: "2" }],
            field_provenance: [],
            limits: "synthetic",
          },
          report: { ...REPORT, tenant_id: "tenant-x" },
        }),
        { status: 200 },
      );
    }) as typeof fetch;
    const admitted = await executeDispaterDocument(
      { serviceUrl: "https://a.example", serviceToken: TOKEN, tenantId: "tenant-x" },
      doc,
    );
    expect(admitted.financial_authority).toBe("NONE");
    expect(admitted.ingestion_authenticated).toBe(false);
    expect(admitted.report.financial_summary.confirmed_recovery_usd).toBe("0.00");
    const fail = (async () => new Response("secret internal trace", { status: 500 })) as typeof fetch;
    await expect(
      executeDispaterReconciliation(
        { serviceUrl: "https://a.example", serviceToken: TOKEN },
        undefined,
        fail,
      ),
    ).rejects.toThrow(/^DISPATER API error \(500\)$/);
    const denied = (async () => new Response("token=secret", { status: 401 })) as typeof fetch;
    await expect(
      executeDispaterReconciliation(
        { serviceUrl: "https://a.example", serviceToken: TOKEN },
        undefined,
        denied,
      ),
    ).rejects.toThrow(/^DISPATER API error \(401\)$/);
  });
  it("reads back the same receipt and refuses a mismatched run", async () => {
    const stored = { ...REPORT, tenant_id: "tenant-x", run_id: "run-" + "a".repeat(32), receipt_sha256: "abc" };
    const ok = (async () => new Response(JSON.stringify(stored), { status: 200 })) as typeof fetch;
    const report = await readDispaterRun(
      { serviceUrl: "https://a.example", serviceToken: TOKEN, tenantId: "tenant-x" },
      stored.run_id,
      ok,
    );
    expect(report.receipt_sha256).toBe("abc");
    expect(report.financial_summary.confirmed_recovery_usd).toBe("0.00");
    const wrong = (async () =>
      new Response(JSON.stringify({ ...stored, run_id: "run-" + "b".repeat(32) }), { status: 200 })) as typeof fetch;
    await expect(
      readDispaterRun(
        { serviceUrl: "https://a.example", serviceToken: TOKEN, tenantId: "tenant-x" },
        stored.run_id,
        wrong,
      ),
    ).rejects.toThrow("DISPATER API returned an invalid report");
  });
  it("lists stored runs and refuses a failed receipt export", async () => {
    const runId = "run-" + "a".repeat(32);
    const listed = (async (url: string) => {
      expect(url).toContain("limit=8");
      return new Response(
        JSON.stringify({
          tenant_id: "tenant-x",
          count: 1,
          runs: [
            {
              run_id: runId,
              dataset_sha256: "a",
              receipt_sha256: "ab".repeat(32),
              status: "AUDIT_COMPLETE",
              created_at: "2026-11-06T22:00:00+00:00",
            },
          ],
        }),
        { status: 200 },
      );
    }) as typeof fetch;
    const history = await listDispaterRuns(
      { serviceUrl: "https://a.example", serviceToken: TOKEN, tenantId: "tenant-x" },
      listed,
    );
    expect(history.runs[0]?.run_id).toBe(runId);
    const failed = (async () =>
      new Response(
        JSON.stringify({
          export_authorization: "TENANT_BEARER",
          third_party_release: false,
          training_reuse: "NOT_AUTHORIZED",
          deletion: "NOT_IMPLEMENTED",
          receipt_authenticity: "FAIL",
          report: { ...REPORT, tenant_id: "tenant-x", run_id: runId },
        }),
        { status: 200 },
      )) as typeof fetch;
    await expect(
      exportVerifiedDispaterRun(
        { serviceUrl: "https://a.example", serviceToken: TOKEN, tenantId: "tenant-x" },
        runId,
        failed,
      ),
    ).rejects.toThrow("DISPATER API returned an invalid report");
  });
  it("records an observation only when the effect stays none", async () => {
    const ok = (async (_url: string, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body)) as { effect?: string; tenant_id?: string };
      expect(body.effect).toBe("NONE");
      expect(body.tenant_id).toBe("tenant-x");
      return new Response(
        JSON.stringify({
          schema: "aurex.proposal.v1",
          decision: "RECORDED",
          effect: "NONE",
          authority: "NONE",
          financial_authority: "NONE",
          production: "HOLD",
          launch: "NOT_STARTED",
          independent_verification: "NOT_VERIFIED",
          problems: [],
          tenant_id: "tenant-x",
        }),
        { status: 200 },
      );
    }) as typeof fetch;
    const decision = await recordSyntheticObservation(
      { serviceUrl: "https://a.example", serviceToken: TOKEN, tenantId: "tenant-x" },
      "ab".repeat(32),
      ok,
    );
    expect(decision.decision).toBe("RECORDED");
    expect(decision.effect).toBe("NONE");
  });
});
