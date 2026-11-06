import { z } from "zod";

export const DispaterXaeliSchema = z
  .object({
    now: z.string(),
    changed: z.string(),
    next: z.string(),
    why: z.string(),
    proof: z.string(),
  })
  .passthrough();

// Preserve additive fields at every object boundary: receipts authenticate the complete
// report structure, including metadata this client does not yet understand.
export const DispaterEvidenceIntegritySchema = z
  .object({
    qualification: z.string(),
    observation_state: z.string(),
    independent_root_count: z.number().int().nonnegative(),
    independent_verification: z.string(),
    source_root_sha256: z.string(),
    reasons: z.array(z.string()),
  })
  .passthrough();

export const DispaterFindingSchema = z
  .object({
    finding_id: z.string(),
    code: z.string(),
    subject: z.string(),
    severity: z.enum(["CRITICAL", "HIGH", "MEDIUM", "LOW", "ROUTINE"]),
    exposure_usd: z.string(),
    exposure_class: z.string().optional(),
    evidence: z.array(
      z
        .object({
          kind: z.string(),
          record_sha256: z.string(),
        })
        .passthrough(),
    ),
    evidence_integrity: DispaterEvidenceIntegritySchema.optional(),
    authority: z.string(),
    xaeli_explanation: DispaterXaeliSchema,
    finding_sha256: z.string(),
  })
  .passthrough();

export const DispaterReconciliationReportSchema = z
  .object({
    schema: z.string(),
    tenant_id: z.string(),
    dataset_sha256: z.string(),
    status: z.string(),
    authority_state: z.string(),
    human_review_required: z.boolean(),
    counts: z
      .object({
        jobs: z.number(),
        invoices: z.number(),
        rates: z.number(),
        payments: z.number(),
        findings: z.number(),
      })
      .passthrough(),
    financial_summary: z
      .object({
        identified_exposure_usd: z.string(),
        potential_underbilling_usd: z.string().optional(),
        potential_overbilling_usd: z.string().optional(),
        unverified_exposure_usd: z.string().optional(),
        human_confirmed_discrepancy_usd: z.string().optional(),
        confirmed_recovery_usd: z.string(),
        recovery_rate_disclaimer: z.string(),
      })
      .passthrough(),
    findings: z.array(DispaterFindingSchema),
    limits: z.string(),
    receipt_sha256: z.string(),
    run_id: z.string().optional(),
  })
  .passthrough();

export type DispaterFinding = z.infer<typeof DispaterFindingSchema>;
export type DispaterReconciliationReport = z.infer<typeof DispaterReconciliationReportSchema>;

export type DispaterDemoState =
  | { status: "IDLE" }
  | { status: "LOADING" }
  | { status: "SUCCESS"; report: DispaterReconciliationReport }
  | { status: "ERROR"; error: string };

// Presentation cannot independently authenticate receipts or establish trusted roots.
// Neither AUDIT_COMPLETE nor a supplied verification label grants authority.
export function getDispaterEvidencePresentation(finding: DispaterFinding) {
  const integrity = finding.evidence_integrity;
  return {
    verification: "NOT VERIFIED",
    freshness: "UNKNOWN",
    qualification: integrity?.qualification ?? "NOT VERIFIED",
    observationState: integrity?.observation_state ?? "UNKNOWN",
    independentRootCount: integrity?.independent_root_count ?? null,
    reportedVerification: integrity?.independent_verification ?? "NOT VERIFIED",
    sourceRootSha256: integrity?.source_root_sha256 ?? null,
    reasons: integrity?.reasons ?? ["Legacy report: verification metadata is absent."],
  };
}
