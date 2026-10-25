import { describe, expect, it } from "bun:test";
import { createDispaterAuditClient } from "../lib/dispater-audit-client.server";

describe("DISPATER customer-facing audit workflow client", () => {
  it("fails closed when unconfigured", async () => {
    const client = createDispaterAuditClient({});
    expect(client.configured).toBe(false);
    const result = await client.runTowingAudit();
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toBe("not_configured");
    }
  });

  it("executes synthetic towing audit when authenticated", async () => {
    const url = "https://valexii.com";
    const token = "12345678901234567890123456789012";
    const mockFetcher = (async () => {
      return new Response(
        JSON.stringify({
          id: "job-123456789012",
          kind: "regression_scan",
          state: "succeeded",
          createdAt: "2026-10-25T12:00:00Z",
          updatedAt: "2026-10-25T12:00:05Z",
          reservationUsd: 0.0,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      );
    }) as unknown as typeof fetch;

    const client = createDispaterAuditClient({ url, token, fetcher: mockFetcher });
    expect(client.configured).toBe(true);

    const result = await client.runTowingAudit();
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.report.sector).toBe("towing");
      expect(result.report.status).toBe("HOLD");
      expect(result.report.independent_verification).toBe("NOT VERIFIED");
      expect(result.report.counts.revenue_findings).toBe(3);
      expect(result.report.counts.readiness_findings).toBe(2);
      expect(result.report.findings.length).toBe(5);
      expect(result.report.self_issued_receipt_sha256).toContain("rcpt_");
    }
  });

  it("handles backend authentication failure fail-closed", async () => {
    const url = "https://valexii.com";
    const token = "12345678901234567890123456789012";
    const mockFetcher = (async () => {
      return new Response(JSON.stringify({ detail: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }) as unknown as typeof fetch;

    const client = createDispaterAuditClient({ url, token, fetcher: mockFetcher });
    const result = await client.runTowingAudit();
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toBe("unauthorized");
      expect(result.status).toBe(401);
    }
  });
});
