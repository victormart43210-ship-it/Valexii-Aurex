/**
 * DISPATER customer-facing audit client connecting to authenticated AUREX endpoints.
 * Provides synthetic towing and oilfield audit evaluation and receipt verification.
 */
import { z } from "zod";
import { createAurexClient } from "./aurex-client.server";

export const AuditFindingSchema = z.object({
  finding_id: z.string(),
  domain: z.string(),
  code: z.string(),
  source_evidence: z.array(z.string()).default([]),
  rule_evidence_hash: z.string().nullable().optional(),
  subject: z.string().optional(),
  explanation: z.string(),
  explanation_provenance: z.string(),
  review: z.object({
    status: z.string(),
    note: z.string().optional(),
    reviewer: z.string().optional(),
    effect_authority: z.string().optional(),
  }),
});

export const AuditReportSchema = z.object({
  schema: z.string(),
  sector: z.string(),
  input_sha256: z.string(),
  status: z.string(),
  dataset_classification: z.string(),
  independent_verification: z.string(),
  nvidia_inference: z.string(),
  nvidia_reason: z.string().optional(),
  revenue_snapshot_sha256: z.string(),
  readiness_snapshot_sha256: z.string(),
  reviewer: z.string(),
  counts: z.object({
    revenue_findings: z.number(),
    readiness_findings: z.number(),
    reviewed: z.number(),
    awaiting_review: z.number(),
  }),
  findings: z.array(AuditFindingSchema),
  limits: z.string(),
  self_issued_receipt_sha256: z.string(),
});

export type AuditReport = z.infer<typeof AuditReportSchema>;
export type AuditFinding = z.infer<typeof AuditFindingSchema>;

export interface DispaterAuditConfig {
  url?: string;
  token?: string;
  timeoutMs?: number;
  fetcher?: typeof fetch;
}

export function createDispaterAuditClient(cfg: DispaterAuditConfig) {
  const client = createAurexClient(cfg);

  return {
    get configured() {
      return client.configured;
    },
    async runTowingAudit(reviewDecisions: Array<{ finding_id: string; decision: string; note: string }> = []): Promise<
      { ok: true; report: AuditReport } | { ok: false; error: string; status?: number }
    > {
      if (!client.configured) {
        return { ok: false, error: "not_configured" };
      }

      const key = "dispaterKey000123";

      const res = await client.createJob(
        {
          kind: "regression_scan",
          params: { probe: "sqlite_roundtrip_v1" },
          maxCostUsd: 0,
        },
        key,
      );

      if (!res.ok) {
        return { ok: false, error: res.error, status: res.status };
      }

      const syntheticReport: AuditReport = {
        schema: "dispater.synthetic.end_to_end.v1",
        sector: "towing",
        input_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        status: "HOLD",
        dataset_classification: "FICTIONAL_DATA_ONLY",
        independent_verification: "NOT VERIFIED",
        nvidia_inference: "NOT RUN",
        nvidia_reason: "Provider not connected or authorized for this demo.",
        revenue_snapshot_sha256: "a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890",
        readiness_snapshot_sha256: "b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1",
        reviewer: "DEMO_MANAGER",
        counts: {
          revenue_findings: 3,
          readiness_findings: 2,
          reviewed: reviewDecisions.length,
          awaiting_review: 5 - reviewDecisions.length,
        },
        findings: [
          {
            finding_id: "find-01-unbilled",
            domain: "REVENUE",
            code: "UNBILLED_JOB",
            source_evidence: ["TOW-101"],
            explanation: "Job TOW-101 completed on 2026-10-21 has no associated invoice.",
            explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
            review: { status: reviewDecisions.find(d => d.finding_id === "find-01-unbilled")?.decision ?? "NOT_REVIEWED", effect_authority: "NONE" },
          },
          {
            finding_id: "find-02-ratemismatch",
            domain: "REVENUE",
            code: "RATE_MISMATCH",
            source_evidence: ["INV-100", "RT-1"],
            explanation: "Invoice INV-100 amount ($150.00) differs from rate table amount ($180.00).",
            explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
            review: { status: reviewDecisions.find(d => d.finding_id === "find-02-ratemismatch")?.decision ?? "NOT_REVIEWED", effect_authority: "NONE" },
          },
          {
            finding_id: "find-03-unreconciled",
            domain: "REVENUE",
            code: "PAID_STATUS_UNRECONCILED",
            source_evidence: ["PAY-100", "INV-100"],
            explanation: "Payment PAY-100 ($140.00) does not match invoice INV-100 amount ($150.00).",
            explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
            review: { status: reviewDecisions.find(d => d.finding_id === "find-03-unreconciled")?.decision ?? "NOT_REVIEWED", effect_authority: "NONE" },
          },
          {
            finding_id: "find-04-expired",
            domain: "RECORD_READINESS",
            code: "EVIDENCE_MISSING_OR_EXPIRED",
            source_evidence: ["D-1"],
            explanation: "Vehicle inspection document D-1 expired on 2026-09-01.",
            explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
            review: { status: reviewDecisions.find(d => d.finding_id === "find-04-expired")?.decision ?? "NOT_REVIEWED", effect_authority: "NONE" },
          },
          {
            finding_id: "find-05-applicability",
            domain: "RECORD_READINESS",
            code: "EVIDENCE_MISSING_OR_EXPIRED",
            source_evidence: ["DEMO-IRS-1"],
            explanation: "Receipt index requirements require human verification.",
            explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
            review: { status: reviewDecisions.find(d => d.finding_id === "find-05-applicability")?.decision ?? "NOT_REVIEWED", effect_authority: "NONE" },
          },
        ],
        limits: "Not an IRS/DOT audit, tax opinion, regulatory certification, or financial authorization.",
        self_issued_receipt_sha256: `rcpt_${res.value.id.substring(4, 20)}`,
      };

      return { ok: true, report: syntheticReport };
    },
  };
}
