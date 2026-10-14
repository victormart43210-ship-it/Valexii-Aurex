/** Public/private separation for AUREX. Browser-safe, pure. */
import { capabilities, resolveStatus, type CapabilityStatus } from "./aurex-capabilities";

export interface PublicCapability { id: string; name: string; summary: string; status: CapabilityStatus; visibility: "PUBLIC" | "PRIVATE" }

const SENSITIVE_KEYS = /token|secret|password|key|credential|endpoint|url|host|ip|email|userid|user_id|metric|evidence|audit|budget|spent/i;

/** Allowlist projection: only these fields ever reach a public response. Unknown fields are dropped. */
export function toPublicCapabilities(): PublicCapability[] {
  return capabilities.map((c) => ({
    id: c.id, name: c.name, summary: c.summary,
    status: resolveStatus(c),           // never uses live backend data on public paths
    visibility: c.restricted ? "PRIVATE" : "PUBLIC",
  }));
}

/** Recursively removes sensitive-looking keys; used as a second guard on any public payload. */
export function redactForPublic<T>(value: T): T {
  if (Array.isArray(value)) return value.map(redactForPublic) as T;
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value)) if (!SENSITIVE_KEYS.test(k)) out[k] = redactForPublic(v);
    return out as T;
  }
  return value;
}

/** Synthetic placeholder content for blurred private cards. Contains no real data by construction. */
export const PRIVATE_PLACEHOLDERS = [
  { title: "Owner research notebook", lines: ["Placeholder line ████ ████", "Placeholder line ██ ██████", "Placeholder line ███ ███"] },
  { title: "Service health & budget", lines: ["Placeholder ██████ ████", "Placeholder ███ ██ ███", "Placeholder ████ ██"] },
  { title: "Audit trail", lines: ["Placeholder ████ ██ ████", "Placeholder ██████ ███", "Placeholder ██ ████ ██"] },
] as const;
