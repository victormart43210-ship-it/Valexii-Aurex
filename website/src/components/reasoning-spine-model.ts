/** Public architectural intent. This copy cannot authorize an effect. */
export const spineFlow = "EVIDENCE → QUALIFICATION → REALITY → AUTHORITY → EFFECT";
export const reverseFlow = "Result → Authority → Truth → Admissibility → Source";
export const spineStages = [
  {
    name: "Evidence",
    question: "What was observed?",
    detail:
      "Record what was observed, where it came from, when it was collected and what it cannot tell us. A statement without a traceable source is not established evidence.",
    example: "Example: an Android permission-change record, not a claim that the app is malicious.",
  },
  {
    name: "Qualification",
    question: "Can we rely on it here?",
    detail:
      "Check source integrity, relevance, freshness and permitted use. Missing, stale or unverified evidence never counts as PASS; disagreement stays HOLD for human review.",
    example:
      "Example: an old scan may describe an earlier state, but cannot establish the state of the phone now.",
  },
  {
    name: "Reality",
    question: "What is supported?",
    detail:
      "Distinguish measured reality from hypotheses. Advocate makes the strongest supported case; Challenger tests alternatives; Arbiter checks whether requirements are met. Independent witnesses must support consequential claims; three roles alone do not establish independence.",
    example:
      "Example: compare an expected app update with a suspicious change. If neither account is supported, keep the conclusion unknown.",
  },
  {
    name: "Authority",
    question: "What is permitted now?",
    detail:
      "Check domain permissions, scope, fresh evidence, human approval where required, and a valid time-limited authorization lease. Expiry or revocation stops future permission. Recheck these gates at effect time; historical evidence is not present authorization.",
    example:
      "Example: yesterday’s approval does not authorize a changed action today. Human control remains the boundary for irreversible actions.",
  },
  {
    name: "Effect",
    question: "What happened within bounds?",
    detail:
      "Only after the earlier gates pass may an authorized, bounded effect proceed. Record its outcome separately from the proposal; verify that outcome through evidence beyond the system’s own assertion.",
    example:
      "Example: record the result of an approved action and independently inspect its scope. This website performs no security action.",
  },
] as const;

export const spineContexts = {
  home: {
    title: "An answer should show what holds it up.",
    copy: "Intelligence should answer to evidence—and to people. Our design follows Evidence → Qualification → Reality → Authority → Effect: gather observations, check their quality, test what they support, confirm permission and inspect the outcome.",
    application:
      "One portable reasoning design, three separate application boundaries: BCXMET mobile security, DISPATER subsurface operations and XAITA capital analysis. Reuse is architectural intent, not verified cross-domain functionality.",
  },
  system: {
    title: "One reasoning spine, domain-specific safeguards.",
    copy: "Follow the observation, test its support, then check permission. This evidence-governed framework is intended for VALEXII applications; it is a design contract, not a claim that every gate is operational.",
    application:
      "Domain-specific adapters translate local observations and rules. They may carry structured context and evidence references, but permissions, authorization leases and security authority do not transfer between domains.",
  },
  bcxmet: {
    title: "How the spine applies here",
    copy: "BCXMET is designed to explain Android security observations before proposing a response. A changed permission is a reason to investigate—not proof of malware.",
    application:
      "The framework would qualify mobile evidence, compare expected changes with adversarial explanations, and check current Android permissions and human authority before a bounded action. The phone, radar and scan cards here share simulated fixtures; they do not scan, block or protect a device.",
  },
  xaeli: {
    title: "How the spine applies here",
    copy: "XAELI is the planned explanation layer: what was observed, what it supports, what is missing and what you can review next. Website examples are scripted, not connected AI answers.",
    application:
      "The abstract Orb presents state; it never supplies evidence or authorization. Advocate, Challenger and Arbiter describe reasoning checks, not independent security agents. XAELI’s explanation cannot grant itself permission to act.",
  },
  aurex: {
    title: "What would prove the design wrong?",
    copy: "AUREX is an experimental research and reasoning evaluation lab. It explores evidence handling through reproducible questions, adversarial cases, model limits and abstention.",
    application:
      "Its role is to support independent adversarial evaluation, not arbitrate BCXMET product security. An internally produced test is not an independent witness. Protocols, item-level records and external replication are required before promoting a performance claim.",
  },
  dispater: {
    title: "How the spine applies here",
    copy: "For subsurface operations, a measured signal and an inferred geological model are different kinds of information. The reasoning framework is intended to keep that difference visible.",
    application:
      "A DISPATER domain adapter would qualify source and calibration context, challenge interpretations, and check local operational permissions before bounded recommendations. No resource discovery, machinery control or verified environmental outcome is claimed. Functionality remains unverified.",
  },
  xaita: {
    title: "How the spine applies here",
    copy: "For capital analysis, a market observation is not a trading decision. The reasoning framework is intended to preserve sources, competing interpretations and the limits of a conclusion.",
    application:
      "A XAITA domain adapter would check timing and admissibility, distinguish observations from forecasts, and retain capital-specific permissions. BCXMET security authority cannot authorize financial effects. No live trading, custody, advice or verified returns are offered.",
  },
  ecosystem: {
    title: "Shared architecture is a hypothesis to test.",
    copy: "The Unified Reasoning Spine is the canonical shared backbone; BCXMET, DISPATER and XAITA remain distinct developmental applications, with XAELI explaining evidence and limits.",
    application:
      "Portable structured context is architectural intent. Each domain adapter retains its own evidence requirements, permissions and authority. A supported conclusion in one domain cannot become authorization in another.",
  },
  evaluation: {
    title: "Measure the failure, not just the answer.",
    copy: "Evaluation asks whether evidence was admitted correctly, alternatives survived challenge, and unsupported consequences remained contained.",
    application:
      "Internal synthetic tests can expose failures; they cannot certify phone protection or official benchmark standing. AUREX supports adversarial evaluation, while independent witnesses and inspectable artifacts remain separate requirements.",
  },
  research: {
    title: "A promising pattern must survive a rival explanation.",
    copy: "Evidence-aware reasoning connects observations to qualified claims without treating an attractive hypothesis as measured reality. That distinction matters in both evaluation and manuscript research.",
    application:
      "Voynich, Linear A and Rongorongo remain research tracks, not verified translations. Corpus provenance, matched comparisons, held-out prediction and independent replication are required before promotion. Research results never confer device-security authority.",
  },
  collaboration: {
    title: "A roadmap with questions, not hidden assumptions.",
    copy: "Investors welcome. Grant assistance, university research and independent review are welcome too. The useful next step is a scoped question and the evidence needed to answer it.",
    application:
      "The opportunity is to test reusable architecture and a cross-domain product vision—not assume operational capability, returns or traction. The 10,000 retained-user target is not an achieved result. No filed grant, approved award or existing partnership is asserted.",
  },
  contact: {
    title: "Start with a question we can test.",
    copy: "Ask about the Unified Reasoning Spine, independent evaluation or a domain-specific application. Investors and grant collaborators are welcome; begin with non-confidential information.",
    application:
      "We can discuss public design without exposing private repositories or unpublished patentable details. The contact form stores your inquiry and separately reports whether an email was sent. A saved message is not proof of email delivery.",
  },
} as const;
export type SpineContext = keyof typeof spineContexts;
