import { describe, expect, it } from "vitest";
import {
  getDemoTelemetry,
  phoneTopics,
  spectrumFixture,
  plotSpectrumObservation,
  demoModes,
  type DemoKind,
  type DemoPhase,
} from "./phone-scenarios";

describe("canonical simulated instrument model", () => {
  const phases: DemoPhase[] = ["idle", "review", "returning", "complete"];
  const kinds: (DemoKind | null)[] = [null, "routine", "qualified", "scan", "review", "ambiguous"];
  it("never promotes demo progress to evidence, clearance, freshness or authority", () => {
    for (const phase of phases)
      for (const kind of kinds) {
        const data = getDemoTelemetry(phase, kind);
        expect(data.current).toBe("UNKNOWN");
        expect(data.verification).toBe("NOT VERIFIED");
        expect(data.authority).toBe("NONE");
        expect(data.lastCheck).toBe("Unknown · no device check");
        expect(data.freshness).toBe("Unverified");
        expect(data.historical).toBe("CLEAR not established");
      }
  });
  it("shares authored evidence with phone scan cards", () => {
    expect(getDemoTelemetry("review", "routine").evidenceTopic).toBe(
      phoneTopics["Command Center"][0],
    );
    expect(getDemoTelemetry("review", "qualified").evidenceTopic).toBe(phoneTopics.Home[0]);
  });
  it("maps every active mode to its explicit hue and returns to neutral without a trusted verdict", () => {
    for (const kind of kinds) {
      const data = getDemoTelemetry("review", kind);
      expect(data.hue).toBe(kind ? demoModes[kind].hue : "unknown");
      expect(data.hue).not.toBe("mint");
      expect(data.current).not.toMatch(/green|protected|trusted|clear/i);
      expect(getDemoTelemetry("complete", kind).hue).toBe("unknown");
      expect(getDemoTelemetry("idle", kind).hue).toBe("unknown");
    }
  });
  it("separates FIELD domains and radio observations without upgrading unknown domains", () => {
    const data = getDemoTelemetry("review", "scan");
    expect(data.observations).toBe(spectrumFixture);
    expect(data.fields.map((field) => field.name)).toEqual([
      "Device",
      "Communications",
      "Network",
      "Spectrum",
      "Identity-Privacy",
    ]);
    expect(
      data.fields
        .filter((field) => field.status === "UNKNOWN")
        .every((field) => field.hue === "unknown"),
    ).toBe(true);
    expect(getDemoTelemetry("idle", "scan").observations).toHaveLength(0);
  });
  it("cannot supply invented bearing, distance, live identity or confidence from RSSI", () => {
    for (const observation of spectrumFixture) {
      const plot = plotSpectrumObservation(observation);
      expect(Object.keys(observation)).not.toContain("bearing");
      expect(Object.keys(observation)).not.toContain("distance");
      expect(Object.keys(plot).sort()).toEqual(["band", "trace", "x", "y"]);
      expect(observation.confidence).toBe("Uncalibrated");
      expect(observation.qualification).not.toBe("PASS");
      expect(plot.trace).toContain(",");
    }
    expect(spectrumFixture[0]?.name).toContain("name unknown");
  });
  it("synchronizes progress and presentation through bounded phases", () => {
    expect(phases.map((phase) => getDemoTelemetry(phase, "qualified").progress)).toEqual([
      0, 40, 80, 100,
    ]);
    expect(phases.map((phase) => getDemoTelemetry(phase, "qualified").orb)).toEqual([
      "REST",
      "DEFEND",
      "RETURN",
      "REST",
    ]);
    expect(getDemoTelemetry("review", "routine").orb).toBe("AWARE");
    expect(getDemoTelemetry("complete", "qualified").phase).toContain("HOLD");
  });
});
