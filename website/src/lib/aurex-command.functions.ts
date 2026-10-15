import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import { PromptSchema } from "./aurex-api-schema";
const jobId = z.string().regex(/^[a-z0-9][a-z0-9_-]{0,63}$/);
const key = z.string().regex(/^[A-Za-z0-9_-]{16,128}$/);
async function client(userId: string) {
  const { ownerCommandClient } = await import("./aurex-command.server");
  return ownerCommandClient(userId, {
    ownerId: process.env["AUREX_OWNER_USER_ID"],
    url: process.env["AUREX_SERVICE_URL"],
    token: process.env["AUREX_SERVICE_TOKEN"],
  });
}
export const commandConnection = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const api = await client(context.userId);
    const health = await api.health();
    if (!health.ok)
      return {
        state: health.error === "not_configured" ? "UNVERIFIED" : "UNAVAILABLE",
        inferenceAvailable: false,
      };
    const caps = await api.capabilities();
    return {
      state: caps.ok ? "CONNECTED" : "DEGRADED",
      inferenceAvailable:
        caps.ok && caps.value.capabilities.some((c) => c.id === "local-inference" && c.available),
    };
  });
export const submitAurexCommand = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator(z.object({ prompt: PromptSchema, idempotencyKey: key }).strict())
  .handler(async ({ context, data }) =>
    (await client(context.userId)).createJob(
      { kind: "local_inference", params: { prompt: data.prompt }, maxCostUsd: 0 },
      data.idempotencyKey,
    ),
  );
export const readAurexCommand = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .inputValidator(z.object({ jobId }).strict())
  .handler(async ({ context, data }) => {
    const api = await client(context.userId);
    const status = await api.jobStatus(data.jobId);
    if (!status.ok) return { status, result: null, evidence: null };
    const result = await api.jobResult(data.jobId);
    const evidence = await api.jobEvidence(data.jobId);
    return { status, result, evidence };
  });
export const cancelAurexCommand = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator(z.object({ jobId, idempotencyKey: key }).strict())
  .handler(async ({ context, data }) =>
    (await client(context.userId)).cancelJob(data.jobId, data.idempotencyKey),
  );
