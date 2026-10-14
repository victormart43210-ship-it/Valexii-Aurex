import { ReasoningSpine } from "@/components/reasoning-spine";
import bcxmetLogo from "../../public/assets/bcxmet-guardian-eye-logo.jpg.asset.json";
import { EarlyAccessForm } from "@/components/inquiry-forms";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  BCXMETInterface,
  CTA,
  GovernedIntelligenceFlow,
  PageHero,
  PageShell,
  SectionHeading,
  TwinView,
} from "@/components/site";
import { ProductComposition } from "@/components/visuals";
import { OrbLaboratory } from "@/components/orb-laboratory";
import { SectionIllustration } from "@/components/section-illustration";
import { ScamQuiz } from "@/components/scam-quiz";
import { TopicGuide } from "@/components/topic-guide";
import { androidSecurityFaqs, androidSecuritySources } from "@/components/topic-guide-content";
import cometArtwork from "@/assets/valexii-comet.webp";
import mobileAtmosphere from "@/assets/bcxmet-atmosphere-mobile.webp.asset.json";
import { CometSystem, GovernancePrinciple, ScanConcept } from "@/components/brand";
export const Route = createFileRoute("/bcxmet")({
  head: () => ({
    meta: [
      {
        title: "BCXMET — Android security in development | VALEXII.AI",
      },
      {
        name: "description",
        content:
          "Explore simulated call and suspicious-app journeys in BCXMET’s developmental Android security concept, with XAELI evidence explanations and limitations.",
      },
      { property: "og:title", content: "BCXMET — BCXME THE CHANGE" },
      {
        property: "og:description",
        content:
          "Developmental Android security preview: simulated scenarios, transparent evidence and human review. No live protection or released APK offered here.",
      },
      { property: "og:url", content: "https://valexii.com/bcxmet" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/bcxmet" }],
  }),
  component: BCXMET,
});
function BCXMET() {
  return (
    <PageShell>
      <div className="bcxmet-atmosphere">
        <picture className="bcxmet-atmosphere-art">
          <source media="(max-width: 640px)" srcSet={mobileAtmosphere.url} />
          <img
            src={cometArtwork}
            alt=""
            width={1536}
            height={1024}
            decoding="async"
            fetchPriority="high"
          />
        </picture>
        <PageHero
          eyebrow="BCXMET · Powered by VALEXII.AI · BCXME THE CHANGE"
          title="BCXMET"
          visual={
            <img
              src={bcxmetLogo.url}
              alt="BCXMET logo: ornate gold guardian-lion face forming the upper contour of an eye whose cyan iris holds a comet, above the BCXMET wordmark with a cyan X."
              width={1536}
              height={1536}
              fetchPriority="high"
              decoding="async"
              className="mx-auto aspect-square w-full max-w-md rounded-2xl object-cover"
            />
          }
        >
          <p>
            Your private life deserves more than an unexplained warning. BCXMET is an Android
            security product under development, aiming to help people review suspicious behavior
            with evidence, clear limits and informed next steps. V43 is DESIGN INTENT /
            DEVELOPMENTAL, not a released-version claim. This website provides no live scanning or
            protection.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button asChild variant="hero">
              <Link to="/system">
                Review the framework <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/bcxmet" hash="early-access" data-activation="beta_interest">
                Early beta interest <ArrowRight />
              </Link>
            </Button>
          </div>
        </PageHero>
      </div>
      <ReasoningSpine context="bcxmet" />
      <section className="section-space border-t border-border" id="command-center">
        <div className="site-grid">
          <SectionIllustration subject="phone" />
          <SectionHeading
            eyebrow="BCXMET / Interactive simulation"
            title="BCXMET phone simulator"
            copy="Explore authored call and app examples. No live scan, blocking or device protection; Orb motion has no authority."
          />
          <ol className="discovery-steps" aria-label="Product discovery">
            <li>
              <strong>01 / See the value</strong>
              <span>Choose a call or app concern.</span>
            </li>
            <li>
              <strong>02 / Try & review</strong>
              <span>Interact, then inspect the evidence.</span>
            </li>
            <li>
              <strong>03 / Choose your next step</strong>
              <span>Optional beta interest. No download promise.</span>
            </li>
          </ol>
          <ProductComposition
            initialView="Command Center"
            expandedDetails
            fullCommand
            showFlagships={false}
          />
        </div>
      </section>
      <ScamQuiz />
      <OrbLaboratory />
      <section className="section-space border-b border-border">
        <div className="site-grid grid items-center gap-12 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="The product"
              title="A warning should come with a reason."
              copy="A changed permission, an unfamiliar app or a convincing caller can leave you unsure what to trust. BCXMET aims to make the evidence and its limits readable. These are simulated workflows, not a verified Android beta release or complete protection."
            />
            <div className="mt-8">
              <GovernancePrinciple />
            </div>
          </div>
          <CometSystem compact />
        </div>
      </section>
      <section className="section-space border-y border-border">
        <div className="site-grid">
          <SectionHeading
            eyebrow="V43 product surface · Design intent / Developmental"
            title="Home. Command Center. XAELI. Activity. More."
            copy="BCXMET · Powered by VALEXII.AI. V43 is a developmental design direction, not a released version."
          />
          <div className="mt-10 grid items-start gap-10 lg:grid-cols-[1fr_1.1fr]">
            <div className="grid gap-8">
              <div>
                <h3 className="font-display text-xl">Command Center journeys</h3>
                <ul className="mt-4 grid gap-2 sm:grid-cols-2">
                  {[
                    "Scams & Phishing",
                    "Transactions",
                    "Privacy",
                    "Network & Travel",
                    "Identity",
                  ].map((j) => (
                    <li key={j} className="border-l-2 border-primary/50 py-2 pl-4 text-sm">
                      {j}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-display text-xl">XAELI, context first</h3>
                <ul className="mt-4 flex flex-wrap gap-2">
                  {["Explain it", "Show proof", "Help me review it"].map((j) => (
                    <li key={j} className="border border-gold/45 px-3 py-2 text-sm">
                      {j}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-display text-xl">Activity is the evidence trail</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">
                  The proposed Activity view would keep observations, changes and supporting
                  evidence together. Here those records are authored examples. The Orb shows
                  simulated state; it never decides whether your device is safe.
                </p>
                <p className="mt-3 text-xs leading-6 text-muted-foreground">
                  DESIGN INTENT: routine spam-call blocks may briefly illuminate the Orb; serious
                  alerts may use a fuller comet transition. Reduced-motion presentation remains
                  static. ORB MOTION AUTHORITY = NONE; there is no return edge into security
                  authority. These are proposed behaviors, not released protection or runtime
                  claims.
                </p>
              </div>
            </div>
            <BCXMETInterface />
          </div>
        </div>
      </section>
      <section className="section-space bg-card/25">
        <div className="site-grid grid items-start gap-12 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="Deep Scan / Premium Scan · Design intent"
              title="Transparency is the feature."
              copy="The proposed deeper scan would say what it examined, what it missed and what remains unknown—not compress everything into a comforting score. It is not available here. Payment would never change objective security truth."
            />
            <div className="mt-9 space-y-4 text-sm leading-7 text-muted-foreground">
              <p>
                <strong className="text-foreground">Checked</strong> and{" "}
                <strong className="text-foreground">not checked</strong> remain separate.{" "}
                <strong className="text-foreground">Clean</strong> only describes the examined
                scope.
              </p>
              <p>
                <strong className="text-foreground">Attention</strong> calls for review.{" "}
                <strong className="text-foreground">Unknown</strong> stays unknown. Limitations and
                supporting evidence travel with each result.
              </p>
            </div>
          </div>
          <ScanConcept />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Independent challenge"
            title="A conclusion must survive scrutiny."
            copy="Constructive and adversarial perspectives can test the same evidence. These are analytical roles, not autonomous authorities."
          />
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {[
              [
                "Angels",
                "Constructive analytical perspectives investigate the strongest supported case.",
              ],
              [
                "Demons",
                "Adversarial, red-team challenge looks for contradictions and missing context.",
              ],
              [
                "EMET",
                "A verification layer checks whether claims remain supported by the available evidence.",
              ],
            ].map(([name, copy]) => (
              <article key={name} className="border-t border-primary/50 pt-6">
                <h3 className="font-display text-2xl">{name}</h3>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">{copy}</p>
                <span className="mt-5 inline-block text-xs uppercase text-gold">Developmental</span>
              </article>
            ))}
          </div>
        </div>
      </section>
      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid grid gap-12 lg:grid-cols-[.85fr_1.15fr]">
          <div>
            <SectionHeading
              eyebrow="XAELI / Twin View"
              title="See the case. Then challenge it."
              copy="The planned XAELI interface would put a supported interpretation beside the questions that could change it. Here both views are scripted examples, not a connected AI verdict."
            />
            <Button asChild variant="glass" className="mt-8">
              <Link to="/xaeli">
                Explore XAELI <ArrowRight />
              </Link>
            </Button>
          </div>
          <TwinView />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Supporting capabilities · Developmental"
            title="Context without delegated authority."
          />
          <div className="mt-10 grid gap-x-10 gap-y-8 md:grid-cols-2 lg:grid-cols-4">
            {[
              [
                "Canary",
                "Bounded monitoring and verification, not a claim of universal detection.",
              ],
              [
                "LUX",
                "Research / observatory only: contribution intelligence that never owns authority.",
              ],
              [
                "Analyst mode",
                "An advanced technical view for evidence relationships and unresolved questions.",
              ],
              [
                "Evidence Ledger",
                "Provenance and limitations stay attached to what is observed and concluded.",
              ],
            ].map(([name, copy]) => (
              <div key={name} className="border-t border-border pt-5">
                <h3 className="font-display text-xl">{name}</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{copy}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="section-space border-t border-border">
        <div className="site-grid">
          <SectionHeading eyebrow="Public reasoning framework" title="From evidence to effect." />
          <GovernedIntelligenceFlow />
        </div>
      </section>
      <section className="section-space border-t border-border">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Developmental / Internal directions"
            title="Better evidence before broader claims."
            copy="These are engineering directions, not completed capabilities or release qualification results."
          />
          <div className="mt-8 grid gap-6 md:grid-cols-2">
            {[
              [
                "Admit evidence carefully",
                "Check where an observation came from, how recent it is and whether it belongs in this review. Missing support should stop a proposed response—not become reassurance.",
              ],
              [
                "Make the experience accountable",
                "Keep each observation, interpretation and proposed response distinct. A reviewer should be able to retrace the basis; old evidence must never be described as CURRENT.",
              ],
              [
                "Verify independently",
                "Follow evidence toward a conclusion, then trace the proposed result back to its sources through separate checks. Agreement within one system is not independent proof.",
              ],
              [
                "Integrate with controlled authority",
                "A proposal is not permission. Current scope, Android permissions and human approval must be checked before a consequential step. These requirements still need independent validation.",
              ],
            ].map(([title, copy]) => (
              <article key={title} className="border-t border-border pt-5">
                <h3 className="font-display text-xl">{title}</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{copy}</p>
              </article>
            ))}
          </div>
          <Button asChild variant="glass" className="mt-8">
            <Link to="/build-with-us">
              Build with us <ArrowRight />
            </Link>
          </Button>
        </div>
      </section>
      <TopicGuide
        id="android-security-guide"
        eyebrow="Android security basics · educational"
        title="Android phishing and suspicious app permissions: what to check"
        intro="General guidance from public sources. BCXMET is in development; this page's demonstrations are simulated and do not protect your device."
        faqs={androidSecurityFaqs}
        sources={androidSecuritySources}
      >
        <nav aria-label="Next steps" className="mt-8 flex flex-wrap gap-3">
          <Button asChild variant="glass">
            <a href="#command-center">
              Try the simulated call and app reviews <ArrowRight />
            </a>
          </Button>
          <Button asChild variant="glass">
            <Link to="/security">
              How we handle security reports <ArrowRight />
            </Link>
          </Button>
          <Button asChild variant="glass">
            <a href="#early-access">
              Request early-access updates <ArrowRight />
            </a>
          </Button>
        </nav>
        <section
          id="early-access"
          className="mt-10 scroll-mt-24"
          aria-labelledby="early-access-title"
        >
          <h2 id="early-access-title" className="font-display text-2xl">
            BCXMET early-access updates
          </h2>
          <p className="mt-3 mb-6 text-sm leading-7 text-muted-foreground">
            Register interest in future testing—not a place in an available beta. The form states
            whether a confirmation email was sent; stored interest alone does not enroll you. No
            public beta, download or device protection is active today.
          </p>
          <EarlyAccessForm />
        </section>
      </TopicGuide>
      <CTA
        title="Help us earn the next claim."
        copy="BCXMET seeks thoughtful beta interest and independent security review. Human authority remains the boundary for consequential action."
        label="Start a conversation"
      />
    </PageShell>
  );
}
