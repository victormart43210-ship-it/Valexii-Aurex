import { NewsletterSignup } from "@/components/newsletter-signup";
import { Link } from "@tanstack/react-router";
import { ArrowRight, Check, ChevronRight, CircleAlert, Menu, X } from "lucide-react";
import { useState, useRef, useId, type ReactNode, type KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Card, SectionHeader } from "@/components/ui-system";
import { cn } from "@/lib/utils";

export const navItems = [
  ["Home", "/"],
  ["BCXMET", "/bcxmet"],
  ["XAELI", "/xaeli"],
  ["VALEXII System", "/system"],
  ["Research", "/research"],
  ["AUREX", "/aurex"],
  ["Frontier", "/decipherment-frontier"],
  ["About", "/about"],
] as const;

const companyItems = [
  ["About", "/about"],
  ["Security", "/security"],
  ["Privacy", "/privacy"],
  ["Terms", "/terms"],
  ["Contact", "/contact"],
  ["Support", "/support"],
] as const;

export function Header() {
  const [open, setOpen] = useState(false);
  const toggle = useRef<HTMLButtonElement>(null);
  return (
    <header
      onKeyDown={(e) => {
        if (e.key === "Escape") {
          setOpen(false);
          toggle.current?.focus();
        }
      }}
      className="site-header fixed inset-x-0 top-0 z-50 border-b border-border/70 bg-background/85 backdrop-blur-xl"
    >
      <a
        href="#main-content"
        className="absolute left-4 top-2 z-[60] -translate-y-20 rounded-sm bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground focus:translate-y-0"
      >
        Skip to content
      </a>
      <div className="header-inner site-grid grid h-20 grid-cols-[minmax(0,1fr)_auto] items-center gap-3 xl:flex xl:justify-between">
        <Link
          to="/"
          className="group flex min-h-11 min-w-0 items-center gap-3"
          aria-label="VALEXII.AI home"
        >
          <BrandMark />
          <span className="font-display text-lg font-semibold tracking-[0.12em] text-foreground">
            VALEXII<span className="text-primary">.AI</span>
          </span>
        </Link>
        <nav aria-label="Primary navigation" className="hidden items-center gap-4 xl:gap-7 xl:flex">
          {navItems.map(([label, to]) => (
            <Link
              key={to}
              to={to}
              className="flex min-h-11 items-center text-sm font-semibold uppercase text-muted-foreground transition-colors hover:text-foreground"
              activeOptions={{ exact: true }}
              activeProps={{ className: "text-primary" }}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="hidden xl:block">
          <Button asChild variant="glass">
            <Link to="/support">
              Support research <ArrowRight />
            </Link>
          </Button>
        </div>
        <Button
          variant="ghost"
          size="icon"
          aria-label={open ? "Close navigation" : "Open navigation"}
          aria-expanded={open}
          aria-controls="mobile-navigation"
          ref={toggle}
          onClick={() => setOpen(!open)}
          className="min-h-11 min-w-11 xl:hidden"
        >
          {open ? <X /> : <Menu />}
        </Button>
      </div>
      {open && (
        <nav
          id="mobile-navigation"
          aria-label="Mobile navigation"
          className="max-h-[calc(100dvh-5rem)] overflow-y-auto border-t border-border bg-background xl:hidden"
        >
          <div className="site-grid grid py-4">
            {[
              ...navItems,
              ["Build with us", "/build-with-us"],
              ["Contact", "/contact"],
              ["Support", "/support"],
            ].map(([label, to]) => (
              <Link
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className="flex min-h-12 items-center justify-between border-b border-border/60 text-sm font-semibold text-foreground"
              >
                {label}
                <ChevronRight className="size-4 text-primary" />
              </Link>
            ))}
          </div>
        </nav>
      )}
    </header>
  );
}

function BrandMark() {
  return (
    <span
      aria-hidden="true"
      className="relative grid size-9 shrink-0 place-items-center rounded-full border border-primary/45"
    >
      <span className="absolute inset-1 rounded-full border border-primary/25" />
      <span className="absolute left-0 top-4 h-px w-5 -rotate-35 bg-primary" />
      <span className="ml-2 size-2 rotate-45 border border-gold bg-primary" />
    </span>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-border bg-card/35">
      <div className="site-grid pt-14">
        <NewsletterSignup compact />
      </div>
      <div className="site-grid grid gap-12 py-14 md:grid-cols-[1.4fr_1fr_1fr]">
        <div>
          <div className="flex items-center gap-3">
            <BrandMark />
            <span className="font-display tracking-[0.12em]">VALEXII.AI</span>
          </div>
          <p className="mt-5 max-w-sm text-sm leading-7 text-muted-foreground">
            Building privacy-centered Android security and evidence-governed AI. Privacy is
            personal. Proof matters. People remain in control.
          </p>
          <p className="mt-5 text-xs text-gold">BCXMET · BCXME THE CHANGE</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">Explore</p>
          <div className="mt-4 grid gap-3 text-sm">
            {[...navItems, ["Build with us", "/build-with-us"]].map(([l, t]) => (
              <Link
                key={l}
                to={t}
                className="flex min-h-9 items-center text-muted-foreground hover:text-foreground"
              >
                {l}
              </Link>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">Company</p>
          <div className="mt-4 grid gap-3 text-sm">
            {companyItems.map(([l, t]) => (
              <Link
                key={l}
                to={t}
                className="flex min-h-11 items-center text-muted-foreground hover:text-foreground"
              >
                {l}
              </Link>
            ))}
          </div>
          <p className="mt-5 text-xs text-muted-foreground">
            BCXMET · Powered by VALEXII.AI · BCXME THE CHANGE
          </p>
        </div>
      </div>
      <div className="border-t border-border">
        <div className="site-grid flex flex-col gap-2 py-6 text-xs text-muted-foreground sm:flex-row sm:justify-between">
          <span>© 2026 VALEXII.AI. Public research and development website.</span>
          <span>In development. Human control by design.</span>
        </div>
      </div>
    </footer>
  );
}

export function PageShell({ children }: { children: ReactNode }) {
  return (
    <>
      <Header />
      <main id="main-content" className="site-main min-h-dvh pt-20">
        {children}
      </main>
      <Footer />
    </>
  );
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return (
    <div className="ui-eyebrow">
      <span aria-hidden="true" />
      {children}
    </div>
  );
}

export interface PageHeroProps {
  eyebrow: string;
  title: string;
  children: ReactNode;
  visual?: ReactNode;
}

export function PageHero({ eyebrow, title, children, visual }: PageHeroProps) {
  return (
    <section className="relative overflow-hidden border-b border-border technical-grid">
      <div className="absolute inset-0 radial-field" />
      <div
        className={cn(
          "site-grid relative grid min-h-[min(680px,72dvh)] items-center gap-12 py-16",
          visual && "lg:grid-cols-[1.08fr_.92fr]",
        )}
      >
        <div className="min-w-0">
          <Eyebrow>{eyebrow}</Eyebrow>
          <h1 className="max-w-4xl font-display text-4xl font-medium leading-[1.08] tracking-[0.04em] text-balance sm:text-6xl lg:text-7xl">
            {title}
          </h1>
          <div className="mt-7 max-w-2xl text-base leading-8 text-muted-foreground sm:text-lg">
            {children}
          </div>
        </div>
        {visual && <div className="relative mx-auto w-full max-w-xl">{visual}</div>}
      </div>
    </section>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  copy,
}: {
  eyebrow: string;
  title: string;
  copy?: string;
}) {
  return <SectionHeader eyebrow={eyebrow} title={title} copy={copy} />;
}

export function FeatheredEyeVisual({
  compact = false,
  label = "Governed observation visual",
}: {
  compact?: boolean;
  label?: string;
}) {
  const rays = Array.from({ length: 20 });
  return (
    <figure
      className={cn(
        "relative mx-auto aspect-square w-full max-w-[620px]",
        compact && "max-w-[420px]",
      )}
      aria-label={label}
      role="img"
    >
      <svg viewBox="0 0 600 600" className="size-full overflow-visible" aria-hidden="true">
        <defs>
          <radialGradient id="iris">
            <stop offset="0" stopColor="var(--foreground)" />
            <stop offset=".22" stopColor="var(--cyan)" />
            <stop offset=".65" stopColor="var(--teal)" stopOpacity=".4" />
            <stop offset="1" stopColor="var(--background)" stopOpacity="0" />
          </radialGradient>
        </defs>
        <g fill="none" stroke="var(--primary)">
          <circle cx="300" cy="300" r="244" opacity=".12" />
          <circle cx="300" cy="300" r="205" opacity=".25" strokeDasharray="2 12" />
          <circle cx="300" cy="300" r="166" opacity=".18" />
        </g>
        <g className="motion-orbit">
          {rays.map((_, i) => (
            <line
              key={i}
              x1="300"
              y1="43"
              x2="300"
              y2={i % 5 === 0 ? "68" : "58"}
              stroke={i % 5 === 0 ? "var(--gold)" : "var(--primary)"}
              opacity={i % 5 === 0 ? ".75" : ".32"}
              transform={`rotate(${i * 18} 300 300)`}
            />
          ))}
        </g>
        <path
          d="M88 300 Q180 205 300 244 Q420 205 512 300 Q420 395 300 356 Q180 395 88 300Z"
          fill="var(--card)"
          stroke="var(--primary)"
          strokeWidth="2"
        />
        <g opacity=".65" fill="none" stroke="var(--primary)">
          <path d="M105 279 Q173 180 275 218" />
          <path d="M105 321 Q173 420 275 382" />
          <path d="M495 279 Q427 180 325 218" />
          <path d="M495 321 Q427 420 325 382" />
        </g>
        <g fill="var(--primary)" opacity=".18">
          {[0, 1, 2, 3].map((i) => (
            <path
              key={i}
              d={`M${118 + i * 30} ${262 - i * 10} Q${170 + i * 27} ${190 - i * 4} ${264 + i * 8} 230 Q${188 + i * 22} ${230 - i * 2} ${118 + i * 30} ${262 - i * 10}Z`}
            />
          ))}
          {[0, 1, 2, 3].map((i) => (
            <path
              key={i}
              d={`M${482 - i * 30} ${338 + i * 10} Q${430 - i * 27} ${410 + i * 4} ${336 - i * 8} 370 Q${412 - i * 22} ${370 + i * 2} ${482 - i * 30} ${338 + i * 10}Z`}
            />
          ))}
        </g>
        <circle cx="300" cy="300" r="91" fill="url(#iris)" className="motion-pulse" />
        <circle
          cx="300"
          cy="300"
          r="45"
          fill="var(--background)"
          stroke="var(--gold)"
          strokeWidth="1.5"
        />
        <circle cx="300" cy="300" r="20" fill="var(--foreground)" />
        <circle cx="289" cy="289" r="5" fill="var(--primary)" />
        <path
          d="M300 108 A192 192 0 0 1 492 300"
          fill="none"
          stroke="var(--gold)"
          strokeWidth="2"
          opacity=".65"
        />
      </svg>
    </figure>
  );
}

export const flowSteps = [
  {
    name: "Evidence",
    short: "What was observed.",
    detail:
      "Provenance-bearing observations retain their source, timing, scope and limits. They are not conclusions.",
  },
  {
    name: "Qualification",
    short: "Can it be relied on?",
    detail:
      "Admissibility requires relevant, permitted and fresh evidence. Missing, stale or unverified evidence never counts as PASS.",
  },
  {
    name: "Reality",
    short: "What can be concluded.",
    detail:
      "Measured observations stay separate from hypotheses. Advocate, Challenger and Arbiter checks require independent witnesses; role agreement is not proof.",
  },
  {
    name: "Authority",
    short: "What is permitted.",
    detail:
      "Check current domain permissions, freshness, time-limited authorization lease and revocation before effect. Historical evidence is not present authorization.",
  },
  {
    name: "Effect",
    short: "What actually happens.",
    detail:
      "Only authorized bounded effects may proceed. Record the outcome separately and seek independent support; this website performs no security action.",
  },
] as const;

export function GovernedIntelligenceFlow() {
  const [active, setActive] = useState(0);
  const id = useId();
  const item = flowSteps[active] ?? flowSteps[0];
  function selectStep(index: number) {
    setActive(index);
    document.getElementById(`${id}-flow-tab-${index}`)?.focus();
  }
  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      event.preventDefault();
      selectStep((active + 1) % flowSteps.length);
    }
    if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      event.preventDefault();
      selectStep((active - 1 + flowSteps.length) % flowSteps.length);
    }
    if (event.key === "Home") {
      event.preventDefault();
      selectStep(0);
    }
    if (event.key === "End") {
      event.preventDefault();
      selectStep(flowSteps.length - 1);
    }
  }
  return (
    <div className="mt-12 grid gap-8 lg:grid-cols-[1.25fr_.75fr]">
      <div
        className="grid gap-px overflow-hidden rounded-md border border-border bg-border sm:grid-cols-5"
        role="tablist"
        aria-label="Governed intelligence stages"
        onKeyDown={handleKeyDown}
      >
        {flowSteps.map((step, i) => (
          <Button
            key={step.name}
            variant="ghost"
            role="tab"
            aria-selected={active === i}
            aria-controls={`${id}-flow-panel`}
            id={`${id}-flow-tab-${i}`}
            tabIndex={active === i ? 0 : -1}
            onClick={() => setActive(i)}
            className={cn(
              "h-auto min-h-28 items-start justify-start rounded-none bg-card p-4 text-left whitespace-normal transition-colors focus-visible:z-10",
              active === i ? "bg-accent" : "hover:bg-muted",
            )}
          >
            <span className="flex flex-col">
              <span className="text-xs tabular-nums text-primary">0{i + 1}</span>
              <span className="mt-3 block text-sm font-semibold text-foreground">{step.name}</span>
              <span className="mt-2 block text-xs leading-5 text-muted-foreground">
                {step.short}
              </span>
            </span>
          </Button>
        ))}
      </div>
      <div
        id={`${id}-flow-panel`}
        role="tabpanel"
        aria-labelledby={`${id}-flow-tab-${active}`}
        className="relative border-l border-gold/60 py-3 pl-7"
      >
        <span className="text-xs font-semibold uppercase tracking-[0.16em] text-gold">
          Stage {active + 1} of 5
        </span>
        <h3 className="mt-3 font-display text-2xl tracking-[0.04em]">{item.name}</h3>
        <p className="mt-4 leading-7 text-muted-foreground">{item.detail}</p>
      </div>
    </div>
  );
}

export function ProductCard({
  name,
  label,
  copy,
  to,
  accent = "primary",
}: {
  name: string;
  label: string;
  copy: string;
  to: string;
  accent?: "primary" | "sense" | "analyze" | "amber";
}) {
  return (
    <Card
      padding="roomy"
      className="group relative overflow-hidden transition-colors hover:border-primary/60"
    >
      <div
        className={cn(
          "absolute inset-x-0 top-0 h-px",
          accent === "sense"
            ? "bg-sense"
            : accent === "analyze"
              ? "bg-analyze"
              : accent === "amber"
                ? "bg-amber"
                : "bg-primary",
        )}
      />
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        {label}
      </p>
      <h3 className="mt-4 font-display text-2xl tracking-[0.05em]">{name}</h3>
      <p className="mt-4 text-sm leading-7 text-muted-foreground">{copy}</p>
      <Link
        to={to}
        aria-label={`Explore ${name}`}
        className="mt-6 inline-flex min-h-11 items-center gap-2 text-sm font-semibold text-primary"
      >
        Explore <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
      </Link>
    </Card>
  );
}

export function ConceptLabel() {
  return (
    <div className="inline-flex max-w-full items-center gap-2 whitespace-normal rounded-sm border border-gold/40 bg-gold/10 px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-gold">
      <CircleAlert className="size-3.5 shrink-0" />
      Concept interface — not a production screenshot
    </div>
  );
}

export function StateIndicator({
  label,
  tone = "primary",
}: {
  label: string;
  tone?: "primary" | "sense" | "analyze" | "amber";
}) {
  return (
    <span className="inline-flex items-center gap-2 text-xs font-semibold text-foreground">
      <span
        className={cn(
          "size-2 rounded-full bg-primary ring-4 ring-primary/10",
          tone === "sense" && "bg-sense ring-sense/10",
          tone === "analyze" && "bg-analyze ring-analyze/10",
          tone === "amber" && "bg-amber ring-amber/10",
        )}
      />
      {label}
    </span>
  );
}

export function ModeCard({
  name,
  premise,
  children,
  tone,
}: {
  name: string;
  premise: string;
  children: ReactNode;
  tone: "primary" | "sense" | "analyze";
}) {
  return (
    <Card padding="roomy">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4">
        <StateIndicator label={name} tone={tone} />
        <span className="text-xs uppercase tracking-[0.14em] text-muted-foreground">Mode</span>
      </div>
      <h3 className="mt-7 font-display text-2xl tracking-[0.04em]">{premise}</h3>
      <div className="mt-4 text-sm leading-7 text-muted-foreground">{children}</div>
    </Card>
  );
}

export { ProductComposition as BCXMETInterface } from "@/components/visuals";

export function TwinView() {
  return (
    <div className="rounded-md border border-border bg-card p-5 sm:p-7">
      <ConceptLabel />
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-sm border border-primary/40 bg-primary/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
            What I see
          </p>
          <h3 className="mt-4 text-lg font-semibold">A change worth reviewing</h3>
          <p className="mt-3 text-sm leading-7 text-muted-foreground">
            The strongest evidence-supported interpretation, presented with the observations behind
            it.
          </p>
          <div className="mt-5 space-y-3">
            {[
              "Recent system change",
              "Freshness requires verification",
              "Scope appears limited",
            ].map((x) => (
              <div className="flex items-center gap-3 text-sm" key={x}>
                <Check className="size-4 text-primary" />
                {x}
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-sm border border-gold/35 bg-gold/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-gold">
            What I’d check
          </p>
          <h3 className="mt-4 text-lg font-semibold">Context before action</h3>
          <p className="mt-3 text-sm leading-7 text-muted-foreground">
            A challenge view that surfaces alternate explanations, uncertainty, and missing
            evidence.
          </p>
          <div className="mt-5 space-y-3 text-sm text-muted-foreground">
            <p>• Confirm whether the change was intentional.</p>
            <p>• Compare with the prior trusted state.</p>
            <p>• Keep action subject to human approval.</p>
          </div>
        </div>
      </div>
      <p className="mt-5 text-xs leading-6 text-muted-foreground">
        Scripted examples of two views in the same planned XAELI interface. Neither acts
        independently; no connected AI response is shown.
      </p>
    </div>
  );
}

export function IndustrialPanel() {
  return (
    <div className="rounded-md border border-steel/50 bg-card p-5">
      <ConceptLabel />
      <div className="mt-6 grid gap-4 sm:grid-cols-[1fr_1.4fr]">
        <div className="space-y-3">
          {["FIELD NODE 04", "SENSOR GROUP B", "OPERATIONS DESK"].map((x, i) => (
            <div className="rounded-sm border border-border bg-background p-4" key={x}>
              <span className="text-[10px] tracking-[0.16em] text-muted-foreground">{x}</span>
              <div className="mt-3">
                <StateIndicator
                  label={i === 1 ? "Review needed" : "Signal present"}
                  tone={i === 1 ? "amber" : "primary"}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="relative min-h-64 overflow-hidden rounded-sm border border-border bg-background technical-grid">
          <div className="absolute inset-0 radial-field" />
          <svg
            viewBox="0 0 400 260"
            className="relative size-full"
            aria-label="Concept telemetry visualization"
            role="img"
          >
            <polyline
              points="0,190 48,180 78,120 112,156 150,92 185,118 230,68 272,135 320,98 400,110"
              fill="none"
              stroke="var(--primary)"
              strokeWidth="2"
            />
            <polyline
              points="0,220 70,212 130,190 182,204 245,160 300,175 400,145"
              fill="none"
              stroke="var(--amber)"
              strokeWidth="1"
              opacity=".7"
            />
          </svg>
        </div>
      </div>
    </div>
  );
}

export function CTA({
  title,
  copy,
  label = "Start a conversation",
}: {
  title: string;
  copy: string;
  label?: string;
}) {
  return (
    <section className="border-y border-border bg-card/35">
      <div className="site-grid flex flex-col items-start justify-between gap-8 py-16 lg:flex-row lg:items-center">
        <div>
          <h2 className="font-display text-3xl tracking-[0.035em] text-balance sm:text-4xl">
            {title}
          </h2>
          <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">{copy}</p>
        </div>
        <Button asChild variant="hero" size="lg">
          <Link to="/contact">
            {label}
            <ArrowRight />
          </Link>
        </Button>
      </div>
    </section>
  );
}

export function LegalLayout({
  label,
  title,
  updated,
  children,
}: {
  label: string;
  title: string;
  updated: string;
  children: ReactNode;
}) {
  return (
    <>
      <PageHero eyebrow={label} title={title}>
        <p>Draft / subject to legal review</p>
        <p className="mt-2 text-sm">Last revised for public-site review: {updated}</p>
      </PageHero>
      <section className="section-space">
        <div className="site-grid grid gap-12 lg:grid-cols-[220px_1fr]">
          <div>
            <div className="sticky top-28 rounded-sm border border-gold/35 bg-gold/5 p-4 text-sm leading-6 text-gold">
              This page is structural draft copy. It does not create finalized legal commitments.
            </div>
          </div>
          <article className="max-w-3xl space-y-10 text-sm leading-7 text-muted-foreground">
            {children}
          </article>
        </div>
      </section>
    </>
  );
}

export function LegalSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h2 className="font-display text-2xl tracking-[0.035em] text-foreground">{title}</h2>
      <div className="mt-4 space-y-4">{children}</div>
    </section>
  );
}

export function EvidenceCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-sm border border-border bg-card p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-primary">{title}</p>
      <div className="mt-3 text-sm leading-7 text-muted-foreground">{children}</div>
    </div>
  );
}

export function ResearchBlock({
  number,
  title,
  children,
}: {
  number: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <article className="border-t border-border py-8 sm:grid sm:grid-cols-[100px_1fr] sm:gap-8">
      <span className="font-display text-2xl text-primary">{number}</span>
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-muted-foreground">{children}</p>
      </div>
    </article>
  );
}
