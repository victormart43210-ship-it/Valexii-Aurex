import { createFileRoute, Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useEffect, useState } from "react";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { PageHero, PageShell } from "@/components/site";
import { confirmEarlyAccess } from "@/lib/inquiries.functions";

export const Route = createFileRoute("/early-access/confirm")({
  validateSearch: z.object({ token: z.string().optional() }),
  head: () => ({
    meta: [
      { title: "Confirm BCXMET early-access interest — VALEXII.AI" },
      { name: "description", content: "Confirm your BCXMET early-access email request. Interest is not a beta invitation or download." },
      { name: "robots", content: "noindex, nofollow" },
      { property: "og:title", content: "Confirm BCXMET early-access interest — VALEXII.AI" },
      { property: "og:description", content: "Confirm your BCXMET early-access email request." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Confirm,
});

function Confirm() {
  const { token } = Route.useSearch();
  const confirm = useServerFn(confirmEarlyAccess);
  const [state, setState] = useState<"idle" | "busy" | "ok" | "fail">("idle");
  const valid = !!token && /^[a-f0-9]{64}$/.test(token);

  // Confirmation needs an explicit click so mail scanners that prefetch links cannot confirm.
  async function run() {
    if (!valid) return;
    setState("busy");
    try {
      const r = await confirm({ data: { token: token! } });
      setState(r.ok ? "ok" : "fail");
    } catch {
      setState("fail");
    }
  }
  useEffect(() => { if (!valid) setState("fail"); }, [valid]);

  return (
    <PageShell>
      <PageHero eyebrow="BCXMET early access" title="Confirm your interest.">
        {state === "ok" ? (
          <p role="status">Confirmed. You will receive occasional early-access updates. This is not a beta invitation, download or device protection.</p>
        ) : state === "fail" ? (
          <p role="alert">This link is invalid, expired or already used. You can request a new one on the BCXMET page.</p>
        ) : (
          <p>Press the button to confirm you asked for BCXMET early-access emails.</p>
        )}
        <div className="mt-6 flex flex-wrap gap-3">
          {state !== "ok" && state !== "fail" && (
            <Button variant="hero" className="min-h-11" onClick={run} disabled={state === "busy"}>
              {state === "busy" ? "Confirming…" : "Confirm early-access interest"}
            </Button>
          )}
          <Button asChild variant="glass" className="min-h-11"><Link to="/bcxmet">Back to BCXMET</Link></Button>
        </div>
      </PageHero>
    </PageShell>
  );
}
