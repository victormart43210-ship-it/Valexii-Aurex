import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const home = readFileSync("src/routes/index.tsx", "utf8");
const css = readFileSync("src/styles.css", "utf8");
const guardian = JSON.parse(
  readFileSync("public/assets/bcxmet-guardian-eye-logo.jpg.asset.json", "utf8"),
);

describe("homepage original-art identity contract", () => {
  it("orders the comet, divider, original logo, hook, disclaimer, CTAs and phone", () => {
    const landmarks = [
      "<HomeHeroArt />",
      'className="home-chapter-divider"',
      'className="home-guardian-art"',
      'className="home-bcxmet-brand"',
      "Your digital life",
      "belongs to you.",
      "Conceptual Android security preview",
      'className="hero-actions"',
      "<CometDynamics />",
    ];
    const body = home.slice(home.indexOf("function Home()"));
    const positions = landmarks.map((landmark) => body.indexOf(landmark));
    expect(positions.every((position) => position >= 0)).toBe(true);
    expect(positions).toEqual([...positions].sort((a, b) => a - b));
    expect(home.match(/<HomeHeroArt \/>/g)).toHaveLength(1);
  });

  it("uses the existing exact asset with reserved square dimensions and no crop", () => {
    expect(guardian.original_filename).toBe("bcxmet-guardian-eye-logo.jpg");
    expect(home).toContain('public/assets/bcxmet-guardian-eye-logo.jpg.asset.json"');
    expect(home).toMatch(/src=\{guardianEye.url\}\s+width=\{1536\}\s+height=\{1536\}/);
    expect(home).toContain("complete BCXMET wordmark");
    expect(css).toMatch(/\.home-guardian-art img\s*\{[^}]*object-fit: contain;/);
  });

  it("keeps truthful limits, attribution and the three existing destinations", () => {
    expect(home).toContain("No live call blocking,");
    expect(home).toContain("scanning or verified protection.");
    expect(home).toContain("Powered by VALEXII.AI · BCXME THE CHANGE");
    expect(home).not.toContain("<Eyebrow>BCXMET · Powered by VALEXII.AI</Eyebrow>");
    expect(home).toContain('href="#spam-demo"');
    expect(home).toContain('href="#malware-demo"');
    expect(home).toContain('to="/bcxmet" hash="command-center"');
  });

  it("scopes the vertical flow and copy reset to the homepage", () => {
    expect(home).toContain('className="cinematic-hero home-identity-hero"');
    expect(css).toMatch(/\.home-identity-hero \.hero-art-layer\s*\{\s*position: relative;/);
    expect(css).toMatch(
      /\.cinematic-hero\.home-identity-hero \.cinematic-layout\s*\{\s*grid-template-columns: minmax\(0, 1fr\)/,
    );
    expect(css).toMatch(
      /\.cinematic-hero\.home-identity-hero \.cinematic-copy\s*\{[^}]*padding-top: 0;/,
    );
  });
});
