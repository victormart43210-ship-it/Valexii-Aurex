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
  exposure_event_id: z.string().optional(),
  qualification: z.string().optional(),
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
    withheld_unresolved_usd: z.string().optional(),
    human_confirmed_discrepancy_usd: z.string().optional(),
    confirmed_recovery_usd: z.string(),
    recovery_rate_disclaimer: z.string(),
  }),
  findings: z.array(DispaterFindingSchema),
  limits: z.string(),
  receipt_sha256: z.string(),
  receipt_auth: z.object({ alg: z.string(), kid: z.string(), v: z.number().optional() }).optional(),
  receipt_mac: z.string().optional(),
  receipt_binding: z.string().optional(),
  run_id: z.string().optional(),
  created_at: z.string().optional(),
});

export const DispaterDocumentIngestionSchema = z.object({
  authority_state: z.literal("HOLD"),
  financial_authority: z.literal("NONE"),
  ingestion_authenticated: z.literal(false),
  ocr_status: z.string(),
  ingestion: z.object({
    source_sha256: z.string(),
    filename: z.string(),
    kind: z.string(),
    processor: z.object({ name: z.string(), version: z.string(), model: z.null(), ocr: z.string() }),
    provenance: z.array(z.object({ source_sha256: z.string(), row: z.string() }).passthrough()),
    field_provenance: z.array(z.record(z.any())),
    limits: z.string(),
  }),
  report: DispaterReconciliationReportSchema,
});

export type DispaterFinding = z.infer<typeof DispaterFindingSchema>;
export type DispaterReconciliationReport = z.infer<typeof DispaterReconciliationReportSchema>;
export type DispaterDocumentIngestion = z.infer<typeof DispaterDocumentIngestionSchema>;

export type DispaterDemoState =
  | { status: "IDLE" }
  | { status: "LOADING" }
  | { status: "SUCCESS"; report: DispaterReconciliationReport }
  | { status: "ERROR"; error: string };
