import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, FlaskConical, SearchCheck, Split } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  BreakthroughWatch,
  EvidenceFlow,
  NewsletterSignup,
  ResearchTriptych,
} from "@/components/decipherment-frontier";
import { Eyebrow, PageShell, SectionHeading } from "@/components/site";
import { SectionIllustration } from "@/components/section-illustration";

export const Route = createFileRoute("/decipherment-frontier")({
  head: () => ({
    meta: [
      { title: "The Decipherment Frontier — Weekly research briefing | VALEXII.AI" },
      {
        name: "description",
        content:
          "Follow evidence, competing hypotheses, reproducibility checks, and open questions across Voynich, Linear A, and Rongorongo research. No claimed decipherment.",
      },
      { property: "og:title", content: "The Decipherment Frontier — VALEXII.AI" },
      {
        property: "og:description",
        content:
          "Three ancient mysteries, testable questions and visible uncertainty. Explore the planned research briefing; newsletter signup is not active.",
      },
      { property: "og:url", content: "https://valexii.com/decipherment-frontier" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/decipherment-frontier" }],
  }),
  component: DeciphermentFrontier,
});

function DeciphermentFrontier() {
  return (
    <PageShell>
      <section className="frontier-hero technical-grid">
        <div className="site-grid frontier-hero-grid">
          <div>
            <Eyebrow>VALEXII Research / Weekly briefing</Eyebrow>
            <h1>THE DECIPHERMENT FRONTIER</h1>
            <p className="frontier-subhead">
              Three ancient mysteries. One disciplined approach to discovery.
            </p>
            <p className="frontier-signature">
              CURIOSITY OPENS THE QUESTION. <span>EVIDENCE SETS THE LIMIT.</span>
            </p>
            <div className="frontier-hero-actions">
              <Button asChild variant="hero" size="lg">
                <a href="#briefing">
                  View planned weekly briefing <ArrowRight />
                </a>
              </Button>
              <Button asChild variant="glass" size="lg">
                <a href="#breakthrough-watch">See the evidence status</a>
              </Button>
            </div>
            <p className="frontier-microcopy">
              Planned weekly research notes. No claimed decipherment. Signup is not active.
            </p>
          </div>
          <ResearchTriptych />
        </div>
      </section>

      <section className="section-space border-b border-border">
        <div className="site-grid frontier-intro">
          <p className="frontier-lead">
            The Voynich Manuscript. Linear A. Rongorongo. What do these texts say—and what evidence
            would make a proposed reading credible?
          </p>
          <div className="frontier-body-copy">
            <p>
              VALEXII.AI is investigating how evidence-governed methods could make computational
              decipherment research more transparent and testable. A model may suggest a reading;
              sources, reconstruction and independent checks must support it.
            </p>
            <p>
              The planned weekly briefing will follow patterns, competing hypotheses,
              reproducibility checks, failed tests and open questions. Signup is not connected; no
              addresses are collected and no delivery is promised. Any future interpretation must
              include its evidence and uncertainty, not a claim of privileged certainty.
            </p>
          </div>
        </div>
      </section>

      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Three research tracks"
            title="Distinct records. The same burden of proof."
            copy="Curiosity starts the investigation. Qualification, reconstruction, and independent evidence determine what can responsibly be claimed."
          />
          <div className="frontier-tracks">
            {[
              [
                "01",
                "Voynich Manuscript",
                "Test transcription, boundaries, local order, and competing historical explanations without converting structure into meaning.",
              ],
              [
                "02",
                "Linear A",
                "Build controlled corpora and test structural hypotheses while keeping language identification and translation explicitly unestablished.",
              ],
              [
                "03",
                "Rongorongo",
                "Respect object context, sign order, segmentation, and competing accounts before proposing any semantic reading.",
              ],
            ].map(([number, title, copy]) => (
              <article key={number}>
                <SectionIllustration
                  subject={
                    number === "01" ? "voynich" : number === "02" ? "linear-a" : "rongorongo"
                  }
                />
                <span>{number} / RESEARCH IN PROGRESS</span>
                <h3>{title}</h3>
                <p>{copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section-space frontier-architecture" id="inside-architecture">
        <div className="site-grid grid gap-12 lg:grid-cols-[.78fr_1.22fr]">
          <div>
            <SectionHeading
              eyebrow="Inside the architecture"
              title="Generate possibilities. Investigate their support."
              copy="Governance can structure provenance, competing interpretations, counterchecks, and authorization. It does not establish a breakthrough or outperform a baseline model by itself."
            />
            <ul className="frontier-principles">
              <li>
                <FlaskConical aria-hidden="true" /> Failed tests remain part of the record.
              </li>
              <li>
                <Split aria-hidden="true" /> Competing interpretations stay visible.
              </li>
              <li>
                <SearchCheck aria-hidden="true" /> Independent evidence is required for promotion.
              </li>
            </ul>
          </div>
          <EvidenceFlow />
        </div>
      </section>

      <section className="section-space" id="breakthrough-watch">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Breakthrough Watch"
            title="Status before spectacle."
            copy="A clear public ledger of what is being investigated, what remains hypothetical, and what has not been established."
          />
          <BreakthroughWatch />
        </div>
      </section>

      <section className="section-space frontier-briefing-band" id="briefing">
        <div className="site-grid">
          <NewsletterSignup />
        </div>
      </section>

      <section className="section-space border-t border-border">
        <div className="site-grid flex flex-wrap items-center justify-between gap-6">
          <div>
            <p className="frontier-kicker">Continue the investigation</p>
            <h2 className="font-display text-3xl">Read what remains unanswered.</h2>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button asChild variant="glass">
              <Link to="/voynich">
                Voynich status <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/decipherment">
                All research tracks <ArrowRight />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </PageShell>
  );
}
