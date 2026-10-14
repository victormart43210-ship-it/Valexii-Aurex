import { useEffect, useState } from "react";
import { useRouterState } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import {
  activationEventNames,
  activationStatus,
  captureAttribution,
  clearAttribution,
  emitActivation,
  setActivationConsent,
  type ActivationEventName,
} from "@/lib/activation-events";
const consentKey = "valexii-activation-consent";
export function ActivationConsent() {
  const [allowed, setAllowed] = useState(false);
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  useEffect(() => {
    // Only consent preference is persisted. No visitor/session identifier is generated.
    try {
      const yes = localStorage.getItem(consentKey) === "yes";
      setAllowed(yes);
      setActivationConsent(yes);
    } catch {
      setActivationConsent(false);
    }
    return () => setActivationConsent(false);
  }, []);
  useEffect(() => {
    if (!allowed) return;
    captureAttribution();
    try {
      if (!sessionStorage.getItem("valexii-activation-visit")) {
        if (localStorage.getItem("valexii-activation-seen") === "yes") {
          emitActivation("return_session");
          emitActivation("return_visit");
        }
        sessionStorage.setItem("valexii-activation-visit", "yes");
        localStorage.setItem("valexii-activation-seen", "yes");
      }
    } catch {
      /* No storage means no return-session observation. */
    }
  }, [allowed]);
  useEffect(() => {
    const depths = new Set<number>();
    let scheduled = false;
    const scroll = () => {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(() => {
        scheduled = false;
        const range = document.documentElement.scrollHeight - innerHeight;
        const percent = range > 0 ? (scrollY / range) * 100 : 0;
        for (const depth of [25, 50, 75, 100] as const)
          if (percent >= depth && !depths.has(depth)) {
            depths.add(depth);
            emitActivation("scroll_depth", depth);
          }
      });
    };
    const click = (event: MouseEvent) => {
      if (!(event.target instanceof Element)) return;
      const link = event.target.closest("[data-activation], a");
      const name = link?.getAttribute("data-activation");
      if (name && activationEventNames.includes(name as ActivationEventName))
        emitActivation(name as ActivationEventName);
      else if (
        link instanceof HTMLAnchorElement &&
        link
          .getAttribute("href")
          ?.startsWith("mailto:developer@valexii.com?subject=Weekly%20Research%20Dispatch")
      )
        emitActivation("opt_in_request");
      else if (
        link instanceof HTMLAnchorElement &&
        link.getAttribute("href")?.startsWith("https://cash.app/")
      )
        emitActivation("support_cta_click");
    };
    const exit = () => emitActivation("page_exit");
    document.addEventListener("click", click);
    window.addEventListener("scroll", scroll, { passive: true });
    window.addEventListener("pagehide", exit);
    return () => {
      exit();
      document.removeEventListener("click", click);
      window.removeEventListener("scroll", scroll);
      window.removeEventListener("pagehide", exit);
    };
  }, [pathname]);
  const change = (yes: boolean) => {
    setActivationConsent(yes);
    setAllowed(yes);
    try {
      localStorage.setItem(consentKey, yes ? "yes" : "no");
      if (!yes) {
        localStorage.removeItem("valexii-activation-seen");
        sessionStorage.removeItem("valexii-activation-visit");
        clearAttribution();
      }
    } catch {
      /* Consent still applies for this page lifetime. */
    }
  };
  return (
    <aside
      className="border-t border-border bg-background py-5"
      aria-label="Optional measurement preferences"
    >
      <div className="site-grid">
        <details>
          <summary className="min-h-11 cursor-pointer text-xs text-muted-foreground">
            Optional usage measurement · {allowed ? "allowed" : "off"}
          </summary>
          <p className="max-w-2xl text-xs leading-6 text-muted-foreground">
            Optional aggregate event names only; no phone numbers, app lists, messages or visitor
            IDs. Consent and a yes/no visit marker are stored only if allowed.{" "}
            {activationStatus().connected
              ? "An event adapter is configured; delivery and retention remain unverified."
              : "TELEMETRY NOT CONNECTED / NOT MEASURED. No events are sent or queued."}{" "}
            Declining does not affect the site.
          </p>
          <div className="mt-3 flex flex-wrap gap-3">
            <Button variant="glass" aria-pressed={allowed} onClick={() => change(true)}>
              Allow optional events
            </Button>
            <Button variant="glass" aria-pressed={!allowed} onClick={() => change(false)}>
              Decline / withdraw
            </Button>
          </div>
        </details>
      </div>
    </aside>
  );
}
