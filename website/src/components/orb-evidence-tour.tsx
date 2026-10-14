import { useState } from "react";
import { ArrowLeft, ArrowRight, Check, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { PresentationOrb } from "@/components/presentation-orb";
import { phoneTopics } from "@/components/phone-scenarios";
import type { DemoTelemetry } from "@/components/phone-scenarios";
import { type OrbState } from "@/components/orb-states";
import { emitActivation } from "@/lib/activation-events";

const steps = [
  { title: "What changed?", topic: 1 },
  { title: "Why?", topic: 3 },
  { title: "Show proof", topic: 4 },
] as const;

/** Authored educational content only; opening the Orb does not change its state. */
export function OrbEvidenceTour({
  state,
  motion,
  telemetry,
  deliberate = false,
  eventKey = 0,
}: {
  state: OrbState;
  motion: boolean;
  telemetry?: DemoTelemetry;
  deliberate?: boolean;
  eventKey?: number;
}) {
  const [step, setStep] = useState(0);
  const [open, setOpen] = useState(false);
  const current = steps[step] ?? steps[0];
  const topic = phoneTopics.Home[current.topic];
  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (next) setStep(0);
      }}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" className="orb-tour-trigger" aria-label="Open XAELI evidence tour">
          <PresentationOrb
            compact
            state={state}
            motion={motion}
            telemetry={telemetry}
            deliberate={deliberate}
            eventKey={eventKey}
          />
          <span className="orb-tour-hint">
            <Search aria-hidden="true" /> Review with XAELI
          </span>
        </Button>
      </DialogTrigger>
      <DialogContent className="orb-tour-dialog">
        <p className="pr-11 text-xs text-gold">XAELI · GUIDED DEMO · {step + 1} / 3</p>
        <DialogTitle className="font-display text-2xl">{current.title}</DialogTitle>
        <DialogDescription>
          Simulated permission-change example. No device access, live AI or security verdict.
        </DialogDescription>
        <ol className="orb-tour-progress" aria-label="Tour progress">
          {steps.map((item, index) => (
            <li key={item.title} aria-current={step === index ? "step" : undefined}>
              <span>{index + 1}</span>
              {item.title}
            </li>
          ))}
        </ol>
        <div className="orb-tour-evidence" aria-live="polite" aria-atomic="true">
          <p className="text-sm leading-6 text-foreground">{topic?.summary}</p>
          <dl className="phone-detail-fields">
            {topic?.fields.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </div>
        <p className="text-xs leading-6 text-muted-foreground">
          Evidence → Qualification → Reality → Authority → Effect.
          <br />
          Unknown ≠ Safe. The system may never be its own sole witness.
          <br />
          <span className="text-gold">ORB MOTION AUTHORITY = NONE</span>
        </p>
        <div className="flex items-center justify-between gap-3">
          <Button variant="glass" disabled={step === 0} onClick={() => setStep(step - 1)}>
            <ArrowLeft />
            Back
          </Button>
          {step < 2 ? (
            <Button
              variant="hero"
              onClick={() => {
                setStep(step + 1);
                if (step === 1) emitActivation("proof_view");
              }}
            >
              Next
              <ArrowRight />
            </Button>
          ) : (
            <Button variant="hero" onClick={() => setOpen(false)}>
              <Check />
              Done
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
