import { z } from "zod";

/** Browser-safe schemas shared by the forms and the server functions. */
export const CONTACT_CATEGORIES = [
  "Research",
  "Security review",
  "University testing",
  "Commercialization",
  "Product interest",
  "General",
] as const;

export const PARTNERSHIP_CATEGORIES = [
  "Investment inquiry",
  "Grants / NSF proposal collaboration",
  "University research partnership",
  "Strategic partnership / acquisition",
  "Industrial pilot discussion",
] as const;

const email = z.string().trim().toLowerCase().email("Enter a valid email address.").max(254);
const antiSpam = {
  website: z.string().max(0), // honeypot must remain empty
  startedAt: z.number().int().positive(),
};

export const inquirySchema = z.object({
  kind: z.enum(["contact", "partnership"]),
  name: z.string().trim().min(1, "Enter your name.").max(100),
  email,
  organization: z.string().trim().max(150).optional().default(""),
  category: z.string().trim().min(1).max(80),
  message: z
    .string()
    .trim()
    .min(10, "Message must be at least 10 characters.")
    .max(4000, "Message must be under 4,000 characters."),
  consent: z.literal(true, { errorMap: () => ({ message: "Consent is required to submit." }) }),
  ...antiSpam,
}).superRefine((v, ctx) => {
  const allowed: readonly string[] = v.kind === "contact" ? CONTACT_CATEGORIES : PARTNERSHIP_CATEGORIES;
  if (!allowed.includes(v.category)) ctx.addIssue({ code: "custom", path: ["category"], message: "Choose a category." });
});

export const earlyAccessSchema = z.object({
  email,
  device: z.string().trim().max(80).optional().default(""),
  consent: z.literal(true, { errorMap: () => ({ message: "Consent is required to request early access." }) }),
  ...antiSpam,
});

export const confirmSchema = z.object({ token: z.string().regex(/^[a-f0-9]{64}$/) });

export type InquiryInput = z.input<typeof inquirySchema>;
export type EarlyAccessInput = z.input<typeof earlyAccessSchema>;

export type SubmitResult =
  | { ok: true; stored: true; emailed: boolean; duplicate?: boolean }
  | { ok: false; reason: "invalid" | "rate" | "server"; message: string };

export const MIN_FILL_MS = 2500;
