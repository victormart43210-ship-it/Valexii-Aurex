import { useId } from "react";

/** Original, deterministic vector illustrations. Geometry is not security telemetry. */
export function JourneyArt({ kind }: { kind: "call" | "malware" }) {
  const id = useId();
  return (
    <svg
      className="journey-art"
      viewBox="0 0 320 150"
      role="img"
      aria-label={
        kind === "call"
          ? "Original illustration: layered cyan call-screening waves around a gold phone shield"
          : "Original illustration: magnified app tiles and an amber permission-question marker; not scanned apps"
      }
    >
      <defs>
        <radialGradient id={id}>
          <stop stopColor="var(--cyan)" stopOpacity=".24" />
          <stop offset="1" stopColor="var(--background)" stopOpacity="0" />
        </radialGradient>
      </defs>
      <ellipse cx="160" cy="90" rx="130" ry="56" fill={`url(#${id})`} />
      {kind === "call" ? (
        <g fill="none">
          {[42, 62, 84, 109, 133].map((r, i) => (
            <ellipse
              key={r}
              cx="160"
              cy="100"
              rx={r}
              ry={r * 0.29}
              stroke={i % 2 ? "var(--gold)" : "var(--cyan)"}
              strokeOpacity={0.8 - i * 0.12}
            />
          ))}
          <path
            d="M126 24L160 14L194 24V64Q194 95 160 112Q126 95 126 64Z"
            fill="var(--card)"
            stroke="var(--gold)"
            strokeWidth="1.5"
          />
          <rect x="146" y="34" width="28" height="47" rx="5" stroke="var(--cyan)" strokeWidth="2" />
          <path
            d="M154 73h12M151 28h18M108 44q-12 22 0 43M212 44q12 22 0 43M94 34q-20 32 0 62M226 34q20 32 0 62"
            stroke="var(--cyan)"
          />
          <path d="M160 113v23M140 136h40" stroke="var(--gold)" />
        </g>
      ) : (
        <g>
          {Array.from({ length: 24 }, (_, i) => (
            <g key={i} transform={`translate(${54 + (i % 8) * 27} ${30 + Math.floor(i / 8) * 28})`}>
              <rect
                width="19"
                height="19"
                rx="3"
                fill="var(--secondary)"
                stroke="var(--cyan)"
                strokeOpacity=".4"
              />
              <path d="M5 8h9M5 12h5" stroke="var(--cyan)" strokeOpacity=".5" />
            </g>
          ))}
          <circle
            cx="174"
            cy="77"
            r="48"
            fill="var(--card)"
            fillOpacity=".9"
            stroke="var(--gold)"
          />
          <circle cx="174" cy="77" r="41" fill="none" stroke="var(--cyan)" strokeDasharray="2 6" />
          <rect
            x="157"
            y="59"
            width="34"
            height="34"
            rx="6"
            fill="var(--accent)"
            stroke="var(--amber)"
          />
          <text x="174" y="83" textAnchor="middle" fill="var(--amber)" fontSize="24">
            ?
          </text>
          <path d="M209 112l21 21" stroke="var(--gold)" strokeWidth="5" />
          <path d="M133 76H106M174 35V20M174 119v16" stroke="var(--cyan)" />
        </g>
      )}
    </svg>
  );
}
