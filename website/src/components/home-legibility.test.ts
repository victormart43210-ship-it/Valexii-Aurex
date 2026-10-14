import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const css = readFileSync("src/styles.css", "utf8");

describe("homepage reading contrast", () => {
  it("uses near-white reading tokens with a bounded local dark scrim", () => {
    expect(css).toContain("--home-reading-foreground: #f1f5fa");
    expect(css).toContain("--home-reading-surface: color-mix(in srgb, var(--background) 96%, transparent)");
    expect(css).toContain("--muted-foreground: var(--home-reading-foreground)");
  });

  it("shields editorial copy without changing geometry or the core", () => {
    const readingRules = css.split("/* Local reading surfaces only:")[1]?.split("@keyframes home-core-breathe")[0];
    expect(readingRules).toContain('[data-reasoning-spine="home"]');
    expect(readingRules).toContain("background: var(--home-reading-surface)");
    expect(readingRules).not.toMatch(/padding:|margin:|opacity:|\.home-core-field|\.phone/);
  });

  it("keeps links identifiable and focus visible without relying on color alone", () => {
    expect(css).toContain("text-decoration: underline;");
    expect(css).toMatch(/\.home-core-page a:focus-visible\s*\{\s*outline: 2px solid var\(--foreground\);/);
  });

  it("assigns six harmonized heading tokens without recoloring brands or controls", () => {
    const headings = css.split("/* Art-directed editorial headings;")[1]?.split("@keyframes home-core-breathe")[0];
    for (const name of ["cyan", "violet", "cobalt", "magenta", "emerald", "gold"]) {
      expect(headings).toContain(`--home-heading-${name}: oklch(`);
    }
    expect(headings).toContain('.home-core-page > section:nth-of-type(2)');
    expect(headings).toContain(':is(h2, h3)');
    expect(headings).toContain('.home-core-page .home-bcxmet-hook');
    expect(headings).not.toMatch(/home-bcxmet-brand|button|BrandMark|padding:|margin:|font-size:|animation:/);
  });
});