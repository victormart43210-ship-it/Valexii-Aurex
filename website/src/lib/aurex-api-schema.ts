/**
 * AUREX external service contract v1 (mirrors docs/aurex-api/openapi.yaml).
 * Browser-safe zod schemas with strict bounds. Unknown fields are rejected.
 */
import { z } from "zod";

export const API_VERSION = "v1";
export const MAX_RESPONSE_BYTES = 256 * 1024;
const id = z.string().regex(/^[a-z0-9][a-z0-9_-]{0,63}$/);
const iso = z.string().datetime({ offset: true });

export const HealthSchema = z
  .object({ status: z.literal("ok"), version: z.string().max(32), time: iso })
  .strict();

export const CapabilitySchema = z
  .object({
    id: z.string().regex(/^[a-z-]{1,64}$/),
    available: z.boolean(),
    evidenceId: id.nullable(),
    verifiedAt: iso.nullable(),
  })
  .strict();
export const CapabilitiesSchema = z
  .object({ capabilities: z.array(CapabilitySchema).max(100) })
  .strict();

export const JobStateSchema = z.enum(["queued", "running", "succeeded", "failed", "cancelled"]);
export const JobSchema = z
  .object({
    id,
    kind: z.enum(["benchmark", "hypothesis_test", "regression_scan"]),
    state: JobStateSchema,
    createdAt: iso,
    updatedAt: iso,
    reservationUsd: z.number().min(0).max(10_000),
  })
  .strict();
export const JobListSchema = z
  .object({ jobs: z.array(JobSchema).max(200), nextCursor: z.string().max(128).nullable() })
  .strict();
/** Job creation accepts only a named kind and bounded params; never code, shell or URLs. */
export const JobCreateSchema = z
  .object({
    kind: JobSchema.shape.kind,
    params: z
      .record(
        z.string().regex(/^[a-z_]{1,32}$/),
        z.union([z.string().max(256), z.number(), z.boolean()]),
      )
      .refine((p) => Object.keys(p).length <= 16, "too many params"),
    maxCostUsd: z.number().min(0).max(100),
  })
  .strict();

export const EvidenceSchema = z
  .object({
    id,
    capabilityId: z.string().regex(/^[a-z-]{1,64}$/),
    kind: z.enum(["test_run", "health_probe", "benchmark_record"]),
    collectedAt: iso,
    sha256: z.string().regex(/^[0-9a-f]{64}$/),
    summary: z.string().max(500),
  })
  .strict();
export const EvidenceListSchema = z.object({ evidence: z.array(EvidenceSchema).max(200) }).strict();

export const BudgetSchema = z
  .object({
    limitUsd: z.number().min(0),
    reservedUsd: z.number().min(0),
    spentUsd: z.number().min(0),
    period: z.enum(["day", "month"]),
  })
  .strict();

export const ErrorSchema = z
  .object({ error: z.object({ code: z.string().max(64), message: z.string().max(300) }).strict() })
  .strict();

export type Health = z.infer<typeof HealthSchema>;
export type Job = z.infer<typeof JobSchema>;
export type JobCreate = z.infer<typeof JobCreateSchema>;
export type Evidence = z.infer<typeof EvidenceSchema>;
export type Budget = z.infer<typeof BudgetSchema>;

/** Evidence older than maxAgeMs, from the future, or missing never counts as support. */
export const EVIDENCE_MAX_AGE_MS = 7 * 24 * 3600 * 1000;
export function evidenceFresh(
  e: { collectedAt: string } | null | undefined,
  now = Date.now(),
  maxAgeMs = EVIDENCE_MAX_AGE_MS,
): boolean {
  if (!e) return false;
  const t = Date.parse(e.collectedAt);
  return Number.isFinite(t) && t <= now + 60_000 && now - t <= maxAgeMs;
}

/** A capability is evidence-backed only if available, linked to fresh evidence for the same capability. */
export function capabilityBacked(
  cap: z.infer<typeof CapabilitySchema>,
  evidence: readonly Evidence[],
  now = Date.now(),
): boolean {
  if (!cap.available || !cap.evidenceId) return false;
  const e = evidence.find((x) => x.id === cap.evidenceId);
  return !!e && e.capabilityId === cap.id && evidenceFresh(e, now);
}
