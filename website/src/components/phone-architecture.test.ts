import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { getDemoTelemetry, type DemoKind, type DemoPhase } from "./phone-scenarios";
import { universeNodes } from "./telemetry-universe-model";

describe("mobile phone and public research authority boundaries", () => {
  it("keeps one viewport, accessible tabs and outside default-open controls", () => {
    const source = readFileSync("src/components/visuals.tsx", "utf8");
    expect(source.match(/className="phone-viewport"/g)).toHaveLength(1);
    expect(source).toContain("<TabsContent");
    expect(source).toContain("forceMount");
    expect(source).toContain("screenViewport.current.scrollTop = 0");
    expect(source).toContain('className="phone-demo-drawer"');
    expect(source).toContain("const [demoControlsOpen, setDemoControlsOpen] = useState(true)");
    expect(source).toContain("open={demoControlsOpen}");
    expect(source).toContain("setDemoControlsOpen(event.currentTarget.open)");
    expect(source).toContain("aria-expanded={demoControlsOpen}");
    expect(source).toContain("EXPLORE THE ORB STATES");
    expect(source).toContain("Choose a state or trigger a simulated event");
    expect(source).not.toContain('className="screen-navigation"');
  });
  it("retains manual state selection, simulated events and touch-safe drawer layout", () => {
    const source = readFileSync("src/components/visuals.tsx", "utf8");
    const styles = readFileSync("src/styles.css", "utf8");
    expect(source).toContain("setDemoEvent(null)");
    expect(source).toContain("setOrbState(next)");
    for (const kind of ["scan", "review", "ambiguous", "routine", "qualified"]) {
      expect(source).toContain(`triggerDemo("${kind}")`);
    }
    expect(source).toContain("NO LIVE SCAN · ORB MOTION AUTHORITY = NONE");
    const actions = styles.slice(
      styles.indexOf(".phone-demo-drawer .phone-orb-actions button"),
      styles.indexOf(".phone-demo-drawer .phone-orb-actions svg"),
    );
    expect(actions).toContain("min-height: 44px");
    expect(actions).toContain("min-width: 0");
    expect(actions).toContain("white-space: normal");
  });
  it("repeated adversarial view traversal cannot mutate evidence or authority", () => {
    for (const kind of [
      null,
      "scan",
      "routine",
      "qualified",
      "review",
      "ambiguous",
    ] as (DemoKind | null)[]) {
      for (const phase of ["idle", "review", "returning", "complete"] as DemoPhase[]) {
        const data = getDemoTelemetry(phase, kind);
        const before = JSON.stringify(data);
        for (let i = 0; i < 20; i++) universeNodes(data);
        expect(JSON.stringify(data)).toBe(before);
        expect(data.authority).toBe("NONE");
        expect(data.current).toBe("UNKNOWN");
        expect(data.verification).toBe("NOT VERIFIED");
        expect(data.historical).toBe("CLEAR not established");
        expect(data.observations.every((o) => !("distance" in o) && !("bearing" in o))).toBe(true);
      }
    }
  });
  it("AUREX is internal, experimental and not a security or benchmark endorsement", () => {
    const source = readFileSync("src/routes/aurex.tsx", "utf8").replace(/\s+/g, " ");
    expect(source).toContain("experimental evidence-first");
    expect(source).toContain("separate from BCXMET phone security authority");
    expect(source).toContain("No independently verified benchmark result");
    expect(source).toContain("system must never be its own sole witness");
    expect(source).toContain("ORB MOTION AUTHORITY = NONE");
    expect(source).toContain("UNKNOWN ≠ SAFE");
    expect(source).not.toMatch(/href=["']https?:/);
  });
});
