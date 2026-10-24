/**
 * Typed, fail-closed client for the external AUREX service (contract v1).
 * Server-only. Endpoints are NOT assumed to exist; every failure maps to a typed error.
 */
import type { z } from "zod";
import {
  BudgetSchema,
  CapabilitiesSchema,
  EvidenceListSchema,
  HealthSchema,
  JobCreateSchema,
  JobListSchema,
  JobSchema,
  PipelineReceiptSchema,
  MAX_RESPONSE_BYTES,
  type JobCreate,
} from "./aurex-api-schema";
import { validServiceUrl } from "./aurex-service.server";

export type ClientErrorCode =
  | "not_configured"
  | "timeout"
  | "network"
  | "http_error"
  | "unauthorized"
  | "too_large"
  | "malformed"
  | "invalid_input";
export type Result<T> =
  { ok: true; value: T } | { ok: false; error: ClientErrorCode; status?: number };

export interface ClientConfig {
  url?: string | undefined;
  token?: string | undefined;
  timeoutMs?: number;
  fetcher?: typeof fetch;
}

export function createAurexClient(cfg: ClientConfig) {
  const base = validServiceUrl(cfg.url);
  const configured = !!base && !!cfg.token && cfg.token.length >= 32;
  const fetcher = cfg.fetcher ?? fetch;
  const timeoutMs = Math.min(Math.max(cfg.timeoutMs ?? 5000, 500), 10_000);

  async function call<S extends z.ZodTypeAny>(
    method: "GET" | "POST",
    path: string,
    schema: S,
    init: { body?: unknown; idempotencyKey?: string } = {},
  ): Promise<Result<z.infer<S>>> {
    if (!configured || !base) return { ok: false, error: "not_configured" };
    const headers: Record<string, string> = {
      Authorization: `Bearer ${cfg.token}`,
      Accept: "application/json",
    };
    if (init.body !== undefined) headers["Content-Type"] = "application/json";
    if (init.idempotencyKey) headers["Idempotency-Key"] = init.idempotencyKey;
    let res: Response;
    try {
      res = await fetcher(new URL(`/v1${path}`, base), {
        method,
        headers,
        redirect: "manual",
        signal: AbortSignal.timeout(timeoutMs),
        ...(init.body !== undefined ? { body: JSON.stringify(init.body) } : {}),
      });
    } catch (e) {
      return {
        ok: false,
        error:
          (e as Error)?.name === "TimeoutError" || (e as Error)?.name === "AbortError"
            ? "timeout"
            : "network",
      };
    }
    if (res.status === 401 || res.status === 403)
      return { ok: false, error: "unauthorized", status: res.status };
    if (!res.ok) return { ok: false, error: "http_error", status: res.status };
    const len = Number(res.headers.get("content-length") ?? "0");
    if (len > MAX_RESPONSE_BYTES) return { ok: false, error: "too_large" };
    let text: string;
    try {
      text = await res.text();
    } catch {
      return { ok: false, error: "network" };
    }
    if (text.length > MAX_RESPONSE_BYTES) return { ok: false, error: "too_large" };
    let json: unknown;
    try {
      json = JSON.parse(text);
    } catch {
      return { ok: false, error: "malformed" };
    }
    const parsed = schema.safeParse(json);
    return parsed.success ? { ok: true, value: parsed.data } : { ok: false, error: "malformed" };
  }

  const idOk = (s: string) => /^[a-z0-9][a-z0-9_-]{0,63}$/.test(s);
  const keyOk = (s: string) => /^[A-Za-z0-9_-]{16,128}$/.test(s);

  return {
    configured,
    health: () => call("GET", "/health", HealthSchema),
    capabilities: () => call("GET", "/capabilities", CapabilitiesSchema),
    listJobs: () => call("GET", "/jobs", JobListSchema),
    jobStatus: async (jobId: string) =>
      idOk(jobId)
        ? call("GET", `/jobs/${jobId}`, JobSchema)
        : { ok: false as const, error: "invalid_input" as const },
    /** Authenticated *server-only* receipt; not a claim of financial accuracy. */
    jobReceipt: async (jobId: string) =>
      idOk(jobId)
        ? call("GET", `/jobs/${jobId}/receipt`, PipelineReceiptSchema)
        : { ok: false as const, error: "invalid_input" as const },
    createJob: async (input: JobCreate, idempotencyKey: string) => {
      if (!keyOk(idempotencyKey) || !JobCreateSchema.safeParse(input).success)
        return { ok: false as const, error: "invalid_input" as const };
      return call("POST", "/jobs", JobSchema, { body: input, idempotencyKey });
    },
    cancelJob: async (jobId: string, idempotencyKey: string) =>
      idOk(jobId) && keyOk(idempotencyKey)
        ? call("POST", `/jobs/${jobId}/cancel`, JobSchema, { idempotencyKey })
        : { ok: false as const, error: "invalid_input" as const },
    evidence: () => call("GET", "/evidence", EvidenceListSchema),
    budget: () => call("GET", "/budgets", BudgetSchema),
  };
}
