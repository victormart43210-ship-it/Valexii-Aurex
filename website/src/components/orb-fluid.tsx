/** Deterministic projected flow geometry. Stylized axial motion, not a CFD model. */
export function OrbFluid({ id }: { id: string }) {
  return (
    <g className="orb-fluid" clipPath={`url(#${id}-fluid-clip)`} aria-hidden="true">
      <defs>
        <clipPath id={`${id}-fluid-clip`}>
          <circle cx="330" cy="330" r="176" />
        </clipPath>
        <linearGradient id={`${id}-fluid-light`} x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="var(--cyan)" stopOpacity=".06" />
          <stop offset=".42" stopColor="var(--orb-tone)" stopOpacity=".9" />
          <stop offset=".64" stopColor="var(--orb-tone)" stopOpacity=".3" />
          <stop offset="1" stopColor="var(--gold)" stopOpacity=".5" />
        </linearGradient>
      </defs>
      <g className="orb-axial-flow" fill="none" stroke={`url(#${id}-fluid-light)`}>
        {Array.from({ length: 12 }, (_, i) => (
          <path
            key={i}
            d={`M${150 + i * 8} 165 C${490 - i * 7} ${170 + i * 12}, ${105 + i * 15} ${430 - i * 8}, ${500 - i * 6} 496`}
            strokeWidth={i % 3 === 0 ? 9 : 2}
            opacity={i % 3 === 0 ? ".25" : ".65"}
          />
        ))}
        <g className="orb-vortex-flow" strokeWidth="2">
          <path d="M239 236c-83 95 50 186 134 105s-11-162-67-108 13 104 50 65" />
          <path d="M409 435c62-92-31-141-96-91s-4 107 39 82-3-58-26-43" />
        </g>
      </g>
      <g className="orb-axial-meridian" fill="none" stroke="var(--cyan)" strokeOpacity=".22">
        <ellipse cx="330" cy="330" rx="133" ry="175" />
        <ellipse cx="330" cy="330" rx="90" ry="175" />
      </g>
    </g>
  );
}
