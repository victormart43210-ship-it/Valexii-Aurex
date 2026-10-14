import { describe, expect, it } from "vitest";
import { getDemoTelemetry, type DemoKind } from "./phone-scenarios";
import { universeLevel, universeNodes } from "./telemetry-universe-model";
describe("XAELI semantic zoom", () => {
  it("reveals additional native nodes at each threshold", () => {
    const nodes = universeNodes(getDemoTelemetry("review", "scan"));
    const counts = [1, 1.6, 2.5, 4, 6].map(
      (k) => nodes.filter((n) => n.level <= universeLevel(k)).length,
    );
    expect(counts).toEqual([0, 5, 8, 12, 17]);
  });
  it("uses only available radio observations and never invents location", () => {
    expect(universeNodes(getDemoTelemetry("idle", null)).filter((n) => n.level === 2)).toHaveLength(
      0,
    );
    const nodes = universeNodes(getDemoTelemetry("review", "scan"));
    expect(nodes.find((n) => n.id === "S1")?.details).toContainEqual([
      "Name",
      "SSID withheld · name unknown",
    ]);
    expect(nodes.every((n) => !("distance" in n) && !("bearing" in n))).toBe(true);
  });
  it("view depth cannot promote any canonical mode to authority", () => {
    for (const kind of ["scan", "routine", "qualified", "review", "ambiguous"] as DemoKind[]) {
      const telemetry = getDemoTelemetry("review", kind);
      universeNodes(telemetry);
      expect(telemetry.current).toBe("UNKNOWN");
      expect(telemetry.authority).toBe("NONE");
      expect(universeNodes(telemetry).find((n) => n.id === "trace-3")?.details).toContainEqual([
        "Status",
        "NONE",
      ]);
    }
  });
});
