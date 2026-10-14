import type { DemoTelemetry } from "./phone-scenarios";

export const universeLevels = [
  "Orbital sphere",
  "FIELD / radio rings",
  "Signal observations",
  "Evidence provenance",
  "Governance trace",
] as const;
export function universeLevel(scale: number) {
  return scale >= 6 ? 4 : scale >= 4 ? 3 : scale >= 2.5 ? 2 : scale >= 1.6 ? 1 : 0;
}
export type UniverseNode = {
  id: string;
  label: string;
  x: number;
  y: number;
  level: number;
  details: [string, string][];
};
export function universeNodes(telemetry: DemoTelemetry): UniverseNode[] {
  const nodes: UniverseNode[] = telemetry.fields.map((field, i) => {
    const angle = (i * Math.PI * 2) / 5 - Math.PI / 2;
    return {
      id: `field-${i}`,
      label: field.name,
      x: 330 + Math.cos(angle) * 114,
      y: 330 + Math.sin(angle) * 114,
      level: 1,
      details: [
        ["Scope", "Whole-phone FIELD domain · not radio sensing"],
        ["Status", field.status],
        ["Source", "Authored canonical demo model"],
        ["Current authority", telemetry.authority],
      ],
    };
  });
  telemetry.observations.forEach((obs, i) => {
    const x = 280 + i * 50,
      y = 298 + (i % 2) * 42;
    nodes.push({
      id: obs.id,
      label: `${obs.id} / ${obs.source}`,
      x,
      y,
      level: 2,
      details: [
        ["Source", "Authored Spectrum fixture · DEMO / SIMULATED"],
        ["Name", obs.name],
        ["RSSI", `${obs.rssi} dBm · not range or bearing`],
        ["Channel / frequency", `${obs.channel} / ${obs.frequency}`],
        ["Timestamp / freshness", `${obs.lastSeen} · no real clock timestamp · unverified`],
        ["Qualification", obs.qualification],
        ["Confidence", obs.confidence],
        [
          "Observed vs inferred",
          "Synthetic observation only; identity, location and threat not inferred",
        ],
        ["Authority", telemetry.authority],
      ],
    });
  });
  telemetry.evidenceTopic?.fields.forEach(([label, value], i) => {
    nodes.push({
      id: `evidence-${i}`,
      label,
      x: 299 + (i % 2) * 62,
      y: 305 + Math.floor(i / 2) * 25,
      level: 3,
      details: [
        ["Provenance", telemetry.evidence],
        [label, value],
        ["Timestamp", "Authored snapshot A → B · no real clock timestamp"],
        ["Observed vs inferred", "Authored example, not independent device observation"],
        ["Freshness", telemetry.freshness],
        ["Authority", telemetry.authority],
      ],
    });
  });
  ["Evidence", "Qualification", "Reality", "Authority", "Effect"].forEach((label, i) =>
    nodes.push({
      id: `trace-${i}`,
      label,
      x: 302 + i * 14,
      y: i % 2 === 0 ? 320 : 345,
      level: 4,
      details: [
        ["Stage", label],
        [
          "Status",
          [
            telemetry.evidence,
            telemetry.verification,
            "Not independently established",
            telemetry.authority,
            "NONE · no device action",
          ][i] ?? "HOLD",
        ],
        ["Boundary", "Missing / stale ≠ PASS. No self-witness. UNKNOWN ≠ SAFE."],
        ["Historical", telemetry.historical],
      ],
    }),
  );
  return nodes;
}
