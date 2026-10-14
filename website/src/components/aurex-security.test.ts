import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { PRIVATE_PLACEHOLDERS, redactForPublic, toPublicCapabilities } from "@/lib/aurex-public";
import { SECURITY_HEADERS, withSecurityHeaders } from "@/lib/security-headers";
import { applyGate, approvalValid, auditEntry, createRateLimiter } from "@/lib/aurex-control";

const owner = "11111111-2222-3333-4444-555555555555";
const other = "99999999-2222-3333-4444-555555555555";

describe("public redaction", () => {
  it("public capabilities expose only allowlisted fields and no live status", () => {
    for (const c of toPublicCapabilities()) {
      expect(Object.keys(c).sort()).toEqual(["id", "name", "status", "summary", "visibility"]);
      if (c.status === "REAL_CONNECTED") expect(["private-command-center", "website-claims-auditor", "repo-metadata", "cost-governor"]).toContain(c.id);
    }
  });
  it("redactForPublic strips sensitive keys recursively", () => {
    const r = redactForPublic({ name: "x", token: "t", nested: [{ endpointUrl: "https://a", budgetUsd: 5, ok: 1 }], AUREX_SERVICE_URL: "u", ownerEmail: "e" });
    expect(JSON.stringify(r)).not.toMatch(/https:\/\/a|"t"|"u"|"e"|budget|token/);
    expect(r).toMatchObject({ name: "x", nested: [{ ok: 1 }] });
  });
});

describe("blurred placeholders contain no sensitive payload", () => {
  const text = JSON.stringify(PRIVATE_PLACEHOLDERS);
  it("contain only placeholder text", () => {
    for (const c of PRIVATE_PLACEHOLDERS) for (const l of c.lines) expect(l).toMatch(/^Placeholder( line)?[ █]+$/);
    expect(text).not.toMatch(/https?:|@|sb_|Bearer|AUREX_|\d{2,}|[0-9a-f]{8}-/i);
  });
  it("placeholder component never imports server functions or private data", () => {
    const src = readFileSync("src/components/aurex-private-preview.tsx", "utf8");
    expect(src).not.toMatch(/functions|useQuery|useServerFn|process\.env|fetch\(/);
  });
});

describe("access bypass guards", () => {
  const fns = readFileSync("src/lib/aurex-control.functions.ts", "utf8");
  it("every server function requires auth middleware", () => {
    const count = (fns.match(/createServerFn\(/g) ?? []).length;
    expect((fns.match(/\.middleware\(\[requireSupabaseAuth\]\)/g) ?? []).length).toBe(count);
  });
  it("every privileged handler checks the owner", () => {
    expect((fns.match(/assertOwner\(context\.userId/g) ?? []).length).toBe((fns.match(/createServerFn\(/g) ?? []).length - 1);
  });
  it("admin route is client-only and noindex", () => {
    const route = readFileSync("src/routes/admin.aurex-control.tsx", "utf8");
    expect(route).toContain("ssr: false");
    expect(route).toContain("noindex");
  });
  it("public /aurex never calls owner functions", () => {
    expect(readFileSync("src/routes/aurex.tsx", "utf8")).not.toMatch(/aurex-control\.functions/);
  });
});

describe("approval gates and abuse limits", () => {
  it("forbids self-approval and non-owner approval", () => {
    expect(approvalValid({ proposerId: owner, approverId: owner, ownerId: owner })).toBe(false);
    expect(approvalValid({ proposerId: other, approverId: other, ownerId: owner })).toBe(false);
    expect(approvalValid({ proposerId: other, approverId: owner, ownerId: owner })).toBe(true);
    expect(approvalValid({ proposerId: other, approverId: owner, ownerId: undefined })).toBe(false);
    expect(applyGate({ proposalId: "p", ownerApproved: true, selfApproved: true }).reason).toMatch(/Self-approval/);
  });
  it("rate limiter blocks after the limit and resets after the window", () => {
    const lim = createRateLimiter(2, 1000);
    expect([lim("a", 0), lim("a", 1), lim("a", 2)]).toEqual([true, true, false]);
    expect(lim("a", 1001)).toBe(true);
  });
  it("audit entries hold no full ids or values", () => {
    const e = auditEntry("observe https://x?token=1", "denied", owner);
    expect(JSON.stringify(e)).not.toContain(owner);
    expect(e.action).not.toMatch(/[:/?=]/);
  });
});

describe("security headers", () => {
  it("adds baseline headers without overwriting existing ones", () => {
    const r = withSecurityHeaders(new Response("x", { headers: { "Referrer-Policy": "no-referrer" } }));
    expect(r.headers.get("X-Content-Type-Options")).toBe("nosniff");
    expect(r.headers.get("Referrer-Policy")).toBe("no-referrer");
    expect(r.headers.get("Content-Security-Policy")).toContain("object-src 'none'");
    expect(SECURITY_HEADERS["Permissions-Policy"]).toContain("camera=()");
  });
  it("handles immutable headers", () => {
    const res = Response.redirect("https://valexii.com/", 302);
    expect(withSecurityHeaders(res).headers.get("X-Content-Type-Options")).toBe("nosniff");
  });
  it("CSRF middleware remains registered for server functions", () => {
    expect(readFileSync("src/start.ts", "utf8")).toMatch(/csrfMiddleware/);
  });
});
