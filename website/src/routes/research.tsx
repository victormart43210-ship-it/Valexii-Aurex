import { ReasoningSpine } from "@/components/reasoning-spine";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CTA, PageHero, PageShell, SectionHeading } from "@/components/site";
import { ResearchGraphic } from "@/components/visuals";
import { SectionIllustration } from "@/components/section-illustration";
export const Route = createFileRoute("/research")({
  head: () => ({
    meta: [
      { title: "Research — Evaluation & manuscript investigation | VALEXII.AI" },
      {
        name: "description",
        content:
          "Explore VALEXII internal synthetic evaluation and Voynich structural research. Evidence attachment required; no official benchmark scores or claimed decipherment.",
      },
      { property: "og:title", content: "VALEXII Research — Questions before claims" },
      {
        property: "og:description",
        content:
          "Internal self-testing and manuscript structure investigation. Uncertainty, methodology and evidence gaps stay visible.",
      },
      { property: "og:url", content: "https://valexii.com/research" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/research" }],
  }),
  component: Research,
});
function Research() {
  return (
    <PageShell>
      <PageHero eyebrow="Research · Internal-prepublication" title="Questions before claims.">
        <p>
          Curiosity opens a question. Evidence decides how far an answer can go. Our manuscript
          research and internal evaluation keep competing explanations, failed tests and limits in
          view. Independent challenge is welcome; no completed decipherment is claimed.
        </p>
      </PageHero>
      <ReasoningSpine context="research" />
      <section className="section-space research-band">
        <div className="site-grid grid items-center gap-10 lg:grid-cols-2">
          <div>
            <SectionIllustration subject="voynich" />
            <SectionHeading
              eyebrow="01 / Voynich Manuscript"
              title="Structure is not meaning."
              copy="Computational work explores transcription consistency, segmentation, local order and historical hypotheses. Research in progress—not a claimed decipherment."
            />
            <p className="mt-6 border-l-2 border-gold pl-4 text-xs leading-7 text-gold">
              STRUCTURAL FINDINGS: INTERNAL-PREPUBLICATION / EVIDENCE ATTACHMENT REQUIRED
              <br />
              SEMANTIC INTERPRETATION: NOT ESTABLISHED · HOLD
            </p>
            <p className="mt-5 text-sm leading-7 text-muted-foreground">
              Supporting artifacts and independent replication are not attached here. A structural
              result may be labeled SUPPORTED only when the supporting evidence establishes that
              specific claim; it would still not establish a translation.
            </p>
            <Button asChild variant="glass" className="mt-7">
              <Link to="/voynich">
                Explore the investigation <ArrowRight />
              </Link>
            </Button>
          </div>
          <ResearchGraphic />
        </div>
      </section>
      <section className="section-space border-y border-border">
        <div className="site-grid grid gap-10 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="02 / Evaluation & self-testing"
              title="AUREX: the failures belong in the record."
              copy="Internal synthetic tests ask what evidence was used, what could contradict an answer and when to decline to conclude. Scores are not promoted without inspectable artifacts."
            />
            <Button asChild variant="hero" className="mt-7 mr-3">
              <Link to="/aurex">
                Explore AUREX <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass" className="mt-7">
              <Link to="/evaluation">
                Review evaluation scope <ArrowRight />
              </Link>
            </Button>
          </div>
          <div className="border-t border-primary pt-6">
            <p className="text-xs leading-7 text-gold">
              INTERNAL / SYNTHETIC · EVIDENCE ATTACHMENT REQUIRED
            </p>
            <h3 className="mt-4 font-display text-2xl">Not official Humanity’s Last Exam.</h3>
            <p className="mt-5 text-sm leading-7 text-muted-foreground">
              No official independently verifiable HLE evidence is attached to this project.
              Internal mock exercises are not live XAELI benchmarks, product efficacy evidence, or
              directly comparable leaderboard results.
            </p>
            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              {[
                "Reproducible protocols",
                "Item-level records",
                "Failure analysis",
                "Independent replication",
              ].map((x) => (
                <p key={x} className="border-l border-border pl-4 text-sm">
                  {x}
                  <span className="mt-2 block text-xs text-muted-foreground">
                    Evidence required
                  </span>
                </p>
              ))}
            </div>
          </div>
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid flex flex-wrap items-center justify-between gap-6">
          <div>
            <h2 className="font-display text-2xl">Related investigation & collaboration</h2>
            <p className="mt-4 max-w-xl text-sm leading-7 text-muted-foreground">
              <Link to="/linear-a" className="underline underline-offset-4">
                Linear A
              </Link>{" "}
              and{" "}
              <Link to="/rongorongo" className="underline underline-offset-4">
                Rongorongo
              </Link>{" "}
              are secondary structural research tracks, not verified translations. University
              testing and independent validation are invited, not claimed partnerships.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button asChild variant="hero">
              <Link to="/decipherment-frontier">
                The Decipherment Frontier <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/decipherment">
                Other research tracks <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/build-with-us">
                Build with us <ArrowRight />
              </Link>
            </Button>
          </div>
        </div>
      </section>
      <section className="section-space border-t border-border">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Cultural & historical exploration / Symbolism, not scientific evidence"
            title="Names and patterns in cultural context."
            copy="Geomancy has historical traditions of interpreting symbolic figures. Numerology assigns symbolic meanings to names and numbers through conventions that vary by tradition. Both can be studied as cultural practices—not as validated methods of prediction."
          />
          <p className="mt-5 max-w-3xl text-sm leading-7 text-muted-foreground">
            Exploring brand names such as VALEXII.AI, BCXMET, AUREX, DISPATER.AI, XAITA.AI and XAELI
            through those traditions is optional symbolic interpretation. No calculated name score
            or historical origin is asserted here. Such interpretations do not qualify scientific
            evidence, establish cybersecurity, authorize actions or verify a manuscript
            decipherment.
          </p>
        </div>
      </section>
      <CTA
        title="Bring a question that could prove us wrong."
        copy="We welcome research collaboration, university testing and independent evaluation. No affiliations or completed validation are implied."
      />
    </PageShell>
  );
}
