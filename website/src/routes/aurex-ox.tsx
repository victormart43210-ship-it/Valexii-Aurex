import { createFileRoute, Link } from "@tanstack/react-router";
import { PageHero, PageShell } from "@/components/site";
import { AurexOxStatus } from "@/components/aurex-ox-status";

export const Route = createFileRoute("/aurex-ox")({
  head: () => ({
    meta: [
      { title: "AUREX-OX — Model laboratory | VALEXII.AI" },
      {
        name: "description",
        content:
          "AUREX-OX is the offline laboratory for model registration, evaluation, and synthetic customization. Production is on hold.",
      },
      { property: "og:title", content: "AUREX-OX model laboratory" },
      {
        property: "og:description",
        content: "Offline model registration and evaluation. No live connection and no production release.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: AurexOx,
});

function AurexOx() {
  return (
    <PageShell>
      <PageHero eyebrow="AUREX-OX / sovereign laboratory" title="Test models before they are allowed to speak for the audit.">
        <p>
          The laboratory registers candidates, scores them on frozen synthetic fixtures, and keeps
          training and paid inference off. A model cannot approve its own result or a financial
          recovery.
        </p>
      </PageHero>
      <AurexOxStatus context="public" />
      <section className="section-space">
        <div className="site-grid">
          <p className="text-sm">
            <Link to="/aurex-ox/model-laboratory" className="text-primary">
              View the offline model registry
            </Link>
          </p>
        </div>
      </section>
    </PageShell>
  );
}
