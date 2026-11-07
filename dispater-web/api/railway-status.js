/**
 * Coarse, read-only Railway STAGING health probe.
 * No access token, source data, raw response, or audit authorization.
 * Deployment protection must remain enabled on the preview project.
 */
const STAGING_HEALTH = "https://aurex-api-aurex-staging.up.railway.app/v1/health";
export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return res.status(405).json({ state: "HOLD", error: "METHOD_NOT_ALLOWED" });
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 4500);
  try {
    const upstream = await fetch(STAGING_HEALTH, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: controller.signal,
      redirect: "error",
      cache: "no-store",
    });
    if (!upstream.ok) {
      return res.status(200).json({
        state: "HOLD",
        stagingReachability: "NOT VERIFIED",
        reason: upstream.status === 401 ? "BEARER_AUTHORIZATION_REQUIRED" : "UPSTREAM_HEALTH_UNAVAILABLE",
        auditRuntime: "NOT CONNECTED",
        modelInference: "NOT RUN",
        financialAuthority: "NONE",
      });
    }
    return res.status(200).json({
      state: "HOLD",
      stagingReachability: "HEALTH_ENDPOINT_RESPONDED",
      reason: "READ_ONLY_HEALTH_PROBE_ONLY",
      auditRuntime: "NOT CONNECTED",
      modelInference: "NOT RUN",
      financialAuthority: "NONE",
    });
  } catch {
    return res.status(200).json({
      state: "HOLD",
      stagingReachability: "NOT VERIFIED",
      reason: "STAGING_HEALTH_REQUEST_FAILED",
      auditRuntime: "NOT CONNECTED",
      modelInference: "NOT RUN",
      financialAuthority: "NONE",
    });
  } finally {
    clearTimeout(timeout);
  }
}
