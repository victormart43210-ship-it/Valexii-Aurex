# VALEXII.AI website audit and newsletter approval plan

## Verified current state

- **Primary live site:** `https://valexii.com` returns 200 and is the project’s active primary custom domain. The Lovable URL redirects to it.
- **`www` is broken:** `www.valexii.com` is marked drifted and does not resolve publicly. Its expected A and verification TXT records are missing. No DNS change is part of this plan.
- **`valexi.com` is unrelated:** it is not connected to this project and currently uses Afternic nameservers. Ownership is unknown; do not redirect, brand, or canonicalize it.
- **Canonical mismatch:** every inspected content route still declares `https://valexii-ai.lovable.app/...` as canonical and `og:url`, although public traffic resolves at `https://valexii.com/...`.
- **Published-versus-preview drift:** the live Support page still shows “$50+ founding support,” while the current project source contains newer support wording. Future review must compare preview and production before publication.
- **Publication wording:** the Terms page does not currently say “unpublished.” It does call the offering a “Prototype,” the Privacy page calls it a “preview,” and the footer says “Private prototype.” Those labels conflict with a publicly reachable marketing site unless narrowed to the developmental product/demo rather than the website itself.
- **Navigation and links:** all internal route references resolve to existing route files. Live Home, Support, Contact, Terms, Privacy, Research, Voynich, and Decipherment pages returned 200 without runtime errors. Mobile Support at 393px had no horizontal overflow and its principal controls measured 44px high. A complete manual keyboard/screen-reader audit is still required.
- **Forms and newsletter:** Contact only composes a `mailto:` draft; nothing is sent or stored by the site. The Weekly Research Dispatch also opens a prefilled email draft. No mailing-list capture, confirmed subscription record, delivery system, or automated unsubscribe exists.
- **Analytics test mode:** browser-local internal QA exclusion exists under `valexii-internal-test`; it excludes only the custom activation events and logs them locally. No activation adapter is connected, so those public events are not measured. Lovable hosting analytics remain separate and still count test visits; prior traffic cannot be retroactively separated.
- **Research pages:** `/research`, `/voynich`, `/decipherment`, and `/evaluation` exist. Voynich is explicitly HOLD/not deciphered; Linear A and Rongorongo are listed as research/not established rather than having dedicated pages. Supporting artifacts and independent replication are not attached. The Voynich page includes prior internally reported numerical findings with evidence-required labels; the Rongorongo card includes a specific Mamari/lunar-calendar direction that needs source support before newsletter promotion.

## Prioritized defects

### P0 — Truth, ownership, and consent

1. Change route canonicals and `og:url` to `https://valexii.com`, never `valexi.com`, after confirming the apex remains the intended primary host.
2. Reframe “Private prototype,” “preview,” and generic “Prototype” wording so it accurately describes developmental products/research, not a supposedly unpublished website.
3. Do not call the current mailto request a completed subscription. Define who records consent, how confirmation occurs, what address sends the newsletter, and how unsubscribe requests are actioned before launch.
4. Keep all manuscript claims separated into **Finding**, **Hypothesis**, **Open question**, and **Not established**. Governance atop LLMs may organize evidence, provenance, counterchecks, and reproducibility; it does not validate a translation.

### P1 — Discoverability and consistency

1. Give the newsletter a clear public scope: weekly, opt-in, Voynich Manuscript, Linear A, and Rongorongo, with occasional methodology notes.
2. Add direct research-track navigation without implying that Linear A or Rongorongo has a dedicated evidence record until one exists.
3. Align Home and Support newsletter wording, consent language, cadence, confirmation, and unsubscribe instructions from one shared copy source.
4. Resolve the live/preview Support mismatch before publishing any newsletter changes.

### P2 — Quality verification

1. Recheck all routes at 320/393/768/1440px for clipping, contrast, focus order, tap sizes, reduced motion, headings, and link purpose.
2. Test mobile navigation, browser Back, mailto fallbacks, Cash App external links, newsletter request links, and Contact draft composition without sending.
3. Validate metadata and structured data on the production host after an approved publish; external SEO and assistive-technology behavior cannot be proven from source alone.

