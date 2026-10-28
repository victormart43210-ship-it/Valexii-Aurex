import { ReasoningSpine } from "@/components/reasoning-spine";
import dispaterHero from "../../public/assets/dispater-hero.jpg.asset.json";
import { createFileRoute } from "@tanstack/react-router";
import { DomainReasoning } from "@/components/domain-reasoning";
import { DispaterAuditConsole } from "@/components/dispater-audit-console";
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
      { title: "DISPATER.AI — Continuous Industrial Audit & Monitoring | VALEXII.AI" },
      {
        name: "description",
        content:
          "Continuous industrial audit, evidence qualification, anomaly monitoring and human review workflows for oilfield and towing operations.",
      },
      { property: "og:title", content: "DISPATER.AI — Continuous Industrial Audit & Monitoring" },
      {
        property: "og:description",
        content:
          "Explore continuous industrial monitoring, evidence ledgers, audit readiness, and XAELI 5-step explanations.",
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
        eyebrow="Continuous Industrial Audit & Monitoring"
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
              Conceptual artwork — not live product UI or physical machinery control.
            </figcaption>
          </figure>
        }
      >
        <p className="text-gold">Continuous Evidence & Audit Preparedness</p>
        <p>
          Decisions beneath the surface depend on evidence above it. DISPATER.AI provides continuous
          industrial audit monitoring, evidence ledgers, anomaly detection, and XAELI 5-step explanations
          for oilfield operations, pressure pumping, towing/recovery, and industrial facilities.
        </p>
      </PageHero>

      <section className="section-space border-b border-border bg-card/10">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Interactive Audit Console"
            title="Execute Synthetic Industrial Audit & Review Findings"
            copy="Evaluate synthetic field tickets, telemetry observations, rate sheets, and inspection logs against AUREX evidence governance contracts."
          />
          <div className="mt-8">
            <DispaterAuditConsole />
          </div>
        </div>
      </section>

      <ReasoningSpine context="dispater" />

      <section className="section-space">
        <div className="site-grid grid items-center gap-14 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="Evidence Governance / Non-Delegable Authority"
              title="A model is not the ground beneath it."
              copy="Operational records, pressure logs, inspection certificates, and dispatch entries are evaluated against versioned rules. DISPATER keeps measurements, rule evaluations, and recommendations distinct—with uncertainty, human oversight, and cryptographic evidence chains intact."
            />
            <p className="mt-6 leading-7 text-muted-foreground">
              AI model self-declarations hold zero authority. Critical and high-severity safety findings
              require explicit human reviewer identification for closure.
            </p>
            <p className="mt-4 text-sm leading-7 text-amber">
              Model Output Authority = NONE | Industrial Control Authority = NONE | Financial Authority = NONE.
            </p>
            <p className="mt-5 text-sm leading-7 text-muted-foreground">
              Historical name / Dis Pater was a Roman god of the underworld and hidden riches
              beneath the earth. In DISPATER.AI, it represents uncovering hidden evidence and operational risk.
            </p>
          </div>
          <IndustrialPanel />
        </div>
      </section>

      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Application Modules"
            title="Continuous Audit Preparedness Across Operations."
          />
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            <ProductCard
              name="Continuous Operational Monitoring"
              label="Observation"
              copy="Ingest field tickets, telemetry, and inspection logs to detect missing records, rate discrepancies, or overdue inspections."
              to="/research"
              accent="amber"
            />
            <ProductCard
              name="Evidence Ledger & Receipts"
              label="Provenance"
              copy="Preserve cryptographic SHA-256 evidence envelopes and generate self-issued audit receipts."
              to="/research"
            />
            <ProductCard
              name="Corrective Action Retest"
              label="Remediation"
              copy="Track findings through assignment, remediation evidence submission, and independent human retest verification."
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
