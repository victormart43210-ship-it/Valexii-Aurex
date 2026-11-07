export type XaeliLinkState = "unavailable" | "ready" | "disconnected" | "error" | "connected";

export const XAELI_PROMPTS = [
  "Explain a synthetic app permission change.",
  "Explain a synthetic suspicious message.",
  "Explain a synthetic field ticket discrepancy.",
] as const;

export type XaeliPrompt = (typeof XAELI_PROMPTS)[number];

/** Covers the 90s adapter budget plus a short model-list check. Still bounded. */
export const XAELI_INFERENCE_TIMEOUT_MS = 110_000;

export const XAELI_ERROR_CODES = [
  "TIMEOUT",
  "MODEL_UNAVAILABLE",
  "MODEL_IDENTITY_MISMATCH",
  "AUTHENTICATION_FAILURE",
  "PROVIDER_OR_SCHEMA_FAILURE",
  "UNSAFE_OR_EMPTY_MODEL_OUTPUT",
] as const;

export interface XaeliStagingEnv {
  stagingEnabled?: string | undefined;
  operatorApproved?: string | undefined;
  qwenBaseUrl?: string | undefined;
  serviceUrl?: string | undefined;
  serviceToken?: string | undefined;
}

export interface XaeliLinkReport {
  status: XaeliLinkState;
  live: false | true;
  answer: string | null;
  errorCode?: (typeof XAELI_ERROR_CODES)[number] | null;
}

export function xaeliProbeAllowed(env: XaeliStagingEnv): boolean {
  return (
    env.stagingEnabled === "1" &&
    env.operatorApproved === "1" &&
    Boolean(env.qwenBaseUrl) &&
    Boolean(env.serviceUrl) &&
    Boolean(env.serviceToken && env.serviceToken.length >= 32)
  );
}

export function xaeliStagingGate(env: XaeliStagingEnv): XaeliLinkReport {
  if (!xaeliProbeAllowed(env)) return { status: "unavailable", live: false, answer: null };
  return { status: "ready", live: false, answer: null };
}

function knownError(value: unknown): (typeof XAELI_ERROR_CODES)[number] | null {
  return XAELI_ERROR_CODES.find((code) => code === value) ?? null;
}

export function classifyXaeliHttp(status: number, body: unknown): XaeliLinkReport {
  if (status === 503)
    return { status: "unavailable", live: false, answer: null, errorCode: "MODEL_UNAVAILABLE" };
  if (status === 401 || status === 403) {
    return { status: "error", live: false, answer: null, errorCode: "AUTHENTICATION_FAILURE" };
  }
  if (status < 200 || status >= 300)
    return { status: "error", live: false, answer: null, errorCode: null };
  if (!body || typeof body !== "object")
    return { status: "error", live: false, answer: null, errorCode: null };
  const record = body as { execution?: unknown; generated_answer?: unknown; error_code?: unknown };
  const answer = typeof record.generated_answer === "string" ? record.generated_answer.trim() : "";
  if (record.execution === "PASS" && answer) {
    return { status: "connected", live: true, answer: answer.slice(0, 4000), errorCode: null };
  }
  return { status: "error", live: false, answer: null, errorCode: knownError(record.error_code) };
}
