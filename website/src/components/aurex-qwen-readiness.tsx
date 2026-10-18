import { useState } from "react";

/**
 * Operator-only *instructions*, not device telemetry or a browser-side model API.
 * Mount only behind the server-verified owner gate in the existing admin route.
 */
const commands = [
  {
    title: "1. Test installed AUREX source",
    text: "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_qwen_readiness.py",
  },
  {
    title: "2. Check local llama.cpp Qwen model registration (no inference)",
    text: "python -m workstation.qwen_readiness --backend llama.cpp --model '<loaded-model-id>' --check",
  },
  {
    title: "3. Optional, explicit local synthetic inference",
    text: "python -m workstation.qwen_readiness --backend llama.cpp --model '<loaded-model-id>' --infer --approve-local",
  },
] as const;

export function AurexQwenReadiness() {
  const [copied, setCopied] = useState<number | null>(null);

  async function copy(text: string, index: number) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(index);
    } catch {
      setCopied(null);
    }
  }

  return (
    <section aria-labelledby="qwen-readiness-title" className="mt-10 rounded-xl border border-primary/30 bg-background/60 p-5 sm:p-7" data-testid="qwen-readiness">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">KUSANAGI XCIV · LOCAL MODEL LAB</p>
      <h2 id="qwen-readiness-title" className="mt-2 font-display text-2xl">Qwen workstation readiness</h2>
      <p className="mt-3 text-sm text-muted-foreground">
        This is an operator checklist, NOT live machine telemetry. The model file was previously reported on a local computer;
        its loading, inference, and frontend-to-backend connection have not been verified.
      </p>
      <div className="mt-4 flex flex-wrap gap-2 text-xs" aria-label="Current evidence state">
        <span className="rounded-md border border-amber/60 px-3 py-2 text-amber">MODEL STARTUP: NOT VERIFIED</span>
        <span className="rounded-md border border-amber/60 px-3 py-2 text-amber">LOCAL INFERENCE: NOT RUN</span>
        <span className="rounded-md border border-primary/50 px-3 py-2 text-primary">EXTERNAL SPEND: $0 DEFAULT</span>
        <span className="rounded-md border border-border px-3 py-2">AUTHORITY: NONE</span>
      </div>
      <p className="mt-5 text-sm text-muted-foreground">
        Run these commands in your own checked-out AUREX repository on Linux/WSL after confirming
        Python 3.12+, your local model server, and the exact model identifier. Never run them in the public website.
        The local llama.cpp server uses 127.0.0.1:8080; Ollama is also supported on 127.0.0.1:11434.
      </p>
      <ol className="mt-5 space-y-4">
        {commands.map((step, i) => (
          <li key={step.title} className="rounded-lg border border-border p-4">
            <p className="mb-2 text-sm font-semibold text-foreground">{step.title}</p>
            <pre className="overflow-x-auto rounded-md bg-card p-3 text-xs text-foreground"><code>{step.text}</code></pre>
            <button
              type="button"
              className="mt-3 min-h-11 rounded-md border border-primary/50 px-4 py-2 text-sm text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              onClick={() => void copy(step.text, i)}
              aria-label={"Copy command " + (i + 1)}
            >
              {copied === i ? "Copied" : "Copy command"}
            </button>
          </li>
        ))}
      </ol>
      <p className="mt-4 text-sm text-amber">
        Model-list availability is not evidence of successful inference. An observed synthetic response remains
        unverified and never grants BCXMET or financial authority. No model download, public inference endpoint,
        payment, or job execution is activated by this panel.
      </p>
      <p className="mt-4 text-sm">
        <a
          className="underline underline-offset-4 text-primary"
          href="https://github.com/victormart43210-ship-it/Valexii-Aurex"
          rel="noopener noreferrer"
          target="_blank"
        >
          Canonical AUREX backend repository
        </a>
        {" · "}
        <a
          className="underline underline-offset-4 text-primary"
          href="https://github.com/victormart43210-ship-it/Valexii-Aurex/pulls"
          rel="noopener noreferrer"
          target="_blank"
        >
          Integration reviews
        </a>
      </p>
    </section>
  );
}
