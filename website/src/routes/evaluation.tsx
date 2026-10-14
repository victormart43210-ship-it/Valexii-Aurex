import { ReasoningSpine } from "@/components/reasoning-spine";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { CTA, PageHero, PageShell, SectionHeading } from "@/components/site";
export const Route = createFileRoute("/evaluation")({
  head: () => ({
    meta: [
      { title: "Evaluation — Internal synthetic self-testing | VALEXII.AI" },
      {
        name: "description",
        content:
          "VALEXII internal synthetic evaluation scope and evidence requirements. Not official Humanity’s Last Exam, not a live XAELI benchmark, not independently validated.",
      },
      {
        property: "og:title",
        content: "VALEXII Evaluation — Internal, synthetic, evidence-required",
      },
      {
        property: "og:description",
        content:
          "Self-testing for evidence handling and uncertainty. No official HLE claim or independently verified benchmark result.",
      },
      { property: "og:url", content: "https://valexii.com/evaluation" },
      { property: "og:type", content: "article" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/evaluation" }],
  }),
  component: Evaluation,
});
function Evaluation() {
  return (
    <PageShell>
      <PageHero eyebrow="Evaluation / Internal synthetic work" title="Know when not to answer.">
        <p>
          A useful system should recognize when its evidence runs out. Internal synthetic tests
          explore evidence selection, contradictory explanations and the decision not to conclude.
          They are not independently verified product performance.
        </p>
      </PageHero>
      <ReasoningSpine context="evaluation" />
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Internal-prepublication · Evidence attachment required"
            title="A score needs a record behind it."
            copy="Prior internal holdout and hard-mock reports, including an HLE-shaped extreme mock exercise, lack attached protocols, item-level records and scoring artifacts here. Numerical results are withheld from this public presentation pending inspectable supporting evidence."
          />
          <div className="mt-10 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {[
              ["Evidence selection", "What is admitted, excluded or left unresolved?"],
              ["Verification & abstention", "When should the system decline to conclude?"],
              ["Contradiction handling", "Do alternate accounts and failures stay visible?"],
              [
                "Authority containment",
                "Does a proposal remain separate from permission and effect?",
              ],
            ].map(([t, c], i) => (
              <article className="border-t border-primary/50 pt-6" key={t}>
                <p className="text-xs text-primary">0{i + 1} / TEST DIRECTION</p>
                <h3 className="mt-4 font-display text-xl">{t}</h3>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">{c}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid grid gap-10 lg:grid-cols-2">
          <div>
            <h2 className="font-display text-3xl">HLE-shaped. Not official HLE.</h2>
            <p className="mt-5 text-xs leading-7 text-gold">
              INTERNAL MOCK / SYNTHETIC HARNESS EVALUATION / EVIDENCE ATTACHMENT REQUIRED
            </p>
            <p className="mt-5 text-sm leading-7 text-muted-foreground">
              Not official Humanity’s Last Exam. Not a live XAELI benchmark. Not independently
              validated. Not directly comparable to official leaderboard scores. Synthetic results
              can overstate real-world capability.
            </p>
          </div>
          <div>
            <h2 className="font-display text-2xl">What a review would require</h2>
            <ol className="mt-5 grid gap-5">
              {[
                "Frozen dataset and provenance",
                "Harness, version and scoring protocol",
                "Item-level outputs, misses and exclusions",
                "Independent replication and scope limitations",
              ].map((x, i) => (
                <li className="border-b border-border pb-4 text-sm" key={x}>
                  <span className="mr-4 text-primary">0{i + 1}</span>
                  {x}
                </li>
              ))}
            </ol>
            <p className="mt-5 text-xs text-amber">
              HOLD · Independent qualification not established
            </p>
          </div>
        </div>
      </section>
      <section className="section-space border-t border-border">
        <div className="site-grid">
          <SectionHeading
            eyebrow="AUREX / Experimental lab"
            title="Research without a borrowed endorsement."
            copy="AUREX explores reproducible questions, adversarial testing, model limits and abstention. Its research is not BCXMET phone security authority or an independently verified benchmark."
          />
          <Button asChild variant="glass" className="mt-7">
            <Link to="/aurex">
              AUREX purpose and limits <ArrowRight />
            </Link>
          </Button>
        </div>
      </section>
      <CTA
        title="Help test the method behind the claim."
        copy="Independent researchers can help define a scoped, reproducible review. Missing or unresolved evidence never counts as a pass."
      />
    </PageShell>
  );
}
