import type { DemoTelemetry } from "@/components/phone-scenarios";

const ticks = Array.from({ length: 72 }, (_, i) => {
  const angle = (i * Math.PI) / 36;
  const inner = i % 6 === 0 ? 286 : 295;
  return {
    x1: 330 + Math.sin(angle) * inner,
    y1: 330 - Math.cos(angle) * inner,
    x2: 330 + Math.sin(angle) * 304,
    y2: 330 - Math.cos(angle) * 304,
    major: i % 6 === 0,
  };
});

/** Read-only projection of the authored phone model. Geometry cannot supply authority. */
export function OrbInstruments({ telemetry }: { telemetry: DemoTelemetry }) {
  return (
    <g className="orb-instruments" aria-hidden="true" fill="none">
      <circle cx="330" cy="330" r="309" stroke="var(--cyan)" opacity=".28" />
      <g className="instrument-wheel-outer">
        {ticks.map((tick, i) => (
          <path
            key={i}
            d={`M${tick.x1} ${tick.y1}L${tick.x2} ${tick.y2}`}
            stroke={tick.major ? "var(--gold)" : "var(--cyan)"}
            opacity={tick.major ? ".8" : ".45"}
            strokeWidth={tick.major ? 2 : 1}
          />
        ))}
        <circle
          cx="330"
          cy="330"
          r="281"
          stroke="var(--cyan)"
          strokeDasharray="112 19 3 19"
          opacity=".38"
        />
        <path
          d="M71 246A273 273 0 0 1 313 58M491 550A273 273 0 0 1 81 443"
          stroke="var(--gold)"
          strokeWidth="2"
          opacity=".65"
        />
      </g>
      <g className="instrument-wheel-inner">
        <circle cx="330" cy="330" r="246" stroke="var(--cyan)" opacity=".2" />
        <circle
          cx="330"
          cy="330"
          r="251"
          stroke="var(--cyan)"
          strokeDasharray="2 14"
          opacity=".5"
        />
        <circle
          cx="330"
          cy="330"
          r="235"
          stroke="var(--gold)"
          strokeDasharray="70 95 20 110"
          opacity=".5"
        />
      </g>
      <circle
        className="instrument-progress"
        cx="330"
        cy="330"
        r="263"
        pathLength="100"
        stroke="var(--orb-tone)"
        strokeWidth="5"
        strokeDasharray={`${telemetry.progress} 100`}
        transform="rotate(-90 330 330)"
        opacity={telemetry.progress ? ".85" : "0"}
      />
      <path d="M318 18h24M642 318v24M318 642h24M18 318v24" stroke="var(--gold)" opacity=".8" />
      {telemetry.fields.map((field, i) => (
        <circle
          key={field.name}
          data-field={field.name}
          className="field-ring"
          cx="330"
          cy="330"
          r={213 + i * 17}
          pathLength="100"
          stroke={field.status === "UNKNOWN" ? "var(--steel)" : "var(--orb-tone)"}
          strokeWidth="1.5"
          strokeDasharray="14 86"
          transform={`rotate(${i * 72 - 90} 330 330)`}
          opacity={field.status === "UNKNOWN" ? ".2" : ".9"}
        />
      ))}
      {telemetry.observations.map((observation, i) => (
        <g key={observation.id}>
          <circle cx={104 + i * 225} cy={i === 1 ? 62 : 465} r="5" fill="var(--cyan)" />
          <path d={`M${94 + i * 225} ${i === 1 ? 49 : 451}q10-6 20 0`} stroke="var(--cyan)" />
        </g>
      ))}
    </g>
  );
}

export function PhoneScanReadout({ telemetry }: { telemetry: DemoTelemetry }) {
  return (
    <section
      className="phone-scan-readout"
      aria-label="Simulated scan telemetry"
      data-phase={telemetry.phase}
    >
      <p className="instrument-demo-label">DEMO / SIMULATED · NO LIVE TELEMETRY</p>
      <p className="demo-mode-status" data-hue={telemetry.hue}>
        {telemetry.modeLabel}
      </p>
      <div className="instrument-phase">
        <span>{telemetry.phase}</span>
        <strong>{telemetry.progress}% DEMO</strong>
      </div>
      <progress
        aria-label="Simulated storyboard progress, not scan coverage"
        value={telemetry.progress}
        max={100}
      />
      <dl>
        <div>
          <dt>Current status</dt>
          <dd>
            {telemetry.current} / {telemetry.verification}
          </dd>
        </div>
        <div>
          <dt>Historical</dt>
          <dd>{telemetry.historical}</dd>
        </div>
        <div>
          <dt>Last check / age</dt>
          <dd>{telemetry.lastCheck}</dd>
        </div>
        <div>
          <dt>Freshness</dt>
          <dd>{telemetry.freshness}</dd>
        </div>
        <div>
          <dt>Evidence</dt>
          <dd>{telemetry.evidence}</dd>
        </div>
      </dl>
      <p className="mt-2">{telemetry.evidenceTopic?.summary}</p>
      <p className="instrument-boundary">Unknown ≠ Safe · ORB MOTION AUTHORITY = NONE</p>
    </section>
  );
}
