import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  aurexSampleRun,
  disabledAurexClient,
  displayState,
  AUREX_REPO_URL,
} from "@/lib/aurex-integration";

const steps = ["Evidence", "Qualification", "Reality", "Authority", "Effect"] as const;

export function AurexDemo() {
  const [step, setStep] = useState(0);
  const run = aurexSampleRun;
  const state = displayState(run);
  const body: Record<(typeof steps)[number], string> = {
    Evidence: run.evidence.join(" · "),
    Qualification: run.qualification,
    Reality: `${run.reality} Independent verification: ${state.verification}.`,
    Authority: `Authority: ${state.authority}. A candidate answer is not permission to act.`,
    Effect: `Effect: ${state.effect}. Scope: ${state.scope}.`,
  };
  return (
    <section aria-labelledby="aurex-demo-title" className="section-space border-b border-border">
      <div className="site-grid">
        <p className="text-xs text-amber" data-testid="aurex-demo-label">
          PUBLIC · Demonstration — not connected to a live AUREX backend · Fixed synthetic sample
          data
        </p>
        <h2 id="aurex-demo-title" className="mt-3 font-display text-3xl">
          Walk one sample question through the gates
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
          LOCAL_PRACTICE_ONLY means a result produced in local practice runs; it is not an
          independently verified result. This demo runs entirely in your browser and makes no
          network requests. Backend status: {disabledAurexClient.status.replace("_", " / ")}.
        </p>
        <div className="mt-6 border-t border-border pt-5">
          <p className="text-sm">
            <strong>Question:</strong> {run.question}
          </p>
          <p className="mt-2 text-sm">
            <strong>Generated candidate:</strong> {run.candidate}
          </p>
        </div>
        <div role="tablist" aria-label="Reasoning stages" className="mt-6 flex flex-wrap gap-2">
          {steps.map((s, i) => (
            <Button
              key={s}
              role="tab"
              id={`aurex-tab-${i}`}
              aria-selected={step === i}
              aria-controls="aurex-panel"
              variant={step === i ? "hero" : "glass"}
              className="min-h-11"
              onClick={() => setStep(i)}
            >
              {i + 1}. {s}
            </Button>
          ))}
        </div>
        <div
          id="aurex-panel"
          role="tabpanel"
          aria-labelledby={`aurex-tab-${step}`}
          aria-live="polite"
          className="mt-4 rounded-md border border-border bg-card/40 p-5 text-sm leading-7"
        >
          {body[steps[step] ?? "Evidence"]}
        </div>
        <dl className="mt-6 grid gap-4 sm:grid-cols-4 text-sm" data-testid="aurex-demo-state">
          <div>
            <dt className="text-muted-foreground">Verification</dt>
            <dd className="text-amber">{state.verification}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Authority</dt>
            <dd className="text-gold">{state.authority}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Effect</dt>
            <dd>{state.effect}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Scope</dt>
            <dd>{state.scope}</dd>
          </div>
        </dl>
        <p className="mt-6 text-sm">
          <a
            className="underline underline-offset-4"
            href={AUREX_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            AUREX public repository on GitHub (opens in a new tab)
          </a>
        </p>
      </div>
    </section>
  );
}
