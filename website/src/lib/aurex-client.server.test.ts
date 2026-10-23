import { describe, expect, it } from "vitest";
import { createAurexClient } from "@/lib/aurex-client.server";

const BASE = "https://aurex.example.com";
const TOKEN = "x".repeat(32);
const encoder = new TextEncoder();

function streamResponse(chunks: Uint8Array[], headers: Record<string, string> = {}): Response {
  return new Response(
    new ReadableStream<Uint8Array>({
      start(controller) {
        for (const chunk of chunks) controller.enqueue(chunk);
        controller.close();
      },
    }),
    { status: 200, headers: { "content-type": "application/json", ...headers } },
  );
}
function client(fetcher: typeof fetch, token = TOKEN) {
  return createAurexClient({ url: BASE, token, fetcher });
}

describe("AUREX strictly bounded, server-only v1 transport", () => {
  it("refuses an oversized streamed body even without Content-Length", async () => {
    const big = new Uint8Array(64 * 1024).fill(65);
    const fetcher = (async () => streamResponse([big, big, big, big, big])) as typeof fetch;
    expect(await client(fetcher).health()).toEqual({ ok: false, error: "too_large" });
  });

  it("counts UTF-8 raw bytes, not JS string length", async () => {
    const payload = encoder.encode(JSON.stringify({ pad: "€".repeat(100_000) }));
    const fetcher = (async () => streamResponse([payload])) as typeof fetch;
    expect(await client(fetcher).health()).toEqual({ ok: false, error: "too_large" });
  });

  it("rejects falsely small Content-Length when actual streamed bytes overflow", async () => {
    const big = new Uint8Array(280_000).fill(65);
    const fetcher = (async () => streamResponse([big], { "content-length": "10" })) as typeof fetch;
    expect(await client(fetcher).health()).toEqual({ ok: false, error: "too_large" });
  });

  it("rejects huge declared Content-Length before parsing", async () => {
    const fetcher = (async () => streamResponse([encoder.encode("{}")], { "content-length": "99999999" })) as typeof fetch;
    expect(await client(fetcher).health()).toEqual({ ok: false, error: "too_large" });
  });

  it("rejects invalid or negative declared Content-Length", async () => {
    for (const length of ["NaN", "-1"]) {
      const fetcher = (async () => streamResponse([encoder.encode("{}")], { "content-length": length })) as typeof fetch;
      expect(await client(fetcher).health()).toEqual({ ok: false, error: "malformed" });
    }
  });

  it("rejects malformed UTF-8 bytes", async () => {
    const fetcher = (async () => streamResponse([Uint8Array.from([123, 34, 97, 34, 58, 255, 125])])) as typeof fetch;
    expect(await client(fetcher).health()).toEqual({ ok: false, error: "malformed" });
  });

  it("does not send credentials or requests when token is shorter than 32 chars", async () => {
    let calls = 0;
    const fetcher = (async () => { calls += 1; return new Response("{}"); }) as typeof fetch;
    for (const tok of ["x".repeat(16), "x".repeat(31)]) {
      const c = client(fetcher, tok);
      expect(c.configured).toBe(false);
      expect(await c.health()).toEqual({ ok: false, error: "not_configured" });
    }
    expect(calls).toBe(0);
  });

  it("accepts exactly the read-only bridge's five JSON response schemas", async () => {
    const now = new Date().toISOString();
    const responses: Record<string, unknown> = {
      "/v1/health": { status: "ok", version: "1.0.0-readonly", time: now },
      "/v1/capabilities": { capabilities: [] },
      "/v1/jobs": { jobs: [], nextCursor: null },
      "/v1/evidence": { evidence: [] },
      "/v1/budgets": { limitUsd: 0, reservedUsd: 0, spentUsd: 0, period: "month" },
    };
    const seen: string[] = [];
    const fetcher = (async (input: unknown, init?: RequestInit) => {
      const url = new URL(String(input));
      seen.push(url.pathname);
      expect(init?.redirect).toBe("manual");
      expect(init?.headers).toMatchObject({ Authorization: `Bearer ${TOKEN}` });
      const body = responses[url.pathname];
      return new Response(JSON.stringify(body ?? {}), { status: url.pathname in responses ? 200 : 404 });
    }) as typeof fetch;
    const c = client(fetcher);
    expect((await c.health()).ok).toBe(true);
    expect((await c.capabilities()).ok).toBe(true);
    expect((await c.listJobs()).ok).toBe(true);
    expect((await c.evidence()).ok).toBe(true);
    expect((await c.budget()).ok).toBe(true);
    expect(seen).toEqual(Object.keys(responses));
  });

  it("does not infer intelligence from a health payload containing a fake capability", async () => {
    const fetcher = (async () => new Response(JSON.stringify({ status: "ok", capabilities: ["memory-graph"] }))) as typeof fetch;
    expect(await client(fetcher).health()).toEqual({ ok: false, error: "malformed" });
  });

  it("rejects unbounded job submission and malformed response without authority", async () => {
    let calls = 0;
    const fetcher = (async () => { calls += 1; return new Response("{}"); }) as typeof fetch;
    const c = client(fetcher);
    expect((await c.createJob({ kind: "regression_scan", params: {}, maxCostUsd: 0 }, "bad")).ok).toBe(false);
    expect(calls).toBe(0);
    expect(await c.health()).toEqual({ ok: false, error: "malformed" });
  });
});
