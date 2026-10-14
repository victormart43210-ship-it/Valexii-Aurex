import { createFileRoute } from "@tanstack/react-router";
import { CTA, PageHero, PageShell, SectionHeading } from "@/components/site";
export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About VALEXII.AI — independent governed-intelligence research" },
      {
        name: "description",
        content:
          "The origin and cross-domain vision behind VALEXII.AI: developmental, evidence-first governed intelligence for BCXMET, XAELI, DISPATER.AI and research.",
      },
      {
        property: "og:title",
        content: "About VALEXII.AI — independent governed-intelligence research",
      },
      {
        property: "og:description",
        content: "Why VALEXII.AI is developing evidence-first governed intelligence.",
      },
      { property: "og:url", content: "https://valexii.com/about" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/about" }],
  }),
  component: About,
});
function About() {
  return (
    <PageShell>
      <PageHero eyebrow="About · Building VALEXII.AI" title="VALEXII.AI">
        <p>
          Your phone holds conversations, memories and decisions that belong to you. VALEXII.AI
          began with a question: what if security could explain its evidence and leave control where
          it belongs—with people?
        </p>
      </PageHero>
      <section className="section-space">
        <div className="site-grid grid gap-14 lg:grid-cols-2">
          <SectionHeading
            eyebrow="Motivation"
            title="Intelligence should answer to people."
            copy="Privacy is personal. Proof matters. People remain in control. These values guide our work on Android security and evidence-governed AI."
          />
          <div className="space-y-6 text-base leading-8 text-muted-foreground">
            <p>
              BCXMET is our first product focus: Android security under development. XAELI is the
              planned interface for explaining evidence and limits. AUREX explores how to test
              reasoning; DISPATER.AI and XAITA.AI remain separate domain directions.
            </p>
            <p>
              We are building, not claiming a finished portfolio. Demonstrations show ideas, not
              verified protection. Independent review, reproducible tests and honest limits must
              shape what we can responsibly offer.
            </p>
          </div>
        </div>
      </section>
      <CTA
        title="Help make the next question sharper."
        label="Contact VALEXII"
        copy="We welcome research, university testing, commercialization and strategic partnership or acquisition inquiries. Start with the contact form and non-confidential information."
      />
    </PageShell>
  );
}
