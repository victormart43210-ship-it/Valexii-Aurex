import { createServerFn } from "@tanstack/react-start";
import { getRequestIP } from "@tanstack/react-start/server";
import {
  confirmSchema,
  earlyAccessSchema,
  inquirySchema,
  MIN_FILL_MS,
  type SubmitResult,
} from "./inquiry-schema";

// Best-effort per-isolate IP limiter (IPs are never stored); DB checks below are the durable limit.
const hits = new Map<string, number[]>();
function ipLimited(key: string, max = 5, windowMs = 10 * 60_000) {
  const now = Date.now();
  const recent = (hits.get(key) ?? []).filter((t) => now - t < windowMs);
  recent.push(now);
  hits.set(key, recent);
  if (hits.size > 5000) hits.clear();
  return recent.length > max;
}

function clientKey() {
  try {
    return getRequestIP({ xForwardedFor: true }) ?? "unknown";
  } catch {
    return "unknown";
  }
}

const tooFast = (startedAt: number) => Date.now() - startedAt < MIN_FILL_MS;
const silentOk: SubmitResult = { ok: true, stored: true, emailed: false };

export const submitInquiry = createServerFn({ method: "POST" })
  .inputValidator((d: unknown) => inquirySchema.parse(d))
  .handler(async ({ data }): Promise<SubmitResult> => {
    // Bots that fill too fast get a neutral response and nothing is stored.
    if (tooFast(data.startedAt)) return silentOk;
    if (ipLimited(`inq:${clientKey()}`))
      return { ok: false, reason: "rate", message: "Too many submissions. Please try again later." };

    const { supabaseAdmin } = await import("@/integrations/supabase/client.server");
    const { sendEmail, sha256Hex, TEAM_INBOX } = await import("./email-sender.server");
    const { renderInquiryNotification, renderInquiryReceipt } = await import("./email-render");

    const since = new Date(Date.now() - 60 * 60_000).toISOString();
    const { count, error: countErr } = await supabaseAdmin
      .from("inquiries")
      .select("id", { count: "exact", head: true })
      .eq("email", data.email)
      .gte("created_at", since);
    if (countErr) {
      console.error("inquiry count failed", countErr.message);
      return { ok: false, reason: "server", message: "We could not save your message. Please try again." };
    }
    if ((count ?? 0) >= 3)
      return { ok: false, reason: "rate", message: "You have sent several messages recently. Please wait an hour." };

    const dedupe = await sha256Hex(`${data.kind}|${data.email}|${data.message.toLowerCase().replace(/\s+/g, " ")}`);
    const { data: row, error } = await supabaseAdmin
      .from("inquiries")
      .insert({
        kind: data.kind,
        name: data.name,
        email: data.email,
        organization: data.organization || null,
        category: data.category,
        message: data.message,
        dedupe_hash: dedupe,
      })
      .select("id")
      .single();
    if (error) {
      if (error.code === "23505") return { ok: true, stored: true, emailed: false, duplicate: true };
      console.error("inquiry insert failed", error.message);
      return { ok: false, reason: "server", message: "We could not save your message. Please try again." };
    }

    const note = renderInquiryNotification({ ...data, id: row.id });
    const team = await sendEmail({ to: TEAM_INBOX, ...note, replyTo: data.email, idempotencyKey: `inq-team-${row.id}` });
    let emailed = false;
    if (team.sent) {
      await supabaseAdmin.from("inquiries").update({ notified_at: new Date().toISOString() }).eq("id", row.id);
      const receipt = await sendEmail({ to: data.email, ...renderInquiryReceipt(data.name), replyTo: TEAM_INBOX, idempotencyKey: `inq-receipt-${row.id}` });
      emailed = receipt.sent;
    }
    return { ok: true, stored: true, emailed };
  });

export const requestEarlyAccess = createServerFn({ method: "POST" })
  .inputValidator((d: unknown) => earlyAccessSchema.parse(d))
  .handler(async ({ data }): Promise<SubmitResult> => {
    if (tooFast(data.startedAt)) return silentOk;
    if (ipLimited(`ea:${clientKey()}`))
      return { ok: false, reason: "rate", message: "Too many requests. Please try again later." };

    const { supabaseAdmin } = await import("@/integrations/supabase/client.server");
    const { sendEmail, sha256Hex } = await import("./email-sender.server");
    const { renderEarlyAccessConfirm } = await import("./email-render");

    const { data: existing, error: readErr } = await supabaseAdmin
      .from("early_access_leads")
      .select("id,status,last_requested_at")
      .eq("email", data.email)
      .maybeSingle();
    if (readErr) {
      console.error("lead read failed", readErr.message);
      return { ok: false, reason: "server", message: "We could not record your request. Please try again." };
    }
    // Same neutral answer for confirmed/recent duplicates: no account enumeration, no repeat emails.
    if (existing?.status === "confirmed") return { ok: true, stored: true, emailed: false, duplicate: true };
    if (existing && Date.now() - new Date(existing.last_requested_at).getTime() < 15 * 60_000)
      return { ok: true, stored: true, emailed: false, duplicate: true };

    const token = [...crypto.getRandomValues(new Uint8Array(32))].map((b) => b.toString(16).padStart(2, "0")).join("");
    const tokenHash = await sha256Hex(token);
    const now = new Date().toISOString();
    const { data: lead, error } = await supabaseAdmin
      .from("early_access_leads")
      .upsert(
        { email: data.email, device: data.device || null, status: "pending", confirm_token_hash: tokenHash, consent_at: now, last_requested_at: now },
        { onConflict: "email" },
      )
      .select("id")
      .single();
    if (error) {
      console.error("lead upsert failed", error.message);
      return { ok: false, reason: "server", message: "We could not record your request. Please try again." };
    }

    const confirmUrl = `https://valexii.com/early-access/confirm?token=${token}`;
    const sent = await sendEmail({ to: data.email, ...renderEarlyAccessConfirm(confirmUrl), idempotencyKey: `ea-confirm-${lead.id}-${tokenHash.slice(0, 12)}` });
    return { ok: true, stored: true, emailed: sent.sent };
  });

export const confirmEarlyAccess = createServerFn({ method: "POST" })
  .inputValidator((d: unknown) => confirmSchema.parse(d))
  .handler(async ({ data }): Promise<{ ok: boolean }> => {
    const { supabaseAdmin } = await import("@/integrations/supabase/client.server");
    const { sha256Hex } = await import("./email-sender.server");
    const hash = await sha256Hex(data.token);
    const { data: rows, error } = await supabaseAdmin
      .from("early_access_leads")
      .update({ status: "confirmed", confirmed_at: new Date().toISOString() })
      .eq("confirm_token_hash", hash)
      .eq("status", "pending")
      .select("id");
    if (error) {
      console.error("confirm failed", error.message);
      return { ok: false };
    }
    return { ok: (rows?.length ?? 0) > 0 };
  });
