import { ReasoningSpine } from "@/components/reasoning-spine";
import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Network,
  GitBranch,
  ScanSearch,
  Database,
  CircleHelp,
  Blocks,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  CTA,
  PageHero,
  PageShell,
  SectionHeading,
  GovernedIntelligenceFlow,
} from "@/components/site";
import { VerificationDiagram } from "@/components/visuals";
import { SectionIllustration } from "@/components/section-illustration";
export const Route = createFileRoute("/system")({
  head: () => ({
    meta: [
      { title: "VALEXII System — Evidence-governed AI & human control" },
      {
        name: "description",
        content:
          "VALEXII’s five-stage reasoning framework: provenance, qualification, independent challenge, current authority and bounded effects. Architectural intent.",
      },
      { property: "og:title", content: "Unified Reasoning Spine — Evidence before effect" },
      {
        property: "og:description",
        content:
          "Evidence to effect, with independent challenge and human authority. Developmental capabilities, not completed deployment claims.",
      },
      { property: "og:url", content: "https://valexii.com/system" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/system" }],
  }),
  component: System,
});
function System() {
  return (
    <PageShell>
      <PageHero eyebrow="VALEXII System · Developmental" title="VALEXII.AI">
        <p>
          Intelligence should answer to evidence—and to people. Our five-stage design asks what was
          observed, whether it holds up, what it supports and who permits the next step. These are
          requirements we are building toward, not proof that every safeguard is deployed.
        </p>
      </PageHero>
      <ReasoningSpine context="system" detailed />
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Capability directions"
            title="Good answers need more than agreement."
            copy="These are public-safe design directions. They do not establish completed deployment, independent qualification, or autonomous release authority."
          />
          <div className="mt-10 grid gap-x-10 gap-y-12 md:grid-cols-2 lg:grid-cols-3">
            {[
              [
                Network,
                "Agent orchestration",
                "Bounded analytical roles can propose work, compare alternatives and assemble evidence. Their proposals must face separate checks; agreement alone is not proof.",
              ],
              [
                GitBranch,
                "Independent verification",
                "Challenge assumptions and reconstruct a proposed outcome from its supporting observations. Independence must be demonstrated, not inferred from multiple agents.",
              ],
              [
                ScanSearch,
                "Self-testing & evaluation",
                "Use reproducible test cases, failure analysis and abstention to expose limits. A self-test is useful evidence, never the system’s sole witness.",
              ],
              [
                Database,
                "Provenance",
                "Keep source identity, scope, freshness and limitations attached to a claim and the change it informs. Missing lineage holds the decision.",
              ],
              [
                CircleHelp,
                "Uncertainty handling",
                "Separate unknown from safe, unsupported from established, and stale from current. Contradictions and unresolved checks remain visible for human review.",
              ],
              [
                Blocks,
                "Build & improve systems",
                "Explore evidence-backed requirements, proposed changes, test plans and review summaries. Deterministic checks and human approval remain boundaries for integration and release.",
              ],
            ].map(([Icon, title, copy]) => {
              const Symbol = Icon as typeof Network;
              return (
                <article className="border-t border-border pt-6" key={String(title)}>
                  <Symbol aria-hidden="true" className="size-6 text-primary" />
                  <h3 className="mt-5 font-display text-xl">{String(title)}</h3>
                  <p className="mt-4 text-sm leading-7 text-muted-foreground">{String(copy)}</p>
                  <p className="mt-5 text-xs text-gold">DESIGN INTENT / DEVELOPMENTAL</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>
      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid">
          <SectionIllustration subject="architecture" />
          <SectionHeading
            eyebrow="The underlying verification framework"
            title="Show the basis. Check the permission."
            copy="Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness; disagreement or missing checks means HOLD for human review."
          />
          <VerificationDiagram />
          <GovernedIntelligenceFlow />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid grid gap-10 md:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="Technical collaboration"
              title="Inspect the questions. Respect the boundary."
              copy="Help test how evidence is handled, how alternatives are challenged and how permission is checked. Public methodology is open for discussion; private implementation and unpublished research stay private."
            />
            <Button asChild variant="glass" className="mt-8">
              <Link to="/contact">
                Discuss a scoped review <ArrowRight />
              </Link>
            </Button>
          </div>
          <div className="border-l border-gold pl-6">
            <h2 className="font-display text-2xl">One system. Distinct applications.</h2>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              BCXMET is our Android security focus, under development; XAELI is its planned
              explanation interface. Industrial and capital applications remain separate research
              directions, not connected production products.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button asChild variant="link">
                <Link to="/dispater">
                  DISPATER.AI <ArrowRight />
                </Link>
              </Button>
              <Button asChild variant="link">
                <Link to="/xaita">
                  XAITA.AI <ArrowRight />
                </Link>
              </Button>
            </div>
            <Button asChild variant="glass" className="mt-6">
              <Link to="/research">
                Review research limits <ArrowRight />
              </Link>
            </Button>
          </div>
        </div>
      </section>
      <section className="section-space border-t border-border">
        <div className="site-grid">
          <SectionHeading
            eyebrow="AUREX / Experimental research and reasoning evaluation"
            title="Ask difficult questions. Examine the limits."
            copy="AUREX is an experimental evidence-first research and reasoning evaluation lab exploring reproducible questions, adversarial testing, model limits and abstention. It is separate from BCXMET phone security authority and from any independently verified benchmark."
          />
          <Button asChild variant="glass" className="mt-7">
            <Link to="/aurex">
              Explore AUREX <ArrowRight />
            </Link>
          </Button>
        </div>
      </section>
      <CTA
        title="Bring an independent perspective."
        copy="For technical evaluation, commercialization and strategic partnership conversations—without treating a demonstration as qualification."
      />
    </PageShell>
  );
}
