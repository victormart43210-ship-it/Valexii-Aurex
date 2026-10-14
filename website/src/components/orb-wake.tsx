/** Bounded deterministic ribbons and delayed dust; physically inspired art, not CFD. */
export function OrbWake({ id }: { id: string }) {
  return (
    <g className="orb-slingshot-wake" aria-hidden="true" fill="none" stroke={`url(#${id}-ion)`}>
      {[0, 1, 2].map((i) => (
        <path
          key={i}
          className="orb-wake-ribbon"
          d={`M${30 + i * 16} ${48 + i * 10}C${210 - i * 22} 15, 78 ${275 + i * 12}, 230 291S306 325,330 330`}
          strokeWidth={18 - i * 5}
          opacity={0.08 + i * 0.025}
        />
      ))}
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <path
          key={i}
          className="orb-wake-wisp"
          d={`M${48 + i * 15} ${49 + i * 8}C${240 - i * 12} ${15 + i * 6},${56 + i * 18} ${300 + i * 3},245 305Q208 247,264 283T330 330`}
          strokeWidth={i % 2 ? 1 : 2}
          opacity=".55"
        />
      ))}
      <g stroke="var(--cyan)" strokeWidth="1.4" className="orb-entry-shear">
        <path d="M184 218q-43 53-15 100M179 345q-24 65 35 100M414 189q64 22 87 84" />
        <path d="M192 382q-62 47-106 22M196 399q-36 54-81 54M220 422q-30 57-54 56" />
        <ellipse cx="169" cy="434" rx="11" ry="2" transform="rotate(-32 169 434)" />
        <ellipse cx="116" cy="417" rx="7" ry="1.5" transform="rotate(-16 116 417)" />
      </g>
      <g fill="var(--gold)" stroke="none">
        {Array.from({ length: 12 }, (_, i) => (
          <circle
            className="orb-delayed-particle"
            key={i}
            cx={55 + i * 15}
            cy={71 + i * 16}
            r={i % 3 ? 1 : 2}
          />
        ))}
      </g>
    </g>
  );
}
