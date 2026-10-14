import { ReasoningSpine } from "@/components/reasoning-spine";
import { ProductComposition } from "@/components/visuals";
import { PresentationOrb } from "@/components/presentation-orb";
import portrait from "../../public/assets/xaeli-editorial-portrait.jpg.asset.json";
import { createFileRoute } from "@tanstack/react-router";
import {
  CTA,
  EvidenceCard,
  PageHero,
  PageShell,
  SectionHeading,
  TwinView,
} from "@/components/site";
export const Route = createFileRoute("/xaeli")({
  head: () => ({
    meta: [
      { title: "XAELI — Evidence-aware assistant in development | VALEXII.AI" },
      {
        name: "description",
        content:
          "XAELI is a planned evidence-aware assistant for BCXMET. Explore scripted explanations, uncertainty and human review—not a connected AI security service.",
      },
      { property: "og:title", content: "XAELI — Governed intelligence for people" },
      {
        property: "og:description",
        content:
          "A planned BCXMET assistant that makes evidence and limits understandable. Website examples are scripted; human control remains the design boundary.",
      },
      { property: "og:url", content: "https://valexii.com/xaeli" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/xaeli" }],
  }),
  component: Xaeli,
});
function Xaeli() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Assistant interface · In development"
        title="XAELI"
        visual={<PresentationOrb state="REST" />}
      >
        <p>
          A useful assistant should help you understand—not ask you to surrender judgment. XAELI is
          being developed to explain evidence, uncertainty and options in BCXMET. The website shows
          scripted examples, not a connected AI assistant.
        </p>
      </PageHero>
      <ReasoningSpine context="xaeli" />
      <section className="section-space" aria-labelledby="meet-xaeli">
        <div className="site-grid grid items-center gap-12 lg:grid-cols-2">
          <div>
            <p className="text-xs text-gold">EDITORIAL · ARTISTIC PERSONIFICATION</p>
            <h2 id="meet-xaeli" className="mt-4 font-display text-3xl">
              Meet XAELI
            </h2>
            <p className="mt-6 leading-7 text-muted-foreground">
              The planned assistant would explain evidence, uncertainty and options for human
              review. Inside the Android concept and phone simulator, XAELI remains an abstract
              luminous Orb—not a human avatar.
            </p>
            <p className="mt-4 leading-7 text-muted-foreground">
              This original blue-and-gold regal portrait is an artistic personification, not the
              Android assistant’s actual appearance. Presentation has no return edge to security
              authority.
            </p>
          </div>
          <figure className="xaeli-editorial-portrait">
            <img
              src={portrait.url}
              width={709}
              height={1536}
              loading="lazy"
              decoding="async"
              alt="User-supplied XAELI artistic personification: a silver-blue woman with a gold crown, cyan jewels and a celestial halo."
            />
            <figcaption className="mt-4 text-center text-xs leading-6 text-muted-foreground">
              XAELI · Original user-supplied editorial artwork. Artistic personification only—not
              the Android assistant avatar or app UI.
            </figcaption>
          </figure>
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid grid items-center gap-12 lg:grid-cols-2">
          <SectionHeading
            eyebrow="Context first · Design intent"
            title="Explain it. Show proof. Help me review it."
            copy="Explore a synthetic permission-change example. XAELI separates an observation from an interpretation, keeps missing evidence visible and leaves consequential action with you."
          />
          <ProductComposition initialView="XAELI" expandedDetails />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="One interface"
            title="An explanation that keeps its limits visible."
          />
          <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <EvidenceCard title="Observed">What the available evidence shows.</EvidenceCard>
            <EvidenceCard title="Known">What can be supported now.</EvidenceCard>
            <EvidenceCard title="Uncertain">What remains incomplete or ambiguous.</EvidenceCard>
            <EvidenceCard title="Reasoning">
              A concise summary of the evidence and assumptions—not private chain-of-thought.
            </EvidenceCard>
            <EvidenceCard title="Next">What bounded action could be reviewed next.</EvidenceCard>
          </div>
        </div>
      </section>
      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid grid gap-12 lg:grid-cols-[.75fr_1.25fr]">
          <SectionHeading
            eyebrow="Twin View"
            title="Interpretation and challenge, side by side."
            copy="The design puts a supported interpretation beside a challenge to it. Both website views are authored examples from the same interface; two views do not establish independence."
          />
          <TwinView />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid grid gap-10 md:grid-cols-3">
          <div>
            <p className="font-display text-2xl">Calm</p>
            <p className="mt-4 leading-7 text-muted-foreground">
              The design prioritizes what matters without manufacturing urgency.
            </p>
          </div>
          <div>
            <p className="font-display text-2xl">Grounded</p>
            <p className="mt-4 leading-7 text-muted-foreground">
              The aim is to keep every explanation connected to its sources and limits.
            </p>
          </div>
          <div>
            <p className="font-display text-2xl">Governed</p>
            <p className="mt-4 leading-7 text-muted-foreground">
              A recommendation must not silently become permission or action.
            </p>
          </div>
        </div>
      </section>
      <CTA
        title="Explore a more accountable interface."
        copy="XAELI seeks thoughtful feedback from people working with evidence, uncertainty, and consequential decisions."
        label="Discuss XAELI"
      />
    </PageShell>
  );
}
