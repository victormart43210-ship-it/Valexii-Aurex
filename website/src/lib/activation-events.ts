/** Privacy-minimal presentation events. No endpoint, cookies, IDs, raw URLs or buffering. */
export const activationEventNames = [
  "hero_call_click",
  "command_open",
  "call_demo_start",
  "call_demo_finish",
  "malware_demo_start",
  "malware_demo_finish",
  "proof_view",
  "xaeli_explain",
  "quiz_start",
  "quiz_finish",
  "beta_interest",
  "return_visit",
  "hero_spam_click",
  "hero_malware_click",
  "demo_start",
  "spam_card_open",
  "malware_card_open",
  "xaeli_proof_click",
  "opt_in_request",
  "scroll_depth",
  "page_exit",
  "return_session",
  "support_cta_click",
  "dispater_request_audit_click",
  "dispater_book_consultation_click",
  "dispater_view_demo_click",
] as const;
export type ActivationEventName = (typeof activationEventNames)[number];

/** Conversion events: only emitted by UI that actually exists (scam quiz, mailto opt-in, Cash App links). */
export const conversionEventNames: readonly ActivationEventName[] = [
  "quiz_start",
  "quiz_finish",
  "opt_in_request",
  "support_cta_click",
  "dispater_request_audit_click",
  "dispater_book_consultation_click",
  "dispater_view_demo_click",
];

export type Attribution = {
  /** Coarse referrer class only; never the referring URL. */
  referrer: "direct" | "internal" | "search" | "social" | "other";
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
};

export type ActivationEvent = {
  name: ActivationEventName;
  page: "home" | "bcxmet" | "xaeli" | "dispater" | "support" | "other";
  depth?: 25 | 50 | 75 | 100;
  conversion: boolean;
  /** Always "public" for events reaching an adapter; internal-test events are never sent. */
  traffic: "public";
  attribution?: Attribution;
};
export type ActivationAdapter = { send: (event: ActivationEvent) => void };
let adapter: ActivationAdapter | undefined;
let consent = false;

/**
 * Internal QA mode. Private, browser-local, opt-in. Activate in your own browser console:
 *   localStorage.setItem("valexii-internal-test", "on")
 * Not a secret or access control — it only excludes this browser's custom events.
 */
export const internalTestKey = "valexii-internal-test";
export function isInternalTest() {
  try {
    return typeof window !== "undefined" && localStorage.getItem(internalTestKey) === "on";
  } catch {
    return false;
  }
}

const attributionKey = "valexii-attribution";
const clean = (v: string | null) => {
  if (!v) return undefined;
  const s = v
    .toLowerCase()
    .replace(/[^a-z0-9_.-]/g, "")
    .slice(0, 40);
  // Reject anything resembling an email/phone/long number to avoid PII in campaign tags.
  return s && !/\d{6,}/.test(s) ? s : undefined;
};
function readAttribution(): Attribution | undefined {
  if (typeof window === "undefined") return undefined;
  try {
    const stored = sessionStorage.getItem(attributionKey);
    if (stored) return JSON.parse(stored) as Attribution;
  } catch {
    /* fall through */
  }
  return undefined;
}
/** Captures landing UTM tags + coarse referrer once per tab session; only called after consent. */
export function captureAttribution() {
  if (typeof window === "undefined" || readAttribution()) return;
  const params = new URLSearchParams(window.location.search);
  let referrer: Attribution["referrer"] = "direct";
  try {
    if (document.referrer) {
      const host = new URL(document.referrer).hostname;
      if (host === window.location.hostname) referrer = "internal";
      else if (/(google|bing|duckduckgo|yahoo|ecosia|brave)\./.test(host)) referrer = "search";
      else if (
        /(facebook|instagram|linkedin|x\.com|twitter|t\.co|reddit|youtube|tiktok)/.test(host)
      )
        referrer = "social";
      else referrer = "other";
    }
  } catch {
    referrer = "other";
  }
  const attribution: Attribution = { referrer };
  for (const key of ["utm_source", "utm_medium", "utm_campaign"] as const) {
    const value = clean(params.get(key));
    if (value) attribution[key] = value;
  }
  try {
    sessionStorage.setItem(attributionKey, JSON.stringify(attribution));
  } catch {
    /* no storage, no attribution */
  }
}
export function clearAttribution() {
  try {
    sessionStorage.removeItem(attributionKey);
  } catch {
    /* ignore */
  }
}

export function configureActivationAdapter(next?: ActivationAdapter) {
  adapter = next;
}
export function setActivationConsent(allowed: boolean) {
  consent = allowed;
}
export function activationStatus() {
  return { consent, connected: Boolean(adapter), internalTest: isInternalTest() };
}
export function emitActivation(name: ActivationEventName, depth?: 25 | 50 | 75 | 100) {
  if (typeof window === "undefined" || !activationEventNames.includes(name)) return;
  const path = window.location.pathname;
  const page: ActivationEvent["page"] =
    path === "/"
      ? "home"
      : path === "/bcxmet"
        ? "bcxmet"
        : path === "/xaeli"
          ? "xaeli"
          : path === "/support"
            ? "support"
            : path === "/dispater"
              ? "dispater"
              : "other";
  const event: ActivationEvent = {
    name,
    page,
    conversion: conversionEventNames.includes(name),
    traffic: "public",
  };
  if (name === "scroll_depth" && depth && [25, 50, 75, 100].includes(depth)) event.depth = depth;
  if (isInternalTest()) {
    // QA only: log locally, never send. Nothing leaves the browser.
    console.info("[valexii internal-test] event excluded:", { ...event, traffic: "internal_test" });
    return;
  }
  if (!consent || !adapter) return;
  const attribution = readAttribution();
  if (attribution) event.attribution = attribution;
  // An adapter failure must never affect navigation or review.
  try {
    adapter.send(event);
  } catch {
    /* Default to no measurement, not a false success. */
  }
}
