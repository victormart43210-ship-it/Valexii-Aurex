import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { createAurexClient } from "@/lib/aurex-client.server";
import { capabilityBacked, evidenceFresh, type Evidence } from "@/lib/aurex-api-schema";
import { createBudgetLedger } from "@/lib/aurex-budget";

const token = "t".repeat(32);
const url = "https://aurex.example.com";
const now = new Date().toISOString();
const respond = (body: unknown, status = 200, headers: Record<string, string> = {}) =>
  (async () =>
    new Response(typeof body === "string" ? body : JSON.stringify(body), {
      status,
      headers,
    })) as unknown as typeof fetch;

describe("client fails closed", () => {
  it("not configured without url/token or with local url", async () => {
    expect((await createAurexClient({}).health()).ok).toBe(false);
    expect(await createAurexClient({ url: "https://127.0.0.1", token }).health()).toEqual({
      ok: false,
      error: "not_configured",
    });
    expect(
      await createAurexClient({ url: "http://aurex.example.com", token }).capabilities(),
    ).toEqual({ ok: false, error: "not_configured" });
  });
  it.each([
    ["non-JSON", "<html>", "malformed"],
    ["wrong literal", { status: "up", version: "1", time: now }, "malformed"],
    ["extra fields", { status: "ok", version: "1", time: now, secret: "x" }, "malformed"],
    ["bad time", { status: "ok", version: "1", time: "yesterday" }, "malformed"],
  ])("rejects malformed health: %s", async (_n, body, err) => {
    expect(await createAurexClient({ url, token, fetcher: respond(body) }).health()).toEqual({
      ok: false,
      error: err,
    });
  });
  it("maps 401/403 to unauthorized and 5xx to http_error", async () => {
    expect(
      (
        (await createAurexClient({ url, token, fetcher: respond({}, 401) }).health()) as {
          error: string;
        }
      ).error,
    ).toBe("unauthorized");
    expect(
      (
        (await createAurexClient({ url, token, fetcher: respond({}, 503) }).health()) as {
          error: string;
        }
      ).error,
    ).toBe("http_error");
  });
  it("treats redirects as errors (no following)", async () => {
    expect(
      (
        await createAurexClient({
          url,
          token,
          fetcher: respond("", 302, { location: "http://169.254.169.254/" }),
        }).health()
      ).ok,
    ).toBe(false);
  });
  it("rejects oversized responses", async () => {
    const big = respond("x", 200, { "content-length": String(10 * 1024 * 1024) });
    expect(await createAurexClient({ url, token, fetcher: big }).health()).toEqual({
      ok: false,
      error: "too_large",
    });
  });
  it("times out slow services", async () => {
    const slow = ((_u: unknown, init: RequestInit) =>
      new Promise((_r, rej) => {
        const timer = setTimeout(() => {}, 15000);
        init.signal?.addEventListener("abort", () => {
          clearTimeout(timer);
          rej(Object.assign(new Error("t"), { name: "TimeoutError" }));
        });
      })) as unknown as typeof fetch;
    expect(await createAurexClient({ url, token, timeoutMs: 500, fetcher: slow }).health()).toEqual(
      { ok: false, error: "timeout" },
    );
  });
  it("validates job inputs and idempotency keys before any request", async () => {
    let called = 0;
    const f = (async () => {
      called++;
      return new Response("{}");
    }) as unknown as typeof fetch;
    const c = createAurexClient({ url, token, fetcher: f });
    expect((await c.createJob({ kind: "benchmark", params: {}, maxCostUsd: 1 }, "short")).ok).toBe(
      false,
    );
    expect(
      (
        await c.createJob(
          { kind: "shell" as "benchmark", params: {}, maxCostUsd: 1 },
          "k".repeat(20),
        )
      ).ok,
    ).toBe(false);
    expect((await c.jobStatus("../etc/passwd")).ok).toBe(false);
    expect((await c.cancelJob("job1", "bad key!")).ok).toBe(false);
    expect(called).toBe(0);
  });
  it("sends idempotency key and only to the fixed /v1 path", async () => {
    let seen: { url: string; key: string | null } | null = null;
    const f = (async (u: URL, init: RequestInit) => {
      seen = { url: String(u), key: new Headers(init.headers).get("Idempotency-Key") };
      return new Response(
        JSON.stringify({
          id: "j1",
          kind: "benchmark",
          state: "queued",
          createdAt: now,
          updatedAt: now,
          reservationUsd: 0,
        }),
      );
    }) as unknown as typeof fetch;
    const r = await createAurexClient({ url, token, fetcher: f }).createJob(
      { kind: "benchmark", params: { n: 1 }, maxCostUsd: 0 },
      "k".repeat(20),
    );
    expect(r.ok).toBe(true);
    expect(seen).toEqual({ url: "https://aurex.example.com/v1/jobs", key: "k".repeat(20) });
  });
  it("authenticates the five read-only service endpoints", async () => {
    const paths: string[] = [];
    const fetcher = (async (url: URL, init: RequestInit) => {
      paths.push(url.pathname);
      expect(init.method).toBe("GET");
      expect(new Headers(init.headers).get("Authorization")).toBe("Bearer " + token);
      const body =
        url.pathname === "/v1/health"
          ? { status: "ok", version: "0.1.0", time: now }
          : url.pathname === "/v1/capabilities"
            ? { capabilities: [] }
            : url.pathname === "/v1/evidence"
              ? { evidence: [] }
              : url.pathname === "/v1/budgets"
                ? { limitUsd: 0, reservedUsd: 0, spentUsd: 0, period: "month" }
                : { jobs: [], nextCursor: null };
      return new Response(JSON.stringify(body));
    }) as unknown as typeof fetch;
    const client = createAurexClient({ url, token, fetcher });
    const results = await Promise.all([
      client.health(),
      client.capabilities(),
      client.evidence(),
      client.budget(),
      client.listJobs(),
    ]);
    expect(results.every((result) => result.ok)).toBe(true);
    expect(paths.sort()).toEqual([
      "/v1/budgets",
      "/v1/capabilities",
      "/v1/evidence",
      "/v1/health",
      "/v1/jobs",
    ]);
  });
});

