import { createFileRoute } from "@tanstack/react-router";
import { LegalLayout, LegalSection, PageShell } from "@/components/site";
export const Route = createFileRoute("/terms")({
  head: () => ({
    meta: [
      { title: "Terms Draft — VALEXII.AI" },
      {
        name: "description",
        content:
          "Draft terms for VALEXII.AI’s website demonstration and voluntary support. No product license, protection guarantee or annual subscription included.",
      },
      { property: "og:title", content: "Terms Draft — VALEXII.AI" },
      { property: "og:description", content: "Draft terms subject to legal review." },
      { property: "og:url", content: "https://valexii.com/terms" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/terms" }],
  }),
  component: Terms,
});
function Terms() {
  return (
    <PageShell>
      <LegalLayout
        label="Legal draft"
        title="Terms"
        updated="13 October 2026 · editorial revision, legal review pending"
      >
        <LegalSection title="Developmental products and research">
          <p>
            This is a public research and development website. It presents developmental product
            concepts and ongoing research; publication of the website does not establish a released
            Android product, verified translation, or production service. No production protection
            service, APK, or commercial access plan is offered here.
          </p>
        </LegalSection>
        <LegalSection title="Reasoning and visualization boundaries">
          <p>
            The Unified Reasoning Spine is architectural intent, not verified operational
            functionality. Historical evidence is not present authorization. Missing, stale or
            unverified evidence never counts as PASS. UNKNOWN ≠ SAFE; a system must never be its own
            sole witness. The website’s simulated phone, Orb, wheels and radar cannot scan a device
            or authorize security, industrial or financial actions. ORB MOTION AUTHORITY = NONE.
          </p>
        </LegalSection>
        <LegalSection title="Informational content">
          <p>
            Descriptions concern developing product and research directions. They are not
            warranties, security guarantees, professional advice, or commitments to deliver specific
            capabilities.
          </p>
        </LegalSection>
        <LegalSection title="Intellectual property">
          <p>
            Names, visual identity, and original content remain subject to applicable rights. No
            license is granted by viewing this website.
          </p>
        </LegalSection>
        <LegalSection title="Future terms">
          <p>
            Commercial terms require qualified legal review before a future product offering. No
            lawyer approval is asserted here. Contributions are voluntary and do not include a
            license, annual plan, product access, protection guarantee or delivery commitment;
            future pricing and eligibility will be announced separately.
          </p>
        </LegalSection>
      </LegalLayout>
    </PageShell>
  );
}
