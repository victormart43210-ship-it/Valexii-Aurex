import { Link } from "@tanstack/react-router";
import { ArrowRight, Usb, QrCode, FileKey2, Hammer } from "lucide-react";
import { Button } from "@/components/ui/button";

export const supportFaq = [
  {
    question: "Is this an annual subscription?",
    answer:
      "No. Contributions do not buy 12 months, a license or product access. A possible future optional annual access offering is a vision only, conditional on commercial terms being finalized. Future pricing and eligibility will be announced separately.",
  },
  {
    question: "Why APK instead of Play?",
    answer:
      "Website APK distribution is a possible future option, not a decision to avoid Play requirements. Android officially supports call screening and website distribution with user opt-in for unknown apps. Play policy is not an Android permission bypass: the sandbox, OS restrictions, user permissions and applicable privacy rules still apply. Separately distributed builds may differ only when independently verified and lawful.",
  },
  {
    question: "Is it safe to install?",
    answer:
      "No APK is offered here, so installation safety is not established. A future release would need a verified official source, matching SHA-256, signed artifact, release notes, compatibility information and independent physical-device testing. These checks do not guarantee safety. Sideloading carries risk; do not disable safeguards or install unknown files on our behalf.",
  },
  {
    question: "What does the USB contain?",
    answer:
      "An optional archive request for public project materials, artwork, research summaries and documentation—not a functioning Android protection device. Availability, contents, costs and fulfillment require individual confirmation by email. Support does not create an entitlement or delivery commitment. Do not post a shipping address publicly.",
  },
  {
    question: "When will QR download be available?",
    answer:
      "No date is promised. A QR link to the same official verified download page is planned only after signed release verification, published SHA-256, release notes, compatibility and risk disclosures, and independent physical-device testing. Until those gates are satisfied, there is no QR code or download link.",
  },
];

const accessFormats = [
  {
    icon: FileKey2,
    tone: "border-primary",
    iconTone: "text-primary",
    label: "01 / PRIVATE DIGITAL ACCESS — PLANNED",
    title: "Official signed Android APK",
    body: "A future private link to the official signed Android APK, shared only once the release is independently verified. The release would include the signature, published SHA-256, compatibility information, release notes and installation guidance. No verified APK is offered on this website today.",
  },
  {
    icon: QrCode,
    tone: "border-gold",
    iconTone: "text-gold",
    label: "02 / SCAN TO DOWNLOAD — PLANNED",
    title: "QR to the same verified page",
    body: "A future QR code pointing to the same official verified download page—nothing more. There is no scannable code or active link now, and there will not be one until the release gates above are satisfied. The icon shown is a symbol, not a code.",
  },
  {
    icon: Usb,
    tone: "border-primary",
    iconTone: "text-primary",
    label: "03 / USB ARCHIVE — BY REQUEST",
    title: "Optional public materials archive",
    body: "An optional USB archive of public project materials, artwork, research summaries and documentation. Availability, contents, costs and fulfillment require individual confirmation by email. It is not an automatic entitlement, not a protection device, and contains no APK.",
  },
];

export function SupportRoadmap() {
  return (
    <>
      <section
        className="section-space border-y border-border"
        aria-labelledby="support-roadmap-title"
      >
        <div className="site-grid">
          <p className="text-sm text-primary">Three formats · two planned, one by request</p>
          <h2 id="support-roadmap-title" className="mt-3 font-display text-3xl">
            Understand the planned access paths.
          </h2>
          <p className="mt-5 max-w-3xl text-sm leading-7 text-muted-foreground">
            Three distinct paths—not a bundle, pre-order or protection promise. Nothing is delivered
            automatically, and no contribution guarantees any item.
          </p>
          <ol className="support-release-timeline mt-10 grid gap-8 md:grid-cols-3">
            {accessFormats.map(({ icon: Icon, tone, iconTone, label, title: t, body }) => (
              <li key={t} className={`border-t-2 ${tone} pt-6`}>
                <Icon className={iconTone} aria-hidden="true" size={30} />
                <p className={`mt-4 text-sm ${iconTone}`}>{label}</p>
                <h3 className="mt-3 font-display text-2xl">{t}</h3>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">{body}</p>
              </li>
            ))}
          </ol>
          <div className="mt-10 flex flex-wrap gap-3">
            <Button asChild variant="hero" className="min-h-11">
              <a
                href="https://cash.app/$illuminaughty210"
                target="_blank"
                rel="noopener noreferrer"
              >
                Support BCXMET Development <ArrowRight />
              </a>
            </Button>
            <Button asChild variant="glass" className="min-h-11">
              <Link to="/bcxmet" hash="command-center">
                Explore the BCXMET Demonstration <ArrowRight />
              </Link>
            </Button>
            <Button asChild variant="glass" className="min-h-11">
              <Link to="/contact">
                Ask About Future APK Access <ArrowRight />
              </Link>
            </Button>
          </div>
          <p className="mt-10 border-l-2 border-gold pl-5 text-sm leading-7">
            Voluntary support is not an investment, equity, purchase, subscription or pre-order. No
            APK, license, protection, release date or future access is guaranteed. Demonstrations
            and planned capabilities are not verified production protection. Any future download is
            conditional on security, release, compatibility and distribution gates. Evidence →
            Qualification → Reality → Authority → Effect: missing verification is never treated as
            passed.
          </p>
        </div>
      </section>
      <section className="section-space" aria-labelledby="support-trust-title">
        <div className="site-grid max-w-4xl">
          <Hammer className="text-primary" aria-hidden="true" />
          <h2 id="support-trust-title" className="mt-4 font-display text-3xl">
            You're supporting the work behind the technology.
          </h2>
          <p className="mt-5 text-sm leading-7 text-muted-foreground">
            Contributions support careful engineering, responsible testing and independent review.
            BCXMET aims to explain evidence and uncertainty while leaving control with you. That is
            the work to validate—not a promise that protection is already available. Where
            verification is missing, we say so; unknown is never presented as safe.
          </p>
          <Button asChild variant="hero" className="mt-6 min-h-11">
            <Link to="/bcxmet" hash="command-center">
              Explore call demo <ArrowRight />
            </Link>
          </Button>
        </div>
      </section>
      <section className="section-space border-t border-border" aria-labelledby="support-faq-title">
        <div className="site-grid max-w-4xl">
          <h2 id="support-faq-title" className="font-display text-3xl">
            Before you decide
          </h2>
          <div className="mt-8">
            {supportFaq.map(({ question, answer }) => (
              <details key={question} className="border-b border-border py-3">
                <summary className="min-h-11 cursor-pointer py-3 font-medium">{question}</summary>
                <p className="pb-4 text-sm leading-7 text-muted-foreground">{answer}</p>
              </details>
            ))}
          </div>
          <p className="mt-8 text-sm leading-7 text-muted-foreground">
            Official references:{" "}
            <a
              className="text-primary underline"
              href="https://developer.android.com/reference/android/telecom/CallScreeningService"
              target="_blank"
              rel="noopener noreferrer"
            >
              Android call screening
            </a>{" "}
            ·{" "}
            <a
              className="text-primary underline"
              href="https://developer.android.com/distribute/marketing-tools/alternative-distribution"
              target="_blank"
              rel="noopener noreferrer"
            >
              Website distribution
            </a>{" "}
            ·{" "}
            <a
              className="text-primary underline"
              href="https://support.google.com/googleplay/android-developer/answer/16559646"
              target="_blank"
              rel="noopener noreferrer"
            >
              Play policy
            </a>
            . These explain platform requirements, not BCXMET certification or legal approval.
          </p>
        </div>
      </section>
    </>
  );
}
