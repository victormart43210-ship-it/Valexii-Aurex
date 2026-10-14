import { useId, useRef, useState } from "react";
import { Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { Button } from "@/components/ui/button";
import { requestEarlyAccess, submitInquiry } from "@/lib/inquiries.functions";
import {
  CONTACT_CATEGORIES,
  earlyAccessSchema,
  inquirySchema,
  PARTNERSHIP_CATEGORIES,
  type SubmitResult,
} from "@/lib/inquiry-schema";

type Status = { tone: "ok" | "warn" | "error"; text: string } | null;
const field = "min-h-12 w-full rounded-sm border border-input bg-background px-4 text-foreground";
const label = "mb-2 block text-sm font-semibold";

function describe(r: SubmitResult, what: string): Status {
  if (!r.ok) return { tone: "error", text: r.message };
  if (r.duplicate)
    return {
      tone: "ok",
      text: `Thanks — this ${what} was already received. No duplicate was created.`,
    };
  if (r.emailed)
    return {
      tone: "ok",
      text: `Thanks — your ${what} was received and stored. A confirmation email is on its way.`,
    };
  return {
    tone: "warn",
    text: `Your ${what} was received and stored securely. Email confirmations are not active yet, so no email will arrive.`,
  };
}

function StatusLine({ status }: { status: Status }) {
  if (!status) return null;
  const cls =
    status.tone === "error"
      ? "border-destructive/50 text-destructive"
      : status.tone === "warn"
        ? "border-amber/40 text-amber"
        : "border-primary/40 text-primary";
  return (
    <p
      role={status.tone === "error" ? "alert" : "status"}
      className={`rounded-sm border bg-card p-4 text-sm ${cls}`}
    >
      {status.text}
    </p>
  );
}

function Honeypot() {
  return (
    <div aria-hidden="true" className="absolute -left-[9999px] h-px w-px overflow-hidden">
      <label>
        Website
        <input name="website" tabIndex={-1} autoComplete="off" defaultValue="" />
      </label>
    </div>
  );
}

function Consent({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <label
      htmlFor={id}
      className="flex min-h-11 items-start gap-3 text-sm leading-6 text-muted-foreground"
    >
      <input
        id={id}
        name="consent"
        type="checkbox"
        required
        className="mt-1 size-5 shrink-0 accent-[var(--primary)]"
      />
      <span>{children}</span>
    </label>
  );
}

/** Contact or partnership inquiry; stored server-side, never a mailto draft. */
export function InquiryForm({ kind }: { kind: "contact" | "partnership" }) {
  const id = useId();
  const send = useServerFn(submitInquiry);
  const started = useRef(Date.now());
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<Status>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const cats = kind === "contact" ? CONTACT_CATEGORIES : PARTNERSHIP_CATEGORIES;
  const what = kind === "contact" ? "message" : "partnership inquiry";

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy) return;
    const form = e.currentTarget;
    const f = new FormData(form);
    const payload = {
      kind,
      name: String(f.get("name") ?? ""),
      email: String(f.get("email") ?? ""),
      organization: String(f.get("organization") ?? ""),
      category: String(f.get("category") ?? ""),
      message: String(f.get("message") ?? ""),
      consent: f.get("consent") === "on",
      website: String(f.get("website") ?? ""),
      startedAt: started.current,
    };
    const parsed = inquirySchema.safeParse(payload);
    if (!parsed.success) {
      const errs: Record<string, string> = {};
      for (const i of parsed.error.issues) errs[String(i.path[0])] ??= i.message;
      setErrors(errs);
      setStatus({ tone: "error", text: "Please fix the highlighted fields." });
      return;
    }
    setErrors({});
    setBusy(true);
    setStatus(null);
    try {
      const r = await send({ data: payload });
      setStatus(describe(r, what));
      if (r.ok) form.reset();
    } catch {
      setStatus({
        tone: "error",
        text: "Something went wrong and your message was not confirmed as saved. Please try again.",
      });
    } finally {
      setBusy(false);
    }
  }

  const err = (k: string) =>
    errors[k] ? (
      <p id={`${id}-${k}-err`} className="mt-2 text-sm text-destructive">
        {errors[k]}
      </p>
    ) : null;
  const a = (k: string) => ({
    "aria-invalid": !!errors[k] || undefined,
    "aria-describedby": errors[k] ? `${id}-${k}-err` : undefined,
  });

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      aria-busy={busy}
      className="relative grid gap-6 rounded-md border border-border bg-card p-6 sm:p-8"
      data-form={kind}
    >
      <Honeypot />
      <div>
        <label htmlFor={`${id}-category`} className={label}>
          {kind === "contact" ? "Inquiry category" : "Partnership type"}
        </label>
        <select id={`${id}-category`} name="category" required className={field} {...a("category")}>
          {cats.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
        {err("category")}
      </div>
      <div className="grid gap-6 sm:grid-cols-2">
        <div>
          <label htmlFor={`${id}-name`} className={label}>
            Name
          </label>
          <input
            id={`${id}-name`}
            name="name"
            required
            maxLength={100}
            autoComplete="name"
            className={field}
            {...a("name")}
          />
          {err("name")}
        </div>
        <div>
          <label htmlFor={`${id}-email`} className={label}>
            Email
          </label>
          <input
            id={`${id}-email`}
            name="email"
            type="email"
            required
            maxLength={254}
            autoComplete="email"
            className={field}
            {...a("email")}
          />
          {err("email")}
        </div>
      </div>
      {kind === "partnership" && (
        <div>
          <label htmlFor={`${id}-org`} className={label}>
            Organization <span className="font-normal text-muted-foreground">(optional)</span>
          </label>
          <input
            id={`${id}-org`}
            name="organization"
            maxLength={150}
            autoComplete="organization"
            className={field}
          />
        </div>
      )}
      <div>
        <label htmlFor={`${id}-message`} className={label}>
          Message
        </label>
        <textarea
          id={`${id}-message`}
          name="message"
          required
          minLength={10}
          maxLength={4000}
          rows={6}
          className="w-full rounded-sm border border-input bg-background p-4"
          {...a("message")}
        />
        {err("message")}
      </div>
      <Consent id={`${id}-consent`}>
        I agree that VALEXII.AI stores this message to respond to me, as described in the{" "}
        <Link to="/privacy" className="underline">
          Privacy notice
        </Link>
        . I will keep it non-confidential.
      </Consent>
      {err("consent")}
      <Button type="submit" variant="hero" className="min-h-11 justify-self-start" disabled={busy}>
        {busy ? "Sending…" : kind === "contact" ? "Send message" : "Send partnership inquiry"}
      </Button>
      <StatusLine status={status} />
    </form>
  );
}

