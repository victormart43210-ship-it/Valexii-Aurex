# BCXMET UX convergence & experiment plan

## Evidence boundary — 10 October 2026

This pass targets activation, not measured retention. Public homepage patterns are
observations supplied by the project owner after their independent Firecrawl review;
they are not experiments proving a cause of conversion. This implementation did not
independently reproduce that scrape. Competitor private analytics, cohorts, conversion
rates and acquisition mix are unobservable from these public pages.

## Site-by-site public observations and sources

| Public source                                              | Owner-reported visible pattern                                                                  | BCXMET experiment hypothesis                                                                |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [Truecaller](https://www.truecaller.com/)                  | Immediate Scam Checker, educational scam quiz, video, simple feature links                      | An original educational exercise may make evidence review easier to discover.               |
| [Malwarebytes](https://www.malwarebytes.com/)              | App-in-context imagery, malware/scam proposition, download/plan actions, category illustrations | Editable phone plus explicit call/app entries may clarify product intent. No fake download. |
| [Bitdefender](https://www.bitdefender.com/en-us/consumer/) | Large brand visual, audience/plan segmentation, comparisons, category taxonomy                  | Two featured entries followed by five journeys may clarify choices. No invented plans.      |
| [Avast](https://www.avast.com/)                            | OS-specific pathways                                                                            | State Android scope without implying installed capabilities.                                |
| [Norton](https://www.norton.com/)                          | International region routes                                                                     | Keep scope legible; do not invent regional availability.                                    |

## Aggregate benchmark, not competitor or BCXMET analytics

Owner-reported Contentsquare 2026 figures: 99 billion sessions / 6,500 sites;
approximately 70% mobile traffic; product-detail pages approximately 40% of views;
61% PDP bounce; 13% aggregate 30-day return. These figures were not independently
confirmed in this pass and must retain that provenance. Aggregate mix, definitions,
sampling and industry differences prevent a site-specific target or competitor inference.
Sources: [engagement guide](https://contentsquare.com/guides/digital-experience-benchmark/engagement/)
and [report](https://go.contentsquare.com/en/digital-experience-benchmark).
Desktop depth is a reported general observation, not evidence of this site's preferences.

## Lovable baseline — reported, not independently audited

Owner's Oct 1–10 snapshot: 25 visitors, 41 pageviews, 1.64 views/visit, reported
97% bounce, 2 BCXMET visit/page records versus 15 homepage records. Session-duration
total 37 has an unknown unit. Desktop 19 / mobile 5 leaves one potentially unclassified.
These are dashboard aggregates, not an identity-linked cohort. Small sample and uncertain
record definitions cannot establish retention, preference or uplift. Post-change activation
and retention: **NOT MEASURED**.

## Discovery funnel and event semantics

### Published demo and retention research — checked 10 October 2026

Read the public [Navattic 2026 demo report](https://www.navattic.com/report/state-of-the-interactive-product-demo-2026)
and [Contentsquare retention guide](https://contentsquare.com/guides/digital-experience-benchmark/retention/).
Navattic describes short, choice-based flows and recommends balancing depth with
completion, including a 5–13-step flow range. Its dataset comparisons are observational,
not randomized proof that a particular tour length causes uplift. The retrieved public
text did not establish a quantified gated-versus-ungated effect.
Contentsquare discusses repeat visits, device differences and continuity across devices;
aggregate returning-visitor comparisons cannot establish causality or BCXMET retention.
No published benchmark is adopted as this site's measured result or target.

Applied as a testable UX hypothesis: keep entry ungated and above-fold CTAs, with
two selectable evidence tours, six desktop steps and five compact mobile steps.
Both devices show the same authored evidence, permissions and unresolved-authority
boundaries. No identity, synced login, personal tracking or additional service is added.
Activation and retention remain **NOT MEASURED**.

1. See value: `hero_call_click`, `hero_malware_click`, `command_open`.
2. Interact: `call_demo_start`, `malware_demo_start`, `quiz_start`.
3. Review: `proof_view`, `xaeli_explain`; `call_demo_finish` / `malware_demo_finish`
   mean explicitly opening proof after starting the corresponding fixture, not defense success.
   `quiz_finish` means completing both questions, not passing a security qualification.
4. Optional interest: `beta_interest` means opening Contact, not receiving email or enrollment.
5. `return_visit` is only a consented browser seen-marker signal, not D1/D7/D30 retention.

Legacy allowlisted events remain for compatibility. Consent defaults off. No endpoint,
provider, queue, phone numbers, app inventory, messages, visitor ID or raw URL is configured.
Only coarse page category and optional scroll bucket accompany an event. No event is
collected by these hooks without both consent and a configured adapter. Hosting analytics
is separate; this implementation cannot attest its compliance. Withdrawal clears visit markers.

## Proposed cohorts — definitions, not implemented measurement

Define an eligible consented first visit as cohort day 0 (UTC). D1/D7/D30 exact-day
return: eligible users with a qualifying visit on UTC cohort day +1/+7/+30 divided by
eligible cohort users with a fully elapsed observation window. Exclude bots/test traffic;
document consent loss, identity resets and incomplete windows. Report exact-day return
separately from a cumulative “returned within 30 days” metric; they are not equivalent.
The current anonymous adapter cannot reliably deduplicate people or connect day-level
cohorts. Do not silently add identifiers: approve a privacy-preserving provider, legal
basis, consent behavior, minimal retention and deletion policy first.

## Proposed A/B test — not running

Control: previous call/app entry labels. Variant: Call Shield / Malware Shield plus
Command Center discovery, keeping evidence warnings and support unchanged.
Primary outcome: consented eligible visits reaching fixture start then explicit proof review.
Secondary: quiz completion and Contact opens; neither means subscription or protection.
Guardrails: accessibility errors, mobile overflow, loading performance, consent refusal,
unwanted navigation and misunderstanding of simulation. Assign consistently only after
an approved measurement design; do not implement silent persistent assignment now.
Pre-register sample size, minimum detectable effect, allocation, exclusions and observation
window with statistical review. No invented uplift, significance, target conversion or winner.

## Capability and release blockers

Implemented presentation: clickable website screens, authored evidence drill-downs,
quiz feedback and decorative SVG. Android screening/detection/efficacy remain under
development and unverified; independent device evidence is absent. Exact requested
hero and editorial portrait were installed 10 October 2026 from user-supplied originals.
Research attachments and legal review are pending.
No publication, DNS, payments, email delivery or Android authority change is authorized.
