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

/**
 * Strict v1 handshake. Health has ONLY status/version/time, never capabilities.
 * Separate capabilities + evidence must be validated before any capability
 * is treated as evidence-linked. This does NOT prove independent authority.
 */
export async function checkAurexService(
  env: { url?: string | undefined; token?: string | undefined },
  fetcher: typeof fetch = fetch,
): Promise<ServiceState> {
  if (!validServiceUrl(env.url) || !env.token || env.token.length < 32) {
    return { state: "NOT_CONFIGURED", checks: NO_BACKEND };
  }
  // Lazy import keeps validServiceUrl re-usable by the client without a
  // top-level circular-import initialization failure.
  const [{ createAurexClient }, { capabilityBacked }] = await Promise.all([
    import("./aurex-client.server"),
    import("./aurex-api-schema"),
  ]);
  const client = createAurexClient({ url: env.url, token: env.token, fetcher });
  const health = await client.health();
  if (!health.ok) return { state: "OFFLINE", checks: NO_BACKEND };
  const caps = await client.capabilities();
  const evidence = await client.evidence();
  if (!caps.ok || !evidence.ok) return { state: "OFFLINE", checks: NO_BACKEND };
  const now = Date.now();
  const enabled = caps.value.capabilities.filter(
    (c) => c.verifiedAt !== null &&
      Number.isFinite(Date.parse(c.verifiedAt)) &&
      Date.parse(c.verifiedAt) <= now + 60_000 &&
      capabilityBacked(c, evidence.value.evidence, now),
  );
  return {
    state: "HEALTHY",
    checks: {
      serviceHealthy: true,
      serviceCapabilities: enabled.map((c) => c.id),
    },
  };
}
