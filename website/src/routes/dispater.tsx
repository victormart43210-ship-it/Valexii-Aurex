import { ReasoningSpine } from "@/components/reasoning-spine";
import dispaterHero from "../../public/assets/dispater-hero.jpg.asset.json";
import { createFileRoute } from "@tanstack/react-router";
import { DomainReasoning } from "@/components/domain-reasoning";
import { TowingAuditConsole } from "@/components/towing-audit-console";
import { OfficeWorkQueue } from "@/components/office-work-queue";
import { DigitalAuditBinder } from "@/components/digital-audit-binder";
import {
  CTA,
  IndustrialPanel,
  PageHero,
  PageShell,
  ProductCard,
  SectionHeading,
} from "@/components/site";

export const Route = createFileRoute("/dispater")({
  head: () => ({
    meta: [
      { title: "DISPATER.AI — Intelligence Beneath the Surface | VALEXII.AI" },
      {
        name: "description",
        content:
          "Developmental industrial intelligence for exploration, drilling, completions, production and risk review. Not independently validated or commercially deployed.",
      },
      { property: "og:title", content: "DISPATER.AI — Intelligence Beneath the Surface" },
      {
        property: "og:description",
        content:
          "Explore developmental subsurface analytics and bounded industrial reasoning; functionality remains unverified.",
      },
      { property: "og:url", content: "https://valexii.com/dispater" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/dispater" }],
  }),
  component: Dispater,
});

function Dispater() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Developmental / Industrial intelligence"
        title="DISPATER.AI"
        visual={
          <figure>
            <img
              src={dispaterHero.url}
              alt="DISPATER.AI artwork: Roman god Dis Pater enthroned with a trident staff and a glowing oil-derrick sphere, three hounds and subsurface oilfield displays."
              width={768}
              height={788}
              fetchPriority="high"
              decoding="async"
              className="mx-auto w-full max-w-md rounded-2xl"
            />
            <figcaption className="mt-2 text-center text-xs text-muted-foreground">
              Conceptual artwork — not product UI or field data.
            </figcaption>
          </figure>
        }
      >
        <p className="text-gold">Intelligence Beneath the Surface</p>
        <p>
          Decisions beneath the surface depend on evidence above it. DISPATER.AI explores industrial
          intelligence for exploration, drilling, completions and production—aiming to make
          operational analysis and risk review clearer. This is research direction, not deployed
          field capability.
        </p>
      </PageHero>

      <ReasoningSpine context="dispater" />

      {/* Commercial Towing & Office Management Suite */}
      <section className="section-space">
        <div className="site-grid space-y-12">
          <SectionHeading
            eyebrow="Commercial Pilot Operations Suite"
            title="Synthetic Commercial Towing & Office Audit Suite"
            copy="Independently verify end-to-end industrial record intake, authenticated backend processing, XAELI findings, office work queue dispositions, and cryptographic audit binder generation."
          />
          <TowingAuditConsole />
          <OfficeWorkQueue />
          <DigitalAuditBinder />
        </div>
      </section>

      <section className="section-space">
        <div className="site-grid grid items-center gap-14 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="Purpose / Unverified functionality"
              title="A model is not the ground beneath it."
              copy="Geological observations, drilling records and production information could help teams review risk. The design keeps measurements, interpretations and recommendations distinct—with uncertainty and human oversight intact."
            />
            <p className="mt-6 leading-7 text-muted-foreground">
              Private repositories exist, as reported by the project owner; their functionality has
              not been independently verified. This public page is a developmental direction, not
              proof of deployed oilfield analytics, operational readiness, environmental performance
              or autonomous control.
            </p>
            <p className="mt-4 text-sm leading-7 text-amber">
              Not independently validated or commercially deployed.
            </p>
            <p className="mt-5 text-sm leading-7 text-muted-foreground">
              Historical name / Dis Pater was a Roman god of the underworld and hidden riches
              beneath the earth, later associated with Pluto. The name is a cultural reference to
              what lies below the surface—not evidence of technical capability.
            </p>
          </div>
          <IndustrialPanel />
        </div>
      </section>

      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Application themes"
            title="Keep uncertainty in the operational picture."
          />
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            <ProductCard
              name="Subsurface exploration"
              label="Context"
              copy="Explore geological and subsurface evidence with source provenance, model uncertainty and explicit interpretation limits. No resource discovery or reserve estimate is claimed."
              to="/research"
              accent="amber"
            />
            <ProductCard
              name="Operations & risk"
              label="Observation"
              copy="Study how operational signals and risk assumptions could support reviewable planning. Recommendations never grant permission to control machinery."
              to="/research"
            />
            <ProductCard
              name="Sustainability"
              label="Decision support"
              copy="Examine environmental constraints, resource use and trade-offs without claiming verified emissions reductions or environmental outcomes."
              to="/research"
              accent="amber"
            />
          </div>
        </div>
      </section>

      <DomainReasoning />

      <CTA
        title="Collaborate on responsible industrial application."
        copy="DISPATER.AI seeks validation around operational evidence, safe boundaries, and human decision authority."
      />
    </PageShell>
  );
}
