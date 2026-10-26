import dispaterHero from "../../public/assets/dispater-hero.jpg.asset.json";
import { ReasoningSpine } from "@/components/reasoning-spine";
import { DomainReasoning } from "@/components/domain-reasoning";
import { CTA, PageHero, PageShell, SectionHeading } from "@/components/site";
import { Button } from "@/components/ui/button";
import { emitActivation } from "@/lib/activation-events";
import { createFileRoute } from "@tanstack/react-router";
import { ArrowRight, ClipboardCheck, FileCheck2, Truck } from "lucide-react";

export const Route = createFileRoute("/dispater")({
  head: () => ({
    meta: [
      { title: "DISPATER.AI — Revenue Intelligence & Audit Readiness | VALEXII.AI" },
      {
        name: "description",
        content:
          "Explore proposed oilfield and towing revenue intelligence, workflow integration, and IRS/DOT evidence-readiness services. Fictional demo; no live customer audits or certified compliance.",
      },
      { property: "og:title", content: "DISPATER.AI — Revenue Intelligence & Audit Readiness" },
      {
        property: "og:description",
        content:
          "Connect work tickets, invoices, and reviewable evidence. Initial oilfield and towing discovery services are in development.",
      },
      { property: "og:url", content: "https://valexii.com/dispater" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/dispater" }],
  }),
  component: Dispater,
});

const offerings = [
  {
    title: "Oilfield operations",
    copy: "Explore field-ticket to invoice reconciliation, purchase orders, rate differences, crew records, and manager-reviewed exceptions.",
    icon: ClipboardCheck,
  },
  {
    title: "Towing & recovery",
    copy: "Explore completed tow tickets, dispatch records, storage documentation, billing discrepancies, and payment matching.",
    icon: Truck,
  },
  {
    title: "Audit-readiness evidence",
    copy: "Organize selected tax and transportation records for qualified human review. Requirements depend on each company's operations.",
    icon: FileCheck2,
  },
] as const;

function DispaterActions() {
  return (
    <div className="flex flex-wrap gap-3" aria-label="DISPATER.AI discovery actions">
      <Button asChild variant="hero" className="h-auto min-h-11 whitespace-normal text-center">
        <a
          href="/contact?service=dispater-audit"
          onClick={() => emitActivation("dispater_request_audit_click")}
        >
          Request an Audit <ArrowRight aria-hidden="true" className="size-4 shrink-0" />
        </a>
      </Button>
      <Button asChild variant="glass" className="h-auto min-h-11 whitespace-normal text-center">
        <a
          href="/contact?service=dispater-consultation"
          onClick={() => emitActivation("dispater_book_consultation_click")}
        >
          Book a Consultation <ArrowRight aria-hidden="true" className="size-4 shrink-0" />
        </a>
      </Button>
      <Button asChild variant="glass" className="h-auto min-h-11 whitespace-normal text-center">
        <a href="#dispater-demo" onClick={() => emitActivation("dispater_view_demo_click")}>
          View Demonstration <ArrowRight aria-hidden="true" className="size-4 shrink-0" />
        </a>
      </Button>
    </div>
  );
}

function Dispater() {
  return (
    <PageShell>
      <PageHero
        eyebrow="DISPATER.AI / Proposed oilfield & towing services"
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
        <p className="text-gold">Revenue Intelligence & Audit Readiness</p>
        <p>
          Connect the work your business performs to its billing and records. We are developing
          evidence-led review tools and managed integration services for oilfield contractors
          and towing companies, without requiring them to replace their existing software.
        </p>
        <p className="text-sm text-amber">
          Developmental offering. No live customer CRM, tax service, DOT certification, or
          production financial automation is represented here.
        </p>
        <div className="mt-6">
          <DispaterActions />
        </div>
        <p className="mt-3 text-xs leading-6 text-muted-foreground">
          Audit and consultation links open a contact request; no appointment is booked
          automatically. Please do not send confidential financial, payroll, driver, or tax records.
        </p>
      </PageHero>

      <ReasoningSpine context="dispater" />

      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Two sectors / One evidence-first approach"
            title="Keep the tools that already run your business."
            copy="Proposed pilots begin with authorized record exports and human decisions. Neither an AI answer nor a dashboard replaces your accountant, DOT specialist, or operating manager."
          />
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {offerings.map(({ title, copy, icon: Icon }) => (
              <article key={title} className="min-w-0 rounded-xl border border-border bg-background p-6">
                <Icon aria-hidden="true" className="size-7 text-primary" />
                <h3 className="mt-5 font-display text-xl">{title}</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="dispater-demo" aria-labelledby="dispater-demo-heading" className="section-space scroll-mt-28">
        <div className="site-grid">
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-gold">
            CONCEPT PREVIEW · FICTIONAL DATA · NOT LIVE
          </p>
          <h2 id="dispater-demo-heading" className="font-display text-3xl sm:text-4xl">
            See what an evidence-backed review could look like.
          </h2>
          <p className="mt-5 max-w-3xl leading-8 text-muted-foreground">
            The examples below illustrate the proposed DISPATER workflow. They are not live
            customer records or connected accounting and dispatch systems; NVIDIA explanations
            and customer-data processing are not enabled on this public page.
          </p>
          <div className="mt-8 grid gap-5 lg:grid-cols-2">
            <article className="rounded-xl border border-primary/40 bg-card p-6">
              <p className="text-xs font-semibold uppercase text-primary">Towing · Synthetic example</p>
              <h3 className="mt-3 font-display text-2xl">Unbilled recovery job</h3>
              <p className="mt-3 leading-7 text-muted-foreground">
                Fictional tow ticket TOW-101 has a completion record but no matching
                invoice in the supplied sample. An operator would inspect the original
                ticket before taking action.
              </p>
              <p className="mt-5 border-t border-border pt-4 text-sm text-amber">
                REVIEW REQUIRED · SOURCE-SNAPSHOT MATCH ONLY
              </p>
            </article>
            <article className="rounded-xl border border-gold/40 bg-card p-6">
              <p className="text-xs font-semibold uppercase text-gold">Oilfield · Synthetic example</p>
              <h3 className="mt-3 font-display text-2xl">Missing field-ticket invoice</h3>
              <p className="mt-3 leading-7 text-muted-foreground">
                Fictional flowback field ticket WELL-10-TICKET is present without
                an invoice in its example dataset. A manager would verify the
                approved rate, purchase order, and supporting documents.
              </p>
              <p className="mt-5 border-t border-border pt-4 text-sm text-amber">
                REVIEW REQUIRED · NO AUTOMATIC BILLING
              </p>
            </article>
          </div>
          <p className="mt-5 text-xs leading-6 text-muted-foreground">
            AUREX prototypes can flag possible discrepancies using fictional records.
            Record completeness does not establish IRS or DOT compliance. Audit findings
            require professional assessment and human authorization.
          </p>
        </div>
      </section>

      <DomainReasoning />
      <section className="section-space border-t border-border bg-card/25">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Start with a conversation"
            title="Bring clarity to your operation."
            copy="Tell us where disconnected tickets, invoices, and records create extra work. We can discuss a scoped discovery audit or managed workflow consultation; proposals and timing are confirmed by a person."
          />
          <div className="mt-7"><DispaterActions /></div>
        </div>
      </section>
      <CTA
        title="Explore evidence-led industrial operations."
        copy="DISPATER.AI is seeking qualified oilfield and towing discovery partners. A conversation is not a guarantee of deployed service, compliance, savings, or financing."
      />
    </PageShell>
  );
}
