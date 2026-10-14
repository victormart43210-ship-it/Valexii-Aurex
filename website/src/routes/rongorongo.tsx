import { researchBreadcrumb } from "@/components/topic-guide-content";
import { SectionIllustration } from "@/components/section-illustration";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHero, PageShell } from "@/components/site";
import { TopicGuide } from "@/components/topic-guide";
import { rongorongoFaqs, rongorongoSources } from "@/components/topic-guide-content";

export const Route = createFileRoute("/rongorongo")({
  head: () => ({
    meta: [
      { title: "Rongorongo: Easter Island script, research status | VALEXII.AI" },
      {
        name: "description",
        content:
          "What Rongorongo is, why the Rapa Nui glyphs remain undeciphered, the Mamari calendar debate, and VALEXII's unverified computational hypotheses.",
      },
      {
        property: "og:title",
        content: "Rongorongo: Easter Island script, research status | VALEXII.AI",
      },
      {
        property: "og:description",
        content:
          "What Rongorongo is, why the Rapa Nui glyphs remain undeciphered, the Mamari calendar debate, and VALEXII's unverified computational hypotheses.",
      },
      { property: "og:url", content: "https://valexii.com/rongorongo" },
      { property: "og:type", content: "article" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/rongorongo" }],
    scripts: [researchBreadcrumb("Rongorongo", "/rongorongo")],
  }),
  component: Page,
});

function Page() {
  return (
    <PageShell>
      <PageHero
        eyebrow="VALEXII Research / Rongorongo · Not deciphered"
        title="Rongorongo: the undeciphered glyphs of Rapa Nui"
      >
        <p>
          Carved signs invite a reading; object context and independent evidence must constrain it.
          Explore the surviving record, the Mamari calendar debate and VALEXII’s unverified
          computational research questions.
        </p>
        <p className="mt-3 text-amber">Research in progress — not a claimed decipherment.</p>
      </PageHero>
      <section className="section-space">
        <div className="site-grid max-w-xl">
          <SectionIllustration subject="rongorongo" loading="eager" />
        </div>
      </section>
      <TopicGuide
        id="rongorongo-guide"
        eyebrow="Background and research status"
        title="Frequently asked questions"
        faqs={rongorongoFaqs}
        sources={rongorongoSources}
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
