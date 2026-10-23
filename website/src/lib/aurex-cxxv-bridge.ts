/** KUSANAGI CXXV — candidate-only, pure AUREX/OX contract bridge.
 * No fetch, jobs, inference, accounts, billing, or authorization effects.
 * These schemas describe staged interoperability; they do not announce deployment.
 */
import { z } from "zod";
import {
  BudgetSchema,
  CapabilitiesSchema,
  EvidenceListSchema,
  JobListSchema,
  capabilityBacked,
} from "./aurex-api-schema";

export const CXXV_CONTRACT_VERSION = "aurex-cxxv-candidate-v1";
export const CXXV_SOURCE = "PR104+PR106+PR107_UNMERGED" as const;
const wholeCents = z.number().int().positive().max(100_000_000);
const rateCents = z.number().int().positive().max(10_000_000);

export const SyntheticFieldCaseSchema = z.object({
  case_id: z.string().regex(/^BETA-[0-9]{3}$/),
  invoice_id: z.string().regex(/^INV-[0-9]{4}$/),
  invoice_cents: wholeCents,
  ticket_cents: wholeCents,
  approved_rate_cents_per_hour: rateCents.nullable(),
  documented_hours: z.number().int().min(1).max(10_000),
  synthetic: z.literal(true),
}).strict();

export const SyntheticFieldBatchSchema = z.array(SyntheticFieldCaseSchema)
  .min(1).max(100)
  .superRefine((rows, ctx) => {
    const cases = new Set<string>();
    for (const [index, row] of rows.entries()) {
      if (cases.has(row.case_id)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: [index, "case_id"],
          message: "Duplicate case ID",
        });
      }
      cases.add(row.case_id);
    }
  });

export type SyntheticFieldCase = z.infer<typeof SyntheticFieldCaseSchema>;

/** Local validation for PR #104's Python reconcile_field_cases input contract.
 * Never emits a request or implies an audit was performed. The Python engine
 * retains exclusive ownership of deterministic reconciliation and findings.
 */
export function stageSyntheticFieldAudit(value: unknown):
  | { status: "HOLD"; authority: "NONE"; reason: "INVALID_OR_NON_SYNTHETIC_INPUT" }
  | { status: "STAGED"; authority: "NONE"; release: "HOLD"; version: string; cases: SyntheticFieldCase[] } {
  const parsed = SyntheticFieldBatchSchema.safeParse(value);
  if (!parsed.success) {
    return { status: "HOLD", authority: "NONE", reason: "INVALID_OR_NON_SYNTHETIC_INPUT" };
  }
  return {
    status: "STAGED", authority: "NONE", release: "HOLD",
    version: CXXV_CONTRACT_VERSION, cases: parsed.data,
  };
}

export const NVIDIA_BRIDGE_CANDIDATES = [
  { id: "nvidia_document_intelligence", name: "NVIDIA Document Intelligence", sourcePr: 106 },
  { id: "quantitative_signal_discovery", name: "Quantitative Signal Discovery Agent", sourcePr: 107 },
  { id: "transaction_foundation_model", name: "Transaction Foundation Model", sourcePr: 107 },
  { id: "financial_model_distillation", name: "Financial Model Distillation", sourcePr: 107 },
  { id: "financial_fraud_detection", name: "Financial Fraud Detection", sourcePr: 107 },
] as const satisfies ReadonlyArray<{ id: string; name: string; sourcePr: number }>;

export type CandidateId = typeof NVIDIA_BRIDGE_CANDIDATES[number]["id"];
export type CandidateState = {
  id: CandidateId;
  sourcePr: number;
  runtime: "NOT DEPLOYED";
  inference: "NOT RUN";
  independentVerification: "NOT VERIFIED";
  financialEffect: "NONE";
  authority: "NONE";
  release: "HOLD";
};

/** Static review catalog only; never deduce availability from a draft PR's CI. */
export function candidateRegistry(): CandidateState[] {
  return NVIDIA_BRIDGE_CANDIDATES.map((candidate) => ({
    id: candidate.id,
    sourcePr: candidate.sourcePr,
    runtime: "NOT DEPLOYED",
    inference: "NOT RUN",
    independentVerification: "NOT VERIFIED",
    financialEffect: "NONE",
    authority: "NONE",
    release: "HOLD",
  }));
}

export const OX_WORKSTATION_SECTIONS = [
  "Intelligence Map", "Execute", "Evidence", "Context", "Agents",
  "Jobs", "Models", "Security", "Analytics", "Nexus",
] as const;

export const CXXV_PROJECTION = z.object({
  capabilities: CapabilitiesSchema,
  evidence: EvidenceListSchema,
  budgets: BudgetSchema,
  jobs: JobListSchema,
  checkedAt: z.string().datetime({ offset: true }),
}).strict();

/** Project service-reported data only. Linked evidence is NOT a separate
 * cryptographic witness; even 'supported' stays NOT VERIFIED.
 */
export function projectWorkstationCandidate(input: unknown, now = Date.now()) {
  const parsed = CXXV_PROJECTION.safeParse(input);
  if (!parsed.success || !Number.isFinite(now)) {
    return { status: "HOLD" as const, authority: "NONE" as const, source: "INVALID_OR_MISSING" as const };
  }
  const { capabilities, evidence, budgets, jobs, checkedAt } = parsed.data;
  const observed = Date.parse(checkedAt);
  const recent = Number.isFinite(observed) && observed <= now + 5000
    && now - observed < 90_000;
  if (!recent) {
    return { status: "HOLD" as const, authority: "NONE" as const, source: "STALE_OR_FUTURE" as const };
  }
  return {
    status: "REACHABLE_NOT_VERIFIED" as const,
    authority: "NONE" as const,
    release: "HOLD" as const,
    source: "SERVICE_REPORTED_NOT_INDEPENDENTLY_VERIFIED" as const,
    budgetLimitUsd: budgets.limitUsd,
    jobCount: jobs.jobs.length,
    supportedLinkCount: capabilities.capabilities.filter((c) =>
      capabilityBacked(c, evidence.evidence, now)).length,
    independentVerification: "NOT VERIFIED" as const,
    modelRuntime: "NOT DEPLOYED" as const,
    tabs: OX_WORKSTATION_SECTIONS,
  };
}
