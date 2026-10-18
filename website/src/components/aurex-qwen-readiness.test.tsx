import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { AurexQwenReadiness } from "./aurex-qwen-readiness";

describe("Qwen operator-only staging panel", () => {
  it("reports unknown machine status and refuses to invent a local model result", () => {
    const html = renderToStaticMarkup(<AurexQwenReadiness />);
    expect(html).toContain("MODEL STARTUP: NOT VERIFIED");
    expect(html).toContain("LOCAL INFERENCE: NOT RUN");
    expect(html).toContain("EXTERNAL SPEND: $0 DEFAULT");
    expect(html).toContain("AUTHORITY: NONE");
    expect(html).not.toContain("MODEL: READY");
    expect(html).not.toContain("Qwen connected");
  });

  it("provides a gated local CLI workflow without embedding credentials or browser inference", () => {
    const html = renderToStaticMarkup(<AurexQwenReadiness />);
    expect(html).toContain("--check");
    expect(html).toContain("--infer --approve-local");
    expect(html).not.toContain("AUREX_SERVICE_TOKEN");
    expect(html).not.toContain("VITE_");
    expect(html).not.toContain("<form");
  });
});
