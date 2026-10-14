import { ReasoningSpine } from "@/components/reasoning-spine";
import { createFileRoute, Link } from "@tanstack/react-router";
import { InquiryForm } from "@/components/inquiry-forms";
import { Button } from "@/components/ui/button";
import { PageHero, PageShell } from "@/components/site";
export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [
      { title: "Contact — VALEXII.AI" },
      {
        name: "description",
        content:
          "Contact VALEXII.AI about research, university collaboration, grants, partnerships or investment. Messages are stored securely and read by a person.",
      },
      { property: "og:title", content: "Contact — VALEXII.AI" },
      {
        property: "og:description",
        content:
          "Investors, universities and partners are welcome to explore developmental research. Send a message securely through the contact form.",
      },
      { property: "og:url", content: "https://valexii.com/contact" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/contact" }],
  }),
  component: Contact,
});
function Contact() {
  return (
    <PageShell>
      <PageHero eyebrow="Contact" title="What would you like to help make clearer?">
        <p>
          Ask about BCXMET, evidence-governed AI, independent testing or research collaboration.
          Messages submitted through this form are stored securely so a person can respond.
        </p>
        <p className="mt-4">
          Investors welcome. We also welcome universities, grant collaborators and industrial
          partners exploring reusable reasoning architecture and cross-domain product development.
          These are invitations, not existing funding or partnership claims.
        </p>
      </PageHero>
      <ReasoningSpine context="contact" />
      <section className="section-space">
        <div className="site-grid grid gap-12 lg:grid-cols-[.65fr_1.35fr]">
          <div>
            <h2 className="font-display text-2xl">Contact VALEXII</h2>
            <p className="mt-4 leading-7 text-muted-foreground">
              The form stores your message for follow-up. It separately reports whether a
              confirmation email was sent—saving a message does not imply email delivery.
            </p>
            <Button asChild variant="glass" className="mt-6">
              <a href="mailto:developer@valexii.com">Or email developer@valexii.com directly</a>
            </Button>
            <p className="mt-3 text-xs leading-6 text-muted-foreground">
              That link opens your own email app instead.
            </p>
            <p className="mt-6 leading-7 text-muted-foreground">
              Please keep first contact non-confidential. Do not send credentials, private
              repository contents or unpublished patentable details. Patent strategy and trademark
              clearance are being pursued; no filing, registration or investment offering is
              represented here.
            </p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              Partnership or investment topic? Use the{" "}
              <Link to="/build-with-us" hash="partnership-inquiry" className="underline">
                partnership inquiry form
              </Link>
              .
            </p>
          </div>
          <InquiryForm kind="contact" />
        </div>
      </section>
    </PageShell>
  );
}
