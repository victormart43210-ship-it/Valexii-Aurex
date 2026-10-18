import { describe, expect, it } from "vitest";
import { createAurexClient } from "./aurex-client.server";

const TOKEN = "t".repeat(32);
const URL_OK = "https://aurex.example.com";
const res = (status: number, body: unknown = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

describe("AUREX server client fail-closed wiring", () => {
  it("refuses non-https, local and token-less configuration without calling", async () => {
    let calls = 0;
    const f = (async () => { calls++; return res(200); }) as typeof fetch;
    for (const url of ["http://aurex.example.com", "https://localhost", "https://127.0.0.1:8765", "https://10.0.0.2", undefined]) {
      const c = createAurexClient({ url, token: TOKEN, fetcher: f });
      expect(c.configured).toBe(false);
      expect(await c.health()).toEqual({ ok: false, error: "not_configured" });
    }
    expect((await createAurexClient({ url: URL_OK, token: "short", fetcher: f }).health()).ok).toBe(false);
    expect(calls).toBe(0);
  });

  it("sends the token only as a bearer header, never follows redirects", async () => {
    let seen: RequestInit | undefined;
    const f = (async (_u: unknown, init?: RequestInit) => { seen = init; return res(302); }) as typeof fetch;
    const r = await createAurexClient({ url: URL_OK, token: TOKEN, fetcher: f }).capabilities();
    expect(seen?.redirect).toBe("manual");
    expect((seen?.headers as Record<string, string>)["Authorization"]).toBe(`Bearer ${TOKEN}`);
    expect(r).toEqual({ ok: false, error: "http_error", status: 302 });
    expect(JSON.stringify(r)).not.toContain(TOKEN);
  });

  it("maps 401/403/404/409/503, network and timeout to typed errors", async () => {
    const at = (s: number) => createAurexClient({ url: URL_OK, token: TOKEN, fetcher: (async () => res(s)) as typeof fetch });
    expect(await at(401).listJobs()).toMatchObject({ ok: false, error: "unauthorized" });
    expect(await at(403).evidence()).toMatchObject({ ok: false, error: "unauthorized" });
    for (const s of [404, 409, 503]) expect(await at(s).budget()).toEqual({ ok: false, error: "http_error", status: s });
    const net = createAurexClient({ url: URL_OK, token: TOKEN, fetcher: (async () => { throw new TypeError("x"); }) as typeof fetch });
    expect(await net.health()).toEqual({ ok: false, error: "network" });
    const slow = createAurexClient({ url: URL_OK, token: TOKEN, fetcher: (async () => { throw Object.assign(new Error("t"), { name: "TimeoutError" }); }) as typeof fetch });
    expect(await slow.health()).toEqual({ ok: false, error: "timeout" });
  });

  it("rejects malformed bodies instead of inventing capabilities", async () => {
    const c = createAurexClient({ url: URL_OK, token: TOKEN, fetcher: (async () => res(200, { capabilities: "all" })) as typeof fetch });
    expect(await c.capabilities()).toEqual({ ok: false, error: "malformed" });
  });

  it("refuses job creation with a bad idempotency key before any request", async () => {
    let calls = 0;
    const c = createAurexClient({ url: URL_OK, token: TOKEN, fetcher: (async () => { calls++; return res(503); }) as typeof fetch });
    const r = await c.createJob({ kind: "regression_scan", params: { probe: "sqlite_roundtrip_v1" }, maxCostUsd: 0 } as never, "bad key");
    expect(r).toEqual({ ok: false, error: "invalid_input" });
    expect(calls).toBe(0);
  });
});

describe("AUREX server client bounded streaming reads", () => {
  const streamRes = (chunks: Uint8Array[], headers: Record<string, string> = {}) =>
    new Response(
      new ReadableStream<Uint8Array>({
        start(c) {
          for (const ch of chunks) c.enqueue(ch);
          c.close();
        },
      }),
      { status: 200, headers: { "content-type": "application/json", ...headers } },
    );
  const client = (f: typeof fetch) => createAurexClient({ url: URL_OK, token: TOKEN, fetcher: f });

  it("rejects a chunked body exceeding 256 KiB even with no Content-Length", async () => {
    const chunk = new Uint8Array(64 * 1024).fill(65);
    const f = (async () => streamRes([chunk, chunk, chunk, chunk, chunk])) as typeof fetch;
    expect(await client(f).health()).toEqual({ ok: false, error: "too_large" });
  });

  it("counts raw bytes, not UTF-16 length: multibyte evasion fails", async () => {
    // 100k three-byte characters: 300,000 bytes but text.length only 100,000.
    const payload = "€".repeat(100_000);
    const bytes = new TextEncoder().encode(`{"pad":"${payload}"}`);
    const f = (async () => streamRes([bytes])) as typeof fetch;
    expect(await client(f).health()).toEqual({ ok: false, error: "too_large" });
  });

  it("ignores a forged small Content-Length and still enforces the byte limit", async () => {
    const big = new Uint8Array(300 * 1024).fill(66);
    const f = (async () => streamRes([big], { "content-length": "10" })) as typeof fetch;
    expect(await client(f).health()).toEqual({ ok: false, error: "too_large" });
  });

  it("rejects early on a forged large Content-Length without reading", async () => {
    const f = (async () => streamRes([new Uint8Array(4)], { "content-length": "999999999" })) as typeof fetch;
    expect(await client(f).health()).toEqual({ ok: false, error: "too_large" });
  });

  it("fails closed on invalid UTF-8 bytes", async () => {
    const bad = new Uint8Array([0x7b, 0x22, 0x61, 0x22, 0x3a, 0xff, 0xfe, 0x7d]); // {"a":ÿþ} invalid
    const f = (async () => streamRes([bad])) as typeof fetch;
    expect(await client(f).health()).toEqual({ ok: false, error: "malformed" });
  });

  it("requires a >=32 character token before any request", async () => {
    let calls = 0;
    const f = (async () => { calls++; return res(200); }) as typeof fetch;
    for (const t of ["t".repeat(16), "t".repeat(31)]) {
      const c = createAurexClient({ url: URL_OK, token: t, fetcher: f });
      expect(c.configured).toBe(false);
      expect(await c.health()).toEqual({ ok: false, error: "not_configured" });
    }
    expect(calls).toBe(0);
  });

  it("accepts valid five-GET replies through the streaming path", async () => {
    const bodies: Record<string, unknown> = {
      "/v1/health": { status: "ok", version: "1.0.0-readonly", time: "2026-10-18T00:00:00Z" },
      "/v1/capabilities": { capabilities: [] },
      "/v1/jobs": { jobs: [], nextCursor: null },
      "/v1/evidence": { evidence: [] },
      "/v1/budgets": { limitUsd: 0, reservedUsd: 0, spentUsd: 0, period: "month" },
    };
    const f = (async (u: unknown) => {
      const path = new URL(String(u)).pathname;
      const body = bodies[path];
      if (!body) return res(404);
      return streamRes([new TextEncoder().encode(JSON.stringify(body))]);
    }) as typeof fetch;
    const c = client(f);
    expect((await c.health()).ok).toBe(true);
    expect((await c.capabilities()).ok).toBe(true);
    expect((await c.listJobs()).ok).toBe(true);
    expect((await c.evidence()).ok).toBe(true);
    expect((await c.budget()).ok).toBe(true);
  });
});