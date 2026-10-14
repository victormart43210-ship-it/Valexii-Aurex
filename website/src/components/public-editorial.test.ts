import { readFileSync, readdirSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { spineContexts } from "./reasoning-spine-model";

const read = (path: string) => readFileSync(path, "utf8").replace(/\s+/g, " ");
const contentRoutes = readdirSync("src/routes").filter(
  (file) =>
    file.endsWith(".tsx") && !/^(?:__root|admin\.|medarus|medaurus|mederus|reasoning)/.test(file),
);

describe("human-first public editorial contract", () => {
  it("gives the homepage a clear mission and real product/philosophy destinations", () => {
    const home = read("src/routes/index.tsx");
    expect(home).toContain("Your digital life");
    expect(home).toContain("belongs to you.");
    expect(home).toContain("building privacy-centered Android security");
    expect(home).toContain("Privacy is personal. Proof matters.");
    expect(home).toContain("People remain in control.");
    expect(home).toContain('to="/bcxmet" hash="command-center"');
    expect(home).toContain('to="/system"');
    expect(home).toContain("No live call blocking, scanning or verified protection.");
  });
  it("keeps every public content route individually described without private codenames", () => {
    for (const file of contentRoutes) {
      const source = read(`src/routes/${file}`);
      for (const field of [
        "head:",
        'name: "description"',
        'property: "og:title"',
        'property: "og:description"',
        'property: "og:type"',
        'name: "twitter:card"',
      ])
        expect(source, file).toContain(field);
      expect(source, file).not.toMatch(/\b(?:SATOR|ROTAS|TENET|LEVEL|BKXMET|CoreGuard|Quilla)\b/);
    }
    expect(read("src/components/reasoning-spine.tsx")).not.toMatch(/\bROTAS\b/);
    expect(read("src/components/domain-reasoning.tsx")).not.toMatch(
      /Ghost in the Shell|Ex Machina|Hyperion|Asimov|Dune/,
    );
  });
  it("does not mistake demos, storage or planned newsletters for live services", () => {
    expect(read("src/routes/xaeli.tsx")).toContain("not a connected AI assistant");
    expect(read("src/routes/aurex.tsx")).toContain("public demo is synthetic");
    expect(spineContexts.contact.application).toContain("not proof of email delivery");
    expect(read("src/routes/build-with-us.tsx")).not.toContain("compose an email");
    expect(read("src/routes/bcxmet.tsx")).toContain("stored interest alone does not enroll you");
    expect(read("src/components/newsletter-signup.tsx")).not.toContain("Every email includes");
    expect(read("src/routes/support.tsx")).toContain("footer form is disabled");
  });
  it("never invents an absolute social-image URL for relative project artwork", () => {
    for (const [route, asset] of [
      ["index", "bcxmet-celestial-comet-home.jpg"],
      ["bcxmet", "bcxmet-guardian-eye-logo.jpg"],
      ["dispater", "dispater-hero.jpg"],
      ["xaita", "xaita-hero.jpg"],
    ]) {
      const pointer = JSON.parse(readFileSync(`public/assets/${asset}.asset.json`, "utf8"));
      const source = read(`src/routes/${route}.tsx`);
      if (pointer.url.startsWith("https://")) {
        expect(source).toContain(`property: "og:image", content: "${pointer.url}"`);
        expect(source).toContain(`name: "twitter:image", content: "${pointer.url}"`);
      } else if (route === "index") {
        // Homepage uses a 1200x630 crop of the same comet artwork shipped in public/.
        expect(readFileSync("public/og-valexii.jpg").length).toBeLessThan(400_000);
        expect(source).toContain(
          'property: "og:image", content: "https://valexii.com/og-valexii.jpg"',
        );
        expect(source).toContain(
          'name: "twitter:image", content: "https://valexii.com/og-valexii.jpg"',
        );
      } else {
        expect(source).not.toContain('property: "og:image"');
        expect(source).not.toContain('name: "twitter:image"');
      }
    }
  });
});
