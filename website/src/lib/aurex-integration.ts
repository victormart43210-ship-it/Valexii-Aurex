/**
 * AUREX backend integration boundary. Browser-safe, no network calls.
 * A future authenticated hosted AUREX API must implement AurexClient behind a
 * server function; until configured, the website stays in the disabled state.
 */
export type VerificationStatus = "NOT_VERIFIED" | "INDEPENDENTLY_VERIFIED";
export type AuthorityState = "HOLD" | "AUTHORIZED";
export type EffectState = "NONE" | "BOUNDED_EFFECT_RECORDED";
export type ResultScope = "LOCAL_PRACTICE_ONLY" | "INDEPENDENTLY_VERIFIED";

export interface AurexRunRecord {
  id: string;
  source: "SYNTHETIC_SAMPLE" | "HOSTED_API";
  question: string;
  candidate: string;
  evidence: string[];
  qualification: string;
  reality: string;
  verification: VerificationStatus;
  authority: AuthorityState;
  effect: EffectState;
  scope: ResultScope;
}

export interface AurexClient {
  readonly status: "DISABLED_UNCONFIGURED" | "CONFIGURED";
  getRun(id: string): Promise<AurexRunRecord | null>;
}

/** Default client: nothing is connected; every call fails closed. */
export const disabledAurexClient: AurexClient = {
  status: "DISABLED_UNCONFIGURED",
  async getRun() {
    return null;
  },
};

/**
 * Fail-closed display rules: only a hosted record that is independently
 * verified may show anything other than NOT VERIFIED / HOLD / NONE / LOCAL_PRACTICE_ONLY.
 */
export function displayState(run: AurexRunRecord | null | undefined) {
  const verified =
    !!run && run.source === "HOSTED_API" && run.verification === "INDEPENDENTLY_VERIFIED";
  return {
    verification: verified ? "INDEPENDENTLY VERIFIED" : "NOT VERIFIED",
    authority: verified && run!.authority === "AUTHORIZED" ? "AUTHORIZED" : "HOLD",
    effect: verified && run!.effect === "BOUNDED_EFFECT_RECORDED" ? "BOUNDED EFFECT RECORDED" : "NONE",
    scope: verified && run!.scope === "INDEPENDENTLY_VERIFIED" ? "INDEPENDENTLY_VERIFIED" : "LOCAL_PRACTICE_ONLY",
  } as const;
}

export const AUREX_REPO_URL = "https://github.com/victormart43210-ship-it/Valexii-Aurex";

/** Fixed, labeled synthetic sample. Not produced by any AUREX engine. */
export const aurexSampleRun: AurexRunRecord = {
  id: "synthetic-sample-01",
  source: "SYNTHETIC_SAMPLE",
  question:
    "SYNTHETIC SAMPLE: Two sensor logs disagree about when a valve closed. Which timestamp should be trusted?",
  candidate:
    "Candidate (sample text): prefer log B, because its clock was synchronized more recently.",
  evidence: [
    "Sample log A: 10:02:14, clock sync age unknown",
    "Sample log B: 10:02:31, clock sync age 4 minutes (sample value)",
  ],
  qualification: "Sync records are described, not attached. Freshness of log A is unknown.",
  reality: "A rival explanation (log B delayed by buffering) is not ruled out.",
  verification: "NOT_VERIFIED",
  authority: "HOLD",
  effect: "NONE",
  scope: "LOCAL_PRACTICE_ONLY",
};
