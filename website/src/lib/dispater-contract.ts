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
  event_relation: z.string().optional(),
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
    confirmed_recovery_usd: z.literal("0.00"),
    recovery_rate_disclaimer: z.string(),
    event_separation: z.string().optional(),
  }),
  findings: z.array(DispaterFindingSchema),
  limits: z.string(),
  receipt_sha256: z.string(),
  receipt_auth: z.object({ alg: z.string(), kid: z.string(), v: z.number().optional() }).optional(),
  receipt_mac: z.string().optional(),
  receipt_binding: z.string().optional(),
  receipt_class: z.string().optional(),
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

export const DispaterRunSummarySchema = z.object({
  run_id: z.string().regex(/^run-[0-9a-f]{32}$/),
  dataset_sha256: z.string(),
  receipt_sha256: z.string(),
  status: z.string(),
  created_at: z.string(),
});

export const DispaterRunListSchema = z.object({
  tenant_id: z.string(),
  count: z.number().int().nonnegative(),
  runs: z.array(DispaterRunSummarySchema).max(50),
});

export const DispaterVerifiedExportSchema = z.object({
  export_authorization: z.literal("TENANT_BEARER"),
  third_party_release: z.literal(false),
  training_reuse: z.literal("NOT_AUTHORIZED"),
  deletion: z.literal("NOT_IMPLEMENTED"),
  receipt_authenticity: z.enum(["MAC", "NONE", "FAIL"]),
  report: DispaterReconciliationReportSchema,
});

export const ObservationDecisionSchema = z.object({
  schema: z.literal("aurex.proposal.v1"),
  decision: z.enum(["RECORDED", "ABSTAIN", "REFUSED"]),
  effect: z.literal("NONE"),
  authority: z.literal("NONE"),
  financial_authority: z.literal("NONE"),
  production: z.literal("HOLD"),
  launch: z.literal("NOT_STARTED"),
  independent_verification: z.literal("NOT_VERIFIED"),
  problems: z.array(z.string()),
  tenant_id: z.string(),
});

export type DispaterFinding = z.infer<typeof DispaterFindingSchema>;
export type DispaterRunList = z.infer<typeof DispaterRunListSchema>;
export type DispaterRunSummary = z.infer<typeof DispaterRunSummarySchema>;
export type DispaterVerifiedExport = z.infer<typeof DispaterVerifiedExportSchema>;
export const RelationshipPostSchema = z.object({
  authority_state: z.literal("HOLD"),
  financial_authority: z.literal("NONE"),
  effect: z.literal("NONE"),
  confirmed_recovery_usd: z.literal("0.00"),
  identified_exposure_usd: z.string(),
  withheld_unresolved_usd: z.string(),
  potential_underbilling_usd: z.string(),
  potential_overbilling_usd: z.string(),
  unverified_exposure_usd: z.string(),
  dataset_sha256: z.string().regex(/^[0-9a-f]{64}$/),
  run_id: z.string().regex(/^run-[0-9a-f]{32}$/),
  relationships: z.object({
    object_count: z.number().int().nonnegative(),
    event_count: z.number().int().nonnegative(),
    relation_count: z.number().int().nonnegative(),
    unresolved: z.array(
      z.object({
        source_id: z.string(),
        target_id: z.string(),
        qualifier: z.string(),
        reason: z.string(),
      }),
    ),
    context_sha256: z.string(),
  }),
});

export const RelationshipReadSchema = z.object({
  tenant_id: z.string(),
  dataset_sha256: z.string().regex(/^[0-9a-f]{64}$/),
  objects: z.array(
    z.object({
      object_id: z.string(),
      object_type: z.string(),
      attributes_json: z.string(),
      source_sha256: z.string(),
    }),
  ),
  events: z.array(
    z.object({
      event_id: z.string(),
      event_type: z.string(),
      event_time: z.string(),
      qualifier: z.string(),
    }),
  ),
  relations: z.array(
    z.object({
      source_id: z.string(),
      target_id: z.string(),
      qualifier: z.string(),
    }),
  ),
  effect: z.literal("NONE"),
  financial_authority: z.literal("NONE"),
});

export const FindingExplanationSchema = z.object({
  schema: z.literal("valexii.xaeli.explanation.v1"),
  finding_id: z.string(),
  finding_sha256: z.string(),
  authority: z.literal("NONE"),
  effect: z.literal("NONE"),
  independent_verification: z.literal("NOT_VERIFIED"),
  observed_facts: z.array(z.object({ kind: z.string(), record_sha256: z.string() })).min(1),
  calculated_discrepancy_usd: z.string().nullable(),
  suspected_exposure_usd: z.string().nullable(),
  confirmed_recovery_usd: z.literal("0.00"),
  unverified_interpretation: z.boolean(),
  claim_class: z.enum([
    "SUSPECTED_EXPOSURE",
    "CALCULATED_DISCREPANCY",
    "UNVERIFIED_INTERPRETATION",
  ]),
  workflow: DispaterXaeliSchema,
  limits: z.string(),
});

export type RelationshipPost = z.infer<typeof RelationshipPostSchema>;
export type RelationshipRead = z.infer<typeof RelationshipReadSchema>;
export type FindingExplanation = z.infer<typeof FindingExplanationSchema>;
export type ObservationDecision = z.infer<typeof ObservationDecisionSchema>;
export type DispaterReconciliationReport = z.infer<typeof DispaterReconciliationReportSchema>;
export type DispaterDocumentIngestion = z.infer<typeof DispaterDocumentIngestionSchema>;

export type DispaterDemoState =
  | { status: "IDLE" }
  | { status: "LOADING" }
  | { status: "SUCCESS"; report: DispaterReconciliationReport }
  | { status: "ERROR"; error: string };
