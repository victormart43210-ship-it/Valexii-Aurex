import { describe, expect, it, vi } from "vitest";
import { earlyAccessSchema, inquirySchema } from "./inquiry-schema";
import { esc, renderEarlyAccessConfirm, renderInquiryNotification } from "./email-render";
import { emailConfigured, sendEmail } from "./email-sender.server";

const base = {
  kind: "contact",
  name: "Ada",
  email: "ADA@Example.com ",
  category: "Research",
  message: "Hello there, a question.",
  consent: true,
  website: "",
  startedAt: 1,
};

describe("inquiry validation", () => {
  it("accepts and normalizes valid input", () => {
    expect(inquirySchema.parse(base).email).toBe("ada@example.com");
  });
  it("rejects filled honeypot, missing consent, wrong category", () => {
    expect(inquirySchema.safeParse({ ...base, website: "spam" }).success).toBe(false);
    expect(inquirySchema.safeParse({ ...base, consent: false }).success).toBe(false);
    expect(inquirySchema.safeParse({ ...base, category: "Investment inquiry" }).success).toBe(
      false,
    );
    expect(
      inquirySchema.safeParse({ ...base, kind: "partnership", category: "Investment inquiry" })
        .success,
    ).toBe(true);
  });
  it("bounds message length", () => {
    expect(inquirySchema.safeParse({ ...base, message: "short" }).success).toBe(false);
    expect(inquirySchema.safeParse({ ...base, message: "x".repeat(4001) }).success).toBe(false);
  });
  it("early access requires consent and valid email", () => {
    expect(
      earlyAccessSchema.safeParse({ email: "a@b.co", consent: true, website: "", startedAt: 1 })
        .success,
    ).toBe(true);
    expect(
      earlyAccessSchema.safeParse({ email: "nope", consent: true, website: "", startedAt: 1 })
        .success,
    ).toBe(false);
  });
});

describe("email rendering", () => {
  it("escapes user content", () => {
    const { html } = renderInquiryNotification({
      kind: "contact",
      name: "<script>",
      email: "a@b.co",
      category: "Research",
      message: "<img onerror=x>",
      id: "1",
    });
    expect(html).not.toContain("<script>");
    expect(html).not.toContain("<img onerror");
    expect(esc(`"&'`)).toBe("&quot;&amp;&#39;");
  });
  it("confirmation makes no beta or protection promise", () => {
    expect(renderEarlyAccessConfirm("https://valexii.com/x").html).toContain(
      "not a beta invitation",
    );
  });
});

describe("sender gating (no real email is sent)", () => {
  const msg = { to: "a@b.co", subject: "s", html: "h" };
  it("does not send when disabled or keys missing", async () => {
    const f = vi.fn();
    expect(emailConfigured({})).toBe(false);
    expect(
      await sendEmail(msg, f as never, {
        EMAIL_SENDING_ENABLED: "false",
        LOVABLE_API_KEY: "k",
        RESEND_API_KEY: "r",
      }),
    ).toEqual({ sent: false, reason: "disabled" });
    expect(
      await sendEmail(msg, f as never, { EMAIL_SENDING_ENABLED: "true", LOVABLE_API_KEY: "k" }),
    ).toEqual({ sent: false, reason: "disabled" });
    expect(f).not.toHaveBeenCalled();
  });
  it("uses the gateway with a mocked fetch and reports failures", async () => {
    const env = { EMAIL_SENDING_ENABLED: "true", LOVABLE_API_KEY: "k", RESEND_API_KEY: "r" };
    const ok = vi.fn(async () => new Response("{}", { status: 200 }));
    expect(await sendEmail(msg, ok as never, env)).toEqual({ sent: true });
    const [url, init] = ok.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("https://connector-gateway.lovable.dev/resend/emails");
    expect(JSON.parse(String(init.body)).from).toContain("@valexii.com");
    const bad = vi.fn(async () => new Response("no", { status: 403 }));
    expect(await sendEmail(msg, bad as never, env)).toEqual({ sent: false, reason: "error" });
  });
});
