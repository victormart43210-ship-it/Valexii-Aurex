import { createFileRoute } from "@tanstack/react-router";
import { LegalLayout, LegalSection, PageShell } from "@/components/site";
export const Route = createFileRoute("/privacy")({
  head: () => ({
    meta: [
      { title: "Privacy Draft — VALEXII.AI" },
      {
        name: "description",
        content:
          "Draft privacy notice for VALEXII.AI’s public research and development website, voluntary support links and optional communications. Legal review pending.",
      },
      { property: "og:title", content: "Privacy Draft — VALEXII.AI" },
      { property: "og:description", content: "Draft privacy notice subject to legal review." },
      { property: "og:url", content: "https://valexii.com/privacy" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
    links: [{ rel: "canonical", href: "https://valexii.com/privacy" }],
  }),
  component: Privacy,
});
function Privacy() {
  return (
    <PageShell>
      <LegalLayout
        label="Legal draft"
        title="Privacy"
        updated="13 October 2026 · editorial revision, legal review pending"
      >
        <LegalSection title="Public website status">
          <p>
            This public research and development website does not activate account creation,
            newsletter enrollment, or a custom analytics service. Cash App support opens an external
            service. Contact, partnership and BCXMET early-access forms store what you submit.
          </p>
        </LegalSection>
        <LegalSection title="Optional usage events">
          <p>
            Optional activation events are off by default and no measurement service is connected.
            The footer lets you allow or withdraw consent. Only allowlisted event names and coarse
            page/scroll categories could reach an approved adapter; no messages, phone numbers, app
            inventories, raw URLs or visitor identifiers are collected by these hooks.
          </p>
          <p>
            Consent preference is saved locally. If allowed, a yes/no visit marker supports a
            return-session event; withdrawing removes it. No events are buffered or sent while
            disconnected. Existing hosting analytics are separate and require legal review.
          </p>
        </LegalSection>
        <LegalSection title="Information you enter">
          <p>
            Contact and partnership forms store your name, email, optional organization, category
            and message so a person can reply. BCXMET early-access requests store your email,
            optional device description and consent time; enrollment requires confirmation by email
            when delivery is available. Stored interest is not enrollment. Submissions are readable
            only by server code, not by other visitors. IP addresses are used briefly to limit abuse
            and are not stored. When email delivery is active, a notification goes to
            developer@valexii.com and a confirmation to you. To access or delete your data, email
            developer@valexii.com. Do not include sensitive device data.
          </p>
        </LegalSection>
        <LegalSection title="The Decipherment Frontier">
          <p>
            Newsletter signup is not connected. The website does not currently collect, save, or add
            email addresses to a mailing list. Before signup opens, this notice must be updated with
            the actual provider, purpose, confirmation, retention, and unsubscribe process.
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
        <LegalSection title="Future services">
          <p>
            Any future collection, use, retention, or sharing practices will require a reviewed
            notice appropriate to the activated services and applicable law.
          </p>
        </LegalSection>
        <LegalSection title="Contact">
          <p>
            For privacy questions, email developer@valexii.com. A formal rights-request process and
            hosting-provider data practices still require legal review; no reviewed compliance
            program is claimed.
          </p>
        </LegalSection>
      </LegalLayout>
    </PageShell>
  );
}
