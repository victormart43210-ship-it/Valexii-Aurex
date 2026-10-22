/**
 * KUSANAGI XXVI — DRAFT owner-only NVIDIA bridge for Valexii's TanStack Start site.
 * Server-only. Do not import this module into any client component except via
 * createServerFn handles. Requires verified owner identity and THREE gates:
 * website feature flag, operator test approval, and backend NVIDIA opt-in.
 *
 * The browser NEVER receives AUREX or NVIDIA secrets. Every result is
 * informational, never evidence or authorization. NO autonomous retries.
 */
import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import { createRateLimiter, isOwner } from "./aurex-control";

const STAGING_URL = "https://aurex-api-aurex-staging.up.railway.app";
const WAIT_MS = 15_000;
const MAX_BYTES = 24_000;
const LIMITER = createRateLimiter(2, 60_000);
const Input = z.object({ question: z.string().trim().min(1).max(500) }).strict();
const Reply = z.object({
  reply: z.string().min(1).max(1500),
  provider: z.literal("NVIDIA_NIM"),
  model: z.string().min(1).max(80),
  authority: z.literal("NONE"),
  verification: z.literal("NOT_VERIFIED"),
}).strict();
const AgentStatus = z.object({
  chatConfigured: z.boolean(),
  modelProvider: z.string(),
  providerConnection: z.string(),
}).passthrough();

export type NvidiaResult = {
  status: "HOLD" | "UNVERIFIED_NVIDIA_NARRATIVE";
  answer: string | null;
  model: string | null;
  authority: "NONE";
  verification: "NOT_VERIFIED";
  release: "HOLD";
};
export const HOLD: NvidiaResult = {
  status: "HOLD", answer: null, model: null,
  authority: "NONE", verification: "NOT_VERIFIED", release: "HOLD",
};

function ownerOnly(id: string): void {
  if (!isOwner(id, process.env["AUREX_OWNER_USER_ID"])) {
    throw new Error("Forbidden");
  }
}
function allowSite(): boolean {
  return process.env["AUREX_NVIDIA_SITE_ENABLED"] === "true";
}
function operatorApproved(): boolean {
  // Separate deliberate action required; not silently inferred from website activation.
  return process.env["AUREX_NVIDIA_OPERATOR_TEST_APPROVED"] === "true";
}
function credentials(): string | null {
  const raw = process.env["AUREX_STAGING_SERVICE_URL"];
  const token = process.env["AUREX_STAGING_SERVICE_TOKEN"];
  if (!raw || !token || token.length < 32) return null;
  try {
    const u = new URL(raw);
    if (u.origin !== STAGING_URL || u.pathname !== "/" || u.search || u.hash || u.username || u.password) return null;
  } catch { return null; }
  return token;
}

async function requestBackend(path: "/v1/agent/status" | "/v1/agent/ask", token: string, body?: unknown): Promise<unknown> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), WAIT_MS);
  try {
    const response = await fetch(`${STAGING_URL}${path}`, {
      method: body === undefined ? "GET" : "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      },
      redirect: "manual", cache: "no-store", signal: controller.signal,
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    if (response.status !== 200) return null; // includes 3xx, 4xx, 5xx
    const length = Number(response.headers.get("content-length") || 0);
    if (!Number.isFinite(length) || length > MAX_BYTES) return null;
    const reader = response.body?.getReader();
    if (!reader) return null;
    const chunks: Uint8Array[] = [];
    let n = 0;
    for (;;) {
      const part = await reader.read();
      if (part.done) break;
      n += part.value.byteLength;
      if (n > MAX_BYTES) { await reader.cancel(); return null; }
      chunks.push(part.value);
    }
    const bytes = new Uint8Array(n);
    let i = 0;
    for (const chunk of chunks) { bytes.set(chunk, i); i += chunk.length; }
    return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
  } catch { return null; }
  finally { clearTimeout(timeout); }
}

/** Status reflects configuration only, NOT a provider connection or a model proof. */
export const getNvidiaOwnerStatus = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    ownerOnly(context.userId);
    const base = {
      status: "HOLD" as const, authority: "NONE" as const,
      verification: "NOT_VERIFIED" as const, release: "HOLD" as const,
    };
    if (!allowSite()) return { ...base, stage: "WEBSITE_DISABLED" as const };
    const token = credentials();
    if (!token) return { ...base, stage: "STAGING_SECRETS_MISSING" as const };
    const result = AgentStatus.safeParse(await requestBackend("/v1/agent/status", token));
    if (!result.success) return { ...base, stage: "BACKEND_UNAVAILABLE" as const };
    if (!result.data.chatConfigured || result.data.modelProvider !== "NVIDIA_NIM") {
      return { ...base, stage: "NVIDIA_BACKEND_DISABLED" as const };
    }
    return { ...base,
      stage: operatorApproved() ? "READY_FOR_ONE_OWNER_TEST" as const : "AWAITING_OPERATOR_APPROVAL" as const,
    };
  });

/** User-clicked, owner-only, bounded staging test; no autonomous or public calls. */
export const askNvidiaOwner = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .validator(Input)
  .handler(async ({ context, data }): Promise<NvidiaResult> => {
    ownerOnly(context.userId);
    if (!allowSite() || !operatorApproved() || !LIMITER(context.userId)) return HOLD;
    const token = credentials();
    if (!token) return HOLD;
    // Preflight provider and configuration before making any chargeable request.
    const check = AgentStatus.safeParse(await requestBackend("/v1/agent/status", token));
    if (!check.success || !check.data.chatConfigured || check.data.modelProvider !== "NVIDIA_NIM") return HOLD;
    const response = Reply.safeParse(await requestBackend("/v1/agent/ask", token, { question: data.question }));
    if (!response.success) return HOLD;
    return {
      status: "UNVERIFIED_NVIDIA_NARRATIVE", answer: response.data.reply,
      model: response.data.model, authority: "NONE", verification: "NOT_VERIFIED", release: "HOLD",
    };
  });
