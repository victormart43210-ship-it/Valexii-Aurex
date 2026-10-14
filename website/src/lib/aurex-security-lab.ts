/**
 * AUREX Security Lab — capability contract for FUTURE isolated backend workers.
 * Browser-safe, no network, no execution. Nothing here runs a scan.
 */
export const LAB_AREAS = [
  { id: "website", name: "Website Security", summary: "Passive header, TLS and configuration review of owned sites." },
  { id: "api", name: "API Security", summary: "Contract-bounded checks of owned API endpoints." },
  { id: "auth", name: "Authentication & Access Control", summary: "Session, role and denial-path review on staging." },
  { id: "deps", name: "Dependency Audit", summary: "Known-vulnerability review of declared dependencies." },
  { id: "ai", name: "AI / Prompt-Injection Safety", summary: "Bounded adversarial prompts against owned assistants." },
  { id: "reports", name: "Evidence Reports", summary: "Independently verified findings with provenance." },
] as const;

export type LabStatus = "NOT_CONFIGURED";
export const LAB_STATUS: LabStatus = "NOT_CONFIGURED";

export const INTENSITIES = ["passive", "light-active", "active"] as const;
export type Intensity = (typeof INTENSITIES)[number];
export const DEFAULT_INTENSITY: Intensity = "passive";

/** Contract every future worker must satisfy before any status can leave NOT_CONFIGURED. */
export const WORKER_CONTRACT = {
  isolation: "Separate sandboxed worker; never the website runtime.",
  targets: "Per-target allowlist of exact hostnames with verified ownership (DNS TXT or file token).",
  expiry: "Authorization expires; maximum 7 days, then re-approval.",
  rateLimits: "Per-target request budget; passive default; max 1 req/s active.",
  network: "Public https hosts only; deny private, loopback, link-local, metadata IPs after DNS resolution (SSRF).",
  audit: "Append-only, value-free audit log for every request, approval and cancel.",
  stop: "Owner stop/cancel takes effect immediately and is acknowledged.",
  staging: "Staging targets preferred; production requires explicit separate approval.",
  evidence: "Findings count only after independent verification; worker is never its own sole witness.",
  inputs: "Named test kinds with bounded scalar params only — no URLs typed freely, no shell, no code.",
} as const;

const PRIVATE_HOST = /^(localhost|.*\.local|.*\.internal|127\.|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.|0\.|\[|::)/i;

/** Validates a proposed target hostname (no scheme/path). Never fetched. */
export function validTargetHost(h: string): boolean {
  const s = h.trim().toLowerCase();
  if (!s || s.length > 253 || PRIVATE_HOST.test(s)) return false;
  if (/^\d+\.\d+\.\d+\.\d+$/.test(s)) return false;
  return /^(?!-)[a-z0-9-]{1,63}(\.[a-z0-9-]{1,63})+$/.test(s);
}

export type ScopeDraft = {
  host: string; intensity: Intensity; expiryDays: number;
  ownershipConfirmed: boolean; consent: boolean; stagingPreferred: boolean;
};

export function scopeErrors(d: ScopeDraft): string[] {
  const e: string[] = [];
  if (!validTargetHost(d.host)) e.push("Enter a public hostname you own (no IPs, internal or local hosts).");
  if (!INTENSITIES.includes(d.intensity)) e.push("Invalid intensity.");
  if (!(d.expiryDays >= 1 && d.expiryDays <= 7)) e.push("Expiry must be 1–7 days.");
  if (!d.ownershipConfirmed) e.push("Ownership verification is required.");
  if (!d.consent) e.push("Written authorization/consent is required.");
  return e;
}

/** Approval gate: always disabled until a verified worker and verified ownership exist. */
export function labApprovalGate(i: { workerConfigured?: boolean; ownershipVerified?: boolean; scopeValid?: boolean }) {
  if (!i.scopeValid) return { enabled: false, reason: "Scope incomplete." };
  if (!i.ownershipVerified) return { enabled: false, reason: "Ownership not verified by the server." };
  if (!i.workerConfigured) return { enabled: false, reason: "No authorized isolated test service is configured." };
  return { enabled: false, reason: "Execution is disabled in this phase." };
}
