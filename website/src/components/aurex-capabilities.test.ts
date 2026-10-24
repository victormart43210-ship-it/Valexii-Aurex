import { describe, expect, it } from "vitest";
import { authorizeSpend, capabilities, resolveStatus } from "@/lib/aurex-capabilities";
import { checkAurexService, validServiceUrl } from "@/lib/aurex-service.server";

const token = "x".repeat(32);
const ok = (body: unknown, status = 200) =>
  (async () => new Response(JSON.stringify(body), { status })) as unknown as typeof fetch;

describe("AUREX capability registry", () => {
  it("has unique ids and no service capability is connected without a backend", () => {
    expect(new Set(capabilities.map((c) => c.id)).size).toBe(capabilities.length);
    for (const c of capabilities) {
      const st = resolveStatus(c);
      if (c.kind === "service") expect(st).toBe("NOT_CONFIGURED");
      if (c.kind === "future") expect(st).toBe("PLANNED");
    }
  });
  it("only connects capabilities the healthy service explicitly reports", () => {
    const mem = capabilities.find((c) => c.id === "memory-graph")!;
    expect(resolveStatus(mem, { serviceHealthy: true, serviceCapabilities: [] })).toBe(
      "NOT_CONFIGURED",
    );
    expect(
      resolveStatus(mem, { serviceHealthy: false, serviceCapabilities: ["memory-graph"] }),
    ).toBe("NOT_CONFIGURED");
    expect(
      resolveStatus(mem, { serviceHealthy: true, serviceCapabilities: ["memory-graph"] }),
    ).toBe("REAL_CONNECTED");
    const twin = capabilities.find((c) => c.id === "digital-twin")!;
    expect(
      resolveStatus(twin, { serviceHealthy: true, serviceCapabilities: ["digital-twin"] }),
    ).toBe("PLANNED");
  });
  it("marks shell/python/API capabilities owner-only", () => {
    for (const id of [
      "unix-workers",
      "python-lab",
      "private-research-api",
      "private-command-center",
    ])
      expect(capabilities.find((c) => c.id === id)?.restricted).toBe(true);
  });
});

describe("AUREX service adapter fails closed", () => {
  it("rejects missing, insecure or local URLs", () => {
    for (const u of [
      undefined,
      "",
      "http://aurex.example.com",
      "https://localhost",
      "https://127.0.0.1",
      "https://192.168.1.5",
      "https://10.0.0.1",
      "https://[::1]",
      "https://chromebook.local",
      "https://u:p@aurex.example.com",
    ])
      expect(validServiceUrl(u)).toBeNull();
    expect(validServiceUrl("https://aurex.example.com")).not.toBeNull();
  });
  it("is NOT_CONFIGURED without url or token", async () => {
    expect((await checkAurexService({})).state).toBe("NOT_CONFIGURED");
    expect(
      (await checkAurexService({ url: "https://aurex.example.com", token: "short" })).state,
    ).toBe("NOT_CONFIGURED");
    expect(
      (await checkAurexService({ url: "https://aurex.example.com", token: "x".repeat(16) })).state,
    ).toBe("NOT_CONFIGURED");
  });
  it("is OFFLINE on errors, bad status or malformed body", async () => {
    const env = { url: "https://aurex.example.com", token };
    expect(
      (
        await checkAurexService(env, (async () => {
          throw new Error("down");
        }) as unknown as typeof fetch)
      ).state,
    ).toBe("OFFLINE");
    expect((await checkAurexService(env, ok({}, 503))).state).toBe("OFFLINE");
    expect((await checkAurexService(env, ok({ status: "ok" }))).state).toBe("OFFLINE");
  });
  it("checks the documented routes and only connects evidence-backed capabilities", async () => {
    const calls: string[] = [];
    const fetcher = (async (input: URL, init: RequestInit) => {
      calls.push(String(input));
      expect(new Headers(init.headers).get("Authorization")).toBe("Bearer " + token);
      const body =
        input.pathname === "/v1/health"
          ? { status: "ok", version: "0.1.0", time: new Date().toISOString() }
          : input.pathname === "/v1/capabilities"
            ? {
                capabilities: [
                  { id: "memory-graph", available: true, evidenceId: "ev-1", verifiedAt: null },
                  { id: "evidence-vault", available: true, evidenceId: "ev-2", verifiedAt: null },
                ],
              }
            : {
                evidence: [
                  {
                    id: "ev-1",
                    capabilityId: "memory-graph",
                    kind: "test_run",
                    collectedAt: new Date().toISOString(),
                    sha256: "a".repeat(64),
                    summary: "verified fixture",
                  },
                  {
                    id: "ev-2",
                    capabilityId: "evidence-vault",
                    kind: "test_run",
                    collectedAt: new Date(Date.now() - 8 * 86400_000).toISOString(),
                    sha256: "b".repeat(64),
                    summary: "expired fixture",
                  },
                ],
              };
      return new Response(JSON.stringify(body));
    }) as unknown as typeof fetch;
    const r = await checkAurexService({ url: "https://aurex.example.com", token }, fetcher);
    expect(r.state).toBe("HEALTHY");
    expect(r.checks.serviceCapabilities).toEqual(["memory-graph"]);
    expect(calls).toEqual([
      "https://aurex.example.com/v1/health",
      "https://aurex.example.com/v1/capabilities",
      "https://aurex.example.com/v1/evidence",
    ]);
  });
});

describe("cost governor contract", () => {
  it("defaults to no spend", () => {
    expect(authorizeSpend({ estimateUsd: 0.01, spentUsd: 0, budgetRaw: undefined }).allowed).toBe(
      false,
    );
    expect(authorizeSpend({ estimateUsd: 1, spentUsd: 0, budgetRaw: "abc" }).allowed).toBe(false);
    expect(authorizeSpend({ estimateUsd: 1, spentUsd: 0, budgetRaw: "-5" }).allowed).toBe(false);
    expect(authorizeSpend({ estimateUsd: 0, spentUsd: 0, budgetRaw: undefined }).allowed).toBe(
      true,
    );
  });
  it("enforces budget and rejects invalid estimates", () => {
    expect(authorizeSpend({ estimateUsd: 4, spentUsd: 5, budgetRaw: "10" }).allowed).toBe(true);
    expect(authorizeSpend({ estimateUsd: 6, spentUsd: 5, budgetRaw: "10" }).allowed).toBe(false);
    expect(authorizeSpend({ estimateUsd: NaN, spentUsd: 0, budgetRaw: "10" }).allowed).toBe(false);
    expect(authorizeSpend({ estimateUsd: -1, spentUsd: 0, budgetRaw: "10" }).allowed).toBe(false);
  });
});
