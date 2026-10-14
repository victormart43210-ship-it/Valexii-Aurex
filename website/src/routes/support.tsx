import { ValidationPanels } from "@/components/visuals";
import { SupportRoadmap, supportFaq } from "@/components/support-roadmap";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHero, PageShell, SectionHeading } from "@/components/site";
export const Route = createFileRoute("/support")({
  head: () => ({
    meta: [
      { title: "Support Research — VALEXII.AI" },
      {
        name: "description",
        content:
          "Voluntarily support BCXMET research, testing and independent verification. Not a purchase, subscription or license; no access is guaranteed.",
      },
      { property: "og:title", content: "Support Research — VALEXII.AI" },
      {
        property: "og:description",
        content:
          "Support independent research and testing through the existing Cash App link. Contributions guarantee no access or delivery; newsletter signup is not active.",
      },
      { property: "og:url", content: "https://valexii.com/support" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/support" }],
    scripts: [
      {
        type: "application/ld+json",
        children: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "FAQPage",
          mainEntity: supportFaq.map(({ question, answer }) => ({
            "@type": "Question",
            name: question,
            acceptedAnswer: { "@type": "Answer", text: answer },
          })),
        }),
      },
    ],
  }),
  component: Support,
});
function Support() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Independent research / Founding support"
        title="Support the work. Not a promise."
      >
        <p>Help BCXMET move from design toward independently tested capability.</p>
        <p>
          Privacy is personal. Proof matters. People remain in control. Voluntary contributions
          support the careful engineering, research and testing needed to pursue that mission— not a
          claim of finished protection.
        </p>
        <p>
          Suggested founding contribution: $50. Contributions of any amount are welcome. A
          contribution does not guarantee any item, access or outcome.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Button asChild variant="hero" className="min-h-11">
            <a href="https://cash.app/$illuminaughty210" target="_blank" rel="noopener noreferrer">
              Support BCXMET Development <ArrowRight />
            </a>
          </Button>
          <Button asChild variant="glass" className="min-h-11">
            <a href="#support-roadmap-title">
              Review planned access formats <ArrowRight />
            </a>
          </Button>
          <Button asChild variant="glass" className="min-h-11">
            <Link to="/bcxmet" hash="command-center">
              Explore the BCXMET Demonstration <ArrowRight />
            </Link>
          </Button>
        </div>
        <p className="mt-4 text-sm">
          Cash App opens separately; review the recipient before sending. Voluntary support is not a
          purchase, subscription, pre-order or investment, and includes no product access.
        </p>
      </PageHero>
      <SupportRoadmap />
      <section className="section-space border-b border-border">
        <div className="site-grid">
          <ValidationPanels />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid grid gap-14 lg:grid-cols-[1fr_.8fr]">
          <div>
            <SectionHeading eyebrow="Voluntary contribution" title="Make room for careful work." />
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild variant="hero" className="min-h-11">
                <a
                  href="https://cash.app/$illuminaughty210"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Support via Cash App <ArrowRight />
                </a>
              </Button>
              <Button asChild variant="glass" className="min-h-11">
                <Link to="/contact">
                  Ask a question <ArrowRight />
                </Link>
              </Button>
            </div>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              Contribute directly through Cash App. This website does not process payments or
              confirm receipt; review the recipient and amount in Cash App before sending. Any
              amount is welcome. $50 is a suggested founding contribution, not a purchase price, and
              no contribution guarantees any item or access.
            </p>
            <div className="mt-10 border-t border-border pt-8">
              <h2 className="font-display text-2xl">THE DECIPHERMENT FRONTIER</h2>
              <p className="mt-4 text-sm leading-7 text-muted-foreground">
                Three ancient mysteries. One disciplined approach to discovery. The planned free
                weekly research briefing would distinguish hypotheses, reproducible observations,
                failed tests and evidence still required.
              </p>
              <Button asChild variant="glass" className="mt-5 min-h-11">
                <Link to="/decipherment-frontier">
                  Explore the briefing <ArrowRight />
                </Link>
              </Button>
              <p className="mt-3 text-xs leading-6 text-muted-foreground">
                Signup opens only once the mailing service is configured; until then the footer form
                is disabled and no address is collected.
              </p>
            </div>
          </div>
          <div>
            <h2 className="font-display text-2xl">What support could help fund</h2>
            <ul className="mt-6 space-y-4 text-sm leading-7 text-muted-foreground">
              {[
                "Independent validation and physical-device testing",
                "Compute and research infrastructure",
                "Benchmark and evaluation work",
                "Datasets and manuscript research",
                "Accessibility",
                "Reproducible research and open artifacts",
              ].map((x) => (
                <li key={x} className="border-b border-border pb-3">
                  {x}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    </PageShell>
  );
}
