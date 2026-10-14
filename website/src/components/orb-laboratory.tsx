import { useEffect, useState } from "react";
import { CircleHelp, OctagonAlert, Pause, Play, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PresentationOrb } from "@/components/presentation-orb";
import { orbDescriptions, orbStates, type OrbState } from "@/components/orb-states";
import { usePresentationActivity } from "@/hooks/use-presentation-activity";

const phases = orbStates.slice(0, 6);
const phaseLabels: Record<OrbState, string> = {
  REST: "Quiet shell",
  AWARE: "Observation halo",
  WATCH: "Unresolved attention",
  DEFEND: "Comet transition",
  CONTAIN: "Bounded perimeter",
  RETURN: "Return to quiet",
  UNKNOWN: "Evidence unavailable",
  ERROR: "Presentation error",
};

export function OrbLaboratory() {
  const [state, setState] = useState<OrbState>("REST");
  const [playing, setPlaying] = useState(false);
  const [motion, setMotion] = useState(true);
  const { ref, active, reducedMotion } = usePresentationActivity();
  useEffect(() => {
    if (!playing || !active) return;
    const timer = window.setTimeout(() => {
      const next = phases[phases.indexOf(state) + 1];
      if (next) setState(next);
      else setPlaying(false);
    }, 2800);
    return () => window.clearTimeout(timer);
  }, [playing, active, state]);
  const select = (next: OrbState) => {
    setPlaying(false);
    setMotion(true);
    setState(next);
  };
  return (
    <section
      id="orb-laboratory"
      className="orb-laboratory section-space border-y border-border"
      aria-labelledby="orb-lab-title"
    >
      <div className="site-grid">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="mb-3 text-xs text-gold">BCXMET / SOVEREIGN COMET V5</p>
            <h2 id="orb-lab-title" className="font-display text-3xl md:text-4xl">
              Orb laboratory
            </h2>
          </div>
          <p className="max-w-md text-sm leading-7 text-muted-foreground">
            Interactive simulation · Design intent / Developmental.
            <br />
            No live scan, device defense, or containment. ORB MOTION AUTHORITY = NONE.
          </p>
        </div>
        <div className="orb-lab-layout">
          <figure ref={ref} className="orb-lab-stage">
            <div className="orb-lab-stage-label">
              <span>SIMULATED / {state}</span>
              <span>AUTHORITY: NONE</span>
            </div>
            <PresentationOrb state={state} motion={motion} compact />
            <p className="orb-lab-mode">
              {reducedMotion
                ? "Static equivalent · reduced motion"
                : playing
                  ? active
                    ? "Sequence playing · presentation only"
                    : "Sequence held · preview not visible"
                  : motion && state === "DEFEND"
                    ? "Comet preview · simulated DEFEND only"
                    : motion && ["REST", "AWARE", "RETURN"].includes(state)
                      ? "Restrained filament preview · presentation only"
                      : "Static phase · presentation only"}
            </p>
          </figure>
          <div className="min-w-0">
            <div className="orb-phase-grid" role="group" aria-label="Simulated Orb phases">
              {phases.map((phase, i) => (
                <Button
                  key={phase}
                  variant="outline"
                  className="orb-phase-card"
                  aria-pressed={state === phase}
                  onClick={() => select(phase)}
                  aria-controls="orb-lab-explanation"
                >
                  <span className="orb-phase-index">0{i + 1}</span>
                  <span>
                    {phase}
                    <span className="orb-phase-subtitle">{phaseLabels[phase]}</span>
                  </span>
                </Button>
              ))}
            </div>
            <div
              className="mt-4 flex flex-wrap gap-2"
              role="group"
              aria-label="Unavailable and error states"
            >
              <Button
                variant="outline"
                className="min-h-11"
                aria-pressed={state === "UNKNOWN"}
                onClick={() => select("UNKNOWN")}
              >
                <CircleHelp />
                UNKNOWN
              </Button>
              <Button
                variant="outline"
                className="min-h-11"
                aria-pressed={state === "ERROR"}
                onClick={() => select("ERROR")}
              >
                <OctagonAlert />
                ERROR
              </Button>
            </div>
            <div
              id="orb-lab-explanation"
              className="orb-lab-explanation"
              role="status"
              aria-live="polite"
              aria-atomic="true"
            >
              <h3 className="mb-2 text-sm font-semibold">
                {state} · {phaseLabels[state]}
              </h3>
              <p className="text-sm leading-7 text-muted-foreground">{orbDescriptions[state]}</p>
              <p className="mt-3 text-xs leading-6 text-muted-foreground">
                Unknown ≠ Safe. Missing or stale evidence ≠ PASS. A visual transition never grants
                permission to act.
              </p>
            </div>
            <div className="flex flex-wrap gap-2" role="group" aria-label="Orb sequence controls">
              <Button
                variant="hero"
                className="min-h-11"
                disabled={playing || reducedMotion}
                onClick={() => {
                  if (!phases.includes(state) || state === "RETURN") setState("REST");
                  setMotion(true);
                  setPlaying(true);
                }}
              >
                <Play />
                Play Sequence
              </Button>
              <Button
                variant="outline"
                className="min-h-11"
                disabled={!playing && !motion}
                onClick={() => {
                  setPlaying(false);
                  setMotion(false);
                }}
              >
                <Pause />
                Pause
              </Button>
              <Button
                variant="outline"
                className="min-h-11"
                onClick={() => {
                  setPlaying(false);
                  setMotion(false);
                  setState("REST");
                }}
              >
                <RotateCcw />
                Reset
              </Button>
            </div>
            <p className="mt-4 text-xs leading-6 text-muted-foreground">
              Six presentation phases; comet filaments move only in simulated DEFEND. Reduced motion
              keeps every state selectable and static.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
