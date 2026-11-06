import { describe, it, expect } from "vitest";
import {
  DispaterConfigError,
  executeDispaterDocument,
  executeDispaterReconciliation,
  getFixture,
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
});
