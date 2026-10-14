import { Link } from "@tanstack/react-router";
import {
  ArrowRight,
  CircleCheck,
  CircleHelp,
  Eye,
  LockKeyhole,
  ScanSearch,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ConceptLabel, StateIndicator } from "@/components/site";

export { CanonicalOrb as CometSystem } from "@/components/visuals";

export const scanStates = [
  {
    label: "Checked",
    detail: "Within the scan's stated scope",
    icon: CircleCheck,
    tone: "text-primary",
  },
  {
    label: "Not checked",
    detail: "Outside this pass or unavailable",
    icon: CircleHelp,
    tone: "text-muted-foreground",
  },
  {
    label: "Clean",
    detail: "No issue found in checked scope",
    icon: CircleCheck,
    tone: "text-sense",
  },
  {
    label: "Attention",
    detail: "Evidence merits closer review",
    icon: ShieldAlert,
    tone: "text-amber",
  },
  {
    label: "Unknown",
    detail: "Insufficient basis to conclude",
    icon: CircleHelp,
    tone: "text-analyze",
  },
] as const;

export function ScanConcept() {
  return (
    <div className="border border-border bg-card/85 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <ConceptLabel />
        <StateIndicator label="Developmental" tone="amber" />
      </div>
      <div className="mt-8 flex items-end justify-between border-b border-border pb-6">
        <div>
          <p className="text-xs uppercase text-primary">BCXMET / DEEP SCAN</p>
          <h3 className="mt-3 font-display text-3xl">Scope before certainty.</h3>
        </div>
        <ScanSearch className="hidden size-12 text-primary sm:block" />
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {scanStates.map((s) => (
          <div key={s.label} className="flex gap-3 border-b border-border/60 pb-4">
            <s.icon aria-hidden="true" className={`mt-1 size-5 shrink-0 ${s.tone}`} />
            <div>
              <p className="font-semibold">{s.label}</p>
              <p className="mt-1 text-sm text-muted-foreground">{s.detail}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 border-l-2 border-gold pl-4 text-sm leading-7 text-muted-foreground">
        <strong className="text-foreground">Limitations & evidence</strong>
        <br />A result must show what was examined, what was not, and why the conclusion is bounded.
        Premium depth never changes objective security truth.
      </div>
    </div>
  );
}

export function XaeliDemo() {
  return (
    <div className="overflow-hidden border border-border bg-card/90">
      <div className="flex items-center justify-between border-b border-border px-5 py-4">
        <div className="flex items-center gap-3">
          <span className="grid size-9 place-items-center rounded-full border border-primary/50 text-primary">
            <Sparkles className="size-4" />
          </span>
          <div>
            <p className="text-sm font-bold">XAELI</p>
            <p className="text-[11px] text-muted-foreground">
              Evidence-aware explanation · concept
            </p>
          </div>
        </div>
        <span className="text-[10px] uppercase text-gold">Human control</span>
      </div>
      <div className="space-y-5 p-5 sm:p-8">
        <div className="ml-auto max-w-[85%] border border-border bg-background p-4 text-sm">
          Why is this app a caution?
        </div>
        <div className="max-w-[92%] border-l-2 border-primary pl-5">
          <p className="text-sm leading-7 text-foreground">
            A recent permission change deserves a closer look. That change alone does not prove the
            app is harmful. I would confirm whether you expected it before deciding what to do.
          </p>
          <p className="mt-4 text-xs text-muted-foreground">
            Evidence summary · not an automatic verdict
          </p>
        </div>
        <div className="grid gap-2 sm:grid-cols-2">
          {[
            ["Evidence", "The observed permission change and its time."],
            ["Challenge", "An update may explain the change."],
            ["Verification", "Compare the current and previous state."],
            ["Authority", "You decide whether action is warranted."],
            ["Action", "Review permissions or leave unchanged."],
          ].map(([name, copy]) => (
            <details key={name} className="group border border-border bg-background/55">
              <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between p-3 text-sm font-semibold marker:hidden">
                {name}
                <span className="text-primary transition-transform group-open:rotate-45">+</span>
              </summary>
              <p className="px-3 pb-4 text-sm leading-6 text-muted-foreground">{copy}</p>
            </details>
          ))}
        </div>
      </div>
      <div className="border-t border-border px-5 py-3 text-xs text-muted-foreground">
        Concept interface — not a production screenshot
      </div>
    </div>
  );
}

export function ResearchLink({
  to,
  eyebrow,
  title,
  copy,
}: {
  to: string;
  eyebrow: string;
  title: string;
  copy: string;
}) {
  return (
    <article className="group border-t border-border py-7">
      <p className="text-xs uppercase text-primary">{eyebrow}</p>
      <h3 className="mt-3 font-display text-2xl">{title}</h3>
      <p className="mt-3 max-w-xl text-sm leading-7 text-muted-foreground">{copy}</p>
      <Button asChild variant="link" className="mt-3 px-0 text-primary">
        <Link to={to}>
          Explore <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
        </Link>
      </Button>
    </article>
  );
}

export function GovernancePrinciple() {
  return (
    <div className="flex gap-4 border-l-2 border-gold py-2 pl-5">
      <LockKeyhole className="mt-1 size-5 shrink-0 text-gold" />
      <p className="text-sm leading-7 text-muted-foreground">
        No AI model becomes authoritative evidence merely by saying something. Independent challenge
        and verification inform decisions; people retain authority over consequential action.
      </p>
    </div>
  );
}
