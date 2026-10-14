import { describe, expect, it } from "vitest";
import { applyGate, isAllowedUrl, isOwner, OBSERVE_PATHS, proposeGate } from "@/lib/aurex-control";

const owner = "11111111-2222-3333-4444-555555555555";

describe("AUREX control authorization", () => {
  it("fails closed without a configured owner", () => {
    expect(isOwner(owner, undefined)).toBe(false);
    expect(isOwner(owner, "")).toBe(false);
    expect(isOwner(owner, "not-a-uuid")).toBe(false);
    expect(isOwner(null, owner)).toBe(false);
    expect(isOwner("99999999-2222-3333-4444-555555555555", owner)).toBe(false);
    expect(isOwner(owner, owner)).toBe(true);
  });
});

describe("OBSERVE SSRF allowlist", () => {
  it.each([
    "http://valexii.com/", "https://evil.com/", "https://valexii.com.evil.com/",
    "https://www.valexii.com/", "https://localhost/", "https://127.0.0.1/", "https://169.254.169.254/",
    "https://user:pw@valexii.com/", "https://valexii.com:8080/", "file:///etc/passwd", "not a url",
  ])("blocks %s", (u) => expect(isAllowedUrl(u)).toBe(false));
  it("allows only fixed valexii.com paths", () => {
    for (const p of OBSERVE_PATHS) expect(isAllowedUrl(`https://valexii.com${p}`)).toBe(true);
  });
});

describe("approval gates", () => {
  it("PROPOSE stays disabled without repo and credentials", () => {
    expect(proposeGate({}).enabled).toBe(false);
    expect(proposeGate({ githubRepo: "x/y" }).enabled).toBe(false);
    expect(proposeGate({ githubRepo: "x/y", githubAppConfigured: true }).enabled).toBe(false);
  });
  it("APPLY requires a proposal and owner approval, and stays disabled in Phase 1", () => {
    expect(applyGate({}).reason).toMatch(/No proposal/);
    expect(applyGate({ proposalId: "p" }).reason).toMatch(/owner approval/);
    expect(applyGate({ proposalId: "p", ownerApproved: true }).enabled).toBe(false);
  });
});
