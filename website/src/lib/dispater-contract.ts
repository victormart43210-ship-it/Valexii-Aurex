import { z } from "zod";

export const DispaterXaeliSchema = z.object({
  now: z.string(),
  changed: z.string(),
  next: z.string(),
  why: z.string(),
  proof: z.string(),
});

export const DispaterFindingSchema = z.object({
  finding_id: z.string(),
  code: z.string(),
  subject: z.string(),
  severity: z.enum(["CRITICAL", "HIGH", "MEDIUM", "LOW", "ROUTINE"]),
  exposure_usd: z.string(),
  exposure_class: z.string().optional(),
  evidence: z.array(
    z.object({
      kind: z.string(),
      record_sha256: z.string(),
    }),
  ),
  authority: z.string(),
  xaeli_explanation: DispaterXaeliSchema,
  finding_sha256: z.string(),
});

export const DispaterReconciliationReportSchema = z.object({
  schema: z.string(),
  tenant_id: z.string(),
  dataset_sha256: z.string(),
  status: z.string(),
  authority_state: z.string(),
  human_review_required: z.boolean(),
  counts: z.object({
    jobs: z.number(),
    invoices: z.number(),
    rates: z.number(),
    payments: z.number(),
    findings: z.number(),
  }),
  financial_summary: z.object({
    identified_exposure_usd: z.string(),
    potential_underbilling_usd: z.string().optional(),
    potential_overbilling_usd: z.string().optional(),
    unverified_exposure_usd: z.string().optional(),
    human_confirmed_discrepancy_usd: z.string().optional(),
    confirmed_recovery_usd: z.string(),
    recovery_rate_disclaimer: z.string(),
  }),
  findings: z.array(DispaterFindingSchema),
  limits: z.string(),
  receipt_sha256: z.string(),
  run_id: z.string().optional(),
});

export type DispaterFinding = z.infer<typeof DispaterFindingSchema>;
export type DispaterReconciliationReport = z.infer<typeof DispaterReconciliationReportSchema>;

export type DispaterDemoState =
  | { status: "IDLE" }
  | { status: "LOADING" }
  | { status: "SUCCESS"; report: DispaterReconciliationReport }
  | { status: "ERROR"; error: string };

export const DispaterAuditPackageRequestSchema = z.object({
  tenant_id: z.string().min(1).max(64),
  documents: z.array(z.record(z.any())).default([]),
  vehicles: z.array(z.record(z.any())).default([]),
  drivers: z.array(z.record(z.any())).default([]),
  include_reconciliation_report: z.boolean().default(true),
});
export type DispaterAuditPackageRequest = z.infer<typeof DispaterAuditPackageRequestSchema>;
