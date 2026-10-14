/**
 * Server-only Resend sender via the Lovable connector gateway.
 * Sends ONLY when EMAIL_SENDING_ENABLED === "true" AND the keys exist; otherwise
 * returns { sent: false } so callers report "stored, not emailed" honestly.
 */
const GATEWAY_URL = "https://connector-gateway.lovable.dev/resend";
export const FROM_ADDRESS = "VALEXII.AI <noreply@valexii.com>";
export const TEAM_INBOX = "developer@valexii.com";

export type SendResult = { sent: boolean; reason?: "disabled" | "error" };

export function emailConfigured(env: Record<string, string | undefined> = process.env): boolean {
  return env["EMAIL_SENDING_ENABLED"] === "true" && !!env["LOVABLE_API_KEY"] && !!env["RESEND_API_KEY"];
}

export async function sendEmail(
  msg: { to: string; subject: string; html: string; replyTo?: string; idempotencyKey?: string },
  fetchImpl: typeof fetch = fetch,
  env: Record<string, string | undefined> = process.env,
): Promise<SendResult> {
  if (!emailConfigured(env)) return { sent: false, reason: "disabled" };
  try {
    const res = await fetchImpl(`${GATEWAY_URL}/emails`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${env["LOVABLE_API_KEY"]}`,
        "X-Connection-Api-Key": env["RESEND_API_KEY"]!,
        ...(msg.idempotencyKey ? { "Idempotency-Key": msg.idempotencyKey } : {}),
      },
      body: JSON.stringify({
        from: FROM_ADDRESS,
        to: [msg.to],
        subject: msg.subject,
        html: msg.html,
        ...(msg.replyTo ? { reply_to: msg.replyTo } : {}),
      }),
    });
    if (!res.ok) {
      console.error(`Email send failed [${res.status}]: ${(await res.text()).slice(0, 300)}`);
      return { sent: false, reason: "error" };
    }
    return { sent: true };
  } catch (e) {
    console.error("Email send error", e);
    return { sent: false, reason: "error" };
  }
}

export async function sha256Hex(input: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
