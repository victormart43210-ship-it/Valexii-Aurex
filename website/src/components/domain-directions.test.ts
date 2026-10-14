import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
const read = (path: string) =>
  readFileSync(new URL(path, import.meta.url), "utf8").replace(/\s+/g, " ");
describe("public domain and collaboration boundaries", () => {
  it("keeps private-repository claims unverified and adds no substitute hero", () => {
    for (const path of ["../routes/dispater.tsx", "../routes/xaita.tsx"]) {
      const source = read(path);
      expect(source).toContain("Private repositories exist, as reported by the project owner");
      expect(source).toContain("functionality has not been independently verified");
      expect(source).toContain("<DomainReasoning />");
      expect(source).not.toMatch(/og:image|crystal/i);
    }
  });
  it("separates context from authority and fictional inspiration from capability", () => {
    const source = read("./domain-reasoning.tsx");
    for (const text of [
      "Evidence → Qualification → Reality → Authority → Effect",
      "UNKNOWN ≠ SAFE",
      "never be its own sole witness",
      "Visualization supplies no authority",
      "not verified functionality",
      "not a claim of sentience",
    ])
      expect(source).toContain(text);
  });
  it("distinguishes targets and proposals from traction, filings and awards", () => {
    const source = read("../routes/build-with-us.tsx");
    for (const text of [
      "Investors welcome",
      "10,000 retained users is a future TARGET",
      "No patent-pending status",
      "not submitted, invited, approved or awarded",
      "November 4, 2026",
      "$305,000",
      "official Project Pitch invitation",
      "invitation and eligibility are not verified",
    ])
      expect(source).toContain(text);
    expect(source).toContain(
      "https://www.nsf.gov/funding/opportunities/small-business-innovation-research-small-business-technology/nsf26-510/solicitation",
    );
  });
  it("routes investment and grant inquiries to the stored partnership form", () => {
    const schema = read("../lib/inquiry-schema.ts");
    expect(schema).toContain("Investment inquiry");
    expect(schema).toContain("Grants / NSF proposal collaboration");
    expect(read("../routes/build-with-us.tsx")).toContain('<InquiryForm kind="partnership" />');
    expect(read("../routes/contact.tsx")).not.toContain("mailto:developer@valexii.com?subject");
  });
});
