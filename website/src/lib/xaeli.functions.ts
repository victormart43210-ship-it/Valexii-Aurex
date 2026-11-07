import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import {
  XAELI_INFERENCE_TIMEOUT_MS,
  XAELI_PROMPTS,
  classifyXaeliHttp,
  xaeliProbeAllowed,
  xaeliStagingGate,
  type XaeliLinkReport,
  type XaeliStagingEnv,
} from "./xaeli-status";

const UNAVAILABLE: XaeliLinkReport = { status: "unavailable", live: false, answer: null };

function stagingEnv(): XaeliStagingEnv {
  return {
    stagingEnabled: process.env["AUREX_XAELI_STAGING_ENABLED"],
    operatorApproved: process.env["AUREX_XAELI_OPERATOR_APPROVED"],
    qwenBaseUrl: process.env["AUREX_QWEN_BASE_URL"],
    serviceUrl: process.env["AUREX_SERVICE_URL"] ?? process.env["AUREX_STAGING_SERVICE_URL"],
    serviceToken: process.env["AUREX_SERVICE_TOKEN"] ?? process.env["AUREX_STAGING_SERVICE_TOKEN"],
  };
}

function serviceEndpoint(env: XaeliStagingEnv): string | null {
  if (!xaeliProbeAllowed(env) || !env.serviceUrl) return null;
  try {
    const url = new URL(env.serviceUrl);
    const local =
      url.hostname === "127.0.0.1" || url.hostname === "localhost" || url.hostname === "[::1]";
    const localAllowed =
      process.env["NODE_ENV"] !== "production" && local && url.protocol === "http:";
    if (url.protocol !== "https:" && !localAllowed) return null;
    return new URL("/v1/xaeli-staging/explain", url).toString();
  } catch {
    return null;
  }
}

/** Configuration only. Opening the page does not call the model or claim a connection. */
export const readXaeliStagingStatus = createServerFn({ method: "GET" }).handler(async () => {
  return xaeliStagingGate(stagingEnv());
});

export const submitXaeliSynthetic = createServerFn({ method: "POST" })
  .validator((input: unknown) => z.object({ prompt: z.enum(XAELI_PROMPTS) }).parse(input))
  .handler(async ({ data }): Promise<XaeliLinkReport> => {
    const env = stagingEnv();
    const endpoint = serviceEndpoint(env);
    if (!endpoint) return UNAVAILABLE;
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        redirect: "manual",
        headers: {
          Authorization: `Bearer ${env.serviceToken}`,
          "Content-Type": "application/json",
          Accept: "application/json",
          "x-aurex-operator-approval": "synthetic-only",
        },
        body: JSON.stringify({ prompt: data.prompt }),
        signal: AbortSignal.timeout(XAELI_INFERENCE_TIMEOUT_MS),
      });
      return classifyXaeliHttp(response.status, await response.json().catch(() => null));
    } catch (error) {
      const timedOut =
        error instanceof Error && (error.name === "TimeoutError" || error.name === "AbortError");
      return {
        status: "disconnected",
        live: false,
        answer: null,
        errorCode: timedOut ? "TIMEOUT" : "MODEL_UNAVAILABLE",
      };
    }
  });