## Draft newsletter copy for approval — not for posting yet

### Sign-up block

**Weekly Manuscript Research Dispatch**

Opt in to a weekly email covering ongoing computational research into the Voynich Manuscript, Linear A, and Rongorongo. Each issue will distinguish observed findings, working hypotheses, unresolved questions, and evidence still required. Source and evidence links will be included when publicly available.

VALEXII’s governed-intelligence methods can help organize hypotheses, provenance, counterchecks, and reproducible tests. They do not prove a translation. No manuscript is presented as solved, and no independent validation is claimed unless it is specifically linked and verifiable.

**Button:** Request weekly email opt-in

**Consent note:** Opens an email draft to request enrollment. Nothing is sent or subscribed automatically. Enrollment requires confirmation. You may unsubscribe at any time by replying with “unsubscribe” or emailing `developer@valexii.com` with the subject “Unsubscribe Research Dispatch.”

### Editorial labels for every issue

- **FINDING:** an observation with linked method and evidence; scope and limitations stated.
- **HYPOTHESIS:** a testable interpretation, not a translation.
- **OPEN QUESTION:** evidence is incomplete or competing explanations remain.
- **HOLD / NOT ESTABLISHED:** required qualification, reconstruction, or independent replication is absent.
- **CORRECTION:** a prior statement was changed, with the reason and provenance preserved.

### Suggested issue structure

1. **This week’s evidence** — concise observations with source links.
2. **What we tested** — method, corpus/version, counterchecks, and reproducibility notes.
3. **Findings vs hypotheses** — visibly separated.
4. **What could falsify this** — alternative explanations and missing evidence.
5. **Track notes** — Voynich, Linear A, Rongorongo; omit a track when there is no substantive update.
6. **Corrections and provenance** — changes to prior issues and stable source references.
7. **Next review** — planned questions, not promised discoveries.

### Notification language

Use: “Subscribers receive the weekly public research summary and material updates when available.”

Avoid: “Be first to know,” “exclusive access,” “breakthrough alerts,” “decipherment updates,” or any priority promise suggesting privileged or validated knowledge.

## Implementation plan after copy approval

1. Finalize the exact newsletter name, sender identity, consent record owner, confirmation process, and unsubscribe service level.
2. Update canonical metadata to the confirmed `valexii.com` host and correct public/prototype wording across shared footer, Terms, Privacy, Home, and Support.
3. Add the approved newsletter block using the existing honest mailto flow unless a separately approved consent-capable provider is selected; do not imply automatic enrollment.
4. Add a concise newsletter policy to Privacy covering voluntary email processing, purpose, cadence, unsubscribe, retention, and any provider actually used.
5. Add shared research-status labels and source-link requirements; review specific Voynich numbers and Rongorongo/Linear A statements before they can appear in an issue.
6. Keep internal-test mode private and documented; state plainly that hosting analytics cannot currently exclude owner traffic.
7. Run link, metadata, mobile, keyboard, automated accessibility, runtime, and preview-versus-live checks. Present the preview for approval before any publish or email.

## Manual verification required before implementation or launch

- Confirm `valexii.com` should replace the Lovable URL in all canonical/social metadata.
- Decide whether to repair `www.valexii.com`; it is currently offline. No action is needed for unowned `valexi.com`.
- Approve or revise the draft newsletter copy above.
- Name the responsible sender/list owner and the real process for confirmation, removal, bounced mail, complaints, and consent records.
- Provide public source/evidence links for any research claim promoted beyond hypothesis/HOLD.
- Obtain privacy/legal review for newsletter consent, retention, international recipients, and unsubscribe handling; this audit is not legal advice.

## Boundaries

No code, publication, DNS/domain setting, email, subscription, analytics integration, or backend change occurs until the newsletter copy and implementation are separately approved.