describe("stale evidence never supports a capability", () => {
  const ev = (collectedAt: string, capabilityId = "memory-graph"): Evidence => ({
    id: "e1",
    capabilityId,
    kind: "test_run",
    collectedAt,
    sha256: "a".repeat(64),
    summary: "s",
  });
  const cap = { id: "memory-graph", available: true, evidenceId: "e1", verifiedAt: now };
  it("fresh evidence for the same capability backs it", () =>
    expect(capabilityBacked(cap, [ev(now)])).toBe(true));
  it("stale, future, mismatched or missing evidence does not", () => {
    expect(capabilityBacked(cap, [ev(new Date(Date.now() - 8 * 86400_000).toISOString())])).toBe(
      false,
    );
    expect(capabilityBacked(cap, [ev(new Date(Date.now() + 3600_000).toISOString())])).toBe(false);
    expect(capabilityBacked(cap, [ev(now, "evidence-vault")])).toBe(false);
    expect(capabilityBacked(cap, [])).toBe(false);
    expect(capabilityBacked({ ...cap, available: false }, [ev(now)])).toBe(false);
    expect(evidenceFresh(null)).toBe(false);
  });
  it.each([
    ["valid UTC time", { collectedAt: "2026-10-24T03:00:00.000Z" }, true],
    ["valid offset time", { collectedAt: "2026-10-24T05:00:00.000+02:00" }, true],
    ["expired time", { collectedAt: "2026-10-16T02:59:59.999Z" }, false],
    ["malformed time", { collectedAt: "not-a-timestamp" }, false],
    ["missing time", {}, false],
    ["future time", { collectedAt: "2026-10-24T03:00:00.001Z" }, false],
  ])("evaluates %s fail-closed", (_label, evidence, expected) => {
    const fixedNow = Date.parse("2026-10-24T03:00:00.000Z");
    expect(evidenceFresh(evidence as { collectedAt: string }, fixedNow)).toBe(expected);
  });
});

describe("budget reservations", () => {
  it("zero limit refuses all spend", () =>
    expect(createBudgetLedger(0).reserve(1)).toEqual({ ok: false, reason: "no_spend_default" }));
  it("concurrent requests never overspend", async () => {
    const l = createBudgetLedger(10);
    const out = await Promise.all(
      Array.from({ length: 50 }, () => Promise.resolve().then(() => l.reserve(1))),
    );
    expect(out.filter((r) => r.ok).length).toBe(10);
    expect(l.reserved()).toBe(10);
  });
  it("commit cannot exceed reservation; release frees budget", () => {
    const l = createBudgetLedger(5);
    const r = l.reserve(5);
    if (!r.ok) throw new Error();
    expect(l.commit(r.id, 6)).toBe(false);
    expect(l.release(r.id)).toBe(true);
    expect(l.reserve(5).ok).toBe(true);
  });
});

describe("authorization on new functions", () => {
  const fns = readFileSync("src/lib/aurex-control.functions.ts", "utf8");
  it("diagnostics requires owner and never returns url/token values", () => {
    const block = fns.slice(fns.indexOf("getAurexDiagnostics"));
    expect(block).toContain('assertOwner(context.userId, "diagnostics")');
    const ret = block.slice(block.indexOf("return {"), block.indexOf("evidenceBackedCapabilities"));
    expect(ret).not.toMatch(/(?<!!!)\b(url|token)\b\s*[,}:]/);
    expect(block).toContain("urlSet: !!url");
  });
  it("client module is server-only by filename", () => {
    expect(readFileSync("src/routes/aurex.tsx", "utf8")).not.toMatch(/aurex-client/);
  });
});
