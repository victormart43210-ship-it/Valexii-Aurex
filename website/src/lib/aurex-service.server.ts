/**
 * Server-only adapter for an external AUREX Python/FastAPI service.
 * Requires AUREX_SERVICE_URL (https, non-local) and AUREX_SERVICE_TOKEN. Fails closed.
 * Only a fixed read-only health endpoint is called; no arbitrary execution is exposed.
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
  const base = validServiceUrl(env.url);
  if (!base || !env.token || env.token.length < 16)
    return { state: "NOT_CONFIGURED", checks: NO_BACKEND };
  try {
    const res = await fetcher(new URL("/v1/health", base), {
      headers: { Authorization: `Bearer ${env.token}`, Accept: "application/json" },
      redirect: "manual",
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return { state: "OFFLINE", checks: NO_BACKEND };
    const body = (await res.json()) as { status?: unknown; capabilities?: unknown };
    if (body.status !== "ok" || !Array.isArray(body.capabilities))
      return { state: "OFFLINE", checks: NO_BACKEND };
    const caps = body.capabilities.filter(
      (c): c is string => typeof c === "string" && /^[a-z-]{1,64}$/.test(c),
    );
    return { state: "HEALTHY", checks: { serviceHealthy: true, serviceCapabilities: caps } };
  } catch {
    return { state: "OFFLINE", checks: NO_BACKEND };
  }
}
