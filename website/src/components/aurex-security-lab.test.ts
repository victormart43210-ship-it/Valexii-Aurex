import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { isOwner } from "@/lib/aurex-control";
import { DEFAULT_INTENSITY, LAB_AREAS, LAB_STATUS, labApprovalGate, scopeErrors, validTargetHost } from "@/lib/aurex-security-lab";
const owner = "11111111-2222-3333-4444-555555555555";
describe("Security Lab", () => {
  it("denies anonymous and other users, fails closed when unset", () => {
    expect(isOwner(null, owner)).toBe(false);
    expect(isOwner("99999999-2222-3333-4444-555555555555", owner)).toBe(false);
    expect(isOwner(owner, undefined)).toBe(false);
  });
  it("lab server fn is auth + owner gated", () => {
    const f = readFileSync("src/lib/aurex-control.functions.ts", "utf8");
    expect(f).toMatch(/getSecurityLabState[\s\S]*requireSupabaseAuth[\s\S]*assertOwner\(context\.userId, "security_lab_read"\)/);
  });
  it("all areas NOT_CONFIGURED, passive default, approval always disabled", () => {
    expect(LAB_AREAS).toHaveLength(6); expect(LAB_STATUS).toBe("NOT_CONFIGURED"); expect(DEFAULT_INTENSITY).toBe("passive");
    expect(labApprovalGate({ scopeValid: true, ownershipVerified: true, workerConfigured: true }).enabled).toBe(false);
  });
  it.each(["localhost", "10.0.0.1", "192.168.1.1", "169.254.169.254", "a.internal", "https://x.com", "8.8.8.8", ""])("rejects %s", (h) => expect(validTargetHost(h)).toBe(false));
  it("accepts public host and requires ownership + consent + expiry", () => {
    expect(validTargetHost("staging.valexii.com")).toBe(true);
    expect(scopeErrors({ host: "staging.valexii.com", intensity: "passive", expiryDays: 9, ownershipConfirmed: false, consent: false, stagingPreferred: true })).toHaveLength(3);
  });
  it("lab UI never fetches or executes, and is not on public routes", () => {
    const ui = readFileSync("src/components/aurex-security-lab.tsx", "utf8");
    expect(ui).not.toMatch(/fetch\(|process\.env|useServerFn/);
    expect(readFileSync("src/routes/aurex.tsx", "utf8")).not.toMatch(/security-lab/);
  });
});
