import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { AUREX_OX_STATUS } from "./aurex-ox-status";

const src = readFileSync("src/components/aurex-ox-status.tsx", "utf8");

describe("AUREX OX status", () => {
  it("never reports a live or connected state", () => {
    for (const s of AUREX_OX_STATUS) expect(s.state).toMatch(/^NOT /);
  });
  it("contains no local addresses, ports, paths, tokens or network calls", () => {
    expect(src).not.toMatch(
      /localhost|127\.0\.0\.1|:\d{4}|\/home\/|bearer|fetch\(|useServerFn|process\.env/i,
    );
  });
  it("public /aurex shows the panel without calling owner functions", () => {
    const route = readFileSync("src/routes/aurex.tsx", "utf8");
    expect(route).toContain('<AurexOxStatus context="public" />');
    expect(route).not.toContain("aurex-control.functions");
  });
  it("owner console keeps server-side auth and ssr:false", () => {
    const admin = readFileSync("src/routes/admin.aurex-control.tsx", "utf8");
    expect(admin).toContain("ssr: false");
    expect(admin).toContain('<AurexOxStatus context="owner" />');
    const fns = readFileSync("src/lib/aurex-control.functions.ts", "utf8");
    expect(fns.match(/requireSupabaseAuth\]/g)?.length).toBe(5);
  });
});
