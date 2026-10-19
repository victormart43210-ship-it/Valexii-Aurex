/** Server-only, authenticated read of ORCA R8 counters. No raw evidence enters browser. */
import { createServerFn } from "@tanstack/react-start";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import { createRateLimiter, isOwner } from "./aurex-control";
import { z } from "zod";

const limiter = createRateLimiter(6, 60_000);
const snapshot = z.object({
  sourceId: z.literal("orca-r8"),
  runId: z.string().regex(/^[A-Za-z0-9_-]{8,64}$/),
  sequence: z.number().int().positive(),
  observedAt: z.string().datetime({ offset: true }),
  status: z.enum(["RUNNING", "PAUSED", "COMPLETED", "FAILED"]),
  completedBatches: z.number().int().nonnegative(),
  totalBatches: z.number().int().positive(),
  rowsRemaining: z.number().int().nonnegative().nullable().optional(),
  etaSeconds: z.number().int().nonnegative().nullable().optional(),
  checkpointAgeSeconds: z.number().int().nonnegative().nullable().optional(),
}).strict();

const response = z.object({
  state: z.enum(["NO_DATA", "OBSERVED", "STALE"]),
  checkedAt: z.string().datetime({ offset: true }),
  snapshot: snapshot.nullable(),
  receivedAt: z.string().datetime({ offset: true }).nullable(),
  sha256: z.string().regex(/^[a-f0-9]{64}$/).nullable(),
  evidenceStatus: z.literal("NOT VERIFIED"),
  authority: z.literal("NONE"),
}).strict();

export type OrcaOwnerState =
  | { state: "NOT_CONFIGURED" | "UNAVAILABLE" | "INVALID_RESPONSE"; snapshot: null; evidenceStatus: "NOT VERIFIED"; authority: "NONE" }
  | z.infer<typeof response>;

const FALLBACK = { snapshot: null, evidenceStatus: "NOT VERIFIED", authority: "NONE" } as const;

export const getOrcaR8OwnerStatus = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }): Promise<OrcaOwnerState> => {
    if (!isOwner(context.userId, process.env["AUREX_OWNER_USER_ID"])) throw new Error("Forbidden");
    if (!limiter(context.userId)) throw new Error("Rate limited");
    const { validServiceUrl } = await import("./aurex-service.server");
    const base = validServiceUrl(process.env["AUREX_SERVICE_URL"]);
    const token = process.env["AUREX_SERVICE_TOKEN"];
    if (!base || !token || token.length < 32) return { ...FALLBACK, state: "NOT_CONFIGURED" };
    try {
      const res = await fetch(new URL("/v1/orca/r8/status", base), {
        method: "GET",
        headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
        redirect: "manual",
        cache: "no-store",
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok || !res.body) {
        await res.body?.cancel();
        return { ...FALLBACK, state: "UNAVAILABLE" };
      }
      // Hard byte bound including chunked encoding and forged Content-Length.
      const declared = res.headers.get("content-length");
      if (declared !== null && (!/^\d+$/.test(declared) || Number(declared) > 4096)) {
        await res.body.cancel();
        return { ...FALLBACK, state: "INVALID_RESPONSE" };
      }
      const reader = res.body.getReader();
      const chunks: Uint8Array[] = [];
      let length = 0;
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          length += value.byteLength;
          if (length > 4096) return { ...FALLBACK, state: "INVALID_RESPONSE" };
          chunks.push(value);
        }
      } finally {
        await reader.cancel().catch(() => undefined);
      }
      const bytes = new Uint8Array(length);
      let offset = 0;
      for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
      const parsed = response.safeParse(JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes)));
      if (!parsed.success) return { ...FALLBACK, state: "INVALID_RESPONSE" };
      // The backend is a self-report; this never elevates evidence to verified.
      return parsed.data;
    } catch {
      return { ...FALLBACK, state: "UNAVAILABLE" };
    }
  });
