import { createServerFn } from "@tanstack/react-start";
import { classifyXaeliHttp, xaeliProbeAllowed, type XaeliLinkReport } from "./xaeli-status";

const UNAVAILABLE: XaeliLinkReport = { status: "unavailable", live: false, answer: null };

export const readXaeliStagingStatus = createServerFn({ method: "GET" }).handler(async () => {
  const env = {
    stagingEnabled: process.env["AUREX_XAELI_STAGING_ENABLED"],
    operatorApproved: process.env["AUREX_XAELI_OPERATOR_APPROVED"],
    qwenBaseUrl: process.env["AUREX_QWEN_BASE_URL"],
    serviceUrl: process.env["AUREX_SERVICE_URL"] ?? process.env["AUREX_STAGING_SERVICE_URL"],
    serviceToken: process.env["AUREX_SERVICE_TOKEN"] ?? process.env["AUREX_STAGING_SERVICE_TOKEN"],
  };
  if (!xaeliProbeAllowed(env) || !env.serviceUrl) return UNAVAILABLE;
  let endpoint: string;
  try {
    const url = new URL(env.serviceUrl);
    const local = url.hostname === "127.0.0.1" || url.hostname === "localhost" || url.hostname === "[::1]";
    const localAllowed = process.env["NODE_ENV"] !== "production" && local && url.protocol === "http:";
    if (url.protocol !== "https:" && !localAllowed) return UNAVAILABLE;
    endpoint = new URL("/v1/xaeli-staging/explain", url).toString();
  } catch {
    return UNAVAILABLE;
  }
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
      body: JSON.stringify({ prompt: "Explain a synthetic field ticket discrepancy." }),
      signal: AbortSignal.timeout(6000),
    });
    return classifyXaeliHttp(response.status, await response.json().catch(() => null));
  } catch {
    return { status: "disconnected", live: false, answer: null } satisfies XaeliLinkReport;
  }
});
