import { z } from "zod";
import { createRateLimiter, isOwner } from "./aurex-control";

const STAGING_URL = "https://aurex-api-aurex-staging.up.railway.app";
const MAX_BYTES = 24_000;
// Best-effort local throttle only; Railway must independently enforce durable quota.
const limit = createRateLimiter(2, 60_000);
const Status = z.object({
  chatConfigured: z.boolean(),
  modelProvider: z.string().max(80),
  providerConnection: z.literal("NOT_VERIFIED"),
  inferenceState: z.literal("DISABLED_BY_POLICY").optional(),
  missingConfiguration: z.array(z.enum(["provider_credential", "model"])).max(2).optional(),
});
export type NvidiaEnvironment = {
  owner: string | undefined; enabled: string | undefined; approved: string | undefined;
  url: string | undefined; token: string | undefined;
};
export type NvidiaResult = {
  status: "HOLD" | "UNVERIFIED_NVIDIA_NARRATIVE"; answer: string | null; model: string | null;
  authority: "NONE"; verification: "NOT_VERIFIED"; release: "HOLD";
};
const HOLD: NvidiaResult = {
  status: "HOLD", answer: null, model: null, authority: "NONE", verification: "NOT_VERIFIED", release: "HOLD",
};
function ownerOnly(id: string, env: NvidiaEnvironment) {
  if (!isOwner(id, env.owner)) throw new Error("Forbidden");
}
function gate(env: NvidiaEnvironment) {
  if (!env.url || !env.token || env.token.length < 32 || /\s/.test(env.token)) return "STAGING_SECRETS_MISSING" as const;
  try {
    const u = new URL(env.url);
    if (u.origin !== STAGING_URL || u.pathname !== "/" || u.search || u.hash || u.username || u.password) return "STAGING_SECRETS_MISSING" as const;
  } catch { return "STAGING_SECRETS_MISSING" as const; }
  return null;
}
async function requestBackend(path: "/v1/agent/status", token: string, fetcher: typeof fetch): Promise<unknown> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15_000);
  let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
  try {
    const response = await fetcher(`${STAGING_URL}${path}`, {
      method: "GET", redirect: "manual", cache: "no-store", signal: controller.signal,
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
    });
    if (response.status === 401 || response.status === 403) {
      await response.body?.cancel();
      return { transportFailure: "AUTHORIZATION_DENIED" };
    }
    const length = Number(response.headers.get("content-length") ?? "0");
    if (response.status !== 200 || !Number.isFinite(length) || length < 0 || length > MAX_BYTES || !response.body) {
      await response.body?.cancel();
      return null;
    }
    reader = response.body.getReader();
    const chunks: Uint8Array[] = [];
    let total = 0;
    for (;;) {
      const part = await reader.read();
      if (part.done) break;
      total += part.value.byteLength;
      if (total > MAX_BYTES) { await reader.cancel(); controller.abort(); return null; }
      chunks.push(part.value);
    }
    const bytes = new Uint8Array(total);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
    const text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    // Reject accidental credential echoes rather than returning them to the browser.
    if (text.includes(token) || /Bearer\s+\S+/i.test(text)) return null;
    const decoded: unknown = JSON.parse(text);
    if (JSON.stringify(decoded).includes(token)) return null;
    return decoded;
  } catch {
    try { await reader?.cancel(); } catch { /* best effort */ }
    return null;
  } finally { reader?.releaseLock(); clearTimeout(timer); }
}
export async function readNvidiaOwnerStatus(id: string, env: NvidiaEnvironment, fetcher: typeof fetch = fetch) {
  ownerOnly(id, env);
  const blocked = gate(env);
  if (blocked || !env.token) return { ...HOLD, stage: blocked ?? "STAGING_SECRETS_MISSING" };
  if (!limit(id)) return { ...HOLD, stage: "RATE_LIMITED" as const };
  const raw = await requestBackend("/v1/agent/status", env.token, fetcher);
  if (raw && typeof raw === "object" && "transportFailure" in raw) return { ...HOLD, stage: "AUTHORIZATION_DENIED" as const };
  const status = Status.safeParse(raw);
  if (!status.success) return { ...HOLD, stage: "BACKEND_UNAVAILABLE" as const };
  return { ...HOLD, stage: "DISABLED_BY_POLICY" as const, missingConfiguration: status.data.missingConfiguration ?? [] };
}
export async function askNvidiaOwnerTest(id: string, question: string, env: NvidiaEnvironment, fetcher: typeof fetch = fetch): Promise<NvidiaResult> {
  ownerOnly(id, env);
  // Compatibility signature retained for the existing owner RPC. Neither site flags
  // nor a backend's chatConfigured boolean establish monetary authorization.
  void question; void fetcher;
  return { ...HOLD };
}
