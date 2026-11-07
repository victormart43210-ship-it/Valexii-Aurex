/**
 * Server-only adapter for an external AUREX Python/FastAPI service.
 * Requires AUREX_SERVICE_URL (https, non-local) and AUREX_SERVICE_TOKEN. Fails closed.
 * Only fixed read-only service endpoints are called; no arbitrary execution is exposed.
 */
import { NO_BACKEND, type BackendChecks } from "./aurex-capabilities";
import { HealthSchema, MAX_RESPONSE_BYTES, capabilityBacked } from "./aurex-api-schema";

export type ServiceState = {
  state: "NOT_CONFIGURED" | "OFFLINE" | "HEALTHY";
  checks: BackendChecks;
};

export function validServiceUrl(raw: string | undefined): URL | null {
  if (!raw) return null;
  let u: URL;
  try {
    u = new URL(raw);
  } catch {
    return null;
  }
  const h = u.hostname.toLowerCase();
  const local =
    h === "localhost" ||
    h.endsWith(".local") ||
    h.endsWith(".internal") ||
    /^(127\.|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.|0\.)/.test(h) ||
    h.includes(":") ||
    /^\d+$/.test(h);
  if (u.protocol !== "https:" || local || u.username || u.password) return null;
  return u;
}

export async function checkAurexService(
  env: { url?: string | undefined; token?: string | undefined },
  fetcher: typeof fetch = fetch,
): Promise<ServiceState> {
  const base = validServiceUrl(env.url);
  if (!base || !env.token || env.token.length < 32)
    return { state: "NOT_CONFIGURED", checks: NO_BACKEND };
  try {
    const res = await fetcher(new URL("/v1/health", base), {
      headers: { Authorization: `Bearer ${env.token}`, Accept: "application/json" },
      redirect: "manual",
      signal: AbortSignal.timeout(5000),
    });
    const length = Number(res.headers.get("content-length") ?? "0");
    if (!res.ok || length > MAX_RESPONSE_BYTES) return { state: "OFFLINE", checks: NO_BACKEND };
    const text = await res.text();
    if (text.length > MAX_RESPONSE_BYTES) return { state: "OFFLINE", checks: NO_BACKEND };
    let body: unknown;
    try {
      body = JSON.parse(text);
    } catch {
      return { state: "OFFLINE", checks: NO_BACKEND };
    }
    if (!HealthSchema.safeParse(body).success) return { state: "OFFLINE", checks: NO_BACKEND };
    const { createAurexClient } = await import("./aurex-client.server");
    const client = createAurexClient({ ...env, fetcher });
    const [capabilities, evidence] = await Promise.all([client.capabilities(), client.evidence()]);
    if (!capabilities.ok || !evidence.ok) return { state: "OFFLINE", checks: NO_BACKEND };
    const serviceCapabilities = capabilities.value.capabilities
      .filter((capability) => capabilityBacked(capability, evidence.value.evidence))
      .map((capability) => capability.id);
    return { state: "HEALTHY", checks: { serviceHealthy: true, serviceCapabilities } };
  } catch {
    return { state: "OFFLINE", checks: NO_BACKEND };
  }
}
