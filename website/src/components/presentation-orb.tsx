import { useId } from "react";
import { orbDescriptions, type OrbState } from "@/components/orb-states";
import { usePresentationActivity } from "@/hooks/use-presentation-activity";
import { OrbFluid } from "@/components/orb-fluid";
import { OrbInstruments } from "@/components/orb-instruments";
import { OrbWake } from "@/components/orb-wake";
import type { DemoTelemetry } from "@/components/phone-scenarios";

// Fixed deterministic geometry: no frame loops, random hydration, or external assets.
const particles = Array.from({ length: 46 }, (_, i) => ({
  x: 28 + ((i * 67) % 225),
  y: 24 + ((i * 43) % 230),
  r: i % 7 === 0 ? 2.8 : i % 3 === 0 ? 1.6 : 0.8,
}));
const nodes = Array.from({ length: 19 }, (_, i) => {
  const angle = i * 2.39996;
  const radius = 65 + ((i * 31) % 108);
  return { x: 330 + Math.cos(angle) * radius, y: 330 + Math.sin(angle) * radius };
});

export function PresentationOrb({
  state = "UNKNOWN",
  compact = false,
  motion = true,
  telemetry,
  deliberate = false,
  eventKey = 0,
}: {
  state?: OrbState;
  compact?: boolean;
  motion?: boolean;
  telemetry?: DemoTelemetry | undefined;
  deliberate?: boolean;
  eventKey?: number;
}) {
  const id = useId().replaceAll(":", "");
  const { ref, active } = usePresentationActivity();
  return (
    <figure
      ref={ref}
      data-state={state}
      data-moving={active && motion}
      data-deliberate={deliberate}
      data-hue={telemetry?.hue}
      data-scan={telemetry?.scanActive ?? false}
      className={`canonical-orb presentation-orb ${compact ? "orb-compact" : ""}`}
    >
      <svg
        viewBox="0 0 660 660"
        role="img"
        aria-label={`BCXMET ${state} simulated Orb. ${telemetry?.modeLabel ?? orbDescriptions[state]} Orb motion authority: none.`}
      >
        <defs>
          <radialGradient id={`${id}-shell`} cx="36%" cy="29%" r="72%">
            <stop stopColor="var(--foreground)" stopOpacity=".19" />
            <stop offset=".26" stopColor="var(--orb-tone)" stopOpacity=".11" />
            <stop offset=".61" stopColor="var(--background)" stopOpacity=".7" />
            <stop offset=".86" stopColor="var(--orb-tone)" stopOpacity=".1" />
            <stop offset=".96" stopColor="var(--orb-tone)" stopOpacity=".55" />
            <stop offset="1" stopColor="var(--foreground)" stopOpacity=".14" />
          </radialGradient>
          <radialGradient id={`${id}-halo`}>
            <stop offset=".55" stopColor="var(--orb-tone)" stopOpacity="0" />
            <stop offset=".76" stopColor="var(--orb-tone)" stopOpacity=".1" />
            <stop offset="1" stopColor="var(--orb-tone)" stopOpacity="0" />
          </radialGradient>
          <radialGradient id={`${id}-head`}>
            <stop stopColor="var(--foreground)" />
            <stop offset=".16" stopColor="var(--foreground)" stopOpacity=".95" />
            <stop offset=".32" stopColor="var(--orb-tone)" stopOpacity=".95" />
            <stop offset=".58" stopColor="var(--cyan)" stopOpacity=".32" />
            <stop offset="1" stopColor="var(--cyan)" stopOpacity="0" />
          </radialGradient>
          <linearGradient id={`${id}-rim`} x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="var(--foreground)" stopOpacity=".95" />
            <stop offset=".3" stopColor="var(--orb-tone)" />
            <stop offset=".62" stopColor="var(--orb-tone)" stopOpacity=".08" />
            <stop offset="1" stopColor="var(--orb-tone)" stopOpacity=".8" />
          </linearGradient>
          <linearGradient id={`${id}-ion`} x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="var(--cyan)" stopOpacity="0" />
            <stop offset=".24" stopColor="var(--cyan)" stopOpacity=".3" />
            <stop offset=".7" stopColor="var(--cyan)" stopOpacity=".8" />
            <stop offset=".92" stopColor="var(--gold)" />
            <stop offset="1" stopColor="var(--foreground)" />
          </linearGradient>
          <linearGradient id={`${id}-gold`}>
            <stop stopColor="var(--gold)" stopOpacity="0" />
            <stop offset=".65" stopColor="var(--gold)" stopOpacity=".65" />
            <stop offset="1" stopColor="var(--foreground)" />
          </linearGradient>
        </defs>
        <circle cx="330" cy="330" r="288" fill={`url(#${id}-halo)`} />
        {telemetry && <OrbInstruments telemetry={telemetry} />}
        {telemetry?.scanActive && (
          <g className="orb-scan-beam" fill="none" stroke="var(--cyan)">
            <path d="M330 330V80" strokeWidth="3" />
            <path
              d="M330 330L214 103A256 256 0 0 1 330 74Z"
              fill="var(--glow-primary)"
              stroke="none"
            />
            <circle cx="330" cy="330" r="199" strokeWidth="2" />
          </g>
        )}
        <g key={eventKey} className="orb-slingshot-subject">
          <OrbWake id={id} />
          <g className="orb-v5-tail" fill="none" stroke={`url(#${id}-ion)`}>
            <path
              d="M12 18 C98 40 159 254 328 330 M28 12 C150 100 193 292 330 330 M8 94 C159 112 175 345 330 330"
              strokeWidth="24"
              opacity=".12"
            />
            {Array.from({ length: 14 }, (_, i) => (
              <path
                key={i}
                className="orb-ion-filament"
                d={`M${12 + i * 6} ${14 + i * 7} C${138 + i * 6} ${42 + i * 10}, ${140 + i * 5} ${313 + i * 4}, 330 330`}
                strokeWidth={i % 4 === 0 ? 2.8 : 1.1}
                opacity={i % 3 === 0 ? ".9" : ".5"}
              />
            ))}
            <path d="M14 24 C124 97 220 300 330 330" stroke={`url(#${id}-gold)`} strokeWidth="4" />
            <g className="orb-gold-dust" stroke="none" fill="var(--gold)">
              {particles.map((p, i) => (
                <circle key={i} cx={p.x} cy={p.y} r={p.r} opacity={i % 3 === 0 ? ".85" : ".4"} />
              ))}
            </g>
          </g>
          <g className="orb-v5-orbit orb-orbit-outer" fill="none" stroke="var(--orb-tone)">
            <ellipse
              cx="330"
              cy="330"
              rx="283"
              ry="108"
              transform="rotate(-34 330 330)"
              opacity=".5"
            />
            <ellipse
              cx="330"
              cy="330"
              rx="277"
              ry="115"
              transform="rotate(-34 330 330)"
              opacity=".16"
            />
            <circle cx="330" cy="330" r="266" strokeDasharray="1 19" opacity=".35" />
            <path d="M103 190 A267 267 0 0 1 520 145" stroke="var(--gold)" opacity=".6" />
            <circle cx="111" cy="470" r="3" fill="var(--gold)" stroke="none" />
          </g>
          <g className="orb-v5-orbit orb-orbit-inner" fill="none" stroke={`url(#${id}-rim)`}>
            <ellipse
              cx="330"
              cy="330"
              rx="205"
              ry="261"
              transform="rotate(29 330 330)"
              opacity=".4"
            />
            <ellipse
              cx="330"
              cy="330"
              rx="244"
              ry="66"
              transform="rotate(38 330 330)"
              opacity=".25"
            />
          </g>
          <OrbFluid id={id} />
          <g className="orb-pressure-wave" fill="none" stroke="var(--cyan)">
            <ellipse cx="330" cy="330" rx="192" ry="72" transform="rotate(-24 330 330)" />
            <ellipse cx="330" cy="330" rx="218" ry="84" transform="rotate(-24 330 330)" />
            <path d="M137 390q-58 23-91 11M139 405q-44 35-66 30M520 256q40-28 63-18" />
          </g>
          <g className="orb-glass-shell">
            <circle
              cx="330"
              cy="330"
              r="184"
              fill={`url(#${id}-shell)`}
              stroke={`url(#${id}-rim)`}
              strokeWidth="1.8"
            />
            <circle cx="330" cy="330" r="179" fill="none" stroke="var(--orb-tone)" opacity=".18" />
            <path
              className="orb-glass-highlight"
              d="M164 257 A180 180 0 0 1 365 153"
              fill="none"
              stroke="var(--foreground)"
              strokeWidth="2"
              opacity=".7"
            />
            <path
              d="M210 459 A178 178 0 0 0 498 380"
              fill="none"
              stroke="var(--cyan)"
              strokeWidth="3"
              opacity=".45"
            />
          </g>
          <g className="orb-filament-network" fill="none" stroke="var(--orb-tone)">
            <g className="orb-fine-filaments" stroke={`url(#${id}-rim)`} strokeWidth="1.1">
              <path d="M165 308 C231 152 380 160 479 357 M186 402 C282 453 424 393 468 245" />
              <path d="M233 176 C350 224 430 325 379 488" opacity=".45" />
            </g>
            {Array.from({ length: 7 }, (_, i) => (
              <ellipse
                key={i}
                cx="330"
                cy="330"
                rx={48 + i * 21}
                ry="177"
                transform={`rotate(${i * 26} 330 330)`}
                opacity={i % 2 === 0 ? ".17" : ".09"}
              />
            ))}
            <path
              d="M172 255 Q346 225 459 443 M173 407 Q267 195 475 259 M236 174 Q439 319 239 485 M151 330 Q345 434 506 331"
              opacity=".35"
            />
            {nodes.map((node, i) => {
              const next = nodes[(i + 3) % nodes.length];
              return (
                <g key={i}>
                  {next && <path d={`M${node.x} ${node.y}L${next.x} ${next.y}`} opacity=".14" />}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={i % 5 === 0 ? 2.8 : 1.3}
                    fill={i % 5 === 0 ? "var(--gold)" : "var(--orb-tone)"}
                    stroke="none"
                    opacity=".8"
                  />
                </g>
              );
            })}
          </g>
          <g className="orb-awareness" fill="none" stroke="var(--cyan)">
            <circle cx="330" cy="330" r="211" strokeDasharray="3 12" opacity=".55" />
            <path d="M316 112h28M316 548h28M112 316v28M548 316v28" strokeWidth="2" />
          </g>
          <g className="orb-watch" fill="none" stroke="var(--amber)" strokeWidth="2">
            <path d="M162 191 A218 218 0 0 1 502 190 M502 470 A218 218 0 0 1 162 470" />
            <path d="M330 278v65m0 22v7" strokeWidth="4" />
          </g>
          <circle className="orb-comet-head" cx="330" cy="330" r="93" fill={`url(#${id}-head)`} />
          <g className="orb-containment" fill="none" stroke="var(--gold)">
            <circle cx="330" cy="330" r="207" strokeWidth="2" />
            <circle cx="330" cy="330" r="218" opacity=".4" />
            <path
              d="M190 173h-28v28m336-28h-28m28 0v28M162 459v28h28m280 0h28v-28"
              strokeWidth="3"
            />
            <path d="M308 317v-12a22 22 0 0 1 44 0v12m-51 0h58v48h-58z" strokeWidth="2" />
          </g>
          <g className="orb-return" fill="none" stroke="var(--cyan)">
            <path d="M488 255 A174 174 0 1 1 347 157m0 0l-18-17m18 17l-20 13" strokeWidth="2" />
            <circle cx="330" cy="330" r="201" strokeDasharray="2 20" opacity=".3" />
          </g>
          {state === "UNKNOWN" && (
            <g>
              <circle
                cx="330"
                cy="330"
                r="56"
                fill="var(--background)"
                stroke="var(--steel)"
                strokeDasharray="4 7"
              />
              <text x="330" y="350" textAnchor="middle" fill="var(--foreground)" fontSize="60">
                ?
              </text>
            </g>
          )}
          {state === "ERROR" && (
            <g fill="var(--background)" stroke="var(--destructive)" strokeWidth="3">
              <path d="M330 265l57 33v64l-57 33-57-33v-64z" />
              <path d="M313 313l34 34m0-34l-34 34" stroke="var(--foreground)" strokeWidth="4" />
            </g>
          )}
        </g>
      </svg>
      {!compact && (
        <figcaption className="orb-caption">
          <span>{state} · SIMULATED PRESENTATION</span>
          <span>{orbDescriptions[state]}</span>
          <span>ORB MOTION AUTHORITY = NONE</span>
        </figcaption>
      )}
    </figure>
  );
}
