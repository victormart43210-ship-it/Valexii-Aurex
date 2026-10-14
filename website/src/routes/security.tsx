import { createFileRoute } from "@tanstack/react-router";
import { EvidenceCard, PageHero, PageShell, SectionHeading } from "@/components/site";
import { Button } from "@/components/ui/button";
export const Route = createFileRoute("/security")({
  head: () => ({
    meta: [
      { title: "Security philosophy & responsible disclosure — VALEXII.AI" },
      {
        name: "description",
        content:
          "How VALEXII.AI approaches evidence-led security, bounded claims and a developing responsible-disclosure process for BCXMET and related research.",
      },
      {
        property: "og:title",
        content: "Security philosophy & responsible disclosure — VALEXII.AI",
      },
      {
        property: "og:description",
        content:
          "Evidence-led security, bounded claims, and a future responsible-disclosure direction.",
      },
      { property: "og:url", content: "https://valexii.com/security" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/security" }],
  }),
  component: Security,
});
function Security() {
  return (
    <PageShell>
      <PageHero eyebrow="Security" title="Trust starts with honest limits.">
        <p>
          We are developing security practices around evidence, privacy and human oversight. BCXMET
          is under development: this website does not scan or protect your device, and no
          independent security certification is claimed.
        </p>
      </PageHero>
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading eyebrow="Public philosophy" title="No absolute promises." />
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            <EvidenceCard title="Observe">
              Treat findings as evidence to be qualified, not automatic proof.
            </EvidenceCard>
            <EvidenceCard title="Review">
              Keep uncertainty, impact, and permission visible.
            </EvidenceCard>
            <EvidenceCard title="Respond">
              Separate recommended action from authorized action and outcome.
            </EvidenceCard>
          </div>
          <div className="mt-12 rounded-md border border-gold/40 bg-gold/5 p-7">
            <h2 className="font-display text-2xl">Sensitive reports need a safe channel</h2>
            <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">
              A verified reporting workflow is not yet activated. Reporting instructions will appear
              here only after founder approval. Please do not send sensitive findings through the
              general contact form.
            </p>
            <Button disabled variant="glass" className="mt-6">
              Founder approval pending
            </Button>
          </div>
        </div>
      </section>
    </PageShell>
  );
}
