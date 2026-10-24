import { createServerFn } from "@tanstack/react-start";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import {
  auditEntry,
  createRateLimiter,
  isAllowedUrl,
  isOwner,
  OBSERVE_PATHS,
  type ObserveResult,
} from "./aurex-control";

const limiter = createRateLimiter(10, 60_000);

/** Every privileged handler calls this: rate limit, owner check, value-free audit log. */
function assertOwner(userId: string, action = "privileged") {
  if (!limiter(userId)) {
    console.warn("[aurex-audit]", auditEntry(action, "rate_limited", userId));
    throw new Error("Too many requests");
  }
  if (!isOwner(userId, process.env["AUREX_OWNER_USER_ID"])) {
    console.warn("[aurex-audit]", auditEntry(action, "denied", userId));
    throw new Error("Forbidden");
  }
  console.info("[aurex-audit]", auditEntry(action, "allowed", userId));
}

export const checkAurexOwner = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => ({
    owner: isOwner(context.userId, process.env["AUREX_OWNER_USER_ID"]),
    ownerConfigured: !!process.env["AUREX_OWNER_USER_ID"],
  }));

/** Security Lab: owner-only read. No worker exists, so registry/history are empty and nothing executes. */
export const getSecurityLabState = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    assertOwner(context.userId, "security_lab_read");
    return { targets: [] as never[], history: [] as never[], workerConfigured: false };
  });

/** OBSERVE: bounded, allowlisted, no redirects followed, 5s timeout, owner only. */
export const observeSite = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }): Promise<{ checkedAt: string; results: ObserveResult[] }> => {
    assertOwner(context.userId, "observe");
    const results: ObserveResult[] = [];
    for (const path of OBSERVE_PATHS) {
      const url = `https://valexii.com${path}`;
      if (!isAllowedUrl(url)) {
        results.push({ url, status: null, ms: null, note: "blocked" });
        continue;
      }
      const t = Date.now();
      try {
        const res = await fetch(url, {
          method: "GET",
          redirect: "manual",
          signal: AbortSignal.timeout(5000),
          headers: { "User-Agent": "valexii-aurex-observe" },
        });
        await res.body?.cancel();
        const loc = res.headers.get("location");
        results.push({
          url,
          status: res.status,
          ms: Date.now() - t,
          note:
            res.status >= 300 && res.status < 400
              ? `redirect not followed${loc && isAllowedUrl(new URL(loc, url).href) ? "" : " (off-allowlist)"}`
              : res.ok
                ? "ok"
                : "error",
        });
      } catch {
        results.push({ url, status: null, ms: Date.now() - t, note: "timeout or network error" });
      }
    }
    return { checkedAt: new Date().toISOString(), results };
  });

/** Owner-only live capability status from the external AUREX service (fails closed). */
export const getAurexCapabilityStatus = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    assertOwner(context.userId, "capability_status");
    const { checkAurexService } = await import("./aurex-service.server");
    const { capabilities, resolveStatus, authorizeSpend } = await import("./aurex-capabilities");
    const svc = await checkAurexService({
      url: process.env["AUREX_SERVICE_URL"],
      token: process.env["AUREX_SERVICE_TOKEN"],
    });
    const budget = authorizeSpend({
      estimateUsd: 0,
      spentUsd: 0,
      budgetRaw: process.env["AUREX_BUDGET_USD"],
    });
    return {
      checkedAt: new Date().toISOString(),
      service: svc.state,
      budgetUsd: budget.budgetUsd,
      statuses: capabilities.map((c) => ({ id: c.id, status: resolveStatus(c, svc.checks) })),
    };
  });

/** Owner-only connection diagnostics. Returns result codes and booleans only — never URLs, tokens or raw bodies. */
export const getAurexDiagnostics = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    assertOwner(context.userId, "diagnostics");
    const { createAurexClient } = await import("./aurex-client.server");
    const { capabilityBacked } = await import("./aurex-api-schema");
    const url = process.env["AUREX_SERVICE_URL"];
    const token = process.env["AUREX_SERVICE_TOKEN"];
    const client = createAurexClient({ url, token });
    const code = (r: { ok: boolean; error?: string }) => (r.ok ? "ok" : (r.error ?? "error"));
    const health = await client.health();
    const caps = health.ok ? await client.capabilities() : null;
    const ev = caps?.ok ? await client.evidence() : null;
    const budget = health.ok ? await client.budget() : null;
    const jobs = health.ok ? await client.listJobs() : null;
    const backed =
      caps?.ok && ev?.ok
        ? caps.value.capabilities
            .filter((c) => capabilityBacked(c, ev.value.evidence))
            .map((c) => c.id)
        : [];
    return {
      checkedAt: new Date().toISOString(),
      urlSet: !!url,
      tokenSet: !!token,
      configured: client.configured,
      steps: {
        health: code(health),
        capabilities: caps ? code(caps) : "skipped",
        evidence: ev ? code(ev) : "skipped",
        budget: budget ? code(budget) : "skipped",
        jobs: jobs ? code(jobs) : "skipped",
      },
      remoteBudgetLimitUsd: budget?.ok ? budget.value.limitUsd : null,
      evidenceBackedCapabilities: backed,
    };
  });
