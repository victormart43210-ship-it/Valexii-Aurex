import { createFileRoute, Link } from "@tanstack/react-router";
import { ManuscriptForensicsLab } from "@/components/manuscript-forensics-lab";
import { PageHero, PageShell } from "@/components/site";

export const Route = createFileRoute("/research_/manuscript-forensics")({
  head: () => ({
    meta: [
      { title: "Manuscript forensics laboratory | VALEXII.AI" },
      {
        name: "description",
        content:
          "A feature-gated laboratory for synthetic manuscript images. Enhancements are measurements, not recovered text or a decipherment.",
      },
      { property: "og:title", content: "AUREX manuscript forensics" },
      {
        property: "og:description",
        content: "Synthetic image measurements with provenance. No decipherment is claimed.",
      },
      { property: "og:url", content: "https://valexii.com/research/manuscript-forensics" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/research/manuscript-forensics" }],
  }),
  component: ManuscriptForensicsPage,
});

function ManuscriptForensicsPage() {
  return (
    <PageShell>
      <PageHero eyebrow="Research laboratory · Feature gated" title="Manuscript forensics">
        <p>
          Admit a synthetic scan, keep its digest, and compare reproducible enhancements. A
          brighter residual or a darker component is a pixel measurement. It is not a historical
          fact, and it is not a reading.
        </p>
        <p className="mt-4 text-sm text-muted-foreground">
          <Link to="/research" className="underline underline-offset-4">
            Research
          </Link>
          . Production remains on hold. Financial authority remains none.
        </p>
      </PageHero>
      <section className="section-space" aria-labelledby="forensic-lab-heading">
        <div className="site-grid">
          <h2 id="forensic-lab-heading" className="font-display text-3xl">
            Sources, canvas, and evidence
          </h2>
          <ManuscriptForensicsLab />
        </div>
      </section>
    </PageShell>
  );
}
