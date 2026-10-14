/** AUREX capability registry and fail-closed status/budget rules. Browser-safe, pure. */
export type CapabilityStatus = "REAL_CONNECTED" | "NOT_CONFIGURED" | "PLANNED";
/** website = exists in this site; service = needs external AUREX service; future = no implementation yet */
export type CapabilityKind = "website" | "service" | "future";

export interface Capability {
  id: string;
  name: string;
  kind: CapabilityKind;
  summary: string;
  restricted?: boolean;
}

const s = (id: string, name: string, summary: string, restricted = false): Capability => ({
  id,
  name,
  kind: "service",
  summary,
  restricted,
});
const f = (id: string, name: string, summary: string, restricted = false): Capability => ({
  id,
  name,
  kind: "future",
  summary,
  restricted,
});

export const capabilities: readonly Capability[] = [
  {
    id: "private-command-center",
    name: "Private Command Center",
    kind: "website",
    summary: "Owner-only console with server-verified access.",
    restricted: true,
  },
  {
    id: "website-claims-auditor",
    name: "Website health & claims auditor",
    kind: "website",
    summary: "Owner-run allowlisted page health audit; claim review remains manual.",
    restricted: true,
  },
  {
    id: "repo-metadata",
    name: "Public source metadata",
    kind: "website",
    summary: "Read-only public GitHub branch, commit and CI facts.",
  },
  s("sovereign-computing", "Sovereign computing", "Run research on owner-controlled hardware."),
  s("memory-graph", "Memory graph", "Linked records of sources, claims and decisions."),
  s("semantic-memory", "Semantic memory", "Similarity search over approved research records."),
  s("evidence-vault", "Evidence vault", "Provenance-tracked storage of evidence artifacts."),
  s("model-router", "Model router", "Select models per task within budget limits."),
  s(
    "model-benchmarking",
    "Model benchmarking",
    "Repeatable model comparisons with item-level records.",
  ),
  s("hypothesis-testing", "Hypothesis testing", "Pre-registered tests with held-out evaluation."),
  s(
    "adversarial-council",
    "Adversarial council",
    "Separate challenge perspectives; not proof of independence.",
  ),
  s("research-swarm", "Research swarm", "Coordinated bounded research tasks."),
  s(
    "regression-hunter",
    "Regression hunter",
    "Detect performance or behavior regressions between runs.",
  ),
  s("code-archaeology", "Code archaeology", "Trace history and intent across repositories."),
  s(
    "unix-workers",
    "Unix workers",
    "Sandboxed allowlisted jobs on the AUREX service; never a public shell.",
    true,
  ),
  s(
    "python-lab",
    "Python lab",
    "Sandboxed vetted notebooks on the AUREX service; no arbitrary execution from the website.",
    true,
  ),
  s(
    "private-research-api",
    "Private research API",
    "Authenticated server-to-server AUREX API.",
    true,
  ),
  s(
    "offline-intelligence",
    "Offline intelligence",
    "Local-only operation without network dependence.",
  ),
  f("digital-twin", "Digital twin", "Modeled system replicas for scenario testing."),
  f(
    "scientific-discovery",
    "Scientific discovery",
    "Structured hypothesis generation from open data.",
  ),
  f(
    "model-distillation",
    "Model distillation",
    "Smaller task models trained from approved outputs.",
  ),
  f(
    "temporal-intelligence",
    "Temporal intelligence",
    "Freshness, ordering and time-aware evidence reasoning.",
  ),
  f(
    "patent-evidence-mapping",
    "Patent evidence mapping",
    "Map evidence to claims for counsel review; not legal advice.",
    true,
  ),
  f(
    "reverse-engineering",
    "Reverse engineering (authorized only)",
    "Only on owned or explicitly authorized targets.",
    true,
  ),
  f(
    "controlled-self-improvement",
    "Controlled self-improvement",
    "Proposed changes gated by tests and human approval.",
  ),
  {
    id: "cost-governor",
    name: "Cost governor",
    kind: "website",
    summary: "Server-enforced spend limit; default budget is zero (no spend).",
  },
];

export interface BackendChecks {
  /** true only after an authenticated health check of the AUREX service succeeded */
  serviceHealthy: boolean;
  /** capability ids the healthy service explicitly reports as available */
  serviceCapabilities: readonly string[];
}

export const NO_BACKEND: BackendChecks = { serviceHealthy: false, serviceCapabilities: [] };

export function resolveStatus(
  cap: Capability,
  checks: BackendChecks = NO_BACKEND,
): CapabilityStatus {
  if (cap.kind === "website") return "REAL_CONNECTED";
  if (cap.kind === "future") return "PLANNED";
  return checks.serviceHealthy && checks.serviceCapabilities.includes(cap.id)
    ? "REAL_CONNECTED"
    : "NOT_CONFIGURED";
}

/** Server-enforced budget contract. Missing/invalid budget = 0 = deny all spend. */
export function authorizeSpend(input: {
  estimateUsd: number;
  spentUsd: number;
  budgetRaw: string | undefined;
}): { allowed: boolean; reason: string; budgetUsd: number } {
  const b = Number(input.budgetRaw);
  const budgetUsd = Number.isFinite(b) && b > 0 ? b : 0;
  if (!(input.estimateUsd >= 0) || !(input.spentUsd >= 0))
    return { allowed: false, reason: "Invalid estimate.", budgetUsd };
  if (budgetUsd === 0)
    return {
      allowed: input.estimateUsd === 0,
      reason: input.estimateUsd === 0 ? "No-cost action." : "No-spend default: budget is zero.",
      budgetUsd,
    };
  if (input.spentUsd + input.estimateUsd > budgetUsd)
    return { allowed: false, reason: "Budget would be exceeded.", budgetUsd };
  return { allowed: true, reason: "Within budget.", budgetUsd };
}
