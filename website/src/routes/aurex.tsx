import { AurexCommand } from "@/components/aurex-command";
import { AurexWorkspaceEntry } from "@/components/aurex-workspace-entry";
import { ReasoningSpine } from "@/components/reasoning-spine";
import { AurexDemo } from "@/components/aurex-demo";
import { AurexRepoPanel } from "@/components/aurex-repo-panel";
import { AurexCapabilitiesPanel } from "@/components/aurex-capabilities-panel";
import { AurexOxStatus } from "@/components/aurex-ox-status";
import { AurexPrivatePreview } from "@/components/aurex-private-preview";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHero, PageShell, SectionHeading } from "@/components/site";
import { VerificationDiagram } from "@/components/visuals";
import { SectionIllustration } from "@/components/section-illustration";

export const Route = createFileRoute("/aurex")({
  head: () => ({
    meta: [
      { title: "AUREX — Experimental research & reasoning evaluation | VALEXII.AI" },
      {
        name: "description",
        content:
          "AUREX: experimental research workstation for reproducible questions, adversarial testing, model limits and abstention. Not a verified benchmark.",
      },
      { property: "og:title", content: "AUREX — Evidence first. Limits visible." },
      {
        property: "og:description",
        content:
          "An experimental VALEXII research and reasoning evaluation lab. Methodology, evidence requirements and limits—not official HLE results or claimed decipherment.",
      },
      { property: "og:url", content: "https://valexii.com/aurex" },
      { property: "og:type", content: "article" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/aurex" }],
  }),
  component: Aurex,
});

function Aurex() {
  return (
    <PageShell>
      <PageHero eyebrow="AUREX / Experimental research lab" title="AUREX">
        <p>
          A persuasive answer is not enough. AUREX is our experimental evidence-first research and
          reasoning evaluation lab: a place to test sources, challenge explanations and learn when
          not to conclude.
        </p>
        <p className="mt-4">
          Local workstation work and website integration foundations are not the same as a connected
          production service. Model execution, tool connections and security scans remain unverified
          here; the public demo is synthetic.
        </p>
      </PageHero>
      <AurexCommand />
      <AurexWorkspaceEntry />
      <ReasoningSpine context="aurex" />
      <AurexDemo />
      <AurexRepoPanel />
      <AurexOxStatus context="public" />
      <AurexCapabilitiesPanel />
      <AurexPrivatePreview />
      <section className="section-space border-b border-border">
        <div className="site-grid">
          <SectionHeading
            eyebrow="AUREX Command Center / Local research workstation"
            title="Organize the work. Inspect the evidence."
            copy="These modules describe owner-reported work and design intent. A working connection needs a verifiable run record—not a reassuring status label. Public repository metadata is separate from production readiness."
          />
          <div className="mt-8 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {[
              [
                "Project Manager",
                "Organize research projects, tasks and milestones; completion still requires supporting records.",
              ],
              [
                "Transfer Hub",
                "Explore moving research materials between workspaces with explicit source, destination and access checks.",
              ],
              [
                "GitHub Hub",
                "Coordinate repository-related research work. This website does not connect to or expose private repositories.",
              ],
              [
                "AI Model Manager / Local models",
                "Explore model selection and local model workflows. Installed models, hardware compatibility and successful execution are not verified here.",
              ],
              [
                "Scientific Research",
                "Structure questions, sources, competing hypotheses and reproducible experiments.",
              ],
              [
                "CERN / Open-data research tools",
                "Explore research using public scientific datasets. No CERN affiliation, tool connection or completed analysis is established here.",
              ],
              [
                "Security Lab",
                "MobSF integration is within the reported scope; installation, connectivity and successful scans are unverified. No device protection or scan result is claimed.",
              ],
              [
                "Evaluation Engine",
                "Explore repeatable tests, adversarial cases, failure analysis and abstention—not official benchmark certification.",
              ],
              [
                "Evidence Ledger / Reports",
                "Organize source references, run records, limitations and review summaries. Report presence is not proof of a claim.",
              ],
              [
                "CUSTOS PRIME Ω / Independent verification",
                "A proposed verification layer for separate checks and challenge. Independence must be demonstrated through witnesses and evidence; the module name does not establish it.",
              ],
            ].map(([title, copy]) => (
              <article key={title} className="min-w-0 border-t border-border pt-5">
                <h3 className="font-display text-xl">{title}</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{copy}</p>
              </article>
            ))}
          </div>
          <p className="mt-8 text-sm leading-7 text-amber">
            Implementation scope / Connections and readiness unverified. The original AUREX Ω
            Command Center V6 screenshot is not available here; no dashboard reproduction or
            newer-version status is presented.
          </p>
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid">
          <SectionIllustration subject="architecture" />
          <SectionHeading
            eyebrow="Purpose / Research, not protection"
            title="Let the difficult cases change the answer."
            copy="AUREX explores how conclusions are supported, challenged and withheld. It is separate from BCXMET phone security authority; research activity cannot establish that a device is safe."
          />
          <div className="mt-8 grid gap-8 md:grid-cols-2">
            <article className="border-t border-primary pt-6">
              <h2 className="font-display text-2xl">Experimental directions</h2>
              <p className="mt-4 text-sm leading-7 text-muted-foreground">
                Reproducible questions, competing explanations, adversarial challenge, failure
                analysis and abstention are areas of exploration. Abstention means declining to
                conclude when the evidence is insufficient.
              </p>
            </article>
            <article className="border-t border-gold pt-6">
              <h2 className="font-display text-2xl">Independent verification</h2>
              <p className="mt-4 text-sm leading-7 text-muted-foreground">
                Independent qualification is not established here. No independently verified
                benchmark result is presented. This is not a completed official Humanity’s Last Exam
                evaluation, a live XAELI benchmark or evidence that any manuscript has been solved.
              </p>
              <p className="mt-4 text-xs text-amber">
                HOLD · Supporting artifacts and independent replication required
              </p>
            </article>
          </div>
        </div>
      </section>
      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Methodology / Proposed review requirements"
            title="Make the question repeatable."
            copy="These are review requirements and research directions, not a claim that every gate has already been completed."
          />
          <ol className="mt-8 grid gap-6 md:grid-cols-2">
            {[
              [
                "Define the question",
                "Record scope, sources, dataset version and exclusions before interpreting a result.",
              ],
              [
                "Challenge the answer",
                "Compare alternatives and adversarial cases. Preserve contradictions and wrong answers.",
              ],
              [
                "Record the limits",
                "Separate observations from inferences; disclose freshness, uncertainty and abstentions.",
              ],
              [
                "Invite independent review",
                "Provide protocols, scoring rules and item-level records for scoped replication before promoting a claim.",
              ],
            ].map(([title, copy], i) => (
              <li key={title} className="border-t border-border pt-5">
                <p className="text-xs text-gold">0{i + 1} / REVIEW REQUIREMENT</p>
                <h3 className="mt-3 font-display text-xl">{title}</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{copy}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Evidence → Qualification → Reality → Authority → Effect"
            title="A good explanation cannot authorize itself."
            copy="First collect the evidence. Check its quality and what it says about the present situation. Then check permission before any action. A research result, confident answer or luminous display cannot supply that permission."
          />
          <VerificationDiagram />
          <p className="text-sm leading-7 text-muted-foreground">
            The system must never be its own sole witness. UNKNOWN ≠ SAFE. Missing, stale, skipped,
            failed or unresolved evidence never counts as PASS. Historical findings do not establish
            current clearance. No authority comes from visualization: ORB MOTION AUTHORITY = NONE.
          </p>
          <div className="mt-8 grid gap-3 sm:flex sm:flex-wrap">
            <Button asChild variant="glass">
              <Link to="/evaluation">
                Evaluation scope <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/research">
                Research limits <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/system">
                VALEXII system <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="hero">
              <Link to="/contact">
                Discuss a scoped review <ArrowRight />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </PageShell>
  );
}
