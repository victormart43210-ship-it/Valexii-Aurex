import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const home = readFileSync("src/routes/index.tsx", "utf8");
const ambience = readFileSync("src/components/home-core-ambience.tsx", "utf8");
const css = readFileSync("src/styles.css", "utf8");

describe("homepage-only decorative core", () => {
  it("adds one isolated background without replacing original artwork", () => {
    expect(home.match(/<HomeCoreAmbience \/>/g)).toHaveLength(1);
    expect(home).toContain('className="home-core-page"');
    expect(home).toContain("<HomeHeroArt />");
    expect(home).toContain("src={guardianEye.url}");
    expect(css).toMatch(/\.home-core-page\s*\{[^}]*isolation: isolate;/);
    expect(css).toMatch(/\.home-core-ambience\s*\{[^}]*z-index: -1;[^}]*pointer-events: none;/);
  });
  it("uses inert vectors and existing lifecycle suspension, not telemetry", () => {
    expect(ambience).toContain('aria-hidden="true"');
    expect(ambience).toContain('focusable="false"');
    expect(ambience).toContain("usePresentationActivity()");
    expect(ambience).toContain('active ? "active" : "paused"');
    expect(ambience).not.toMatch(/fetch\(|requestAnimationFrame|setInterval|<canvas|https?:/);
    expect(css).toContain('.home-core-field[data-motion="paused"]');
  });
  it("keeps mobile and reduced-motion ambience static", () => {
    expect(css).toMatch(
      /@media \(max-width: 767px\), \(pointer: coarse\), \(prefers-reduced-motion: reduce\)\s*\{\s*\.home-core-field/,
    );
    expect(css).toMatch(
      /\.home-core-field::before,\s*\.home-core-field g\s*\{\s*animation: none !important;/,
    );
  });
});
