/**
 * Default-off, synthetic-only server-side AUREX staging adapter.
 * Never forwards browser credentials or caller-provided audit records.
 * Requires Vercel deployment protection AND server-side owner admission.
 */
const FIXTURES = new Set(["towing_v1", "oilfield_v1"]);
const reply = (res, status, data) => {
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("X-Content-Type-Options", "nosniff");
  return res.status(status).json(data);
};
export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return reply(res, 405, { status: "HOLD", reason: "METHOD_NOT_ALLOWED" });
  }
  // Vercel SSO is a perimeter, not sufficient owner authorization by itself.
  // No production execution until a verified owner session is wired in.
  if (process.env.DISPATER_INDUSTRIAL_ENABLED !== "true") {
    return reply(res, 503, { status: "NOT VERIFIED", reason: "INDUSTRIAL_ADAPTER_DISABLED", financialAuthority: "NONE" });
  }
  return reply(res, 503, {
    status: "NOT VERIFIED",
    reason: "OWNER_AUTH_AND_TENANT_ISOLATION_NOT_YET_VERIFIED",
    financialAuthority: "NONE",
    permittedFixtures: [...FIXTURES],
  });
}
