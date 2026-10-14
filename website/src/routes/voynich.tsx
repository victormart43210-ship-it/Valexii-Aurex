import { researchBreadcrumb } from "@/components/topic-guide-content";
import { ResearchGraphic } from "@/components/visuals";
import { SectionIllustration } from "@/components/section-illustration";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageShell, PageHero, SectionHeading } from "@/components/site";
import { TopicGuide } from "@/components/topic-guide";
import { voynichFaqs, voynichSources } from "@/components/topic-guide-content";

export const Route = createFileRoute("/voynich")({
  head: () => ({
    meta: [
      { title: "Voynich Manuscript research: status, structure and FAQ | VALEXII.AI" },
      {
        name: "description",
        content:
          "From surface text to testable structure: Voynich research in HOLD, not deciphered. Internal findings await evidence attachment and independent replication.",
      },
      { property: "og:title", content: "VALEXII Research — Voynich" },
      {
        property: "og:description",
        content:
          "From surface text to testable structure. Research in progress; no claimed decipherment.",
      },
      { property: "og:url", content: "https://valexii.com/voynich" },
      { property: "og:type", content: "article" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/voynich" }],
    scripts: [researchBreadcrumb("Voynich Manuscript", "/voynich")],
  }),
  component: Voynich,
});

const pipeline = [
  ["01", "Corpus / transcription control", "ACTIVE"],
  ["02", "Boundary / segmentation structure", "ACTIVE"],
  ["03", "Line / state structure", "ACTIVE"],
  ["04", "Cross-transcription replication", "INTERNAL-PREPUBLICATION"],
  ["05", "Component / relational modeling", "ACTIVE"],
  ["06", "Held-out prediction", "HOLD"],
  ["07", "Semantic anchors", "NOT ESTABLISHED"],
  ["08", "Continuous plaintext", "NOT ESTABLISHED"],
  ["09", "Reverse reconstruction", "NOT ESTABLISHED"],
  ["10", "Independent replication", "NOT ESTABLISHED"],
];
const findings = [
  ["Cross-transcription", "Prior work reported 5,214 shared loci across transcriptions."],
  [
    "Zodiac labels",
    "Prior work reported 298 common label loci; 189 exact sequences (63.42%), mean character similarity 0.92651, and 279/298 (93.62%) in the same coarse first-token family.",
  ],
  [
    "Rosettes",
    "Prior work reported local-order signal above within-region shuffle nulls across several character n-gram representations.",
  ],
  ["Currier B", "Line/state and graded-boundary structure remain active research directions."],
];
const operations = [
  "Underlying record",
  "Page / register operation",
  "Context / state",
  "Encoding grammar",
  "Multi-glyph components",
  "Local relational order + layout",
  "Visible Voynich surface",
];
function Voynich() {
  return (
    <PageShell>
      <PageHero
        eyebrow="VALEXII Research / Voynich · HOLD"
        title="Voynich Manuscript: patterns before meaning."
      >
        <p>
          Research in progress — not a claimed decipherment. The manuscript invites explanations;
          our work tests transcription, boundaries, local order and historical hypotheses. The
          current position is HOLD: a compatible pattern is not an identified language, and no blind
          held-out semantic prediction has established a translation.
        </p>
      </PageHero>
      <section className="section-space border-b border-border">
        <div className="site-grid">
          <ResearchGraphic />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid grid gap-12 lg:grid-cols-[.8fr_1.2fr]">
          <div>
            <SectionIllustration subject="voynich" />
            <SectionHeading
              eyebrow="Method / No meaning without reconstruction"
              title="Reproducible structure before interpretation."
              copy="Compare reliable transcriptions and matched random baselines. A proposed meaning must predict unseen material, decode and reconstruct consistently, and survive independent replication."
            />
            <p className="mt-8 border-l-2 border-gold pl-5 text-sm leading-7 text-muted-foreground">
              DiagramState + LabelState → Record is a working refinement, not a decoded historical
              reading.
            </p>
          </div>
          <div>
            <p className="mb-5 text-xs font-bold uppercase text-primary">
              Neutral architecture / working model
            </p>
            <ol className="border-l border-primary/40 pl-6">
              {operations.map((step, i) => (
                <li key={step} className="border-b border-border py-4 text-sm">
                  <span className="mr-5 text-primary">{String(i + 1).padStart(2, "0")}</span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>
      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Milestones / not a percent decoded"
            title="A plausible key is only a beginning."
            copy="These stage labels describe current research posture, not a total percentage or a verified translation."
          />
          <div className="mt-10 grid gap-x-5 sm:grid-cols-2 lg:grid-cols-5">
            {pipeline.map(([n, title, status]) => (
              <article key={n} className="border-t border-border py-5">
                <span className="text-xs text-primary">
                  {n} / {status}
                </span>
                <h3 className="mt-3 text-sm font-semibold leading-6">{title}</h3>
              </article>
            ))}
          </div>
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Internal / pre-publication / evidence attachment required"
            title="Signals worth testing, not a decipherment."
            copy="The numerical findings below were supplied as prior internal reports; supporting artifacts are not attached to this website project. They are not independently verified here."
          />
          <div className="mt-10 grid gap-x-12 md:grid-cols-2">
            {findings.map(([title, copy]) => (
              <article key={title} className="border-t border-primary/35 py-6">
                <span className="text-xs uppercase text-gold">
                  Internal / evidence attachment required
                </span>
                <h3 className="mt-3 font-display text-xl">{title}</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
      <section className="section-space border-y border-border bg-card/25">
        <div className="site-grid grid gap-12 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="Solution-space reduction"
              title="A failed key is useful evidence."
            />
            <p className="mt-6 text-sm leading-7 text-muted-foreground">
              Simple astronomical cribs, naive zodiac/pharma shared vocabulary, absolute-coordinate
              models, simple zodiac ring-state mappings, fixed degree/decan keys and related
              shortcuts have been weakened or falsified in internal work. Reassessment requires
              attached protocols and artifacts.
            </p>
          </div>
          <div>
            <SectionHeading eyebrow="Versus the field" title="Compare milestones, not rankings." />
            <p className="mt-6 text-sm leading-7 text-muted-foreground">
              Transcription control, null comparisons, held-out prediction, reverse reconstruction
              and independent replication are the comparison criteria. An evidence-backed global
              ranking or percentage comparison is not established; no #1 claim is made.
            </p>
          </div>
        </div>
      </section>
      <TopicGuide
        id="voynich-guide"
        eyebrow="Voynich Manuscript · background"
        title="Voynich Manuscript: frequently asked questions"
        faqs={voynichFaqs}
        sources={voynichSources}
      />
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Related tracks"
            title="One discipline. Distinct scripts."
            copy="Voynich, Linear A and Rongorongo have active research directions. None has a verified translation here."
          />
          <div className="mt-8 flex flex-wrap gap-3">
            <Button asChild variant="glass">
              <Link to="/decipherment">
                View all tracks <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/linear-a">
                Linear A <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/rongorongo">
                Rongorongo <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass">
              <Link to="/build-with-us">
                Challenge the research <ArrowRight />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </PageShell>
  );
}
