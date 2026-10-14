import { researchBreadcrumb } from "@/components/topic-guide-content";
import { SectionIllustration } from "@/components/section-illustration";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHero, PageShell } from "@/components/site";
import { TopicGuide } from "@/components/topic-guide";
import { linearAFaqs, linearASources } from "@/components/topic-guide-content";

export const Route = createFileRoute("/linear-a")({
  head: () => ({
    meta: [
      { title: "Linear A: Minoan script, research status | VALEXII.AI" },
      {
        name: "description",
        content:
          "What Linear A is, how it relates to Linear B, why the Minoan language remains undeciphered, and VALEXII's evidence-first structural research questions.",
      },
      { property: "og:title", content: "Linear A: Minoan script, research status | VALEXII.AI" },
      {
        property: "og:description",
        content:
          "What Linear A is, how it relates to Linear B, why the Minoan language remains undeciphered, and VALEXII's evidence-first structural research questions.",
      },
      { property: "og:url", content: "https://valexii.com/linear-a" },
      { property: "og:type", content: "article" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/linear-a" }],
    scripts: [researchBreadcrumb("Linear A", "/linear-a")],
  }),
  component: Page,
});

function Page() {
  return (
    <PageShell>
      <PageHero
        eyebrow="VALEXII Research / Linear A · Not deciphered"
        title="Linear A: the undeciphered script of Minoan Crete"
      >
        <p>
          The surviving signs preserve a record, but their language remains unresolved. Explore
          Linear A’s relationship to Linear B, the limits of current interpretation and VALEXII’s
          unverified structural research questions.
        </p>
        <p className="mt-3 text-amber">Research in progress — not a claimed decipherment.</p>
      </PageHero>
      <section className="section-space">
        <div className="site-grid max-w-xl">
          <SectionIllustration subject="linear-a" loading="eager" />
        </div>
      </section>
      <TopicGuide
        id="linear-a-guide"
        eyebrow="Background and research status"
        title="Frequently asked questions"
        faqs={linearAFaqs}
        sources={linearASources}
      />
      <section className="section-space border-t border-border">
        <div className="site-grid flex flex-wrap gap-3">
          <Button asChild variant="glass">
            <Link to="/decipherment">
              All research tracks <ArrowRight />
            </Link>
          </Button>
          <Button asChild variant="glass">
            <Link to="/decipherment-frontier">
              Planned research briefing <ArrowRight />
            </Link>
          </Button>
        </div>
      </section>
    </PageShell>
  );
}
