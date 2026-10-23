import { createFileRoute, Link } from "@tanstack/react-router";
import dispaterHero from "../../public/assets/dispater-hero.jpg.asset.json";
import dispaterOilfieldDash from "../../public/assets/dispater-oilfield-dashboard.svg.asset.json";
import dispaterFieldTicket from "../../public/assets/dispater-field-ticket.svg.asset.json";
import dispaterTowingDash from "../../public/assets/dispater-towing-dashboard.svg.asset.json";
import { ReasoningSpine } from "@/components/reasoning-spine";
import { DomainReasoning } from "@/components/domain-reasoning";
import {
  CTA,
  PageHero,
  PageShell,
  SectionHeading,
} from "@/components/site";

export const Route = createFileRoute("/dispater")({
  head: () => ({
    meta: [
      { title: "DISPATER.AI — Operations Intelligence Platform | VALEXII.AI" },
      {
        name: "description",
        content:
          "AI-assisted CRM, operations management, and workflow automation for oilfield service companies and towing & recovery businesses.",
      },
      { property: "og:title", content: "DISPATER.AI — Operations Intelligence Platform" },
      {
        property: "og:description",
        content:
          "From dispatch to field proof to invoice review. Planned managed operations platform for oilfield services and towing fleets.",
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
      {/* Hero Section */}
      <PageHero
        eyebrow="Commercial Operations Platform"
        title="DISPATER.AI"
        visual={
          <figure className="space-y-3">
            <img
              src={dispaterHero.url}
              alt="DISPATER.AI artwork: Roman god Dis Pater enthroned with a trident staff, glowing orb and three hounds."
              width={768}
              height={788}
              fetchPriority="high"
              decoding="async"
              className="mx-auto w-full max-w-md rounded-2xl shadow-xl border border-border/50"
            />
            <figcaption className="text-center text-xs text-muted-foreground">
              Original Roman Dis Pater Artwork — Commercial Operations Identity
            </figcaption>
          </figure>
        }
      >
        <p className="text-xl font-semibold text-gold">Intelligence Beneath the Surface</p>
        <p className="text-lg font-medium text-foreground">
          The Operations Intelligence Platform: From dispatch to field proof to invoice review.
        </p>
        <p className="text-muted-foreground">
          DISPATER.AI is a planned managed-integration platform built for oilfield service contractors
          (drilling, completions, and production support) and towing &amp; recovery businesses.
          By connecting dispatch queues, digital field tickets, equipment tracking, and automated rate
          reconciliation into one operational view, DISPATER helps teams reduce billing cycles and prevent
          unapproved ticket variations.
        </p>
        <p className="text-xs text-amber mt-2">
          Not independently validated or commercially deployed. Private repositories exist, as reported by the project owner; functionality has not been independently verified.
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Historical cultural reference: Dis Pater was a Roman god of the underworld and hidden riches, associated with Pluto.
        </p>
        <div className="pt-4 flex flex-wrap gap-4">
          <Link
            to="/contact"
            className="inline-flex items-center justify-center rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow transition hover:bg-primary/90"
          >
            Discuss an Operations Pilot
          </Link>
          <Link
            to="/solutions/business-operations"
            className="inline-flex items-center justify-center rounded-lg border border-input bg-background px-5 py-2.5 text-sm font-semibold text-foreground transition hover:bg-accent hover:text-accent-foreground"
          >
            Explore Services &amp; Pricing
          </Link>
        </div>
      </PageHero>

      <ReasoningSpine context="dispater" />

      {/* 6-Stage Canonical Workflow */}
      <section className="section-space border-y border-border bg-card/20">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Governed Operations Workflow"
            title="Six Stages from Request to Reconciled Invoice"
            copy="Every operational event follows a governed, auditable lifecycle. Data integrations require explicit authorization, and financial conclusions remain subject to human review."
          />
          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
            {[
              { step: "01", name: "REQUEST", desc: "Incoming job orders, wellsite requests, or towing dispatch calls ingested." },
              { step: "02", name: "DISPATCH", desc: "Crew, driver, truck, and equipment assignments with live availability." },
              { step: "03", name: "FIELD PROOF", desc: "Digital field tickets, customer signatures, GPS, and timestamp records." },
              { step: "04", name: "MANAGER REVIEW", desc: "Operations supervisor review and exception flagging before billing." },
              { step: "05", name: "INVOICE DRAFT", desc: "Automated invoice generation matching approved contract rates." },
              { step: "06", name: "RECONCILIATION", desc: "AUREX evidence-backed audit and AR reconciliation." },
            ].map((stage) => (
              <div key={stage.step} className="rounded-xl border border-border bg-card p-4 flex flex-col justify-between">
                <div>
                  <span className="text-xs font-bold text-primary">{stage.step}</span>
                  <h3 className="mt-1 text-sm font-bold text-foreground">{stage.name}</h3>
                  <p className="mt-2 text-xs text-muted-foreground leading-relaxed">{stage.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Sector A: Oilfield Operations */}
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Sector A — Oilfield Operations"
            title="Built for Fracking, Completions, Equipment & Wellsite Contractors"
            copy="Eliminate lost tickets, delayed approvals, and rate disputes across multi-crew and multi-location drilling, completions, and production operations."
          />
          <div className="mt-10 grid gap-8 lg:grid-cols-2 items-center">
            <div className="space-y-4">
              <h3 className="text-xl font-bold text-foreground">Comprehensive Oilfield Capabilities</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Customer &amp; AFE contract management</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Crew scheduling &amp; wellsite job dispatch</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Equipment availability &amp; maintenance tracking</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Digital field tickets with customer e-signatures</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Purchase order (PO) &amp; contract rate reconciliation</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Employee timecards &amp; daily job logs</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Automated draft invoice preparation &amp; AR reporting</li>
              </ul>
            </div>
            <div className="space-y-4">
              <figure className="rounded-xl overflow-hidden border border-border shadow-lg">
                <img
                  src={dispaterOilfieldDash.url}
                  alt="DISPATER.AI Oilfield Operations Control Dashboard Concept Preview"
                  className="w-full h-auto"
                />
                <figcaption className="p-2 text-center text-xs text-muted-foreground bg-card">
                  CONCEPT PREVIEW — FICTIONAL DATA — NOT LIVE • Oilfield Dashboard
                </figcaption>
              </figure>
              <figure className="rounded-xl overflow-hidden border border-border shadow-lg">
                <img
                  src={dispaterFieldTicket.url}
                  alt="DISPATER.AI Digital Field Ticket Concept Preview"
                  className="w-full h-auto"
                />
                <figcaption className="p-2 text-center text-xs text-muted-foreground bg-card">
                  CONCEPT PREVIEW — FICTIONAL DATA — NOT LIVE • Digital Field Ticket
                </figcaption>
              </figure>
            </div>
          </div>
        </div>
      </section>

      {/* Sector B: Towing & Recovery */}
      <section className="section-space border-t border-border bg-card/10">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Sector B — Towing & Recovery"
            title="Streamlined Dispatch, Storage & Motor-Club Reconciliation"
            copy="Accelerate vehicle dispatch, driver assignments, impound storage logging, and motor-club billing verification."
          />
          <div className="mt-10 grid gap-8 lg:grid-cols-2 items-center">
            <figure className="rounded-xl overflow-hidden border border-border shadow-lg order-2 lg:order-1">
              <img
                src={dispaterTowingDash.url}
                alt="DISPATER.AI Towing & Recovery Dispatch Console Concept Preview"
                className="w-full h-auto"
              />
              <figcaption className="p-2 text-center text-xs text-muted-foreground bg-card">
                CONCEPT PREVIEW — FICTIONAL DATA — NOT LIVE • Towing Console
              </figcaption>
            </figure>
            <div className="space-y-4 order-1 lg:order-2">
              <h3 className="text-xl font-bold text-foreground">Towing &amp; Recovery Capabilities</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Incoming call &amp; service request dispatch queues</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Driver &amp; wrecker/flatbed truck assignments</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Live ETA tracking &amp; roadside service documentation</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Vehicle recovery records &amp; photo evidence capture</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Impound lot &amp; storage fee tracking</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Motor-club paperwork &amp; rate reconciliation</li>
                <li className="flex items-center gap-2"><span className="text-primary font-bold">✓</span> Multi-location fleet reporting &amp; invoice review</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="section-space border-t border-border">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Commercial Services & Pricing"
            title="Indicative Pricing for Managed Operations Pilots"
            copy="DISPATER.AI is offered as a managed integration service with custom configuration, onboarding, and dedicated support."
          />
          <div className="mt-10 max-w-xl mx-auto rounded-2xl border border-primary/30 bg-card p-8 text-center space-y-4 shadow-xl">
            <span className="inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
              MANAGED PILOT
            </span>
            <h3 className="text-2xl font-bold text-foreground">Multi-Location Managed Integration</h3>
            <p className="text-3xl font-extrabold text-gold">From $3,000 <span className="text-sm font-normal text-muted-foreground">/ month</span></p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Indicative pricing only. Final monthly fees depend on fleet size, number of locations,
              required ERP/accounting integrations, and custom SLA requirements. Smaller operators receive custom quotes.
            </p>
            <div className="pt-4">
              <Link
                to="/contact"
                className="inline-block w-full rounded-lg bg-primary px-6 py-3 text-sm font-bold text-primary-foreground shadow transition hover:bg-primary/90"
              >
                Discuss an Operations Pilot
              </Link>
            </div>
          </div>
        </div>
      </section>

      <DomainReasoning />

      <CTA
        title="Transform Your Field Operations & Revenue Control"
        copy="Contact VALEXII.AI to discuss a DISPATER.AI managed operations pilot for your oilfield or towing business."
      />
    </PageShell>
  );
}
