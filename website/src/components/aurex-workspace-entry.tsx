import { Link } from "@tanstack/react-router";
import { ArrowUpRight, FlaskConical, GitBranch, LockKeyhole, ShieldCheck } from "lucide-react";

const pillars = [
  {
    icon: FlaskConical,
    title: "Research",
    copy: "Define a question, compare explanations, and preserve what is still unknown.",
  },
  {
    icon: ShieldCheck,
    title: "Evidence",
    copy: "Trace sources, challenge claims, and separate observations from authority.",
  },
  {
    icon: GitBranch,
    title: "Evaluation",
    copy: "Design repeatable model tests with explicit budgets, limitations, and abstention.",
  },
] as const;

/** Public, browser-safe entry point. Never fetches private data or implies a live service. */
export function AurexWorkspaceEntry() {
  return (
    <section
      aria-labelledby="aurex-workspace-heading"
      className="border-b border-border py-12 md:py-16"
      data-testid="aurex-workspace-entry"
    >
      <div className="site-grid">
        <div className="relative overflow-hidden rounded-xl border border-primary/25 bg-gradient-to-br from-primary/10 via-background to-background p-6 md:p-10">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -right-16 -top-24 size-72 rounded-full border border-primary/20 opacity-50"
          />
          <div className="relative">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-primary">
              VALEXII / AUREX OX · Workspace
            </p>
            <h2
              id="aurex-workspace-heading"
              className="mt-4 max-w-3xl font-display text-3xl leading-tight md:text-5xl"
            >
              Ask harder questions. Demand better evidence.
            </h2>
            <p className="mt-5 max-w-2xl text-sm leading-7 text-muted-foreground md:text-base">
              AUREX is an experimental research and reasoning-evaluation environment. Explore the
              methodology here; private experiments, model execution, and backend operations are not
              exposed to visitors.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <a
                href="#aurex-workspace-methods"
                className="inline-flex min-h-11 items-center gap-2 rounded-md bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                Explore the workspace <ArrowUpRight aria-hidden="true" className="size-4" />
              </a>
              <Link
                to="/admin/aurex-control"
                className="inline-flex min-h-11 items-center gap-2 rounded-md border border-border px-5 py-3 text-sm font-medium hover:border-primary/60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                <LockKeyhole aria-hidden="true" className="size-4" /> Owner console
              </Link>
            </div>
            <p role="status" className="mt-5 text-xs leading-6 text-amber">
              PUBLIC VIEW · Illustrative methodology only · Hosted AUREX service not verified as
              connected
            </p>
          </div>
        </div>
        <div id="aurex-workspace-methods" className="mt-7 grid scroll-mt-24 gap-4 md:grid-cols-3">
          {pillars.map(({ icon: Icon, title, copy }) => (
            <article key={title} className="rounded-lg border border-border bg-background/60 p-6">
              <Icon className="size-6 text-primary" aria-hidden="true" />
              <h3 className="mt-4 font-display text-xl">{title}</h3>
              <p className="mt-2 text-sm leading-7 text-muted-foreground">{copy}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
