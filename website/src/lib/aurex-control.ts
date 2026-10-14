/** Pure, browser-safe rules for the owner-only AUREX Command Center. */
export const ALLOWED_HOSTS = ["valexii.com"] as const;
export const OBSERVE_PATHS = [
  "/", "/bcxmet", "/aurex", "/xaeli", "/dispater", "/xaita", "/system", "/research",
  "/voynich", "/linear-a", "/rongorongo", "/evaluation", "/ecosystem", "/support",
  "/contact", "/build-with-us", "/about", "/security", "/privacy", "/terms",
  "/decipherment-frontier", "/sitemap.xml", "/robots.txt",
] as const;

/** Only https://valexii.com on the default port, no credentials, no IP literals. */
export function isAllowedUrl(raw: string): boolean {
  let u: URL;
  try { u = new URL(raw); } catch { return false; }
  return (
    u.protocol === "https:" &&
    (ALLOWED_HOSTS as readonly string[]).includes(u.hostname.toLowerCase()) &&
    u.port === "" && u.username === "" && u.password === ""
  );
}

/** Owner check fails closed when the owner ID is unset or malformed. */
export function isOwner(userId: string | null | undefined, ownerId: string | null | undefined): boolean {
  const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return !!userId && !!ownerId && UUID.test(ownerId) && userId.toLowerCase() === ownerId.toLowerCase();
}

export type GateState = { enabled: false; reason: string };

export function proposeGate(cfg: { githubRepo?: string | undefined; githubAppConfigured?: boolean | undefined }): GateState | { enabled: true } {
  if (!cfg.githubRepo) return { enabled: false, reason: "No GitHub-linked site repository is connected." };
  if (!cfg.githubAppConfigured) return { enabled: false, reason: "GitHub App credentials are not configured." };
  return { enabled: false, reason: "PROPOSE is not implemented in Phase 1." };
}

/** APPLY requires a proposal and explicit owner approval; in Phase 1 it is always disabled. */
export function applyGate(input: { proposalId?: string | undefined; ownerApproved?: boolean | undefined; selfApproved?: boolean | undefined }): GateState {
  if (!input.proposalId) return { enabled: false, reason: "No proposal exists to apply." };
  if (input.ownerApproved !== true) return { enabled: false, reason: "Explicit owner approval is required." };
  if (input.selfApproved) return { enabled: false, reason: "Self-approval is not permitted." };
  return { enabled: false, reason: "APPLY is disabled in Phase 1 even with approval." };
}

export type ObserveResult = { url: string; status: number | null; ms: number | null; note: string };

/** Separation of duties: the proposer can never approve their own proposal. */
export function approvalValid(a: { proposerId?: string | undefined; approverId?: string | undefined; ownerId?: string | undefined }): boolean {
  return !!a.proposerId && !!a.approverId && a.proposerId !== a.approverId && isOwner(a.approverId, a.ownerId);
}

/** Best-effort per-key fixed-window limiter (per worker instance; not a global guarantee). */
export function createRateLimiter(limit: number, windowMs: number) {
  const hits = new Map<string, { n: number; start: number }>();
  return (key: string, now = Date.now()): boolean => {
    const h = hits.get(key);
    if (!h || now - h.start >= windowMs) { hits.set(key, { n: 1, start: now }); return true; }
    h.n += 1;
    return h.n <= limit;
  };
}

/** Audit entry with no secrets, URLs or payloads: action, outcome and a truncated actor id only. */
export function auditEntry(action: string, outcome: "allowed" | "denied" | "rate_limited", userId?: string | null) {
  return { at: new Date().toISOString(), action: action.replace(/[^a-z_.-]/gi, "").slice(0, 40), outcome, actor: userId ? `${userId.slice(0, 8)}…` : "anonymous" };
}