/** BCXMET early-access interest with double opt-in confirmation. */
export function EarlyAccessForm() {
  const id = useId();
  const send = useServerFn(requestEarlyAccess);
  const started = useRef(Date.now());
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<Status>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy) return;
    const form = e.currentTarget;
    const f = new FormData(form);
    const payload = {
      email: String(f.get("email") ?? ""),
      device: String(f.get("device") ?? ""),
      consent: f.get("consent") === "on",
      website: String(f.get("website") ?? ""),
      startedAt: started.current,
    };
    const parsed = earlyAccessSchema.safeParse(payload);
    if (!parsed.success) {
      setStatus({
        tone: "error",
        text: parsed.error.issues[0]?.message ?? "Please check the form.",
      });
      return;
    }
    setBusy(true);
    setStatus(null);
    try {
      const r = await send({ data: payload });
      if (r.ok && r.emailed)
        setStatus({
          tone: "ok",
          text: "Check your inbox and confirm the email to complete your request.",
        });
      else if (r.ok && r.duplicate)
        setStatus({
          tone: "ok",
          text: "Request received. If a confirmation is pending, check your inbox.",
        });
      else setStatus(describe(r, "early-access request"));
      if (r.ok) form.reset();
    } catch {
      setStatus({
        tone: "error",
        text: "Something went wrong and your request was not confirmed as saved. Please try again.",
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      aria-busy={busy}
      className="relative grid gap-5 rounded-md border border-border bg-card p-6"
      data-form="early-access"
    >
      <Honeypot />
      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label htmlFor={`${id}-email`} className={label}>
            Email
          </label>
          <input
            id={`${id}-email`}
            name="email"
            type="email"
            required
            maxLength={254}
            autoComplete="email"
            className={field}
          />
        </div>
        <div>
          <label htmlFor={`${id}-device`} className={label}>
            Android device <span className="font-normal text-muted-foreground">(optional)</span>
          </label>
          <input
            id={`${id}-device`}
            name="device"
            maxLength={80}
            placeholder="e.g. Pixel 8, Android 15"
            className={field}
          />
        </div>
      </div>
      <Consent id={`${id}-consent`}>
        Email me about BCXMET early-access opportunities. I will confirm by email first; I can ask
        to be removed anytime. Interest is not a beta invitation, download or protection. See the{" "}
        <Link to="/privacy" className="underline">
          Privacy notice
        </Link>
        .
      </Consent>
      <Button type="submit" variant="hero" className="min-h-11 justify-self-start" disabled={busy}>
        {busy ? "Submitting…" : "Request early-access updates"}
      </Button>
      <StatusLine status={status} />
    </form>
  );
}
