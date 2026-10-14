import { ReasoningSpine } from "@/components/reasoning-spine";
import { createFileRoute } from "@tanstack/react-router";
import { PageShell, PageHero, ProductCard } from "@/components/site";
export const Route = createFileRoute("/ecosystem")({
  head: () => ({
    meta: [
      { title: "Ecosystem — VALEXII.AI product directions" },
      {
        name: "description",
        content:
          "BCXMET flagship security, XAELI context-first intelligence and future industrial and finance directions under VALEXII.AI.",
      },
      { property: "og:title", content: "VALEXII.AI — One umbrella. Distinct responsibilities." },
      {
        property: "og:description",
        content:
          "Explore active security development and clearly marked future industrial and financial applications.",
      },
      { property: "og:url", content: "https://valexii.com/ecosystem" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/ecosystem" }],
  }),
  component: Ecosystem,
});
function Ecosystem() {
  return (
    <PageShell>
      <PageHero eyebrow="VALEXII.AI ecosystem" title="One umbrella. Distinct responsibilities.">
        <p>
          One company, different questions. BCXMET is Android security under development; XAELI is
          its planned explanation interface. DISPATER.AI and XAITA.AI explore industrial and capital
          intelligence—not available production products.
        </p>
      </PageHero>
      <ReasoningSpine context="ecosystem" />
      <section className="section-space">
        <div className="site-grid grid gap-6 sm:grid-cols-2">
          <ProductCard
            name="BCXMET"
            label="Active development"
            copy="Android security under development. Simulated reviews show evidence, limits and human control."
            to="/bcxmet"
          />
          <ProductCard
            name="XAELI"
            label="Developmental"
            copy="A planned assistant for evidence and uncertainty. Explore scripted explanations, not connected AI."
            to="/xaeli"
          />
          <ProductCard
            name="DISPATER.AI"
            label="Industrial / resource · Future direction"
            copy="Research into bounded operational decision support."
            to="/dispater"
          />
          <ProductCard
            name="XAITA.AI"
            label="Finance / markets · Future direction"
            copy="Qualified market evidence without financial-performance promises."
            to="/xaita"
          />
        </div>
      </section>
    </PageShell>
  );
}
