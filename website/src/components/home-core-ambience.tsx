import { usePresentationActivity } from "@/hooks/use-presentation-activity";
import { useId } from "react";

/** Authored decorative circuitry only: no telemetry, input or authority. */
export function HomeCoreAmbience() {
  const { ref, active } = usePresentationActivity();
  const id = useId().replace(/:/g, "");
  const spectrum = `${id}-spectrum`;
  const energy = `${id}-energy`;
  return (
    <div className="home-core-ambience" aria-hidden="true">
      <section ref={ref} className="home-core-field" data-motion={active ? "active" : "paused"}>
        <svg viewBox="0 0 1440 1000" preserveAspectRatio="xMidYMid slice" focusable="false">
          <defs>
            <linearGradient id={spectrum} x1="0" y1="1" x2="1" y2="0">
              <stop offset="0" stopColor="var(--home-core-emerald)" />
              <stop offset="0.28" stopColor="var(--home-core-cyan)" />
              <stop offset="0.52" stopColor="var(--home-core-cobalt)" />
              <stop offset="0.74" stopColor="var(--home-core-violet)" />
              <stop offset="1" stopColor="var(--home-core-magenta)" />
            </linearGradient>
            <linearGradient id={energy} x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="var(--home-core-magenta)" />
              <stop offset="0.4" stopColor="var(--home-core-violet)" />
              <stop offset="0.65" stopColor="var(--home-core-cyan)" />
              <stop offset="1" stopColor="var(--home-core-emerald)" />
            </linearGradient>
          </defs>
          <g className="home-core-halo" fill="none" stroke={`url(#${spectrum})`} strokeWidth="18">
            <circle cx="790" cy="510" r="328" />
            <circle cx="790" cy="510" r="218" />
          </g>
          <g
            className="home-core-circuitry"
            fill="none"
            stroke={`url(#${spectrum})`}
            strokeWidth="2.1"
          >
            <circle cx="790" cy="510" r="218" strokeDasharray="310 38 110 24" />
            <circle cx="790" cy="510" r="238" strokeDasharray="1 18" />
            <circle cx="790" cy="510" r="328" strokeDasharray="490 80 220 42" />
            <circle cx="790" cy="510" r="350" strokeDasharray="90 360" />
            <path d="M0 210H280L390 320H520 M1440 790H1240L1110 660H1078 M0 840H260L390 710H530 M1440 150H1210L1070 290H1025" />
            <path d="M0 225H272L382 335H500 M1440 775H1248L1120 647H1100 M220 0V130L420 330 M1360 1000V855L1150 645" />
          </g>
          <g
            className="home-core-filaments"
            fill="none"
            stroke={`url(#${energy})`}
            strokeWidth="2.8"
          >
            <path d="M-80 600C190 600 290 440 475 440S790 610 1030 530 1260 370 1520 400" />
            <path d="M-80 618C180 618 300 458 475 458S795 628 1040 548 1270 388 1520 418" />
            <path d="M0 110C290 110 320 220 540 270S960 260 1130 180 1360 95 1480 120" />
            <path d="M-40 885C220 870 340 760 535 780S970 910 1160 830 1360 680 1490 700" />
          </g>
          <g className="home-core-streams" fill="none" strokeWidth="3">
            <path d="M60 325h44m20 0h5 M1210 700h30m18 0h4 M170 785h28m22 0h7 M1110 230h40m20 0h5" />
          </g>
          <g className="home-core-nodes">
            <circle cx="390" cy="320" r="3.2" />
            <circle cx="1110" cy="660" r="3.2" />
            <circle cx="1070" cy="290" r="2.8" />
            <circle cx="390" cy="710" r="2.8" />
            <circle cx="790" cy="182" r="3" />
            <circle cx="790" cy="838" r="3" />
          </g>
          <g className="home-core-particles">
            {Array.from({ length: 24 }, (_, i) => (
              <circle
                key={i}
                cx={100 + ((i * 193) % 1260)}
                cy={80 + ((i * 137) % 860)}
                r={i % 4 === 0 ? 2.4 : 1.3}
              />
            ))}
          </g>
        </svg>
      </section>
    </div>
  );
}
