import { ReasoningSpine } from "@/components/reasoning-spine";
import xaitaHero from "../../public/assets/xaita-hero.jpg.asset.json";
import { createFileRoute } from "@tanstack/react-router";
import { CTA, PageHero, PageShell, SectionHeading } from "@/components/site";
import { DomainReasoning } from "@/components/domain-reasoning";
export const Route = createFileRoute("/xaita")({
  head: () => ({
    meta: [
      { title: "XAITA.AI — Future Capital Intelligence | VALEXII.AI" },
      {
        name: "description",
        content:
          "XAITA.AI explores future evidence-governed capital intelligence: observing, interpreting, verifying and explaining. Not live trading; functionality unverified.",
      },
      { property: "og:title", content: "XAITA.AI — Future Capital Intelligence" },
      {
        property: "og:description",
        content:
          "Developmental capital intelligence with explicit evidence and authority boundaries. No live trading or verified financial performance.",
      },
      { property: "og:url", content: "https://valexii.com/xaita" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/xaita" }],
  }),
  component: Xaita,
});
function Xaita() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Future / Evidence-governed capital intelligence"
        title="XAITA.AI"
        visual={
          <figure>
            <img
              src={xaitaHero.url}
              alt="XAITA.AI artwork: celestial goddess in white and gold among orbital rings, holding a luminous globe amid marble columns."
              width={768}
              height={788}
              fetchPriority="high"
              decoding="async"
              className="mx-auto w-full max-w-md rounded-2xl"
            />
            <figcaption className="mt-2 text-center text-xs text-muted-foreground">
              Conceptual artwork — not a trading interface or market data.
            </figcaption>
          </figure>
        }
      >
        <p>
          A market signal can inform a decision without making it for you. XAITA.AI explores future
          capital intelligence: observing, interpreting, verifying and explaining information with
          uncertainty intact. Not a live trading service or financial advice.
        </p>
      </PageHero>
      <ReasoningSpine context="xaita" />
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Developmental / Unverified functionality"
            title="Signals are not decisions."
            copy="The research question is how to keep sources, contradictory signals and assumptions visible when money is at stake. Human judgment remains separate from a model’s interpretation."
          />
          <p className="mt-6 max-w-3xl leading-7 text-muted-foreground">
            Private repositories exist, as reported by the project owner; their functionality has
            not been independently verified. XAITA is a future system direction—not a deployed
            trading engine, investment adviser, custody service or evidence of returns.
          </p>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              [
                "Observe",
                "Preserve source, timing and context of information; no live market feed is claimed here.",
              ],
              [
                "Interpret",
                "Explore competing explanations and expose assumptions instead of treating a signal as a decision.",
              ],
              [
                "Verify",
                "Seek independent support, challenge contradictions and abstain when evidence is incomplete.",
              ],
              [
                "Explain",
                "Make provenance, limitations and bounded authority readable; explanation does not authorize a trade.",
              ],
            ].map(([title, copy]) => (
              <article key={title} className="border-t border-border pt-6">
                <h3 className="font-display text-xl">{title}</h3>
                <p className="mt-4 leading-7 text-muted-foreground">{copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
      <DomainReasoning />
      <CTA
        title="Explore the question, not a promise of returns."
        copy="We welcome research-oriented conversations, without implying product availability or financial performance."
      />
    </PageShell>
  );
}
