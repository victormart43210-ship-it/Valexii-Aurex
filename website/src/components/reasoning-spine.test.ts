import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { reverseFlow, spineContexts, spineFlow, spineStages } from "./reasoning-spine-model";
import { getDemoTelemetry } from "./phone-scenarios";

const read = (path: string) => readFileSync(path, "utf8").replace(/\s+/g, " ");
describe("public Unified Reasoning Spine contract", () => {
  it("preserves the exact forward and reverse lineage", () => {
    expect(spineFlow).toBe("EVIDENCE → QUALIFICATION → REALITY → AUTHORITY → EFFECT");
    expect(reverseFlow).toBe("Result → Authority → Truth → Admissibility → Source");
    expect(spineStages.map((s) => s.name.toUpperCase()).join(" → ")).toBe(spineFlow);
  });
  it("defines provenance, adversarial roles and non-self-witness requirements", () => {
    const text = spineStages.map((s) => s.detail).join(" ");
    for (const term of [
      "source",
      "freshness",
      "hypotheses",
      "Advocate",
      "Challenger",
      "Arbiter",
      "Independent witnesses",
      "revocation",
      "lease",
      "effect time",
    ])
      expect(text).toContain(term);
    expect(text).toContain("three roles alone do not establish independence");
  });
  it("uses one authored definition on all twelve requested routes", () => {
    const routes = [
      "index",
      "system",
      "bcxmet",
      "xaeli",
      "aurex",
      "dispater",
      "xaita",
      "ecosystem",
      "evaluation",
      "research",
      "build-with-us",
      "contact",
    ];
    for (const route of routes)
      expect(read(`src/routes/${route}.tsx`)).toMatch(/<ReasoningSpine context=/);
    expect(read("src/routes/system.tsx")).toContain('<ReasoningSpine context="system" detailed');
    expect(Object.keys(spineContexts)).toHaveLength(12);
  });
  it("separates historical evidence and visualization from current permission", () => {
    const source = read("src/components/reasoning-spine.tsx");
    for (const term of [
      "UNKNOWN ≠ SAFE",
      "Missing, stale or unverified evidence never counts as PASS",
      "A system must never be its own sole witness",
      "ORB MOTION AUTHORITY = NONE",
      "History is not permission",
      "HOLD → human review",
    ])
      expect(source).toContain(term);
    const before = JSON.stringify(getDemoTelemetry("review", "scan"));
    Object.values(spineContexts).forEach((c) => JSON.stringify(c));
    const telemetry = getDemoTelemetry("review", "scan");
    expect(JSON.stringify(telemetry)).toBe(before);
    expect(telemetry.authority).toBe("NONE");
    expect(telemetry.current).toBe("UNKNOWN");
  });
  it("retains domain-specific non-transferable authority and AUREX limits", () => {
    expect(spineContexts.system.application).toContain("do not transfer");
    expect(spineContexts.xaita.application).toContain("cannot authorize financial effects");
    expect(spineContexts.dispater.application).toContain("Functionality remains unverified");
    expect(spineContexts.aurex.application).toContain("not arbitrate BCXMET product security");
    expect(spineContexts.aurex.application).toContain("not an independent witness");
  });
  it("aligns public score withholding, planned newsletter and legal disclosures", () => {
    expect(read("src/routes/index.tsx")).not.toContain("99.30%");
    expect(read("src/routes/decipherment-frontier.tsx")).toContain("no delivery is promised");
    for (const route of ["privacy", "terms"])
      expect(read(`src/routes/${route}.tsx`)).toContain("Reasoning and visualization boundaries");
    expect(read("src/routes/decipherment.tsx")).not.toContain("CUSTOS");
  });
  it("does not promote fictional observations or investment targets", () => {
    expect(spineContexts.bcxmet.application).toContain("simulated fixtures");
    expect(spineContexts.collaboration.application).toContain("not an achieved result");
    expect(spineContexts.research.application).toContain("not verified translations");
    expect(spineContexts.contact.application).toContain("stores your inquiry");
    expect(spineContexts.contact.application).toContain("not proof of email delivery");
  });
});
