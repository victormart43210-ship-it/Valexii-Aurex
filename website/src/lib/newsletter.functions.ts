import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

// Server-only config. Nothing here is exposed to the browser.
// LISTMONK_URL (https://lists.example.com), LISTMONK_LIST_UUID (public list UUID),
// NEWSLETTER_SIGNUP_ENABLED="true" to open signup. All three required.
function readConfig() {
  const url = process.env["LISTMONK_URL"]?.replace(/\/+$/, "");
  const list = process.env["LISTMONK_LIST_UUID"];
  const enabled = process.env["NEWSLETTER_SIGNUP_ENABLED"] === "true";
  if (!enabled || !url || !list || !/^https:\/\//.test(url)) return null;
  return { url, list };
}

export const getNewsletterStatus = createServerFn({ method: "GET" }).handler(async () => ({
  active: readConfig() !== null,
}));

// Best-effort per-isolate rate limit; listmonk should also be rate limited upstream.
const hits = new Map<string, number[]>();
function limited(key: string) {
  const now = Date.now();
  const recent = (hits.get(key) ?? []).filter((t) => now - t < 10 * 60_000);
  recent.push(now);
  hits.set(key, recent);
  if (hits.size > 5000) hits.clear();
  return recent.length > 3;
}

const input = z.object({
  email: z.string().trim().toLowerCase().email().max(254),
  consent: z.literal(true),
  website: z.string().max(0), // honeypot must be empty
  startedAt: z.number().int(),
});

export type SubscribeResult = {
  ok: boolean;
  reason?: "inactive" | "rate" | "invalid" | "upstream";
};

export const subscribeNewsletter = createServerFn({ method: "POST" })
  .inputValidator((d: unknown) => input.parse(d))
  .handler(async ({ data }): Promise<SubscribeResult> => {
    const cfg = readConfig();
    if (!cfg) return { ok: false, reason: "inactive" };
    if (Date.now() - data.startedAt < 2000) return { ok: false, reason: "invalid" };
    if (limited(data.email)) return { ok: false, reason: "rate" };
    try {
      // listmonk public endpoint; double opt-in lists send the confirmation email.
      const res = await fetch(`${cfg.url}/api/public/subscription`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email: data.email, name: "", list_uuids: [cfg.list] }),
      });
      return res.ok ? { ok: true } : { ok: false, reason: "upstream" };
    } catch {
      return { ok: false, reason: "upstream" };
    }
  });
