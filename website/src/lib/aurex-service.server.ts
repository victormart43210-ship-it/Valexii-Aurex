/**
 * Server-only adapter for an external AUREX Python/FastAPI service.
 * Requires AUREX_SERVICE_URL (https, non-local) and AUREX_SERVICE_TOKEN. Fails closed.
 * Only fixed read-only health and capability endpoints are called; no arbitrary execution is exposed.
 */
import { NO_BACKEND, type BackendChecks } from "./aurex-capabilities";

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
  const { createAurexClient } = await import("./aurex-client.server");
  const client = createAurexClient({ ...env, fetcher });
  if (!client.configured) return { state: "NOT_CONFIGURED", checks: NO_BACKEND };
  const health = await client.health();
  if (!health.ok) return { state: "OFFLINE", checks: NO_BACKEND };
  const capabilities = await client.capabilities();
  if (!capabilities.ok) return { state: "OFFLINE", checks: NO_BACKEND };
  return {
    state: "HEALTHY",
    checks: {
      serviceHealthy: true,
      serviceCapabilities: capabilities.value.capabilities
        .filter((c) => c.available)
        .map((c) => c.id),
    },
  };
}
