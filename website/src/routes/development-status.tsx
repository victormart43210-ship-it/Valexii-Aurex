import { createFileRoute, Link } from "@tanstack/react-router";
import { PageHero, PageShell } from "@/components/site";

export const Route = createFileRoute("/development-status")({
  head: () => ({
    meta: [
      { title: "Development status — VALEXII.AI" },
      {
        name: "description",
        content:
          "Engineering status for DISPATER, AUREX-OX, XAELI, and BCXMET. Production is on hold. No live model connection is claimed.",
      },
      { property: "og:title", content: "VALEXII development status" },
      {
        property: "og:description",
        content: "Synthetic engineering status. Production remains on hold and no live model is claimed.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: DevelopmentStatus,
});

const ROWS = [
  ["DISPATER.AI", "Industrial audit and continuous monitoring", "Synthetic audits run in the repository. Confirmed recovery stays 0.00."],
  ["AUREX-OX", "Offline model registry and evaluation laboratory", "Candidates are registered. No weight is installed and no live connection is verified."],
  ["XAELI", "Governed advisory assistant", "Explanations do not approve a recovery or replace the calculation."],
  ["BCXMET / MEDAURUS", "Cybersecurity platform", "Security authority stays separate from AUREX explanations."],
  ["Production", "HOLD", "This page is not a deployment and not a customer-data intake."],
] as const;

function DevelopmentStatus() {
  return (
    <PageShell>
      <PageHero eyebrow="Engineering snapshot / not a live service" title="What is built, and what is not connected.">
        <p>
          The dated machine-readable snapshot lives with the repository commit. This page does not
          invent metrics, and a mocked evaluation is not a live model.
        </p>
      </PageHero>
      <section className="section-space">
        <div className="site-grid">
          <ul className="grid gap-4">
            {ROWS.map(([name, role, note]) => (
              <li key={name} className="border-t border-border pt-4">
                <p className="text-xs text-primary">{role}</p>
                <h2 className="mt-1 font-display text-2xl">{name}</h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">{note}</p>
              </li>
            ))}
          </ul>
          <p className="mt-8 text-sm">
            <Link to="/aurex-ox" className="text-primary">
              Open the AUREX-OX laboratory
            </Link>
          </p>
        </div>
      </section>
    </PageShell>
  );
}
