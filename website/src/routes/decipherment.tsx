import { ResearchGraphic } from "@/components/visuals";
import { SectionIllustration } from "@/components/section-illustration";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHero, PageShell, SectionHeading } from "@/components/site";
export const Route = createFileRoute("/decipherment")({
  head: () => ({
    meta: [
      { title: "VALEXII Research — Research Tracks | VALEXII.AI" },
      {
        name: "description",
        content:
          "Voynich, Linear A, and Rongorongo research directions with milestones and explicit uncertainty. No verified translations.",
      },
      { property: "og:title", content: "VALEXII Research — VALEXII.AI" },
      {
        property: "og:description",
        content:
          "Testable structures, held-out predictions, and independent replication across three research tracks.",
      },
      { property: "og:url", content: "https://valexii.com/decipherment" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/decipherment" }],
  }),
  component: Decipherment,
});
const tracks = [
  {
    name: "Voynich",
    status: "ACTIVE / HOLD",
    copy: "Compare transcriptions, boundaries and local patterns against matched random baselines. No semantic decipherment.",
    to: "/voynich" as const,
  },
  {
    name: "Linear A",
    status: "RESEARCH / NOT ESTABLISHED",
    copy: "Build reliable corpora and test structural hypotheses. Specific findings need attached evidence before public promotion.",
    to: "/linear-a" as const,
  },
  {
    name: "Rongorongo",
    status: "RESEARCH / NOT ESTABLISHED",
    copy: "Study object context and 3D records, test Mamari lunar-calendar alignment, and check fixed values on held-out material. No verified translation.",
    to: "/rongorongo" as const,
  },
];
function Decipherment() {
  return (
    <PageShell>
      <PageHero
        eyebrow="VALEXII Research / Manuscript tracks"
        title="Ancient scripts. Open questions."
      >
        <p>
          A plausible reading can be captivating—and wrong. We begin with reliable records, testable
          patterns and rival explanations. No track below has a verified semantic decipherment.
        </p>
      </PageHero>
      <section className="section-space border-b border-border">
        <div className="site-grid">
          <ResearchGraphic />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Current tracks"
            title="Milestones, not a completion percentage."
          />
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {tracks.map(({ name, status, copy, to }) => (
              <article key={name} className="border-t border-primary/50 py-6">
                <SectionIllustration
                  subject={
                    name === "Voynich" ? "voynich" : name === "Linear A" ? "linear-a" : "rongorongo"
                  }
                />
                <span className="text-xs uppercase text-gold">{status}</span>
                <h2 className="mt-5 font-display text-3xl">{name}</h2>
                <p className="mt-5 text-sm leading-7 text-muted-foreground">{copy}</p>
                <Button asChild variant="link" className="px-0 text-primary">
                  <Link to={to}>
                    Explore <ArrowRight />
                  </Link>
                </Button>
              </article>
            ))}
          </div>
          <p className="mt-10 border-l-2 border-gold pl-5 text-sm leading-7 text-muted-foreground">
            Held-out semantic prediction, continuous decoding, reverse reconstruction, and
            independent replication remain required before any translation claim.
          </p>
        </div>
      </section>
    </PageShell>
  );
}
