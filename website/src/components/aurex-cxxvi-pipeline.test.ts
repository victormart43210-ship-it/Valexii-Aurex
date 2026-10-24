import { describe, expect, it, vi } from "vitest";
import {
  CapabilitiesSchema,
  EvidenceListSchema,
  PipelineReceiptSchema,
} from "@/lib/aurex-api-schema";
import { createAurexClient } from "@/lib/aurex-client.server";

const jobId = "job-0123456789abcdef01234567";
const evidenceId = "ev-0123456789abcdef01234567";
const receipt = {
  jobId, evidenceId,
  state: "succeeded", sha256: "a".repeat(64),
  observation: {
    probe: "sqlite_roundtrip_v1",
    executed: true, passed: true,
    sha256: "b".repeat(64),
    verification: "NOT VERIFIED",
  },
  integrity: "RECORDED", verification: "NOT VERIFIED",
  authority: "NONE", release: "HOLD",
};

describe("CXXVI pipeline receipts: trusted transport is not verified capability", () => {
  it("parses the exact wire shape and forbids extra customer fields", () => {
    expect(PipelineReceiptSchema.safeParse(receipt).success).toBe(true);
    expect(PipelineReceiptSchema.safeParse({
      ...receipt, observation: { ...receipt.observation, account: "secret" },
    }).success).toBe(false);
    expect(PipelineReceiptSchema.safeParse({ ...receipt, authority: "APPROVED" }).success).toBe(false);
    expect(PipelineReceiptSchema.safeParse({ ...receipt, verification: "PASS" }).success).toBe(false);
    expect(PipelineReceiptSchema.safeParse({ ...receipt, sha256: "not-a-hash" }).success).toBe(false);
    expect(PipelineReceiptSchema.safeParse({ ...receipt, state: "running" }).success).toBe(false);
  });

  it("accepts actual Python snake_case capabilities and local evidence kind", () => {
    expect(CapabilitiesSchema.safeParse({
      capabilities: [{ id: "regression_scan", available: false, evidenceId: null, verifiedAt: null }],
    }).success).toBe(true);
    expect(EvidenceListSchema.safeParse({
      evidence: [{
        id: evidenceId, capabilityId: "regression_scan",
        kind: "offline_probe", collectedAt: "2026-10-22T14:00:00+00:00",
        sha256: "f".repeat(64), summary: "Persisted locally; not fact verified",
      }],
    }).success).toBe(true);
  });

  it("only uses an authenticated server-side GET for valid IDs", async () => {
    const fetcher = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) =>
      new Response(JSON.stringify(receipt), { status: 200 }));
    const client = createAurexClient({
      url: "https://aurex.example.org",
      token: "x".repeat(40),
      fetcher: fetcher as typeof fetch,
    });
    const result = await client.jobReceipt(jobId);
    expect(result.ok).toBe(true);
    expect(fetcher).toHaveBeenCalledTimes(1);
    const [url, init] = fetcher.mock.calls[0]!;
    expect(String(url)).toBe("https://aurex.example.org/v1/jobs/" + jobId + "/receipt");
    expect(init!.method).toBe("GET");
    expect(init!.headers).toMatchObject({ Authorization: "Bearer " + "x".repeat(40) });
    expect(init!.redirect).toBe("manual");
    const invalid = await client.jobReceipt("../evidence");
    expect(invalid).toEqual({ ok: false, error: "invalid_input" });
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("fails closed on a malformed, fabricated or unavailable receipt", async () => {
    for (const value of [
      { ...receipt, authority: "APPROVED" },
      { ...receipt, observation: { probe: "customer_bank_upload", payload: "private" } },
      { ...receipt, hidden: "secret" },
    ]) {
      const client = createAurexClient({
        url: "https://aurex.example.org", token: "x".repeat(40),
        fetcher: (async () => new Response(JSON.stringify(value), { status: 200 })) as typeof fetch,
      });
      expect(await client.jobReceipt(jobId)).toEqual({ ok: false, error: "malformed" });
    }
    const client = createAurexClient({
      url: "https://aurex.example.org", token: "x".repeat(40),
      fetcher: (async () => new Response("", { status: 404 })) as typeof fetch,
    });
    const unavailable = await client.jobReceipt(jobId);
    expect(unavailable.ok).toBe(false);
  });
});
