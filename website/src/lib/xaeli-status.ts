export type XaeliLinkState = "unavailable" | "disconnected" | "error" | "connected";

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

export function classifyXaeliHttp(status: number, body: unknown): XaeliLinkReport {
  if (status === 503) return { status: "unavailable", live: false, answer: null };
  if (status === 401 || status === 403) return { status: "error", live: false, answer: null };
  if (status < 200 || status >= 300) return { status: "error", live: false, answer: null };
  if (!body || typeof body !== "object") return { status: "error", live: false, answer: null };
  const record = body as { execution?: unknown; generated_answer?: unknown };
  const answer = typeof record.generated_answer === "string" ? record.generated_answer.trim() : "";
  if (record.execution === "PASS" && answer) {
    return { status: "connected", live: true, answer: answer.slice(0, 4000) };
  }
  return { status: "error", live: false, answer: null };
}
