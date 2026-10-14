import { ReasoningSpine } from "@/components/reasoning-spine";
import { ValidationPanels } from "@/components/visuals";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { InquiryForm } from "@/components/inquiry-forms";
import { Button } from "@/components/ui/button";
import { PageHero, PageShell, SectionHeading } from "@/components/site";

export const Route = createFileRoute("/build-with-us")({
  head: () => ({
    meta: [
      { title: "Build with us — VALEXII.AI" },
      {
        name: "description",
        content:
          "Investors welcome: explore reusable architecture, cross-domain research and planned NSF proposal collaboration. No investment offering or partnership is implied.",
      },
      { property: "og:title", content: "Build with us — VALEXII.AI" },
      {
        property: "og:description",
        content:
          "Explore developmental architecture, independent validation and planned grants. Investors welcome; no measured traction or secured funding is claimed.",
      },
      { property: "og:url", content: "https://valexii.com/build-with-us" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/build-with-us" }],
  }),
  component: BuildWithUs,
});

const groups = [
  [
    "Invest & partner",
    "Investors, strategic partners, and infrastructure partners interested in careful qualification rather than unearned certainty.",
  ],
  [
    "Test & challenge",
    "Independent penetration testers and security researchers, adversarial/red-team researchers, and beta testers.",
  ],
  [
    "Engineer & evaluate",
    "Android and cybersecurity engineers, AI/evaluation researchers, and aligned contributors.",
  ],
  [
    "Research together",
    "Academic collaborators and manuscript/decipherment researchers willing to test hypotheses and share limitations.",
  ],
];

function BuildWithUs() {
  return (
    <PageShell>
      <PageHero eyebrow="VALEXII.AI / Open invitation" title="Build with us.">
        <p>
          Help build intelligence that earns trust. Bring a question, a test or a perspective we
          have missed.
        </p>
        <p className="mt-4">
          We welcome Android engineering, independent security review, physical-device testing,
          accessibility and reproducible research. Privacy is personal. Proof matters. People remain
          in control. No partnership or funded commitment is implied.
        </p>
        <div className="mt-8">
          <Button asChild variant="hero">
            <Link to="/contact">
              Explore a conversation <ArrowRight />
            </Link>
          </Button>
        </div>
      </PageHero>
      <ReasoningSpine context="collaboration" />
      <section className="section-space border-b border-border">
        <div className="site-grid">
          <ValidationPanels />
        </div>
      </section>
      <section className="section-space">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Who we're seeking"
            title="Different perspectives. A shared standard of proof."
            copy="These are invitations, not claims of existing partnerships, commitments, or endorsements."
          />
          <div className="mt-12 grid gap-x-12 md:grid-cols-2">
            {groups.map(([title, copy]) => (
              <article key={title} className="border-t border-border py-7">
                <h2 className="font-display text-2xl">{title}</h2>
                <p className="mt-4 max-w-xl leading-7 text-muted-foreground">{copy}</p>
              </article>
            ))}
          </div>
          <p className="mt-8 border-l-2 border-gold pl-5 text-sm leading-7 text-muted-foreground">
            Start with the contact or partnership form. Your inquiry is stored so we can respond;
            the form separately states whether a confirmation email was sent.
          </p>
        </div>
      </section>
      <section className="section-space border-b border-border">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Investment / Exploratory conversations"
            title="Investors welcome."
            copy="Explore the product vision and the evidence needed to evaluate it—not a promise of performance, returns or readiness."
          />
          <div className="mt-10 grid gap-8 md:grid-cols-2">
            {[
              [
                "Reusable architecture",
                "The five-stage evidence framework is designed for reuse, with separate domain evidence and permissions. Cross-domain capability and commercial scalability remain to be validated.",
              ],
              [
                "Cross-domain product vision",
                "BCXMET cybersecurity, DISPATER oilfield/subsurface intelligence and XAITA future capital intelligence are distinct developmental directions. This is a vision, not a portfolio of production-complete products.",
              ],
              [
                "Verifiable security research",
                "The opportunity is to help fund reproducible artifacts, independent challenge and physical-device validation. Synthetic demonstrations are not independently verified protection or benchmark performance.",
              ],
              [
                "IP strategy & adoption target",
                "Patent strategy and trademark clearance are being pursued. No patent-pending status or registered trademark is claimed. 10,000 retained users is a future TARGET—not actual users, measured retention or demonstrated traction.",
              ],
            ].map(([title, copy]) => (
              <article key={title} className="border-t border-border pt-6">
                <h3 className="font-display text-xl">{title}</h3>
                <p className="mt-4 leading-7 text-muted-foreground">{copy}</p>
              </article>
            ))}
          </div>
          <p className="mt-8 max-w-3xl leading-7 text-muted-foreground">
            Universities, industry partners and grant collaborators are welcome to discuss
            evaluation, datasets, research and responsible commercialization. No partner,
            endorsement, funded commitment, investment offering or solicitation of securities is
            implied. Public discussion excludes unpublished patentable details and private
            repository contents.
          </p>
          <Button asChild variant="outline" className="mt-6">
            <Link to="/contact">
              Discuss investment or collaboration <ArrowRight />
            </Link>
          </Button>
        </div>
      </section>
      <section className="section-space border-b border-border bg-card/25">
        <div className="site-grid">
          <SectionHeading
            eyebrow="Grant target / Planned proposal"
            title="NSF America’s Seed Fund"
            copy="SBIR/STTR Phase I · NSF 26-510. A planned proposal target—not submitted, invited, approved or awarded."
          />
          <dl className="mt-10 grid gap-8 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-muted-foreground">Target full-proposal deadline</dt>
              <dd className="mt-3 font-display text-xl">November 4, 2026 · 5 p.m.</dd>
              <dd className="mt-2 text-sm leading-6 text-muted-foreground">
                Submitting organization’s local time, as specified in the solicitation.
              </dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Phase I funding ceiling</dt>
              <dd className="mt-3 font-display text-xl">Up to $305,000</dd>
              <dd className="mt-2 text-sm leading-6 text-muted-foreground">
                A solicitation limit, not funding secured by VALEXII.AI; awards depend on review and
                available funds.
              </dd>
            </div>
          </dl>
          <p className="mt-8 max-w-3xl leading-7 text-muted-foreground">
            A full Phase I proposal requires an official Project Pitch invitation; invitations are
            valid for the next two submission deadlines. Our invitation and eligibility are not
            verified. Before applying, confirm qualifying U.S. small-business status,
            ownership/control and affiliate size rules, principal-investigator employment, required
            registrations and current research-security requirements. STTR also requires a
            qualifying research-institution partner. University interest does not establish that
            partnership or eligibility.
          </p>
          <Button asChild variant="outline" className="mt-6">
            <a href="https://www.nsf.gov/funding/opportunities/small-business-innovation-research-small-business-technology/nsf26-510/solicitation">
              Read official NSF 26-510 solicitation <ArrowRight />
            </a>
          </Button>
        </div>
      </section>
      <section
        id="partnership-inquiry"
        className="section-space border-t border-border"
        aria-labelledby="partnership-inquiry-title"
      >
        <div className="site-grid grid gap-12 lg:grid-cols-[.65fr_1.35fr]">
          <div>
            <h2 id="partnership-inquiry-title" className="font-display text-2xl">
              Partnership inquiry
            </h2>
            <p className="mt-4 leading-7 text-muted-foreground">
              Investors, universities, grant collaborators and industrial partners can start here.
              Your inquiry is stored securely and read by a person. Exploratory only: no investment
              offering, partnership, award or funded commitment is implied.
            </p>
          </div>
          <InquiryForm kind="partnership" />
        </div>
      </section>
    </PageShell>
  );
}
