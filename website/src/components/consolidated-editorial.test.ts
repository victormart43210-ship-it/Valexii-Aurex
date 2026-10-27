import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { spineContexts } from "./reasoning-spine-model";

const read = (path: string) => readFileSync(path, "utf8").replace(/\s+/g, " ");

describe("consolidated public editorial boundaries", () => {
  it("removes the visible acronym without changing the authored model API", () => {
    expect(JSON.stringify(spineContexts)).not.toMatch(/\bURS\b/);
    expect(read("src/components/reasoning-spine.tsx")).not.toMatch(/\bURS\b/);
    expect(Object.keys(spineContexts)).toHaveLength(12);
  });
  it("describes workstation modules without claiming readiness or independence", () => {
    const text = read("src/routes/aurex.tsx");
    for (const name of [
      "Project Manager",
      "Transfer Hub",
      "GitHub Hub",
      "AI Model Manager",
      "Scientific Research",
      "CERN",
      "Security Lab",
      "MobSF",
      "Evaluation Engine",
      "Evidence Ledger",
      "CUSTOS PRIME Ω",
    ])
      expect(text).toContain(name);
    expect(text).toContain("installation, connectivity and successful scans are unverified");
    expect(text).toContain("Independence must be demonstrated");
    expect(text).not.toMatch(/Aurix|V7\.2|<img/i);
  });
  it("keeps industrial demonstrations and research symbolism outside evidence authority", () => {
    const industrial = read("src/routes/dispater.tsx");
    for (const text of [
      "Revenue Intelligence & Audit Readiness",
      "CONCEPT PREVIEW · FICTIONAL DATA · NOT LIVE",
      "Conceptual artwork — not product UI or field data.",
      "NVIDIA explanations and customer-data processing are not enabled",
      "Record completeness does not establish IRS or DOT compliance",
      "require professional assessment and human authorization",
    ])
      expect(industrial).toContain(text);
    const research = read("src/routes/research.tsx");
    expect(research).toContain("Symbolism, not scientific evidence");
    expect(research).toContain("do not qualify scientific evidence");
  });
});
