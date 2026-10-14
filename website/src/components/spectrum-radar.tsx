import { useId } from "react";
import { Radio, CircleHelp, TriangleAlert } from "lucide-react";
import { usePresentationActivity } from "@/hooks/use-presentation-activity";
import { plotSpectrumObservation, type DemoTelemetry } from "@/components/phone-scenarios";
import { EmptyState } from "@/components/ui-system";

export function SpectrumRadar({
  telemetry,
  motion,
}: {
  telemetry: DemoTelemetry;
  motion: boolean;
}) {
  const id = useId().replaceAll(":", "");
  const { ref, active } = usePresentationActivity();
  return (
    <section
      ref={ref}
      className="spectrum-radar"
      data-hue={telemetry.hue}
      data-moving={active && motion && telemetry.scanActive}
      aria-label="Spectrum simulated radio observations"
    >
      <h3>
        <Radio aria-hidden="true" /> SPECTRUM / RADIO
      </h3>
      <p className="instrument-demo-label">DEMO / SIMULATED · NO RADIO ACCESS</p>
      <svg
        viewBox="0 0 280 280"
        role="img"
        aria-label="Nongeographic signal bins; radius shows synthetic RSSI band, not distance. No true bearings or location tracking."
      >
        <defs>
          <linearGradient id={`${id}-beam`}>
            <stop stopColor="var(--cyan)" stopOpacity="0" />
            <stop offset="1" stopColor="var(--cyan)" stopOpacity=".4" />
          </linearGradient>
        </defs>
        <g fill="none" stroke="var(--border)">
          {[45, 75, 105, 123].map((r) => (
            <circle key={r} cx="140" cy="140" r={r} />
          ))}
          <path d="M140 17V263M17 140H263" strokeDasharray="2 8" />
        </g>
        {telemetry.scanActive && (
          <g className="spectrum-beam">
            <path d="M140 140L140 18A122 122 0 0 1 246 79Z" fill={`url(#${id}-beam)`} />
            <path d="M140 140V18" stroke="var(--cyan)" strokeWidth="2" />
          </g>
        )}
        <g fill="var(--muted-foreground)" fontSize="9" textAnchor="middle">
          <text x="140" y="12">
            BIN 01
          </text>
          <text x="245" y="226">
            BIN 02
          </text>
          <text x="35" y="226">
            BIN 03
          </text>
          <text x="140" y="274">
            RSSI BANDS · NOT RANGE
          </text>
        </g>
        {telemetry.observations.map((observation) => {
          const point = plotSpectrumObservation(observation);
          return (
            <g
              key={observation.id}
              data-observation={observation.id}
              className="spectrum-observation"
            >
              <circle
                cx={point.x}
                cy={point.y}
                r="9"
                fill="var(--background)"
                stroke={
                  observation.qualification.includes("STALE") ? "var(--amber)" : "var(--cyan)"
                }
              />
              <path
                d={`M${point.x - 12} ${point.y - 14}q12-8 24 0`}
                stroke="var(--cyan)"
                fill="none"
              />
              <text
                x={point.x}
                y={point.y + 3}
                textAnchor="middle"
                fontSize="8"
                fill="var(--foreground)"
              >
                {observation.id}
              </text>
            </g>
          );
        })}
        <circle cx="140" cy="140" r="4" fill="var(--cyan)" />
      </svg>
      <p className="spectrum-disclaimer">Signal visualization, not location tracking.</p>
      <p className="spectrum-legend">
        Inner / mid / outer = stronger / mid / weaker RSSI. Bins are ordered drawing slots, not
        compass bearings.
      </p>
      {!telemetry.observations.length && (
        <EmptyState title="No demo observations selected · UNKNOWN" className="spectrum-empty">
          Missing observations are not a passed scan. No radio access or live device check.
        </EmptyState>
      )}
      <ul className="spectrum-records">
        {telemetry.observations.map((observation) => (
          <li key={observation.id}>
            <strong>
              {observation.id} / {observation.source} · {observation.rssi} dBm
            </strong>
            <span>{observation.name}</span>
            <span>
              Channel {observation.channel} · {observation.frequency}
            </span>
            <span>
              {plotSpectrumObservation(observation).band} · {observation.lastSeen}
            </span>
            <span>
              <TriangleAlert aria-hidden="true" /> {observation.qualification} · confidence{" "}
              {observation.confidence}
            </span>
            <svg
              viewBox="0 0 144 60"
              role="img"
              aria-label={`${observation.id} authored RSSI history, not live signal measurements`}
            >
              <polyline
                points={plotSpectrumObservation(observation).trace}
                fill="none"
                stroke="var(--cyan)"
                strokeWidth="2"
              />
            </svg>
          </li>
        ))}
      </ul>
      <p className="spectrum-legend">
        Source: authored radio fixture. Freshness unverified; missing or stale ≠ PASS. Hidden SSID
        cues do not identify a network name; RSSI establishes neither physical direction nor precise
        distance.
      </p>
      <p className="spectrum-legend">
        Distance needs genuine measured RTT/UWB; direction needs capable hardware and permission.
        This website has neither and discovers no networks.
      </p>
    </section>
  );
}

export function FieldDomains({ telemetry }: { telemetry: DemoTelemetry }) {
  return (
    <section className="field-domains" aria-label="BCXMET FIELD domains">
      <h3>BCXMET FIELD / WHOLE PHONE</h3>
      <p className="spectrum-legend">DEMO domain rings · not radio measurements</p>
      <ul>
        {telemetry.fields.map((field) => (
          <li key={field.name} data-hue={field.hue}>
            <CircleHelp aria-hidden="true" />
            <span>
              <strong>{field.name}</strong>
              <span>{field.status}</span>
            </span>
          </li>
        ))}
      </ul>
      <p className="spectrum-legend">
        Current authority NONE · historical CLEAR not established. Colors describe the storyboard,
        never proven security.
      </p>
    </section>
  );
}
